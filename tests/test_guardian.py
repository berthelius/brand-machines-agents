import copy
from datetime import date
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/brand-machines'
SCRIPT = SKILL / 'scripts/bm.py'
spec = importlib.util.spec_from_file_location('bm', SCRIPT)
bm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bm)
TODAY = date(2026, 9, 27)


class GuardianTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name) / 'pack'
        shutil.copytree(SKILL / 'assets/brand-machines', self.base)
        self.path = self.base / 'brand.json'
        self.pack = bm.load_pack(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def example(self, name):
        return bm.read_json(SKILL / 'assets/examples' / f'{name}.json')

    def test_chapter_17_detects_both_issues_with_sources(self):
        out = bm.review(self.pack, self.example('chapter-17'), TODAY)
        self.assertEqual(out['status'], 'revise')
        self.assertEqual({f['check'] for f in out['findings']}, {'no_superlativos', 'exclamaciones_excesivas'})
        self.assertTrue(all(f['sources'] and f['suggestion'] for f in out['findings']))

    def test_variation_has_no_false_mechanical_approval(self):
        out = bm.review(self.pack, self.example('variation'), TODAY)
        self.assertTrue(out['checks_passed'])
        self.assertEqual(out['status'], 'needs_review')
        self.assertEqual(out['semantic_review'], 'pending')
        self.assertFalse(out['publication_authorized'])

    def test_semantic_contradiction_is_outside_mechanical_scope(self):
        out = bm.review(self.pack, self.example('semantic-contradiction'), TODAY)
        self.assertEqual(out['status'], 'needs_review')
        self.assertFalse(out['publication_authorized'])

    def test_unsupported_claim_needs_evidence(self):
        out = bm.review(self.pack, self.example('unsupported-claim'), TODAY)
        self.assertEqual(out['status'], 'needs_evidence')
        self.assertEqual(len(out['missing_evidence']), 1)

    def test_unknown_and_expired_evidence_do_not_pass(self):
        artifact = self.example('unsupported-claim')
        for source in ('unknown', 'editorial'):
            with self.subTest(source=source):
                artifact['claims'][0]['sources'] = [source]
                self.pack['sources'][1]['valid_until'] = '2026-09-26'
                self.assertEqual(bm.review(self.pack, artifact, TODAY)['status'], 'needs_evidence')

    def test_source_expiry_requires_calendar_date_and_includes_last_day(self):
        source = self.pack['sources'][0]
        for value in ('20260101', '2026-W01-1', '2026-02-30'):
            source['valid_until'] = value
            with self.subTest(value=value), self.assertRaises(bm.Invalid):
                bm.validate_pack(self.pack, self.base)
        source['valid_until'] = '2026-09-27'
        bm.validate_pack(self.pack, self.base)
        self.assertIn(source['id'], bm.current_sources(self.pack, TODAY))
        self.assertNotIn(source['id'], bm.current_sources(self.pack, date(2026, 9, 28)))

    def test_source_presence_is_not_semantic_approval(self):
        artifact = self.example('unsupported-claim')
        artifact['claims'][0]['sources'] = ['editorial']
        out = bm.review(self.pack, artifact, TODAY)
        self.assertEqual(out['status'], 'needs_review')
        self.assertEqual(out['semantic_review'], 'pending')

    def test_claim_must_be_grounded_in_the_submitted_content(self):
        artifact = self.example('unsupported-claim')
        artifact['claims'][0]['text'] = 'Una afirmación que no aparece'
        with self.assertRaises(bm.Invalid):
            bm.review(self.pack, artifact, TODAY)

    def test_canonical_layer_drift_is_detected(self):
        artifact = self.example('variation')
        artifact['layers'] = bm.LAYERS[:-1] + ['Conexiones']
        self.assertEqual(bm.review(self.pack, artifact, TODAY)['status'], 'revise')
        artifact['layers'] = list(bm.LAYERS)
        self.assertEqual(bm.review(self.pack, artifact, TODAY)['status'], 'needs_review')

    def test_rules_are_contextual(self):
        artifact = self.example('chapter-17')
        artifact['context'] = 'critical_quotation'
        out = bm.review(self.pack, artifact, TODAY)
        self.assertFalse(out['findings'])
        self.assertEqual(out['status'], 'needs_review')

    def test_terms_use_word_boundaries_and_unicode_normalization(self):
        artifact = self.example('variation')
        artifact['content'] = 'La mejoría de una marca se observa.'
        self.assertFalse(bm.review(self.pack, artifact, TODAY)['findings'])
        artifact['content'] = 'Ｌａ ＭＥＪＯＲ oferta'
        self.assertEqual(bm.review(self.pack, artifact, TODAY)['status'], 'revise')

    def test_other_brand_can_choose_different_expression(self):
        self.pack['id'] = 'another-brand'
        self.pack['name'] = 'Otra marca (fixture técnico)'
        self.pack['checks'] = []
        out = bm.review(self.pack, self.example('chapter-17'), TODAY)
        self.assertFalse(out['findings'])
        self.assertEqual(out['brand'], 'another-brand')

    def test_coverage_does_not_invent_missing_layers(self):
        self.pack['layers'][0]['summary'] = ''
        out = bm.diagnose(self.pack, TODAY)
        self.assertEqual(out['scope'], 'documentation_coverage')
        self.assertEqual(out['missing_layers'], ['Núcleo'])
        self.assertEqual(bm.review(self.pack, self.example('variation'), TODAY)['status'], 'needs_evidence')

    def test_unaudited_source_changes_fail(self):
        (self.base / 'sources/editorial.md').write_text('changed')
        with self.assertRaises(bm.Invalid):
            bm.load_pack(self.path)

    def test_paths_and_symlinks_cannot_escape_pack(self):
        source = self.pack['sources'][0]
        original = source['path']
        source['path'] = '../../secret.md'
        with self.assertRaises(bm.Invalid):
            bm.validate_pack(self.pack, self.base)
        outside = Path(self.tmp.name) / 'outside.md'
        outside.write_text('outside')
        link = self.base / 'escape.md'
        link.symlink_to(outside)
        source['path'] = 'escape.md'
        with self.assertRaises(bm.Invalid):
            bm.validate_pack(self.pack, self.base)
        source['path'] = original

    def test_bad_shapes_and_unknown_check_fail_closed(self):
        for value in (None, [], {}, 'unknown'):
            pack = copy.deepcopy(self.pack)
            pack['checks'][0]['kind'] = value
            with self.subTest(value=value), self.assertRaises(bm.Invalid):
                bm.validate_pack(pack, self.base)
        pack = copy.deepcopy(self.pack)
        pack['layers'][0]['id'] = True
        with self.assertRaises(bm.Invalid):
            bm.validate_pack(pack, self.base)

    def test_duplicate_keys_and_nonfinite_numbers_rejected(self):
        for raw in (b'{"content":"first","content":"second"}', b'{"maximum": NaN}'):
            with self.subTest(raw=raw), self.assertRaises(bm.Invalid):
                bm.decode(raw)

    def test_cli_works_outside_repository(self):
        for example, code in [('chapter-17', 1), ('variation', 0)]:
            run = subprocess.run([sys.executable, str(SCRIPT), 'review', '--input',
                                  str(SKILL / 'assets/examples' / f'{example}.json')],
                                 cwd=self.tmp.name, capture_output=True, text=True)
            self.assertEqual(run.returncode, code, run.stderr)
            self.assertEqual(json.loads(run.stdout)['semantic_review'], 'pending')

    def test_api_uses_same_guardian_and_rechecks_sources(self):
        server = bm.make_server(self.path, 0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url = f'http://127.0.0.1:{server.server_port}/api/v1/validate'
        data = json.dumps(self.example('chapter-17')).encode()
        try:
            request = Request(url, data=data, headers={'Content-Type': 'application/json'})
            with urlopen(request, timeout=3) as response:
                out = json.load(response)
            self.assertEqual(out['status'], 'revise')
            (self.base / 'sources/editorial.md').write_text('changed')
            with self.assertRaises(HTTPError) as error:
                urlopen(request, timeout=3)
            self.assertEqual(error.exception.code, 400)
            error.exception.close()
            with self.assertRaises(HTTPError) as error:
                urlopen(Request(url, data=data), timeout=3)
            self.assertEqual(error.exception.code, 415)
            error.exception.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)

    def test_bilingual_examples_preserve_review_boundaries(self):
        for language, directory, layers in [('es', 'brand-machines', bm.LAYERS),
                                            ('en', 'brand-machines-en', bm.LAYERS_EN)]:
            pack = bm.load_pack(SKILL / 'assets' / directory / 'brand.json')
            prefix = 'en/' if language == 'en' else ''
            with self.subTest(language=language):
                for example, status in [('chapter-17', 'revise'), ('variation', 'needs_review'),
                                        ('semantic-contradiction', 'needs_review'),
                                        ('unsupported-claim', 'needs_evidence')]:
                    out = bm.review(pack, self.example(prefix + example), TODAY)
                    self.assertEqual((out['status'], out['language']), (status, language))
                    self.assertEqual(out['semantic_review'], 'pending')
                    self.assertFalse(out['publication_authorized'])
                chapter = bm.review(pack, self.example(prefix + 'chapter-17'), TODAY)
                self.assertEqual({f['check'] for f in chapter['findings']},
                                 {'no_superlativos', 'exclamaciones_excesivas'})
                self.assertEqual({f['layer'] for f in chapter['findings']}, {layers[3]})
                artifact = self.example(prefix + 'variation')
                artifact['layers'] = layers
                self.assertEqual(bm.review(pack, artifact, TODAY)['status'], 'needs_review')
                artifact['layers'] = bm.LAYERS_EN if language == 'es' else bm.LAYERS
                self.assertEqual(bm.review(pack, artifact, TODAY)['status'], 'revise')
        en = bm.load_pack(bm.ENGLISH_PACK)
        artifact = self.example('en/variation')
        artifact['content'] = 'The bestiary contains many creatures.'
        self.assertFalse(bm.review(en, artifact, TODAY)['findings'])

    def test_language_boundaries_and_legacy_spanish_packs(self):
        legacy = copy.deepcopy(self.pack)
        del legacy['language']
        bm.validate_pack(legacy, self.base)
        self.assertEqual(bm.review(legacy, self.example('variation'), TODAY)['language'], 'es')
        for language in ('fr', None, []):
            invalid = copy.deepcopy(self.pack)
            invalid['language'] = language
            with self.subTest(language=language), self.assertRaises(bm.Invalid):
                bm.validate_pack(invalid, self.base)
        with self.assertRaises(bm.Invalid):
            bm.review(self.pack, self.example('en/chapter-17'), TODAY)
        en = bm.load_pack(bm.ENGLISH_PACK)
        en['layers'][0]['name'] = 'Núcleo'
        with self.assertRaises(bm.Invalid):
            bm.validate_pack(en, bm.ENGLISH_PACK.parent)

    def test_english_cli_from_copied_skill_and_explicit_pack(self):
        installed = Path(self.tmp.name) / 'installed'
        shutil.copytree(SKILL, installed)
        script = installed / 'scripts/bm.py'
        result = subprocess.run([sys.executable, str(script), 'review', '--language', 'en',
                                 '--input', str(installed / 'assets/examples/en/chapter-17.json')],
                                cwd=self.tmp.name, text=True, capture_output=True)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(json.loads(result.stdout)['findings'][0]['layer'], 'Skin')
        result = subprocess.run([sys.executable, str(script), 'diagnose', '--pack',
                                 str(installed / 'assets/brand-machines-en/brand.json')],
                                cwd=self.tmp.name, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['layers'][0]['name'], 'Core')
        result = subprocess.run([sys.executable, str(script), 'validate', '--language', 'en',
                                 '--pack', str(self.path)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stderr)['error'], '--language does not match the pack.')
        (installed / 'assets/brand-machines-en/sources/editorial.md').write_text('changed')
        result = subprocess.run([sys.executable, str(script), 'validate', '--pack',
                                 str(installed / 'assets/brand-machines-en/brand.json')],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('Source changed:', json.loads(result.stderr)['error'])

    def test_api_languages_are_isolated_and_errors_localized(self):
        servers = [(bm.make_server(self.path, 0), 'es'), (bm.make_server(bm.ENGLISH_PACK, 0), 'en')]
        threads = [threading.Thread(target=s.serve_forever, daemon=True) for s, _ in servers]
        for thread in threads:
            thread.start()
        try:
            for server, language in servers:
                with self.subTest(language=language):
                    url = f'http://127.0.0.1:{server.server_port}/api/v1/validate'
                    artifact = self.example(('en/' if language == 'en' else '') + 'chapter-17')
                    request = Request(url, data=json.dumps(artifact).encode(),
                                      headers={'Content-Type': 'application/json'})
                    with urlopen(request, timeout=3) as response:
                        out = json.load(response)
                    self.assertEqual((out['status'], out['language']), ('revise', language))
                    bad = Request(url, data=b'{', headers={'Content-Type': 'application/json'})
                    with self.assertRaises(HTTPError) as error:
                        urlopen(bad, timeout=3)
                    self.assertEqual(error.exception.code, 400)
                    self.assertEqual(json.load(error.exception)['error'],
                                     'Invalid JSON.' if language == 'en' else 'JSON inválido.')
                    error.exception.close()
        finally:
            for server, _ in servers:
                server.shutdown()
                server.server_close()
            for thread in threads:
                thread.join(timeout=3)


if __name__ == '__main__':
    unittest.main()

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


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3
"""Brand Machines: evidence diagnosis / diagnóstico y Guardian / Guardián. ES/EN. Python 3.10+."""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import sys
import unicodedata

VERSION = "0.2.0"
LAYERS = ["Núcleo", "Mente", "Cuerpo", "Piel", "Motores", "Brand OS", "Interconexiones"]
LAYERS_EN = ["Core", "Mind", "Body", "Skin", "Engines", "Brand OS", "Interconnections"]
MAX_BYTES = 131072
DEFAULT_PACK = Path(__file__).resolve().parents[1] / "assets/brand-machines/brand.json"
ENGLISH_PACK = DEFAULT_PACK.parent.parent / "brand-machines-en/brand.json"


class Invalid(ValueError):
    def __init__(self, es, en):
        super().__init__(es)
        self.en = en
        self.language = "es"

    def localized(self, language):
        return self.en if language == "en" else str(self)


def text(pack, es, en):
    return en if pack.get("language", "es") == "en" else es


def layers_for(pack):
    return LAYERS_EN if pack.get("language", "es") == "en" else LAYERS


def shape(value, required, optional=()):
    if not isinstance(value, dict):
        raise Invalid("Se esperaba un objeto JSON.", 'Expected a JSON object.')
    missing = set(required) - value.keys()
    extra = value.keys() - set(required) - set(optional)
    if missing or extra:
        raise Invalid(f"Campos ausentes: {sorted(missing)}; desconocidos: {sorted(extra)}.", f"Missing fields: {sorted(missing)}; unknown fields: {sorted(extra)}.")


def string(value, field, empty=False):
    if not isinstance(value, str) or (not empty and not value.strip()):
        raise Invalid(f"{field}: se esperaba texto {'no vacío' if not empty else ''}.", f"{field}: expected a string{' with content' if not empty else ''}.")
    return value


def strings(value, field, empty=False):
    if not isinstance(value, list) or (not empty and not value):
        raise Invalid(f"{field}: se esperaba una lista {'no vacía' if not empty else ''}.", f"{field}: expected a list{' with items' if not empty else ''}.")
    for item in value:
        string(item, field)
    if len(value) != len(set(value)):
        raise Invalid(f"{field}: valores duplicados.", f"{field}: duplicate values.")
    return value


def normalized(value):
    return unicodedata.normalize("NFKC", value).casefold()


def strict_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise Invalid(f"Clave JSON duplicada: {key}.", f"Duplicate JSON key: {key}.")
        out[key] = value
    return out


def decode(raw):
    if len(raw) > MAX_BYTES:
        raise Invalid(f"El JSON supera {MAX_BYTES} bytes.", f"JSON exceeds {MAX_BYTES} bytes.")
    try:
        return json.loads(raw, object_pairs_hook=strict_object,
                          parse_constant=lambda x: (_ for _ in ()).throw(Invalid(f"Número inválido: {x}", f"Invalid number: {x}")))
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise Invalid("JSON inválido.", 'Invalid JSON.') from exc


def read_json(path):
    with Path(path).open("rb") as stream:
        return decode(stream.read(MAX_BYTES + 1))


def validate_pack(pack, base):
    shape(pack, ["schema_version", "id", "name", "version", "sources", "layers", "principles", "checks"], ["language"])
    if pack.get("language", "es") not in ("es", "en"):
        raise Invalid("language debe ser es o en.", "language must be es or en.")
    if pack["schema_version"] != "0.1":
        raise Invalid("schema_version del paquete debe ser 0.1.", 'Pack schema_version must be 0.1.')
    for field in ("id", "name", "version"):
        string(pack[field], field)
    for field in ("sources", "layers", "principles", "checks"):
        if not isinstance(pack[field], list):
            raise Invalid(f"{field}: se esperaba una lista.", f"{field}: expected a list.")
    base = Path(base).resolve()
    sources = {}
    for source in pack["sources"]:
        shape(source, ["id", "title", "path", "sha256"], ["valid_until"])
        for field in ("id", "title", "path", "sha256"):
            string(source[field], field)
        if source["id"] in sources:
            raise Invalid("ID de fuente duplicado.", 'Duplicate source ID.')
        relative = Path(source["path"])
        path = (base / relative).resolve()
        if relative.is_absolute() or not path.is_relative_to(base) or not path.is_file():
            raise Invalid(f"Fuente fuera del paquete o ausente: {source['id']}.", f"Source outside the pack or missing: {source['id']}.")
        if not re.fullmatch(r"[0-9a-f]{64}", source["sha256"]):
            raise Invalid("SHA-256 inválido.", 'Invalid SHA-256.')
        if path.stat().st_size > MAX_BYTES:
            raise Invalid("Fuente demasiado grande; dividir en referencias pequeñas.", 'Source too large; split it into smaller references.')
        if hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
            raise Invalid(f"La fuente cambió: {source['id']}. Revisar antes de actualizar su hash.", f"Source changed: {source['id']}. Review before updating its hash.")
        if "valid_until" in source:
            try:
                date.fromisoformat(string(source["valid_until"], "valid_until"))
            except ValueError as exc:
                raise Invalid("valid_until debe ser una fecha ISO válida.", 'valid_until must be a valid ISO date.') from exc
        sources[source["id"]] = source

    def refs(values):
        strings(values, "sources", empty=True)
        if set(values) - sources.keys():
            raise Invalid("Referencia a una fuente desconocida.", 'Reference to an unknown source.')

    if len(pack["layers"]) != 7:
        raise Invalid("El paquete debe describir las siete capas; usar summary vacío cuando falte información.", 'The pack must describe all seven layers; leave summary empty when information is missing.')
    for index, layer in enumerate(pack["layers"]):
        shape(layer, ["id", "name", "summary", "sources"])
        if type(layer["id"]) is not int or layer["id"] != index + 1 or layer["name"] != layers_for(pack)[index]:
            raise Invalid("Las siete capas deben conservar sus nombres y orden canónicos.", 'The seven layers must keep their canonical names and order.')
        string(layer["summary"], "summary", empty=True)
        refs(layer["sources"])
    principles = {}
    for principle in pack["principles"]:
        shape(principle, ["id", "layer", "name", "definition", "situations", "tradeoff", "example", "counterexample", "sources"])
        for field in ("id", "name", "definition", "tradeoff", "example", "counterexample"):
            string(principle[field], field)
        if type(principle["layer"]) is not int or principle["layer"] not in range(1, 8):
            raise Invalid("Capa del principio inválida.", 'Invalid principle layer.')
        if principle["id"] in principles:
            raise Invalid("ID de principio duplicado.", 'Duplicate principle ID.')
        strings(principle["situations"], "situations")
        refs(principle["sources"])
        principles[principle["id"]] = principle
    ids = set()
    kinds = {"forbidden_terms": ["terms"], "max_exclamations": ["maximum"], "canonical_layers": []}
    for check in pack["checks"]:
        if not isinstance(check, dict) or not isinstance(check.get("kind"), str) or check["kind"] not in kinds:
            raise Invalid("Tipo de comprobación desconocido.", 'Unknown check kind.')
        shape(check, ["id", "kind", "principle", "contexts", "message", "suggestion"] + kinds[check["kind"]])
        for field in ("id", "message", "suggestion", "principle"):
            string(check[field], field)
        strings(check["contexts"], "contexts")
        if check["id"] in ids or check["principle"] not in principles:
            raise Invalid("ID de comprobación duplicado o principio desconocido.", 'Duplicate check ID or unknown principle.')
        if not principles[check["principle"]]["sources"]:
            raise Invalid("Cada comprobación necesita un principio con fuentes.", 'Every check requires a principle with sources.')
        ids.add(check["id"])
        if check["kind"] == "forbidden_terms":
            strings(check["terms"], "terms")
        if check["kind"] == "max_exclamations":
            if type(check["maximum"]) is not int or not 0 <= check["maximum"] <= 100:
                raise Invalid("maximum debe ser un entero entre 0 y 100.", 'maximum must be an integer between 0 and 100.')
    return pack


def load_pack(path):
    path = Path(path)
    pack = read_json(path)
    try:
        return validate_pack(pack, path.parent)
    except Invalid as exc:
        if isinstance(pack, dict) and pack.get("language") == "en":
            exc.language = "en"
        raise


def current_sources(pack, as_of):
    return {s["id"] for s in pack["sources"] if s.get("valid_until", "9999-12-31") >= as_of.isoformat()}


def diagnose(pack, as_of):
    current = current_sources(pack, as_of)
    layers = []
    for layer in pack["layers"]:
        available = sorted(set(layer["sources"]) & current)
        layers.append({**layer, "status": "documented" if layer["summary"].strip() and available else "needs_evidence",
                       "current_sources": available})
    return {"brand": pack["id"], "version": pack["version"], "as_of": as_of.isoformat(),
            "scope": "documentation_coverage", "language": pack.get("language", "es"), "layers": layers,
            "missing_layers": [l["name"] for l in layers if l["status"] == "needs_evidence"],
            "note": text(pack, "Cobertura documental; no mide madurez, veracidad ni coherencia semántica.",
                         "Documentation coverage; does not measure maturity, truth or semantic coherence.")}


def review(pack, artifact, as_of):
    shape(artifact, ["type", "content", "context"], ["claims", "layers", "language"])
    if artifact.get("language", pack.get("language", "es")) != pack.get("language", "es"):
        raise Invalid("El idioma de la pieza no coincide con el paquete.", "Artifact language does not match the pack.")
    for field in ("type", "content", "context"):
        string(artifact[field], field)
    if "layers" in artifact:
        strings(artifact["layers"], "layers")
    claims = artifact.get("claims", [])
    if not isinstance(claims, list):
        raise Invalid("claims debe ser una lista.", 'claims must be a list.')
    current = current_sources(pack, as_of)
    findings, missing, checked = [], [], []
    principles = {p["id"]: p for p in pack["principles"]}
    for claim in claims:
        shape(claim, ["text", "sources"])
        string(claim["text"], "claim.text")
        strings(claim["sources"], "claim.sources", empty=True)
        if normalized(claim["text"]) not in normalized(artifact["content"]):
            raise Invalid("La afirmación declarada no aparece en el contenido.", 'The declared claim does not appear in the content.')
        if not claim["sources"] or set(claim["sources"]) - current:
            missing.append({"claim": claim["text"], "reason": text(pack, "Fuente ausente, desconocida o caducada.", "Missing, unknown or expired source.")})
    coverage = diagnose(pack, as_of)
    if coverage["missing_layers"]:
        missing.append({"layers": coverage["missing_layers"], "reason": text(pack, "Identidad documentada incompleta.", "Incomplete identity documentation.")})
    if not principles:
        missing.append({"reason": text(pack, "Faltan principios de decisión documentados.", "Missing documented decision principles.")})
    for principle in principles.values():
        if not principle["sources"] or set(principle["sources"]) - current:
            missing.append({"principle": principle["id"], "reason": text(pack, "Principio sin fuentes vigentes.", "Principle has no current sources.")})
    for check in pack["checks"]:
        if "*" not in check["contexts"] and artifact["context"] not in check["contexts"]:
            continue
        kind = check["kind"]
        if kind == "canonical_layers" and "layers" not in artifact:
            continue
        checked.append(check["id"])
        if kind == "forbidden_terms":
            evidence = [term for term in check["terms"] if re.search(r"(?<!\w)" + re.escape(normalized(term)) + r"(?!\w)", normalized(artifact["content"]))]
        elif kind == "max_exclamations":
            count = sum(artifact["content"].count(c) for c in "!¡")
            evidence = {"count": count, "maximum": check["maximum"]} if count > check["maximum"] else None
        else:
            evidence = artifact["layers"] if artifact["layers"] != layers_for(pack) else None
        if evidence:
            principle = principles[check["principle"]]
            findings.append({"check": check["id"], "layer": layers_for(pack)[principle["layer"] - 1],
                             "principle": principle["id"], "sources": principle["sources"],
                             "evidence": evidence, "message": check["message"], "suggestion": check["suggestion"]})
    status = "revise" if findings else "needs_evidence" if missing else "needs_review"
    return {"brand": pack["id"], "version": pack["version"], "as_of": as_of.isoformat(),
            "artifact_sha256": hashlib.sha256(json.dumps(artifact, ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
            "status": status, "scope": "deterministic", "language": pack.get("language", "es"), "checks_passed": not findings,
            "checks_run": checked, "findings": findings, "missing_evidence": missing,
            "semantic_review": "pending", "publication_authorized": False,
            "note": text(pack, "Las fuentes declaradas no prueban las afirmaciones. Revisar su contenido, las afirmaciones no declaradas y la alineación entre capas.",
                         "Declared sources do not prove claims. Review their content, undeclared claims and alignment between layers.")}


def make_server(pack_path, port):
    language = load_pack(pack_path).get("language", "es")
    def message(es, en):
        return en if language == "en" else es
    # Recargar el paquete en cada petición detecta cambios de fuentes tras arrancar.
    class Handler(BaseHTTPRequestHandler):
        def send_json(self, status, payload):
            body = json.dumps(payload, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            if self.path != "/api/v1/validate":
                return self.send_json(404, {"error": message("Ruta desconocida.", "Unknown route.")})
            if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
                return self.send_json(415, {"error": message("Usar application/json.", "Use application/json.")})
            try:
                if self.headers.get("Transfer-Encoding"):
                    raise Invalid("Transfer-Encoding no admitido.", 'Transfer-Encoding is not supported.')
                length = int(self.headers.get("Content-Length", "-1"))
                if length < 1:
                    raise Invalid("Content-Length requerido.", 'Content-Length is required.')
                if length > MAX_BYTES:
                    return self.send_json(413, {"error": message("Petición demasiado grande.", "Request too large.")})
                self.connection.settimeout(5)
                artifact = decode(self.rfile.read(length))
                pack = load_pack(pack_path)
                if pack.get("language", "es") != language:
                    raise Invalid("El idioma del paquete cambió; reiniciar el servidor.", "Pack language changed; restart the server.")
                result = review(pack, artifact, date.today())
                self.send_json(200, result)
            except (Invalid, ValueError, OSError) as exc:
                self.send_json(400, {"error": exc.localized(language) if isinstance(exc, Invalid) else str(exc)})

        def log_message(self, *_args):
            pass

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=VERSION)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "diagnose", "review", "serve"):
        p = sub.add_parser(name)
        p.add_argument("--pack", type=Path, help="Identity pack / paquete de identidad")
        p.add_argument("--language", choices=("es", "en"), help="Pack language / idioma del paquete (default: es)")
        if name in ("diagnose", "review"):
            p.add_argument("--as-of", type=date.fromisoformat, default=date.today())
        if name == "review":
            p.add_argument("--input", type=Path, required=True)
        if name == "serve":
            p.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)
    language = args.language
    args.pack = args.pack or (ENGLISH_PACK if language == "en" else DEFAULT_PACK)
    try:
        pack = load_pack(args.pack)
        if args.language and pack.get("language", "es") != args.language:
            raise Invalid("--language no coincide con el paquete.", "--language does not match the pack.")
        language = pack.get("language", "es")
        if args.command == "serve":
            if not 1 <= args.port <= 65535:
                raise Invalid("Puerto fuera de rango.", 'Port out of range.')
            server = make_server(args.pack, args.port)
            print(f"Brand Machines {VERSION}: http://127.0.0.1:{args.port}/api/v1/validate", file=sys.stderr)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
            finally:
                server.server_close()
            return 0
        if args.command == "validate":
            result = {"valid": True, "brand": pack["id"], "language": language, "scope": "package_structure_and_hashes"}
        elif args.command == "diagnose":
            result = diagnose(pack, args.as_of)
        else:
            result = review(pack, read_json(args.input), args.as_of)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        # review: 0 = sin incidencias mecánicas; nunca significa aprobación editorial.
        return 1 if args.command == "review" and result["status"] in ("revise", "needs_evidence") else 0
    except (Invalid, OSError) as exc:
        print(json.dumps({"error": exc.localized(language or exc.language) if isinstance(exc, Invalid) else str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Brand Machines: diagnóstico de evidencia y Guardián local. Python 3.10+."""
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

VERSION = "0.1.0"
LAYERS = ["Núcleo", "Mente", "Cuerpo", "Piel", "Motores", "Brand OS", "Interconexiones"]
MAX_BYTES = 131072
DEFAULT_PACK = Path(__file__).resolve().parents[1] / "assets/brand-machines/brand.json"


class Invalid(ValueError):
    pass


def shape(value, required, optional=()):
    if not isinstance(value, dict):
        raise Invalid("Se esperaba un objeto JSON.")
    missing = set(required) - value.keys()
    extra = value.keys() - set(required) - set(optional)
    if missing or extra:
        raise Invalid(f"Campos ausentes: {sorted(missing)}; desconocidos: {sorted(extra)}.")


def string(value, field, empty=False):
    if not isinstance(value, str) or (not empty and not value.strip()):
        raise Invalid(f"{field}: se esperaba texto {'no vacío' if not empty else ''}.")
    return value


def strings(value, field, empty=False):
    if not isinstance(value, list) or (not empty and not value):
        raise Invalid(f"{field}: se esperaba una lista {'no vacía' if not empty else ''}.")
    for item in value:
        string(item, field)
    if len(value) != len(set(value)):
        raise Invalid(f"{field}: valores duplicados.")
    return value


def normalized(value):
    return unicodedata.normalize("NFKC", value).casefold()


def strict_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise Invalid(f"Clave JSON duplicada: {key}.")
        out[key] = value
    return out


def decode(raw):
    if len(raw) > MAX_BYTES:
        raise Invalid(f"El JSON supera {MAX_BYTES} bytes.")
    try:
        return json.loads(raw, object_pairs_hook=strict_object,
                          parse_constant=lambda x: (_ for _ in ()).throw(Invalid(f"Número inválido: {x}")))
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise Invalid("JSON inválido.") from exc


def read_json(path):
    with Path(path).open("rb") as stream:
        return decode(stream.read(MAX_BYTES + 1))


def validate_pack(pack, base):
    shape(pack, ["schema_version", "id", "name", "version", "sources", "layers", "principles", "checks"])
    if pack["schema_version"] != "0.1":
        raise Invalid("schema_version del paquete debe ser 0.1.")
    for field in ("id", "name", "version"):
        string(pack[field], field)
    for field in ("sources", "layers", "principles", "checks"):
        if not isinstance(pack[field], list):
            raise Invalid(f"{field}: se esperaba una lista.")
    base = Path(base).resolve()
    sources = {}
    for source in pack["sources"]:
        shape(source, ["id", "title", "path", "sha256"], ["valid_until"])
        for field in ("id", "title", "path", "sha256"):
            string(source[field], field)
        if source["id"] in sources:
            raise Invalid("ID de fuente duplicado.")
        relative = Path(source["path"])
        path = (base / relative).resolve()
        if relative.is_absolute() or not path.is_relative_to(base) or not path.is_file():
            raise Invalid(f"Fuente fuera del paquete o ausente: {source['id']}.")
        if not re.fullmatch(r"[0-9a-f]{64}", source["sha256"]):
            raise Invalid("SHA-256 inválido.")
        if path.stat().st_size > MAX_BYTES:
            raise Invalid("Fuente demasiado grande; dividir en referencias pequeñas.")
        if hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
            raise Invalid(f"La fuente cambió: {source['id']}. Revisar antes de actualizar su hash.")
        if "valid_until" in source:
            try:
                date.fromisoformat(string(source["valid_until"], "valid_until"))
            except ValueError as exc:
                raise Invalid("valid_until debe ser una fecha ISO válida.") from exc
        sources[source["id"]] = source

    def refs(values):
        strings(values, "sources", empty=True)
        if set(values) - sources.keys():
            raise Invalid("Referencia a una fuente desconocida.")

    if len(pack["layers"]) != 7:
        raise Invalid("El paquete debe describir las siete capas; usar summary vacío cuando falte información.")
    for index, layer in enumerate(pack["layers"]):
        shape(layer, ["id", "name", "summary", "sources"])
        if type(layer["id"]) is not int or layer["id"] != index + 1 or layer["name"] != LAYERS[index]:
            raise Invalid("Las siete capas deben conservar sus nombres y orden canónicos.")
        string(layer["summary"], "summary", empty=True)
        refs(layer["sources"])
    principles = {}
    for principle in pack["principles"]:
        shape(principle, ["id", "layer", "name", "definition", "situations", "tradeoff", "example", "counterexample", "sources"])
        for field in ("id", "name", "definition", "tradeoff", "example", "counterexample"):
            string(principle[field], field)
        if type(principle["layer"]) is not int or principle["layer"] not in range(1, 8):
            raise Invalid("Capa del principio inválida.")
        if principle["id"] in principles:
            raise Invalid("ID de principio duplicado.")
        strings(principle["situations"], "situations")
        refs(principle["sources"])
        principles[principle["id"]] = principle
    ids = set()
    kinds = {"forbidden_terms": ["terms"], "max_exclamations": ["maximum"], "canonical_layers": []}
    for check in pack["checks"]:
        if not isinstance(check, dict) or not isinstance(check.get("kind"), str) or check["kind"] not in kinds:
            raise Invalid("Tipo de comprobación desconocido.")
        shape(check, ["id", "kind", "principle", "contexts", "message", "suggestion"] + kinds[check["kind"]])
        for field in ("id", "message", "suggestion", "principle"):
            string(check[field], field)
        strings(check["contexts"], "contexts")
        if check["id"] in ids or check["principle"] not in principles:
            raise Invalid("ID de comprobación duplicado o principio desconocido.")
        if not principles[check["principle"]]["sources"]:
            raise Invalid("Cada comprobación necesita un principio con fuentes.")
        ids.add(check["id"])
        if check["kind"] == "forbidden_terms":
            strings(check["terms"], "terms")
        if check["kind"] == "max_exclamations":
            if type(check["maximum"]) is not int or not 0 <= check["maximum"] <= 100:
                raise Invalid("maximum debe ser un entero entre 0 y 100.")
    return pack


def load_pack(path):
    path = Path(path)
    return validate_pack(read_json(path), path.parent)


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
            "scope": "documentation_coverage", "layers": layers,
            "missing_layers": [l["name"] for l in layers if l["status"] == "needs_evidence"],
            "note": "Cobertura documental; no mide madurez, veracidad ni coherencia semántica."}


def review(pack, artifact, as_of):
    shape(artifact, ["type", "content", "context"], ["claims", "layers"])
    for field in ("type", "content", "context"):
        string(artifact[field], field)
    if "layers" in artifact:
        strings(artifact["layers"], "layers")
    claims = artifact.get("claims", [])
    if not isinstance(claims, list):
        raise Invalid("claims debe ser una lista.")
    current = current_sources(pack, as_of)
    findings, missing, checked = [], [], []
    principles = {p["id"]: p for p in pack["principles"]}
    for claim in claims:
        shape(claim, ["text", "sources"])
        string(claim["text"], "claim.text")
        strings(claim["sources"], "claim.sources", empty=True)
        if normalized(claim["text"]) not in normalized(artifact["content"]):
            raise Invalid("La afirmación declarada no aparece en el contenido.")
        if not claim["sources"] or set(claim["sources"]) - current:
            missing.append({"claim": claim["text"], "reason": "Fuente ausente, desconocida o caducada."})
    coverage = diagnose(pack, as_of)
    if coverage["missing_layers"]:
        missing.append({"layers": coverage["missing_layers"], "reason": "Identidad documentada incompleta."})
    if not principles:
        missing.append({"reason": "Faltan principios de decisión documentados."})
    for principle in principles.values():
        if not principle["sources"] or set(principle["sources"]) - current:
            missing.append({"principle": principle["id"], "reason": "Principio sin fuentes vigentes."})
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
            evidence = artifact["layers"] if artifact["layers"] != LAYERS else None
        if evidence:
            principle = principles[check["principle"]]
            findings.append({"check": check["id"], "layer": LAYERS[principle["layer"] - 1],
                             "principle": principle["id"], "sources": principle["sources"],
                             "evidence": evidence, "message": check["message"], "suggestion": check["suggestion"]})
    status = "revise" if findings else "needs_evidence" if missing else "needs_review"
    return {"brand": pack["id"], "version": pack["version"], "as_of": as_of.isoformat(),
            "artifact_sha256": hashlib.sha256(json.dumps(artifact, ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
            "status": status, "scope": "deterministic", "checks_passed": not findings,
            "checks_run": checked, "findings": findings, "missing_evidence": missing,
            "semantic_review": "pending", "publication_authorized": False,
            "note": "Las fuentes declaradas no prueban las afirmaciones. Revisar su contenido, las afirmaciones no declaradas y la alineación entre capas."}


def make_server(pack_path, port):
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
                return self.send_json(404, {"error": "Ruta desconocida."})
            if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
                return self.send_json(415, {"error": "Usar application/json."})
            try:
                if self.headers.get("Transfer-Encoding"):
                    raise Invalid("Transfer-Encoding no admitido.")
                length = int(self.headers.get("Content-Length", "-1"))
                if length < 1:
                    raise Invalid("Content-Length requerido.")
                if length > MAX_BYTES:
                    return self.send_json(413, {"error": "Petición demasiado grande."})
                self.connection.settimeout(5)
                artifact = decode(self.rfile.read(length))
                result = review(load_pack(pack_path), artifact, date.today())
                self.send_json(200, result)
            except (Invalid, ValueError, OSError) as exc:
                self.send_json(400, {"error": str(exc)})

        def log_message(self, *_args):
            pass

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=VERSION)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "diagnose", "review", "serve"):
        p = sub.add_parser(name)
        p.add_argument("--pack", type=Path, default=DEFAULT_PACK)
        if name in ("diagnose", "review"):
            p.add_argument("--as-of", type=date.fromisoformat, default=date.today())
        if name == "review":
            p.add_argument("--input", type=Path, required=True)
        if name == "serve":
            p.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)
    try:
        pack = load_pack(args.pack)
        if args.command == "serve":
            if not 1 <= args.port <= 65535:
                raise Invalid("Puerto fuera de rango.")
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
            result = {"valid": True, "brand": pack["id"], "scope": "package_structure_and_hashes"}
        elif args.command == "diagnose":
            result = diagnose(pack, args.as_of)
        else:
            result = review(pack, read_json(args.input), args.as_of)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        # review: 0 = sin incidencias mecánicas; nunca significa aprobación editorial.
        return 1 if args.command == "review" and result["status"] in ("revise", "needs_evidence") else 0
    except (Invalid, OSError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

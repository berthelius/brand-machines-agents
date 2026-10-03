"""Reproduce the five mechanical checks; this does not run an agent evaluation."""

from datetime import date
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("bm", HERE.parents[2] / "scripts/bm.py")
bm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bm)
AS_OF = date(2026, 10, 4)


def main():
    pack = bm.load_pack(HERE / "brand.json")
    coverage = bm.diagnose(pack, AS_OF)
    missing_layers = ["Mind", "Body", "Engines", "Brand OS"]
    assert coverage["missing_layers"] == missing_layers
    results = {}
    cases = bm.read_json(HERE / "cases.json")
    assert len(cases) == 5
    for case in cases:
        result = bm.review(pack, case["artifact"], AS_OF)
        assert result["status"] == case["expected_mechanical_status"], case["id"]
        assert result["semantic_review"] == "pending"
        assert result["publication_authorized"] is False
        assert result["checks_run"] == ["absolute-impact-warning"]
        expected = ["absolute-impact-warning"] if case["id"] == "absolute-impact" else []
        assert [finding["check"] for finding in result["findings"]] == expected
        assert [item.get("layers") for item in result["missing_evidence"]] == [missing_layers]
        results[case["id"]] = result
    print(json.dumps({"as_of": AS_OF.isoformat(), "missing_layers": missing_layers,
                      "results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

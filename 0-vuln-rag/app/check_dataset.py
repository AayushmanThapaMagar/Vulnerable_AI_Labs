import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def main():
    documents_dir = PROJECT_ROOT / "data" / "documents"
    cases_path = PROJECT_ROOT / "data" / "evaluations" / "baseline.json"

    documents = sorted(documents_dir.glob("*.md"))
    document_names = {path.name for path in documents}
    cases = json.loads(cases_path.read_text(encoding="utf-8"))

    for path in documents:
        if not path.read_text(encoding="utf-8").strip():
            raise ValueError(f"Empty document: {path.name}")

    for case in cases:
        for source in case["expected_sources"]:
            if source not in document_names:
                raise ValueError(
                    f"Case {case['id']} references missing source: {source}"
                )

    print(f"Documents: {len(documents)}")
    print(f"Evaluation cases: {len(cases)}")
    print("All referenced source files exist.")


if __name__ == "__main__":
    main()
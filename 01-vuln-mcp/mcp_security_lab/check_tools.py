import json
from pathlib import Path

REVIEW_DIR = Path(__file__).resolve().parent.parent / "review"


def main() -> None:
    approved = json.loads(
        (REVIEW_DIR / "approved_tools.json").read_text(encoding="utf-8")
    )
    discovered = json.loads(
        (REVIEW_DIR / "discovered_tools.json").read_text(encoding="utf-8")
    )

    if approved != discovered:
        print("CHANGE DETECTED: discovery differs from the approved baseline.")
        raise SystemExit(1)

    print("MATCH: discovery matches the approved baseline.")


if __name__ == "__main__":
    main()
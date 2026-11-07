import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def split_text(
    text: str,
    chunk_size: int = 250,
    overlap: int = 50,
) -> list[dict]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive.")

    if not 0 <= overlap < chunk_size:
        raise ValueError("overlap must be between 0 and chunk_size - 1.")

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))

        chunks.append({
            "start": start,
            "end": end,
            "text": text[start:end],
        })

        if end == len(text):
            break

        start = end - overlap

    return chunks


def main():
    documents_dir = PROJECT_ROOT / "data" / "documents"
    output_path = PROJECT_ROOT / "data" / "processed" / "chunks.json"

    document_paths = sorted(documents_dir.glob("*.md"))

    if not document_paths:
        raise SystemExit("No Markdown documents found.")

    records = []

    for path in document_paths:
        text = path.read_text(encoding="utf-8")

        if not text.strip():
            raise ValueError(f"Empty document: {path.name}")

        chunks = split_text(text)

        for index, chunk in enumerate(chunks):
            records.append({
                "chunk_id": f"{path.stem}:{index}",
                "source": path.name,
                **chunk,
            })

        print(f"{path.name}: {len(chunks)} chunk(s)")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(records, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\nSaved {len(records)} chunks to {output_path}")


if __name__ == "__main__":
    main()
import hashlib
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DIMENSIONS = 768
TASK_TYPE = "RETRIEVAL_DOCUMENT"


def main():
    load_dotenv(PROJECT_ROOT.parent / ".env")

    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_EMBEDDING_MODEL")

    if not api_key or not model:
        raise SystemExit(
            "Set GEMINI_API_KEY and GEMINI_EMBEDDING_MODEL in .env."
        )

    chunks_path = PROJECT_ROOT / "data" / "processed" / "chunks.json"
    output_path = PROJECT_ROOT / "data" / "processed" / "embeddings.json"

    chunks = json.loads(chunks_path.read_text(encoding="utf-8"))

    if not chunks:
        raise SystemExit("No chunks found. Run python -m app.ingest first.")

    # Identify the exact dataset and settings used for this index.
    specification = {
        "model": model,
        "dimensions": DIMENSIONS,
        "task_type": TASK_TYPE,
        "chunks": chunks,
    }

    fingerprint = hashlib.sha256(
        json.dumps(
            specification,
            sort_keys=True,
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()

    # Reuse the saved result if the dataset and settings haven't changed.
    if output_path.exists():
        saved = json.loads(output_path.read_text(encoding="utf-8"))

        if saved.get("fingerprint") == fingerprint:
            print("Unchanged dataset and settings; using saved embeddings.")
            print("No embedding API call made.")
            return

    with genai.Client(api_key=api_key) as client:
        response = client.models.embed_content(
            model=model,
            contents=[chunk["text"] for chunk in chunks],
            config=types.EmbedContentConfig(
                task_type=TASK_TYPE,
                output_dimensionality=DIMENSIONS,
            ),
        )

    embeddings = response.embeddings or []

    if len(embeddings) != len(chunks):
        raise ValueError("The number of embeddings doesn't match the chunks.")

    records = []

    for chunk, embedding in zip(chunks, embeddings):
        vector = embedding.values

        if vector is None or len(vector) != DIMENSIONS:
            raise ValueError(
                f"Unexpected embedding size for {chunk['chunk_id']}."
            )

        records.append({
            **chunk,
            "embedding": vector,
        })

    output = {
        "fingerprint": fingerprint,
        "model": model,
        "dimensions": DIMENSIONS,
        "task_type": TASK_TYPE,
        "chunks": records,
    }

    output_path.write_text(
        json.dumps(output, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Embedded chunks: {len(records)}")
    print(f"Dimensions per chunk: {DIMENSIONS}")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()
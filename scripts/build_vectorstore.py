from pathlib import Path
import sys
import json

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sentence_transformers import SentenceTransformer
import chromadb


def main():
    vectorstore = PROJECT_ROOT / "vectorstore"
    chunks_file = vectorstore / "chunks.json"
    chroma_path = vectorstore / "chroma_db"

    print("Vectorstore:", vectorstore)
    print("Chunks file:", chunks_file)
    print("Chroma path:", chroma_path)

    if not chunks_file.exists():
        raise FileNotFoundError(f"Missing: {chunks_file}")

    chunks = json.loads(
        chunks_file.read_text(encoding="utf-8")
    )

    print("Chunks loaded:", len(chunks))

    texts = [c["text"] for c in chunks]
    ids = [c["chunk_id"] for c in chunks]

    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Generating embeddings...")
    embeddings = model.encode(
        texts,
        normalize_embeddings=True
    ).tolist()

    print("Creating ChromaDB...")
    client = chromadb.PersistentClient(
        path=str(chroma_path)
    )

    # Use a dedicated collection
    collection = client.get_or_create_collection(
        name="autosar_hld"
    )

    print("Collection before:", collection.count())

    metadatas = [
        {
            "filename": str(c.get("filename", "")),
            "page_number": str(c.get("page_number", "")),
            "section": str(c.get("section", "")),
            "document_version": str(c.get("document_version", "")),
        }
        for c in chunks
    ]

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print("Collection after:", collection.count())

    if collection.count() != len(chunks):
        raise RuntimeError(
            f"Expected {len(chunks)} vectors, "
            f"but ChromaDB contains {collection.count()}"
        )

    print("\nSUCCESS")
    print(f"Indexed {collection.count()} chunks into ChromaDB.")
    print(f"Database: {chroma_path}")


if __name__ == "__main__":
    main()
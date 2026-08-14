import os
import re
from pathlib import Path
from typing import List, Dict

import chromadb
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

KNOWLEDGE_DIR = Path("data/knowledge")

CHROMA_PATH = os.getenv(
    "CHROMA_PATH",
    "./data/chroma",
)

COLLECTION_NAME = "insurance_knowledge"

EMBEDDING_MODEL = "text-embedding-3-small"


# ------------------------------------------------------------------
# Clients
# ------------------------------------------------------------------

openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

chroma_client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


# ------------------------------------------------------------------
# Document loading
# ------------------------------------------------------------------

def load_markdown_document(file_path: Path) -> str:
    """
    Load a Markdown knowledge document.
    """

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:
        return file.read()


# ------------------------------------------------------------------
# Chunking
# ------------------------------------------------------------------

def split_markdown_sections(text: str) -> List[Dict]:
    """
    Split a Markdown document using level-2 headings.

    Example:
        ## 3. Early Claims
    becomes one retrievable knowledge chunk.
    """

    pattern = r"(?=^##\s+)"

    sections = re.split(
        pattern,
        text,
        flags=re.MULTILINE,
    )

    chunks = []

    for section in sections:

        section = section.strip()

        if not section:
            continue

        lines = section.splitlines()

        # Section heading
        if lines[0].startswith("## "):
            section_title = lines[0][3:].strip()
        else:
            section_title = "Document Header"

        chunks.append(
            {
                "section": section_title,
                "text": section,
            }
        )

    return chunks


# ------------------------------------------------------------------
# Embeddings
# ------------------------------------------------------------------

def create_embedding(text: str) -> List[float]:
    """
    Generate an embedding using OpenAI.
    """

    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )

    return response.data[0].embedding


# ------------------------------------------------------------------
# Ingestion
# ------------------------------------------------------------------

def ingest_document(file_path: Path) -> int:
    """
    Chunk, embed and store one knowledge document in ChromaDB.
    """

    text = load_markdown_document(file_path)

    chunks = split_markdown_sections(text)

    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    for index, chunk in enumerate(chunks):

        embedding = create_embedding(
            chunk["text"]
        )

        chunk_id = (
            f"{file_path.stem}-chunk-{index}"
        )

        collection.upsert(
            ids=[chunk_id],

            documents=[
                chunk["text"]
            ],

            embeddings=[
                embedding
            ],

            metadatas=[
                {
                    "source": file_path.name,
                    "section": chunk["section"],
                    "document_id": "DEMO-CLM-001",
                    "version": "1.0",
                }
            ],
        )

    return len(chunks)


def ingest_all_documents() -> int:
    """
    Ingest all Markdown documents from the knowledge directory.
    """

    total_chunks = 0

    for file_path in KNOWLEDGE_DIR.glob("*.md"):

        print(
            f"Ingesting: {file_path.name}"
        )

        chunk_count = ingest_document(
            file_path
        )

        total_chunks += chunk_count

        print(
            f"Stored {chunk_count} chunks."
        )

    return total_chunks


# ------------------------------------------------------------------
# Manual execution
# ------------------------------------------------------------------

if __name__ == "__main__":

    total = ingest_all_documents()

    print(
        f"\nRAG ingestion complete. "
        f"Total chunks stored: {total}"
    )
import os
from typing import List, Dict, Any

import chromadb
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


CHROMA_PATH = os.getenv(
    "CHROMA_PATH",
    "./data/chroma",
)

COLLECTION_NAME = "insurance_knowledge"

EMBEDDING_MODEL = "text-embedding-3-small"


openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

chroma_client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


def create_query_embedding(
    query: str,
) -> List[float]:
    """
    Create an embedding for a user query.
    """

    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=query,
    )

    return response.data[0].embedding


def retrieve_knowledge(
    query: str,
    top_k: int = 3,
) -> List[Dict[str, Any]]:
    """
    Retrieve the most relevant knowledge chunks
    from ChromaDB.
    """

    collection = chroma_client.get_collection(
        name=COLLECTION_NAME
    )

    query_embedding = create_query_embedding(
        query
    )

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    retrieved_chunks = []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):

        retrieved_chunks.append(
            {
                "text": document,
                "source": metadata.get("source"),
                "section": metadata.get("section"),
                "document_id": metadata.get(
                    "document_id"
                ),
                "version": metadata.get("version"),
                "distance": distance,
            }
        )

    return retrieved_chunks
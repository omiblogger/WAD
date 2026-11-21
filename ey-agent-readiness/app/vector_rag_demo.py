"""Day 3: genuine embedding-based retrieval using Azure OpenAI.
This demonstrates semantic ranking over 3 documents in memory; Azure AI Search is
an additional hosted indexing/search step (see azure_search_demo.py + README).
Run: python -m app.vector_rag_demo (requires authorized Azure embeddings deployment)
"""
import math
import os
from dotenv import load_dotenv
from app.retrieval import load_policies

load_dotenv()


def cosine_similarity(a: list[float], b: list[float]) -> float:
    numerator = sum(x * y for x, y in zip(a, b))
    denominator = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return numerator / denominator if denominator else 0.0


def semantic_retrieve(question: str, limit: int = 3) -> list[dict]:
    from openai import AzureOpenAI
    client = AzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
    )
    docs = load_policies()
    sentences = [question] + [f"{d['title']}. {d['content']}" for d in docs]
    result = client.embeddings.create(
        model=os.environ["AZURE_OPENAI_EMBEDDING_MODEL"],
        input=sentences,
    )
    vectors = [item.embedding for item in sorted(result.data, key=lambda item: item.index)]
    scored = [(cosine_similarity(vectors[0], vector), doc)
              for vector, doc in zip(vectors[1:], docs)]
    scored.sort(key=lambda item: item[0], reverse=True)
    return [{**doc, "similarity": round(score, 4)} for score, doc in scored[:limit]]


if __name__ == "__main__":
    for doc in semantic_retrieve("How can I verify a customer's identity?"):
        print(doc["id"], doc["similarity"], doc["title"])

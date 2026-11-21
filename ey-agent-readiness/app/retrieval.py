"""Day 1/2: local keyword retrieval. This is NOT embedding/vector RAG.
Day 3: inspect azure_search_demo.py for a hosted search integration.
"""
from pathlib import Path
import json
import re

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "policies.json"


def words(text: str) -> set[str]:
    """Lowercase and split text into unique words."""
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def load_policies() -> list[dict]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def retrieve(question: str, limit: int = 3) -> list[dict]:
    """A tiny transparent retrieval baseline, no database or API key needed."""
    query_words = words(question)
    ranked = []
    for doc in load_policies():
        title_words = words(doc["title"])
        body_words = words(doc["content"])
        score = 3 * len(query_words & title_words) + len(query_words & body_words)
        if score > 0:
            ranked.append((score, doc))
    ranked.sort(key=lambda item: (-item[0], item[1]["id"]))
    return [{"id": doc["id"], "title": doc["title"], "content": doc["content"], "score": score}
            for score, doc in ranked[:limit]]

"""FAQ answering without any paid API.

Primary engine: normalized keyword + fuzzy matching (stdlib only).
Optional engine: a local LLM through Ollama, used only when installed and
reachable — the bot degrades gracefully to fuzzy matching otherwise.
"""

from __future__ import annotations

import difflib
import os
import unicodedata

from .config import FaqEntry

MATCH_THRESHOLD = 0.55


def normalize(text: str) -> str:
    """Lowercase, strip accents and collapse whitespace."""
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return " ".join(text.split())


def score(question: str, entry: FaqEntry) -> float:
    """Similarity between a user question and one FAQ entry (0..1).

    Combines fuzzy string similarity with keyword hits so that short
    messages like "precio?" still match a longer FAQ question.
    """
    q = normalize(question)
    fuzzy = difflib.SequenceMatcher(None, q, normalize(entry.question)).ratio()
    words = set(q.split())
    keywords = {normalize(k) for k in entry.keywords}
    keyword_hit = 1.0 if words & keywords else 0.0
    return max(fuzzy, 0.75 * keyword_hit + 0.25 * fuzzy)


def best_answer(question: str, faq: list[FaqEntry]) -> str | None:
    """Best FAQ answer above the confidence threshold, else None."""
    if not faq:
        return None
    scored = max(faq, key=lambda e: score(question, e))
    return scored.answer if score(question, scored) >= MATCH_THRESHOLD else None


def ollama_answer(question: str, context: str) -> str | None:
    """Answer with a local Ollama model if one is configured.

    Set ``OLLAMA_MODEL`` (e.g. ``llama3.2``) to enable. Returns None on any
    failure so the caller can fall back to fuzzy matching.
    """
    model = os.environ.get("OLLAMA_MODEL")
    if not model:
        return None
    try:
        import requests

        resp = requests.post(
            os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate"),
            json={
                "model": model,
                "prompt": (
                    "Eres el asistente de un negocio. Responde en una o dos "
                    "frases usando SOLO esta información:\n"
                    f"{context}\n\nPregunta del cliente: {question}\nRespuesta:"
                ),
                "stream": False,
            },
            timeout=20,
        )
        resp.raise_for_status()
        text = resp.json().get("response", "").strip()
        return text or None
    except Exception:
        return None

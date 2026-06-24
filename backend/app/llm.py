"""LLM access layer. One generic entrypoint: generate(system, user).

If OPENAI_API_KEY is set it calls an OpenAI-compatible chat endpoint; otherwise it
returns a deterministic mock so the entire app runs offline. Callers (the feature
routers) build their own prompts via prompts.py and never care which path runs."""
import time

from openai import OpenAI

from .config import get_settings

settings = get_settings()

_client: OpenAI | None = None
if not settings.use_mock_llm:
    _client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)


def _mock(system: str, user: str) -> str:
    """Deterministic stand-in. Echoes the request so flows are demoable without a key."""
    # Pull the last non-empty line of the user prompt as the 'content'.
    lines = [l for l in user.splitlines() if l.strip()]
    content = lines[-1] if lines else user
    return f"[mock] {content.strip()}"


def generate(system: str, user: str) -> tuple[str, int]:
    """Returns (text, latency_ms)."""
    start = time.perf_counter()
    if settings.use_mock_llm or _client is None:
        out = _mock(system, user)
    else:
        completion = _client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.7,
            max_tokens=600,
        )
        out = (completion.choices[0].message.content or "").strip()
    latency_ms = int((time.perf_counter() - start) * 1000)
    return out, latency_ms

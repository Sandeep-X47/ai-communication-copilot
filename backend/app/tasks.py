"""Example background tasks. Demonstrates offloading work to a worker. The API
endpoints stay synchronous for low latency; tasks here are for batch/heavy jobs."""
from .celery_app import celery
from .llm import generate
from .prompts import build_rewrite


@celery.task(name="batch_rewrite")
def batch_rewrite(items: list[dict]) -> list[dict]:
    """Rewrite many messages off the request path.
    items: [{"text": "...", "tone": "professional"}, ...]"""
    results = []
    for item in items:
        system, user = build_rewrite(item["text"], item.get("tone", "professional"))
        output, latency_ms = generate(system, user)
        results.append({"input": item["text"], "output": output, "latency_ms": latency_ms})
    return results

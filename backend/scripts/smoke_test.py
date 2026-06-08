"""One-off connectivity check for Supabase, Pinecone, and Gemini.

Run with:
    source .venv/bin/activate && python scripts/smoke_test.py

Reads credentials from .env. Never prints secret values — only pass/fail
and minimal non-secret diagnostic info (status codes, index dimensions, etc.).
"""

import os
import sys

import httpx
from dotenv import load_dotenv

load_dotenv()

results: list[tuple[str, bool, str]] = []


def check(name: str, fn) -> None:
    try:
        results.append((name, True, fn()))
    except Exception as e:
        results.append((name, False, str(e)))


def check_supabase() -> str:
    url = os.environ["SUPABASE_URL"].rstrip("/")
    key = os.environ["SUPABASE_SERVICE_KEY"]
    resp = httpx.get(
        f"{url}/rest/v1/",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
        timeout=10,
    )
    resp.raise_for_status()
    return f"Data API responded with HTTP {resp.status_code}"


def check_pinecone() -> str:
    key = os.environ["PINECONE_API_KEY"]
    index_name = os.environ["PINECONE_INDEX_NAME"]
    resp = httpx.get(
        "https://api.pinecone.io/indexes",
        headers={"Api-Key": key},
        timeout=10,
    )
    resp.raise_for_status()
    indexes = resp.json().get("indexes", [])
    names = [i["name"] for i in indexes]
    if index_name not in names:
        raise RuntimeError(f"index '{index_name}' not found among: {names}")
    target = next(i for i in indexes if i["name"] == index_name)
    return f"index '{index_name}' found — dimension={target.get('dimension')}, metric={target.get('metric')}"


def check_gemini() -> str:
    key = os.environ["GEMINI_API_KEY"]
    resp = httpx.get(
        "https://generativelanguage.googleapis.com/v1beta/models",
        params={"key": key},
        timeout=10,
    )
    resp.raise_for_status()
    models = resp.json().get("models", [])
    return f"reachable — {len(models)} models visible to this key"


check("Supabase", check_supabase)
check("Pinecone", check_pinecone)
check("Gemini", check_gemini)

print("\n--- Connection Smoke Test ---")
all_ok = True
for name, ok, detail in results:
    status = "PASS" if ok else "FAIL"
    if not ok:
        all_ok = False
    print(f"[{status}] {name}: {detail}")

sys.exit(0 if all_ok else 1)

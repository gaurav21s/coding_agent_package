"""Minimal OpenRouter chat client (OpenAI-compatible) with tool calling and cost reporting."""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

from . import config

URL = "https://openrouter.ai/api/v1/chat/completions"


class LLMError(RuntimeError):
    pass


def chat(messages: list[dict], tools: list[dict] | None = None, tool_choice: str | None = None) -> dict:
    """One completion. Returns {"message", "usage", "latency_s", "raw_id"}.

    usage carries prompt_tokens, completion_tokens and cost (USD) as reported by
    OpenRouter's usage accounting.
    """
    body: dict = {
        "model": config.MODEL,
        "messages": messages,
        "temperature": config.TEMPERATURE,
        "usage": {"include": True},
    }
    if tools:
        body["tools"] = tools
        if tool_choice:
            body["tool_choice"] = tool_choice
    headers = {
        "Authorization": f"Bearer {config.secret('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json",
        "X-Title": "live-package-data-experiment",
    }
    data = json.dumps(body).encode()
    last_err = ""
    for attempt in range(6):
        t0 = time.monotonic()
        try:
            req = urllib.request.Request(URL, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=180) as resp:
                payload = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            last_err = f"HTTP {e.code}: {e.read()[:400]!r}"
            if e.code in (408, 429, 500, 502, 503, 504):
                time.sleep(2 ** attempt * 2)
                continue
            raise LLMError(last_err) from e
        except (urllib.error.URLError, TimeoutError) as e:
            last_err = str(e)
            time.sleep(2 ** attempt * 2)
            continue
        latency = time.monotonic() - t0
        if "error" in payload:
            last_err = json.dumps(payload["error"])[:400]
            time.sleep(2 ** attempt * 2)
            continue
        choice = payload["choices"][0]
        usage = payload.get("usage") or {}
        return {
            "message": choice["message"],
            "finish_reason": choice.get("finish_reason"),
            "usage": {
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "cost": float(usage.get("cost") or 0.0),
            },
            "latency_s": latency,
            "raw_id": payload.get("id"),
            "provider": payload.get("provider"),
        }
    raise LLMError(f"gave up after retries: {last_err}")

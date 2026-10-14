"""Bright Data hosted MCP client: JSON-RPC over streamable HTTP, with a disk cache and a hard request cap.

Every live tools/call is counted in Bright Data credits: 1 per scrape/search, and for
run_scraper 1 per input URL, since scrapers bill 1 credit per record. Polling a running
scraper is counted too, which over-counts slightly. Cached calls cost nothing. The running total lives in cache/bd_usage.json so the cap holds across
processes and reruns.
"""
from __future__ import annotations

import hashlib
import json
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from . import config


class BudgetExceeded(RuntimeError):
    pass


class MCPError(RuntimeError):
    pass


class BrightDataMCP:
    def __init__(self, cap: int = config.BD_REQUEST_CAP):
        token = config.secret("BRIGHTDATA_API_TOKEN", "BRIGHTDATA_API_KEY")
        query = urllib.parse.urlencode({"token": token, "groups": config.BD_GROUPS, "tools": config.BD_EXTRA_TOOLS})
        self._url = f"{config.BD_MCP_URL}?{query}"
        self.cap = cap
        self._session: str | None = None
        self._id = 0
        self._lock = threading.Lock()          # guards usage file and session
        self._key_locks: dict[str, threading.Lock] = {}
        self.cache_dir = config.CACHE_DIR / "bd"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.usage_file = config.CACHE_DIR / "bd_usage.json"

    # ---- transport -------------------------------------------------------
    def _post(self, body: dict) -> dict | None:
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
        if self._session:
            headers["mcp-session-id"] = self._session
        req = urllib.request.Request(self._url, json.dumps(body).encode(), headers)
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                sid = resp.headers.get("mcp-session-id")
                if sid:
                    self._session = sid
                text = resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            detail = e.read()[:300].decode("utf-8", "replace")
            if e.code == 401:
                raise MCPError(f"401 from Bright Data MCP ({detail.strip()}). The token in .env is not valid.") from e
            raise MCPError(f"HTTP {e.code}: {detail}") from e
        if "id" not in body:
            return None
        # Replies come either as plain JSON or as SSE `data:` lines.
        candidates = [text] if text.lstrip().startswith("{") else [
            ln[5:].strip() for ln in text.splitlines() if ln.startswith("data:")
        ]
        for raw in candidates:
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if msg.get("id") == body["id"]:
                if "error" in msg:
                    raise MCPError(json.dumps(msg["error"])[:500])
                return msg["result"]
        raise MCPError(f"no JSON-RPC reply for id {body['id']}: {text[:300]}")

    def _rpc(self, method: str, params: dict | None = None) -> dict:
        with self._lock:
            if self._session is None and method != "initialize":
                self._initialize_locked()
            self._id += 1
            body = {"jsonrpc": "2.0", "id": self._id, "method": method, "params": params or {}}
        try:
            return self._post(body)
        except MCPError as e:
            if "404" in str(e) or "session" in str(e).lower():   # session expired: start over once
                with self._lock:
                    self._session = None
                    self._initialize_locked()
                return self._post(body)
            raise

    def _initialize_locked(self) -> None:
        self._id += 1
        self._post({"jsonrpc": "2.0", "id": self._id, "method": "initialize", "params": {
            "protocolVersion": "2025-03-26", "capabilities": {},
            "clientInfo": {"name": "live-package-data-experiment", "version": "1.0"}}})
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"})

    # ---- public API ------------------------------------------------------
    def list_tools(self, refresh: bool = False) -> list[dict]:
        path = config.CACHE_DIR / "bd_tools_list.json"
        if path.exists() and not refresh:
            return json.loads(path.read_text())
        tools = self._rpc("tools/list")["tools"]
        path.write_text(json.dumps(tools, indent=2))
        return tools

    def usage(self) -> dict:
        if self.usage_file.exists():
            return json.loads(self.usage_file.read_text())
        return {"requests": 0, "calls": []}

    def _count(self, name: str, args: dict, units: int = 1) -> None:
        with self._lock:
            usage = self.usage()
            if usage["requests"] + units > self.cap:
                raise BudgetExceeded(f"Bright Data cap {self.cap} reached ({usage['requests']} used)")
            usage["requests"] += units
            usage["calls"].append({"t": time.strftime("%Y-%m-%dT%H:%M:%S"), "tool": name,
                                   "args": {k: v for k, v in args.items() if k != "token"}})
            self.usage_file.write_text(json.dumps(usage, indent=1))

    def call(self, name: str, args: dict) -> dict:
        """Return {"text", "is_error", "cached", "live_requests"}.

        Successful results are cached forever on disk; errors are not cached.
        """
        key = hashlib.sha256(json.dumps([name, args], sort_keys=True).encode()).hexdigest()[:24]
        path = self.cache_dir / f"{key}.json"
        with self._lock:
            key_lock = self._key_locks.setdefault(key, threading.Lock())
        with key_lock:                      # parallel runs asking for the same page fetch it once
            if path.exists():
                hit = json.loads(path.read_text())
                return {"text": hit["text"], "is_error": False, "cached": True, "live_requests": 0}
            units = max(1, len(args.get("input") or [])) if name == "run_scraper" else 1
            self._count(name, args, units)
            live = units
            result = self._rpc("tools/call", {"name": name, "arguments": args})
            text = "\n".join(c.get("text", "") for c in result.get("content", []) if c.get("type") == "text")
            is_error = bool(result.get("isError"))
            if name == "run_scraper" and not is_error:
                text, extra = self._finish_scraper_run(text)
                live += extra
            if not is_error and text.strip():
                path.write_text(json.dumps({"tool": name, "args": args, "text": text,
                                            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S")}))
            return {"text": text, "is_error": is_error, "cached": False, "live_requests": live}

    def _finish_scraper_run(self, text: str) -> tuple[str, int]:
        """run_scraper waits 45 s and may answer {snapshot_id, status: "running"}; poll until ready.

        Shape taken from @brightdata/mcp 3.0.0 scraper_run.js: {snapshot_id, status, data}.
        """
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return text, 0
        if not isinstance(data, dict) or data.get("status") != "running" or not data.get("snapshot_id"):
            return text, 0
        extra = 0
        for _ in range(8):
            time.sleep(10)
            self._count("get_scraper_results", {"snapshot_id": data["snapshot_id"]})
            extra += 1
            res = self._rpc("tools/call", {"name": "get_scraper_results", "arguments": {"snapshot_id": data["snapshot_id"]}})
            out = "\n".join(c.get("text", "") for c in res.get("content", []) if c.get("type") == "text")
            try:
                if json.loads(out).get("status") != "running":
                    return out, extra
            except (json.JSONDecodeError, AttributeError):
                return out, extra
        return text, extra

"""Static and runtime checks for one generated program.

Per run we count:
- deprecated (static): regex hits of the task's ground-truth patterns on comment-free code
- deprecated (runtime): deprecation warnings raised from the script, or matching a ground-truth
  marker, in a normal run; plus failures caused by a ground-truth API that has since been removed
- strict run: the same program under `-W error::DeprecationWarning` (Python) or
  `--throw-deprecation` (Node)
- hallucinated: imported names / attribute chains that do not exist in the installed version
  (static), plus ImportError / AttributeError at runtime (Node: missing export, missing
  module, `x is not a function`), excluding anything explained by the ground truth
- runs: exit code 0 within the timeout
"""
from __future__ import annotations

import io
import json
import os
import re
import shutil
import subprocess
import sys
import tokenize
from pathlib import Path

from . import config

# Generated code gets no network except loopback (the Express task talks to itself).
SANDBOX_PROFILE = ('(version 1)(allow default)(deny network-outbound (remote ip "*:*"))'
                   '(allow network-outbound (remote ip "localhost:*"))')
USE_SANDBOX_EXEC = sys.platform == "darwin" and shutil.which("sandbox-exec") is not None

PY_HALLUCINATION = {"ImportError", "ModuleNotFoundError", "AttributeError"}
JS_HALLUCINATION = re.compile(
    r"does not provide an export named|ERR_PACKAGE_PATH_NOT_EXPORTED|ERR_MODULE_NOT_FOUND|"
    r"Cannot find (?:module|package)|is not a function|is not a constructor|"
    r"Cannot read properties of undefined|is not iterable|is not defined")


def strip_python_comments(code: str) -> str:
    try:
        toks = [t for t in tokenize.generate_tokens(io.StringIO(code).readline) if t.type != tokenize.COMMENT]
        return tokenize.untokenize(toks)
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return re.sub(r"(?m)^\s*#.*$", "", code)


def strip_js_comments(code: str) -> str:
    out, i, n = [], 0, len(code)
    quote = None
    while i < n:
        c = code[i]
        if quote:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(code[i + 1]); i += 2; continue
            if c == quote:
                quote = None
            i += 1; continue
        if c in "'\"`":
            quote = c; out.append(c); i += 1; continue
        if code.startswith("//", i):
            j = code.find("\n", i); i = n if j < 0 else j; continue
        if code.startswith("/*", i):
            j = code.find("*/", i + 2); i = n if j < 0 else j + 2; continue
        out.append(c); i += 1
    return "".join(out)


def _sandboxed(cmd: list[str]) -> list[str]:
    return ["sandbox-exec", "-p", SANDBOX_PROFILE, *cmd] if USE_SANDBOX_EXEC else cmd


def _run(cmd: list[str], cwd: Path, env: dict | None = None) -> dict:
    try:
        p = subprocess.run(_sandboxed(cmd), cwd=cwd, capture_output=True, text=True,
                           timeout=config.EXEC_TIMEOUT_S, env={**os.environ, **(env or {})})
        return {"returncode": p.returncode, "stdout": p.stdout[-8000:], "stderr": p.stderr[-8000:], "timeout": False}
    except subprocess.TimeoutExpired as e:
        def _txt(b):
            return (b.decode("utf-8", "replace") if isinstance(b, bytes) else (b or ""))[-8000:]
        return {"returncode": None, "stdout": _txt(e.stdout), "stderr": _txt(e.stderr), "timeout": True}


def _gt_marker_hits(text: str, task: dict) -> list[str]:
    return [g["deprecated"] for g in task["ground_truth"] if any(m and m in text for m in g["runtime_markers"])]


def static_matches(code: str, task: dict) -> dict:
    clean = strip_python_comments(code) if task["language"] == "python" else strip_js_comments(code)
    hits = {}
    for g in task["ground_truth"]:
        n = sum(len(re.findall(p, clean)) for p in g["static_patterns"])
        if n:
            hits[g["deprecated"]] = n
    return {"clean": clean, "hits": hits}


def _gt_items_for_symbol(u: dict, task: dict, clean: str) -> list[str]:
    """Ground-truth items that explain an unresolved symbol (a removed API, not a hallucination)."""
    symbol, last = u["symbol"], u["symbol"].replace(":", ".").split(".")[-1]
    items = []
    for g in task["ground_truth"]:
        pats, marks = g["static_patterns"], [m.strip("'") for m in g["runtime_markers"] if len(m.strip("'")) > 3]
        if (any(re.search(p, symbol) or re.search(p, f".{last}(") or re.search(p, f".{last} ") for p in pats)
                or any(m in symbol for m in marks)):
            items.append(g["deprecated"])
        elif u.get("kind") in ("module", "named-import"):
            spec = symbol.split(":")[0]
            if any(spec in m.group(0) for p in pats for m in re.finditer(p, clean)):
                items.append(g["deprecated"])
    return items


def evaluate(code: str | None, task: dict, workdir: Path) -> dict:
    res: dict = {"code_extracted": code is not None}
    if code is None:
        res.update(runs=False, strict_runs=False, deprecated_static=0, deprecated_static_items={},
                   deprecated_runtime=0, removed_api_errors=0, gt_items_hit=[], hallucinated=0,
                   hallucinated_symbols=[], error_type="no_code", error_message="no fenced code block in reply")
        return res
    workdir.mkdir(parents=True, exist_ok=True)
    st = static_matches(code, task)
    res["deprecated_static"] = sum(st["hits"].values())
    res["deprecated_static_items"] = st["hits"]
    if task["language"] == "python":
        res.update(_eval_python(code, st["clean"], task, workdir, st["hits"]))
    else:
        res.update(_eval_node(code, st["clean"], task, workdir, st["hits"]))
    gt = set(st["hits"]) | set(res.pop("_gt_runtime", []))
    res["gt_items_hit"] = sorted(gt)
    return res


# ---------------------------------------------------------------- Python
def _eval_python(code: str, clean: str, task: dict, workdir: Path, static_hits: dict) -> dict:
    script = workdir / "main.py"
    script.write_text(code)
    (workdir / "clean.py").write_text(clean)
    py = str(config.SANDBOX_PYTHON)
    env = {"MPLBACKEND": "Agg", "PYTHONDONTWRITEBYTECODE": "1"}
    out: dict = {}

    # Static resolution of imports and module attribute chains.
    r = _run([py, "-I", str(config.TOOLS_DIR / "pyresolve.py"), str(script)], workdir, env)
    try:
        unresolved = json.loads(r["stdout"].strip().splitlines()[-1]) if r["stdout"].strip() else []
    except (json.JSONDecodeError, IndexError):
        unresolved = []
        out["resolver_error"] = r["stderr"][-500:]

    # Normal run with all warnings recorded.
    report_path = workdir / "harness.json"
    normal = _run([py, "-I", str(config.TOOLS_DIR / "pyharness.py"), str(script), str(report_path)], workdir, env)
    (workdir / "stdout.txt").write_text(normal["stdout"])
    (workdir / "stderr.txt").write_text(normal["stderr"])
    report = json.loads(report_path.read_text()) if report_path.exists() else {"exit": "crash", "exception": None, "warnings": []}
    exc = report.get("exception") or {}

    dep_warnings, gt_runtime = set(), set()
    for w in report["warnings"]:
        markers = _gt_marker_hits(w["message"], task)
        if w["deprecation"] and (w["in_script"] or markers):
            dep_warnings.add((w["category"], w["message"].strip().splitlines()[0][:160] if w["message"].strip() else ""))
        gt_runtime.update(markers)

    removed_api_error = False
    runtime_halluc = None
    if exc:
        text = f"{exc.get('type')}: {exc.get('message')}"
        markers = _gt_marker_hits(text, task)
        if markers:
            removed_api_error = True
            gt_runtime.update(markers)
        elif "'NoneType' object has no attribute" in exc.get("message", ""):
            pass                                  # an ordinary bug, not a made-up API
        elif exc.get("type") in PY_HALLUCINATION or set(exc.get("mro") or []) & PY_HALLUCINATION:
            m = re.search(r"attribute '([^']+)'|named '([^']+)'|cannot import name '([^']+)'", exc.get("message", ""))
            runtime_halluc = next((g for g in (m.groups() if m else ()) if g), exc.get("name") or exc.get("message", "")[:80])

    # Strict run: deprecations become errors.
    strict = _run([py, "-I", "-W", "error::DeprecationWarning", "-W", "error::PendingDeprecationWarning",
                   "-W", "error::FutureWarning", str(script)], workdir, env)
    (workdir / "strict_stderr.txt").write_text(strict["stderr"])
    strict_dep = bool(re.search(r"(\w*Deprecat\w*|FutureWarning|LegacyAPIWarning|MovedIn20Warning)\b", strict["stderr"].splitlines()[-1] if strict["stderr"].strip() else ""))

    halluc = [u for u in unresolved if not _gt_items_for_symbol(u, task, clean)]
    gt_static_missing = [u for u in unresolved if _gt_items_for_symbol(u, task, clean)]
    names = {u["missing"] for u in halluc}
    if runtime_halluc and runtime_halluc not in names and not any(runtime_halluc in u["symbol"] for u in halluc):
        halluc.append({"symbol": runtime_halluc, "missing": runtime_halluc, "kind": "runtime"})

    ok = normal["returncode"] == 0 and report.get("exit") == "ok" and not normal["timeout"]
    out.update(
        runs=ok, timeout=normal["timeout"],
        strict_runs=strict["returncode"] == 0 and not strict["timeout"],
        strict_failed_on_deprecation=strict_dep,
        deprecated_runtime=len(dep_warnings) + int(removed_api_error),
        deprecation_warnings=sorted(f"{c}: {m}" for c, m in dep_warnings),
        removed_api_errors=int(removed_api_error),
        hallucinated=len(halluc), hallucinated_symbols=halluc,
        removed_api_symbols=gt_static_missing,
        error_type=exc.get("type") if exc else ("Timeout" if normal["timeout"] else None),
        error_message=(exc.get("message") or "")[:400] if exc else None,
        _gt_runtime=sorted(gt_runtime | {i for u in gt_static_missing for i in _gt_items_for_symbol(u, task, clean)}),
    )
    return out


# ---------------------------------------------------------------- Node
def _js_error(stderr: str) -> tuple[str | None, str | None]:
    m = re.search(r"^(\w*Error)(?: \[(\w+)\])?: (.+)$", stderr, re.M)
    if m:
        return (m.group(2) or m.group(1)), m.group(3)[:400]
    m = re.search(r"code: '(ERR_\w+)'", stderr)
    return (m.group(1), stderr.strip().splitlines()[-1][:400]) if m else (None, None)


def _eval_node(code: str, clean: str, task: dict, workdir: Path, static_hits: dict) -> dict:
    # Scripts must live under sandbox/node so bare imports resolve to its node_modules.
    node_work = config.NODE_SANDBOX / "work" / workdir.relative_to(config.RUNS_DIR)
    if node_work.exists():
        shutil.rmtree(node_work)
    node_work.mkdir(parents=True)
    is_cjs = "require(" in clean and not re.search(r"^\s*import\s", clean, re.M)
    script = node_work / ("main.cjs" if is_cjs else "main.mjs")
    script.write_text(code)
    (workdir / script.name).write_text(code)
    (node_work / "clean.js").write_text(clean)
    shutil.copy(config.TOOLS_DIR / "jsresolve.mjs", node_work / "jsresolve.mjs")
    out: dict = {}

    r = _run(["node", "jsresolve.mjs", str(script), "clean.js"], node_work)
    try:
        unresolved = json.loads(r["stdout"].strip().splitlines()[-1]) if r["stdout"].strip() else []
    except (json.JSONDecodeError, IndexError):
        unresolved = []
        out["resolver_error"] = (r["stderr"] or r["stdout"])[-500:]

    normal = _run(["node", script.name], node_work)
    (workdir / "stdout.txt").write_text(normal["stdout"])
    (workdir / "stderr.txt").write_text(normal["stderr"])
    strict = _run(["node", "--throw-deprecation", script.name], node_work)
    (workdir / "strict_stderr.txt").write_text(strict["stderr"])

    err_type, err_msg = _js_error(normal["stderr"]) if normal["returncode"] not in (0, None) else (None, None)
    gt_runtime = set()
    dep_lines = {ln.strip()[:160] for ln in normal["stderr"].splitlines() if re.search(r"deprecat", ln, re.I)}
    for ln in dep_lines:
        gt_runtime.update(_gt_marker_hits(ln, task))

    removed_api_error, runtime_halluc = False, None
    if err_type:
        text = f"{err_type}: {err_msg}\n{normal['stderr'][-1500:]}"
        markers = _gt_marker_hits(text, task)
        if markers:
            removed_api_error = True
            gt_runtime.update(markers)
        elif static_hits and re.search(r"Cannot read properties of undefined|is not iterable", err_msg or ""):
            # A removed property (e.g. zod's error.errors) shows up as undefined one step later.
            removed_api_error = True
        elif JS_HALLUCINATION.search(text):
            m = re.search(r"export named '([^']+)'|subpath '([^']+)'|(\S+) is not a (?:function|constructor)|reading '([^']+)'|package '([^']+)'|(\S+) is not defined", text)
            runtime_halluc = next((g for g in (m.groups() if m else ()) if g), err_msg[:80] if err_msg else "?")

    halluc = [u for u in unresolved if not _gt_items_for_symbol(u, task, clean)]
    gt_static_missing = [u for u in unresolved if _gt_items_for_symbol(u, task, clean)]
    if runtime_halluc and not any(runtime_halluc in u["symbol"] or u["missing"] in runtime_halluc for u in halluc):
        halluc.append({"symbol": runtime_halluc, "missing": runtime_halluc, "kind": "runtime"})

    out.update(
        runs=normal["returncode"] == 0 and not normal["timeout"], timeout=normal["timeout"],
        strict_runs=strict["returncode"] == 0 and not strict["timeout"],
        strict_failed_on_deprecation=strict["returncode"] not in (0, None) and "DeprecationWarning" in strict["stderr"],
        deprecated_runtime=len(dep_lines) + int(removed_api_error),
        deprecation_warnings=sorted(dep_lines),
        removed_api_errors=int(removed_api_error),
        hallucinated=len(halluc), hallucinated_symbols=halluc,
        removed_api_symbols=gt_static_missing,
        error_type=err_type or ("Timeout" if normal["timeout"] else None),
        error_message=err_msg,
        _gt_runtime=sorted(gt_runtime | {i for u in gt_static_missing for i in _gt_items_for_symbol(u, task, clean)}),
    )
    return out

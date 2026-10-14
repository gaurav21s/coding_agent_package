"""Collect runs/ into results.csv and summary.md.

    python3.11 -m exp.report
"""
from __future__ import annotations

import csv
import json
import statistics
from collections import defaultdict

from . import config

FIELDS = ["task_id", "ecosystem", "package", "agent", "run", "model", "code_extracted", "runs", "strict_runs",
          "strict_failed_on_deprecation", "deprecated_static", "deprecated_runtime", "removed_api_errors",
          "gt_items_hit_count", "deprecated_any", "hallucinated", "error_type", "prompt_tokens",
          "completion_tokens", "total_tokens", "llm_calls", "tool_calls", "tool_errors", "bd_requests",
          "bd_cache_hits", "latency_s", "cost_usd", "stop_reason", "gt_items_hit", "hallucinated_symbols",
          "error_message"]


def collect() -> list[dict]:
    tasks = {t["id"]: t for t in json.loads(config.TASKS_FILE.read_text())["tasks"]}
    rows = []
    for tid, task in tasks.items():
        for agent in ("A", "B"):
            for d in sorted((config.RUNS_DIR / tid / agent).glob("run*")):
                if not (d / "agent.json").exists() or not (d / "eval.json").exists():
                    continue
                a = json.loads((d / "agent.json").read_text())
                e = json.loads((d / "eval.json").read_text())
                rows.append({
                    "task_id": tid, "ecosystem": task["ecosystem"], "package": task["package"], "agent": agent,
                    "run": int(d.name[3:]), "model": a["model"], "code_extracted": e["code_extracted"],
                    "runs": e["runs"], "strict_runs": e["strict_runs"],
                    "strict_failed_on_deprecation": e.get("strict_failed_on_deprecation", False),
                    "deprecated_static": e["deprecated_static"], "deprecated_runtime": e["deprecated_runtime"],
                    "removed_api_errors": e["removed_api_errors"], "gt_items_hit_count": len(e["gt_items_hit"]),
                    "deprecated_any": bool(e["gt_items_hit"]) or e["deprecated_runtime"] > 0,
                    "hallucinated": e["hallucinated"], "error_type": e.get("error_type") or "",
                    "prompt_tokens": a["prompt_tokens"], "completion_tokens": a["completion_tokens"],
                    "total_tokens": a["prompt_tokens"] + a["completion_tokens"], "llm_calls": a["llm_calls"],
                    "tool_calls": a["tool_calls"], "tool_errors": a["tool_errors"], "bd_requests": a["bd_requests"],
                    "bd_cache_hits": a["bd_cache_hits"], "latency_s": a["latency_s"],
                    "cost_usd": round(a["cost_usd"], 6), "stop_reason": a["stop_reason"],
                    "gt_items_hit": "; ".join(e["gt_items_hit"]),
                    "hallucinated_symbols": "; ".join(h["symbol"] for h in e["hallucinated_symbols"]),
                    "error_message": (e.get("error_message") or "").replace("\n", " ")[:300],
                })
    return rows


def _mean(xs):
    return statistics.fmean(xs) if xs else float("nan")


def _pct(xs):
    return 100 * _mean([float(x) for x in xs]) if xs else float("nan")


def _fmt(x, digits=2):
    return "n/a" if x != x else f"{x:.{digits}f}"


def overall_table(rows: list[dict]) -> list[str]:
    by = {a: [r for r in rows if r["agent"] == a] for a in ("A", "B")}
    metrics = [
        ("runs evaluated", lambda rs: len(rs), 0),
        ("deprecated calls per run (static match)", lambda rs: _mean([r["deprecated_static"] for r in rs]), 2),
        ("deprecation warnings + removed-API errors per run (runtime)", lambda rs: _mean([r["deprecated_runtime"] for r in rs]), 2),
        ("ground-truth items hit per run", lambda rs: _mean([r["gt_items_hit_count"] for r in rs]), 2),
        ("% runs using any deprecated/removed API", lambda rs: _pct([r["deprecated_any"] for r in rs]), 1),
        ("% runs failing under -W error / --throw-deprecation because of a deprecation", lambda rs: _pct([r["strict_failed_on_deprecation"] for r in rs]), 1),
        ("hallucinated APIs per run", lambda rs: _mean([r["hallucinated"] for r in rs]), 2),
        ("% runs with at least one hallucinated API", lambda rs: _pct([r["hallucinated"] > 0 for r in rs]), 1),
        ("% runs where the code runs (exit 0)", lambda rs: _pct([r["runs"] for r in rs]), 1),
        ("% runs passing the strict run", lambda rs: _pct([r["strict_runs"] for r in rs]), 1),
        ("prompt tokens per run", lambda rs: _mean([r["prompt_tokens"] for r in rs]), 0),
        ("completion tokens per run", lambda rs: _mean([r["completion_tokens"] for r in rs]), 0),
        ("tool calls per run", lambda rs: _mean([r["tool_calls"] for r in rs]), 2),
        ("Bright Data requests per run (live, uncached)", lambda rs: _mean([r["bd_requests"] for r in rs]), 2),
        ("Bright Data requests total", lambda rs: sum(r["bd_requests"] for r in rs), 0),
        ("cache hits per run", lambda rs: _mean([r["bd_cache_hits"] for r in rs]), 2),
        ("latency per run, mean (s)", lambda rs: _mean([r["latency_s"] for r in rs]), 1),
        ("latency per run, median (s)", lambda rs: statistics.median([r["latency_s"] for r in rs]) if rs else float("nan"), 1),
        ("LLM cost per run (USD)", lambda rs: _mean([r["cost_usd"] for r in rs]), 5),
        ("LLM cost total (USD)", lambda rs: sum(r["cost_usd"] for r in rs), 4),
    ]
    out = ["| metric | A (no tools) | B (Bright Data) | B minus A |", "|---|---:|---:|---:|"]
    for name, fn, d in metrics:
        a = fn(by["A"]) if by["A"] else float("nan")
        b = fn(by["B"]) if by["B"] else float("nan")
        diff = b - a if (a == a and b == b) else float("nan")
        out.append(f"| {name} | {_fmt(a, d)} | {_fmt(b, d)} | {_fmt(diff, d)} |")
    return out


def _badness(rs: list[dict]) -> int:
    """Failures summed over runs: deprecated use, hallucination, code that does not run."""
    return sum(int(r["deprecated_any"]) + int(r["hallucinated"] > 0) + int(not r["runs"]) for r in rs)


def per_task(rows: list[dict], tasks: list[dict]) -> tuple[list[str], list[tuple[str, str, list, list]]]:
    out = ["| task | package | deprecated runs A | deprecated runs B | hallucinated APIs A | hallucinated APIs B | runs OK A | runs OK B | B tool calls (mean) | outcome |",
           "|---|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    verdicts = []
    for t in tasks:
        a = [r for r in rows if r["task_id"] == t["id"] and r["agent"] == "A"]
        b = [r for r in rows if r["task_id"] == t["id"] and r["agent"] == "B"]
        if not a and not b:
            continue
        if a and b:
            ba, bb = _badness(a), _badness(b)
            outcome = "B better" if bb < ba else "B worse" if bb > ba else ("both clean" if ba == 0 else "no difference")
        else:
            outcome = "only one agent ran"
        verdicts.append((t["id"], outcome, a, b))

        def frac(rs, key):
            return f"{sum(bool(r[key]) for r in rs)}/{len(rs)}" if rs else "n/a"
        out.append(f"| {t['id']} | {t['package']} | {frac(a, 'deprecated_any')} | {frac(b, 'deprecated_any')} | "
                   f"{sum(r['hallucinated'] for r in a) if a else 'n/a'} | {sum(r['hallucinated'] for r in b) if b else 'n/a'} | "
                   f"{frac(a, 'runs')} | {frac(b, 'runs')} | {_fmt(_mean([r['tool_calls'] for r in b]), 1) if b else 'n/a'} | {outcome} |")
    return out, verdicts


def detail(rows: list[dict]) -> list[str]:
    out = ["| task | agent | run | runs | deprecated items hit | hallucinated symbols | error |", "|---|---|---:|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (r["task_id"], r["agent"], r["run"])):
        err = f"{r['error_type']}: {r['error_message'][:90]}" if r["error_type"] else ""
        out.append(f"| {r['task_id']} | {r['agent']} | {r['run']} | {'yes' if r['runs'] else 'no'} | "
                   f"{r['gt_items_hit'] or '-'} | {r['hallucinated_symbols'] or '-'} | {err.replace('|', '/')} |")
    return out


DATASET_NAMES = {v["dataset_id"]: k for k, v in config.BD_DATASETS.items()}


def data_quality() -> list[str]:
    """What the cached Bright Data responses actually contained."""
    stats: dict = defaultdict(lambda: defaultdict(int))
    for f in sorted((config.CACHE_DIR / "bd").glob("*.json")):
        c = json.loads(f.read_text())
        kind = c["tool"] if c["tool"] != "run_scraper" else DATASET_NAMES.get(c["args"].get("dataset_id"), "other") + " scraper"
        body = c["text"].split("_BEGIN=====", 1)[-1].split("=====UNTRUSTED", 1)[0]
        st = stats[kind]
        st["fetches"] += 1
        if c["tool"] == "run_scraper":
            try:
                rec = (json.loads(body).get("data") or [{}])[0]
            except (json.JSONDecodeError, AttributeError, IndexError):
                rec = {}
            st["with version"] += int(bool(rec.get("version")))
            st["with README / file content"] += int(bool(rec.get("readme_content") or rec.get("code")))
            st["empty record"] += int(not (rec.get("version") or rec.get("readme_content") or rec.get("code")))
        else:
            st["mean chars"] += len(body)
    out = ["| source | unique fetches | with version | with README / file content | empty record | mean chars |",
           "|---|---:|---:|---:|---:|---:|"]
    for kind, st in sorted(stats.items()):
        mean = st["mean chars"] / st["fetches"] if st["mean chars"] else 0
        if "scraper" in kind:
            out.append(f"| {kind} | {st['fetches']} | {st['with version']} | {st['with README / file content']} | {st['empty record']} | |")
        else:
            out.append(f"| {kind} | {st['fetches']} | | | | {mean:,.0f} |")
    return out


def tool_usage() -> list[str]:
    counts: dict = defaultdict(lambda: defaultdict(int))
    for f in config.RUNS_DIR.glob("*/B/run*/agent.json"):
        for t in json.loads(f.read_text())["tool_log"]:
            name = t["tool"]
            if name == "run_scraper":
                name += f" ({DATASET_NAMES.get(t['args'].get('dataset_id'), 'other dataset')})"
            c = counts[name]
            c["calls"] += 1
            c["cache hits"] += int(bool(t.get("cached")))
            c["errors"] += int(bool(t.get("is_error") or t.get("error")) or "live_requests" not in t)
    out = ["| tool | calls | served from cache | errors or refused |", "|---|---:|---:|---:|"]
    for name, c in sorted(counts.items(), key=lambda kv: -kv[1]["calls"]):
        out.append(f"| {name} | {c['calls']} | {c['cache hits']} | {c['errors']} |")
    return out


def main() -> None:
    rows = collect()
    tasks = json.loads(config.TASKS_FILE.read_text())["tasks"]
    with open(config.ROOT / "results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    versions = {}
    vf = config.SANDBOX_DIR / "versions.json"
    if vf.exists():
        versions = json.loads(vf.read_text())
    usage_file = config.CACHE_DIR / "bd_usage.json"
    bd_used = json.loads(usage_file.read_text())["requests"] if usage_file.exists() else 0
    agents_present = sorted({r["agent"] for r in rows})
    models = sorted({r["model"] for r in rows})

    md = ["# Does live package data reduce deprecated and hallucinated API use?", ""]
    md += [f"Model: `{', '.join(models) or config.MODEL}` at temperature {config.TEMPERATURE}, same system prompt for both agents. "
           f"{len(tasks)} tasks, up to {config.RUNS_PER_TASK} runs per task per agent. "
           f"Bright Data requests used (all time, from cache/bd_usage.json): {bd_used} of a {config.BD_REQUEST_CAP} cap.", ""]
    if "B" not in agents_present:
        md += ["**Agent B has no runs yet.** The Bright Data MCP rejected the token in `.env` (HTTP 401), so only the baseline "
               "ran. Put a valid `BRIGHTDATA_API_TOKEN` in `.env`, run `python3.11 -m exp.bd_check`, then "
               "`python3.11 -m exp.run --agents B`. Finished A runs are kept and the report regenerates.", ""]

    md += ["## A vs B, all tasks", ""] + overall_table(rows) + [""]
    md += ["How to read it. \"Static\" counts regex matches of the ground-truth deprecated APIs in the code with comments removed. "
           "\"Runtime\" counts deprecation warnings raised from the script (or matching a ground-truth API) in a normal run, plus a crash "
           "caused by a ground-truth API that the installed version has removed. Hallucinated APIs are imports, exports and "
           "attribute chains that do not exist in the installed version, found by resolving them statically and by ImportError / "
           "AttributeError at runtime (in Node: missing export or subpath, `x is not a function`). A removed ground-truth API is "
           "counted as deprecated, not hallucinated.", ""]

    analysis = config.ROOT / "analysis.md"
    if analysis.exists():
        md += [analysis.read_text().strip(), ""]

    for eco in ("pypi", "npm"):
        sub = [r for r in rows if r["ecosystem"] == eco]
        if sub:
            md += [f"### {eco} only", ""] + overall_table(sub)[:10] + [""]

    table, verdicts = per_task(rows, tasks)
    md += ["## Every task", "", "Counts are over the runs of each agent (deprecated runs = runs that used at least one deprecated or "
           "removed ground-truth API). Outcome compares the sum of failures (deprecated use, hallucination, code that does not run) "
           "across runs.", ""] + table + [""]

    counts = defaultdict(int)
    for _, o, _, _ in verdicts:
        counts[o] += 1
    md += ["## Where B did not help", ""]
    md += [f"Outcomes: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())) + ".", ""]
    for tid, outcome, a, b in verdicts:
        if outcome in ("B worse", "no difference", "both clean"):
            b_err = sorted({r["error_type"] for r in b if r["error_type"]})
            b_gt = sorted({i for r in b for i in r["gt_items_hit"].split("; ") if i})
            notes = []
            if b_gt:
                notes.append(f"B still used {', '.join(b_gt)}")
            if b_err:
                notes.append(f"B errors: {', '.join(b_err)}")
            if outcome == "both clean":
                notes.append("A already avoided the deprecated APIs, so tools could only add cost")
            md.append(f"- `{tid}`: {outcome}. " + ("; ".join(notes) + "." if notes else ""))
    md += [""]

    if any(config.RUNS_DIR.glob("*/B/run*/agent.json")):
        md += ["## What agent B fetched", "", "Tool calls across all B runs (refused = unknown tool or a dataset outside the "
               "three enabled ones):", ""] + tool_usage() + [""]
        md += ["What the unique (cached) Bright Data responses contained:", ""] + data_quality() + [""]

    md += ["## Ground truth sources", "", "| task | deprecated | replacement | source |", "|---|---|---|---|"]
    for t in tasks:
        for g in t["ground_truth"]:
            md.append(f"| {t['id']} | `{g['deprecated']}` | `{g['replacement']}` | [{g['status']}]({g['source_url']}) |")
    md += [""]

    if versions:
        md += ["## Versions tested against", "",
               "Python: " + ", ".join(f"{k} {v}" for k, v in versions.get("python", {}).items()),
               "", "npm: " + ", ".join(f"{k} {v}" for k, v in versions.get("npm", {}).items()), ""]

    md += ["## Caveats", "",
           "- The Bright Data tool names in the brief (`web_data_npm_package`, `web_data_pypi_package`, the GitHub file tool) no "
           "longer exist. The MCP README of 2026-10-12 maps `groups=code,research` to the `scrapers` group, and npm, PyPI and GitHub "
           "file data come from `run_scraper` with the npmjs, pypi and GitHub repository dataset IDs (npm and PyPI take "
           "`package_name`, GitHub takes a file `url`). Agent B gets `run_scraper` (limited to those three datasets), "
           "`scrape_as_markdown` and `discover`. The hosted server left `discover` out for `groups=code,research`, so the URL "
           "also passes `tools=discover`.",
           "- One B run (js-zod-validate run 1) was discarded and rerun: the first version of the tool description told the model "
           "to pass a URL to the npm scraper, which rejects it. No other run was rerun or dropped.",
           "- Bright Data usage is counted in credits as the free tier bills them: 1 per scrape or search, 1 per scraper record "
           "(one per input URL). Polls of a slow scraper run and failed calls are also counted, so the figure is an upper bound.",
           "- Fetches are cached on disk, so runs 2 and 3 of agent B usually cost no Bright Data requests. Live request counts are "
           "per run; cache hits are listed separately.",
           "- The checks find deprecated and made-up APIs. They do not check that the output is correct.",
           "- Left out of the ground truth on purpose: ESLint's `useEslintrc` option. The ESLint team blog "
           "(eslint.org/blog/2022/08/new-config-system-part-3) says \"The useEslintrc option has been removed\" from the flat-config "
           "class, but no changelog or migration guide names it, so runs that pass it count as code that does not run "
           "(ESLintInvalidOptionsError), not as deprecated use.",
           "- NumPy's 2.0 notes call `np.trapz` deprecated; the installed 2.4 has removed it, so using it fails at runtime.",
           "- Static patterns are regexes and can miss unusual spellings; the runtime checks cover the case where the API was removed.",
           "- Generated code ran under macOS `sandbox-exec` with outbound network blocked except loopback, with a "
           f"{config.EXEC_TIMEOUT_S} s timeout.",
           "- One model, 3 runs per cell. At temperature 0 the runs are often identical, so treat per-task differences as small samples.",
           ""]
    md += ["## Per-run detail", ""] + detail(rows) + [""]
    (config.ROOT / "summary.md").write_text("\n".join(md))
    print(f"wrote results.csv ({len(rows)} rows) and summary.md")


if __name__ == "__main__":
    main()

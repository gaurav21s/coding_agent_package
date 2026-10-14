"""Run the experiment: every task x agent x run, then evaluate each generated program.

    python3.11 -m exp.run                    # all tasks, agents A and B, 3 runs each
    python3.11 -m exp.run --agents A         # baseline only
    python3.11 -m exp.run --tasks js-uuid --runs 1
    python3.11 -m exp.run --eval-only        # re-evaluate saved code, no model calls

Finished runs are skipped, so an interrupted experiment resumes where it stopped.
Raw logs go to runs/<task>/<agent>/run<k>/.
"""
from __future__ import annotations

import argparse
import json
import sys
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

from . import config, evaluate
from .agents import run_agent
from .brightdata import BrightDataMCP, BudgetExceeded, MCPError

_print_lock = threading.Lock()
_stop = threading.Event()


def log(msg: str) -> None:
    with _print_lock:
        print(msg, flush=True)


def run_dir(task_id: str, agent: str, k: int):
    return config.RUNS_DIR / task_id / agent / f"run{k}"


def do_one(task: dict, agent: str, k: int, bd: BrightDataMCP | None, eval_only: bool) -> str:
    d = run_dir(task["id"], agent, k)
    d.mkdir(parents=True, exist_ok=True)
    agent_file = d / "agent.json"
    if not agent_file.exists():
        if eval_only or _stop.is_set():
            return "skipped"
        out = run_agent(task, agent, bd)
        (d / "transcript.json").write_text(json.dumps(out.pop("messages"), indent=1))
        (d / "final_reply.md").write_text(out["final_text"] or "")
        agent_file.write_text(json.dumps({k_: v for k_, v in out.items() if k_ != "final_text"}, indent=1))
    rec = json.loads(agent_file.read_text())
    if eval_only or not (d / "eval.json").exists():
        ev = evaluate.evaluate(rec["code"], task, d / "work")
        (d / "eval.json").write_text(json.dumps(ev, indent=1))
    ev = json.loads((d / "eval.json").read_text())
    return (f"runs={ev['runs']!s:5} dep={ev['deprecated_static']}/{ev['deprecated_runtime']} "
            f"hal={ev['hallucinated']} tools={rec['tool_calls']} bd={rec['bd_requests']} "
            f"${rec['cost_usd']:.4f} {rec['latency_s']}s")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--agents", default="A,B")
    ap.add_argument("--tasks", default="", help="comma-separated task ids (default: all)")
    ap.add_argument("--runs", type=int, default=config.RUNS_PER_TASK)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--eval-only", action="store_true")
    args = ap.parse_args(argv)

    config.load_env()
    tasks = json.loads(config.TASKS_FILE.read_text())["tasks"]
    if args.tasks:
        wanted = set(args.tasks.split(","))
        tasks = [t for t in tasks if t["id"] in wanted]
    agents = [a.strip() for a in args.agents.split(",") if a.strip()]

    bd = None
    if "B" in agents and not args.eval_only:
        try:
            bd = BrightDataMCP()
            names = [t["name"] for t in bd.list_tools(refresh=True)]
            log(f"Bright Data MCP tools: {', '.join(names)}")
            log(f"Bright Data requests used so far: {bd.usage()['requests']} / {bd.cap}")
        except (MCPError, SystemExit) as e:
            log(f"Agent B disabled: {e}")
            agents = [a for a in agents if a != "B"]

    # Run index is the outer loop so run 2 and 3 of a task find run 1's fetches in the cache.
    jobs = [(t, a, k) for k in range(1, args.runs + 1) for t in tasks for a in agents]
    log(f"{len(jobs)} jobs: {len(tasks)} tasks x agents {agents} x {args.runs} runs, model {config.MODEL}")
    failures = 0
    for k in range(1, args.runs + 1):
        batch = [j for j in jobs if j[2] == k]
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futs = {pool.submit(do_one, t, a, k_, bd, args.eval_only): (t["id"], a, k_) for t, a, k_ in batch}
            for f in as_completed(futs):
                tid, a, k_ = futs[f]
                try:
                    log(f"[{a}] {tid:24} run{k_}  {f.result()}")
                except BudgetExceeded as e:
                    _stop.set()
                    log(f"STOP: {e}")
                except Exception:  # noqa: BLE001 - keep going, record the failure
                    failures += 1
                    err = traceback.format_exc()
                    (run_dir(tid, a, k_) / "error.txt").write_text(err)
                    log(f"[{a}] {tid:24} run{k_}  FAILED: {err.strip().splitlines()[-1]}")
        if _stop.is_set():
            break
    if bd:
        log(f"Bright Data requests used in total: {bd.usage()['requests']} / {bd.cap}")
    from . import report
    report.main()
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

# Live package data vs deprecated and hallucinated APIs

This experiment checks whether a coding agent that can read live package data writes fewer deprecated or made-up API calls than the same agent without it.

- Agent A has no tools.
- Agent B gets Bright Data's hosted MCP: `run_scraper` (npm, PyPI and GitHub-file datasets only), `scrape_as_markdown` and `discover`.

Both agents use the same model (`google/gemini-3.1-flash-lite` via OpenRouter, override with `EXP_MODEL`), temperature 0 and the same system prompt.

## Run it

```bash
# 1. secrets in .env (never committed)
#    OPENROUTER_API_KEY=...
#    BRIGHTDATA_API_TOKEN=...   (BRIGHTDATA_API_KEY also works)
python3.11 -m exp.setup_sandbox      # clean venv + node sandbox with the latest of every library
python3.11 -m exp.bd_check           # confirms the token and the tool names, makes no tool calls
python3.11 -m exp.run                # 20 tasks x A,B x 3 runs, then writes results.csv + summary.md
```

Useful flags: `--agents A`, `--tasks js-uuid,py-pandas-append`, `--runs 1`, `--eval-only` (re-score saved code without model calls), `python3.11 -m exp.report` (rebuild the report only). Finished runs are skipped, so an interrupted run resumes.

Only the standard library is needed to drive the experiment. The libraries under test live in `sandbox/`.

## Files

- `tasks.json` holds 20 prompts (12 PyPI, 8 npm). Each lists the deprecated API, its replacement, the official changelog or migration guide URL and a quote from it, regexes for static matching, and the error strings a removed version produces.
- `exp/agents.py` runs both agents and the tool loop. B gets at most 8 tool calls, and results are paged to the model 12k characters at a time.
- `exp/brightdata.py` is the MCP client. It caches every successful fetch on disk under `cache/bd/`, counts live requests in `cache/bd_usage.json`, and raises once 2,000 requests are used.
- `exp/evaluate.py` does static matching, static symbol resolution, a normal run and a strict run (`-W error::DeprecationWarning` or `node --throw-deprecation`). Generated code runs under macOS `sandbox-exec` with outbound network blocked except loopback.
- `runs/<task>/<agent>/run<k>/` holds the transcript, final reply, extracted code, agent stats, evaluation, stdout/stderr and the strict-run stderr.
- `results.csv` has one row per run. `summary.md` holds the A vs B tables, every task, and where B did not help.

## Bright Data tool names

The brief named `web_data_npm_package`, `web_data_pypi_package` and a GitHub file tool. The MCP README (checked 2026-10-12) no longer has them. `groups=code,research` are legacy IDs that turn on the `scrapers` group, and package and repository data come from `run_scraper` with these dataset IDs:

| data | dataset_id |
|---|---|
| npm package (input `package_name`) | `gd_mk57m0301khq4jmsul` |
| PyPI package (input `package_name`) | `gd_mk57kc3t1wwgmnepp9` |
| GitHub repository file (input `url`) | `gd_lyrexgxc24b3d4imjt` |

`scrape_as_markdown` stays on. The hosted server left `discover` out for `groups=code,research`, so the URL also passes `tools=discover`.

Free-tier billing, as the Bright Data dashboard shows it: 5,000 shared credits a month, 1 credit per Web Unlocker or SERP request and 1 credit per scraper record. The harness counts `run_scraper` as one credit per input and stops at 2,000. The full experiment used 60.

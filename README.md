# Live package data vs deprecated and hallucinated APIs

This experiment checks whether a coding agent that can read live package data writes fewer deprecated or made-up API calls than the same agent without it.

- Agent A has no tools.
- Agent B gets Bright Data's hosted MCP: `run_scraper` (npm, PyPI and GitHub-file datasets only), `scrape_as_markdown` and `discover`.
- Agent C is the follow-up: the harness fetches each library's official changelog or migration guide, keeps only the lines announcing a deprecation, removal or rename, and injects them. No tool loop, so the model cannot skip the page that matters. It ran on the six libraries agent B got wrong.

Both agents use the same model (`google/gemini-3.1-flash-lite` via OpenRouter, override with `EXP_MODEL`), temperature 0 and the same system prompt.

## Run it

```bash
# 1. secrets in .env (never committed)
#    OPENROUTER_API_KEY=...
#    BRIGHTDATA_API_TOKEN=...   (BRIGHTDATA_API_KEY also works)
python3.11 -m exp.setup_sandbox      # clean venv + node sandbox with the latest of every library
python3.11 -m exp.bd_check           # confirms the token and the tool names, makes no tool calls
python3.11 -m exp.run                # 20 tasks x A,B x 3 runs, then writes results.csv + summary.md
python3.11 -m exp.agent_c            # the 6 tasks B got wrong, with the changelog injected
python3.11 -m exp.agent_c --filter v2 # same, with the three filter rules (runs/<task>/C2/)
python3.11 -m exp.report             # rebuild results.csv + summary.md
```

## What agent C changed

On those six libraries, 18 runs each:

| | A (no tools) | B (Bright Data) | C (changelog injected) | C2 (filter v2) |
|---|---:|---:|---:|---:|
| runs using an outdated API | 9 of 18 | 15 of 18 | 6 of 18 | **3 of 18** |
| runs where the code ran | 12 of 18 | 6 of 18 | 12 of 18 | **15 of 18** |
| prompt tokens per run | 235 | 11,267 | 1,578 | **1,782** |
| mean seconds per run | 2.7 | 11.8 | 4.4 | **3.1** |

Under C, zod switched to `z.email()` and nanoid dropped `nanoid/async`. scikit-learn dropped `squared=False` but computed `np.sqrt(mse)` instead of calling `root_mean_squared_error`. The other three still failed, and two of them failed because the replacement never survived the filter:

- **scikit-learn**: `scrape_as_markdown` keeps link markup, so the 284-character changelog sentence was 977 characters raw. v1 cut lines at 300 and `root_mean_squared_error` started at character 462.
- **TanStack**: the deprecated methods and their replacements sit in a before/after code block under the sentence. v1 keeps lines that announce a change, and a line of code never does, so the block was dropped.
- **Express**: the whole sentence, "use `/*splat` instead of `/*`", reached the model, and it wrote `app.get('/*')`.

C2 (`--filter v2`) adds one rule for each: strip links before cutting a line, keep the code block that follows a matched line, and inject each named replacement as code. Express then wrote `app.get('/*splat')` and scikit-learn called `root_mean_squared_error`, both in all three runs. TanStack still wrote `fetchQuery({...})` with the before/after in its prompt; the task asks to "imperatively fetch the query", and the model followed the task. ESLint fails on a removed option the changelog never discusses. C2 cost no Bright Data credits because every changelog was already cached.

Useful flags: `--agents A`, `--tasks js-uuid,py-pandas-append`, `--runs 1`, `--eval-only` (re-score saved code without model calls), `python3.11 -m exp.report` (rebuild the report only). Finished runs are skipped, so an interrupted run resumes.

Only the standard library is needed to drive the experiment. The libraries under test live in `sandbox/`.

## Files

- `tasks.json` holds 20 prompts (12 PyPI, 8 npm). Each lists the deprecated API, its replacement, the official changelog or migration guide URL and a quote from it, regexes for static matching, and the error strings a removed version produces.
- `exp/agents.py` runs both agents and the tool loop. B gets at most 8 tool calls, and results are paged to the model 12k characters at a time.
- `exp/brightdata.py` is the MCP client. It caches every successful fetch on disk under `cache/bd/`, counts live requests in `cache/bd_usage.json`, and raises once 2,000 requests are used.
- `exp/evaluate.py` does static matching, static symbol resolution, a normal run and a strict run (`-W error::DeprecationWarning` or `node --throw-deprecation`). Generated code runs under macOS `sandbox-exec` with outbound network blocked except loopback.
- `exp/agent_c.py` is the changelog-first agent: one fetch, one filter, one model call.
- `runs/<task>/<agent>/run<k>/` holds the transcript, final reply, extracted code, agent stats, evaluation, stdout/stderr and the strict-run stderr.
- `results.csv` has one row per run, for agents A, B, C and C2. `summary.md` holds the A vs B tables, every task, and where B did not help.

## Bright Data tool names

The brief named `web_data_npm_package`, `web_data_pypi_package` and a GitHub file tool. The MCP README (checked 2026-10-12) no longer has them. `groups=code,research` are legacy IDs that turn on the `scrapers` group, and package and repository data come from `run_scraper` with these dataset IDs:

| data | dataset_id |
|---|---|
| npm package (input `package_name`) | `gd_mk57m0301khq4jmsul` |
| PyPI package (input `package_name`) | `gd_mk57kc3t1wwgmnepp9` |
| GitHub repository file (input `url`) | `gd_lyrexgxc24b3d4imjt` |

`scrape_as_markdown` stays on. The hosted server left `discover` out for `groups=code,research`, so the URL also passes `tools=discover`.

`discover` is gone. During the experiment it was listed when requested by name and every call returned HTTP 404. On a re-test (2026-10-23) it is absent from `tools/list` in every configuration, including unrestricted, and calling it returns `-32601 Unknown tool: discover`, while the tools reference still lists it. Use `search_engine`, which is in the default set and works.

`run_scraper` is asynchronous. It can answer `{"snapshot_id": ..., "status": "running"}`, and the GitHub-file dataset regularly takes over a minute. Poll until the status changes and never cache a pending answer: the first harness cached the `running` placeholder forever, so a changelog fetch silently returned nothing and the run scored as a pass.

Free-tier billing, as the Bright Data dashboard shows it: 5,000 shared credits a month, 1 credit per Web Unlocker or SERP request and 1 credit per scraper record. The harness counts `run_scraper` as one credit per input and stops at 2,000. The full experiment used 60.

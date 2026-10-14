## What the numbers say

Live package data did not reduce deprecated API use here. B used a deprecated or removed ground-truth API in 15 of 60 runs, A in 9 of 60. Hallucinations went the other way: A made up one API (3 runs), B none. Net, B fixed one task and broke two.

- **B better on 1 task.** `py-matplotlib-cmap`: A wrote `import matplotlib.colormaps as cmaps` in all 3 runs, which fails because `colormaps` is an attribute, not a module. B read the `matplotlib.cm` API page and used `matplotlib.colormaps['viridis']`.
- **B worse on 2 tasks.** `py-sklearn-rmse`: the PyPI scraper returned an empty record for scikit-learn, the PyPI page scrape was mostly navigation, and B then wrote `mean_squared_error(..., squared=False)`, which scikit-learn removed in 1.6 and A had avoided. `js-nanoid`: B fetched the npm record (version 6.0.2) and the GitHub README, neither of which mentions an async API, and still imported `nanoid/async`. A resisted the prompt's "prefer async" hint all 3 times. At temperature 0, extra context changed what the model wrote, and in these two cases for the worse.
- **No change on 4 tasks where A was already wrong.** Express 5 wildcard routes, zod 4's `z.email()` and `z.treeifyError()`, TanStack's new `queryClient.query`, and ESLint's removed `useEslintrc`. B fetched each package's npm record and README, and none of those pages contain the replacement API (`/*splat`, `treeifyError`, `queryClient.query`), so there was nothing to correct the model's habit.
- **Both clean on 13 tasks.** `gemini-3.1-flash-lite` already knows pydantic v2, pandas 2+, NumPy 2, SQLAlchemy 2, Pillow 10, SciPy 1.14, FastAPI lifespan, Polars `group_by`, httpx transports, uuid named exports, React 18 streaming and lru-cache 7+. Tools added cost without a benefit there.

Why grounding missed:

1. **B looked up versions, not migrations.** The system prompt asked for the changelog or migration guide. B called the GitHub file scraper 3 times in 60 runs and mostly read READMEs, which show current usage but rarely say what changed.
2. **The PyPI scraper returned no version in 10 of 10 fetches,** and no README in 5 of them. The npm scraper returned version and README in 12 of 12. Python grounding was much thinner than npm grounding.
3. **`discover` failed every time.** All 15 calls got HTTP 404 from Bright Data, so B had no search tool to find a changelog it didn't already know the URL of.

Cost: B used 41x the prompt tokens (about 9,000 vs 216 per run), 3.3x the LLM cost ($0.0026 vs $0.0008 per run) and 4.7x the mean latency (12.1 s vs 2.6 s). Bright Data usage was 60 credits for the whole experiment, thanks to the cache: 58% of B's tool calls were served from it.

What I'd try next: point B at changelogs directly (a `github_file` call per package for CHANGELOG.md or the migration guide, or a fixed changelog URL per task), drop `discover` until it works, and rerun with a model whose training data predates more of these changes, since this one already knew 13 of the 20.

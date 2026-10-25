# Does live package data reduce deprecated and hallucinated API use?

Model: `google/gemini-3.1-flash-lite` at temperature 0, same system prompt for both agents. 20 tasks, up to 3 runs per task per agent. Bright Data requests used (all time, from cache/bd_usage.json): 69 of a 2000 cap.

## A vs B, all tasks

| metric | A (no tools) | B (Bright Data) | B minus A |
|---|---:|---:|---:|
| runs evaluated | 60 | 60 | 0 |
| deprecated calls per run (static match) | 0.25 | 0.40 | 0.15 |
| deprecation warnings + removed-API errors per run (runtime) | 0.05 | 0.15 | 0.10 |
| ground-truth items hit per run | 0.20 | 0.30 | 0.10 |
| % runs using any deprecated/removed API | 15.0 | 25.0 | 10.0 |
| % runs failing under -W error / --throw-deprecation because of a deprecation | 0.0 | 0.0 | 0.0 |
| hallucinated APIs per run | 0.05 | 0.00 | -0.05 |
| % runs with at least one hallucinated API | 5.0 | 0.0 | -5.0 |
| % runs where the code runs (exit 0) | 85.0 | 80.0 | -5.0 |
| % runs passing the strict run | 85.0 | 80.0 | -5.0 |
| prompt tokens per run | 216 | 8989 | 8773 |
| completion tokens per run | 499 | 557 | 58 |
| tool calls per run | 0.00 | 2.48 | 2.48 |
| Bright Data requests per run (live, uncached) | 0.00 | 0.95 | 0.95 |
| Bright Data requests total | 0 | 57 | 57 |
| cache hits per run | 0.00 | 1.45 | 1.45 |
| latency per run, mean (s) | 2.6 | 12.1 | 9.5 |
| latency per run, median (s) | 2.4 | 7.7 | 5.2 |
| LLM cost per run (USD) | 0.00080 | 0.00264 | 0.00184 |
| LLM cost total (USD) | 0.0481 | 0.1585 | 0.1104 |

How to read it. "Static" counts regex matches of the ground-truth deprecated APIs in the code with comments removed. "Runtime" counts deprecation warnings raised from the script (or matching a ground-truth API) in a normal run, plus a crash caused by a ground-truth API that the installed version has removed. Hallucinated APIs are imports, exports and attribute chains that do not exist in the installed version, found by resolving them statically and by ImportError / AttributeError at runtime (in Node: missing export or subpath, `x is not a function`). A removed ground-truth API is counted as deprecated, not hallucinated.

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

### pypi only

| metric | A (no tools) | B (Bright Data) | B minus A |
|---|---:|---:|---:|
| runs evaluated | 36 | 36 | 0 |
| deprecated calls per run (static match) | 0.00 | 0.08 | 0.08 |
| deprecation warnings + removed-API errors per run (runtime) | 0.00 | 0.08 | 0.08 |
| ground-truth items hit per run | 0.00 | 0.08 | 0.08 |
| % runs using any deprecated/removed API | 0.0 | 8.3 | 8.3 |
| % runs failing under -W error / --throw-deprecation because of a deprecation | 0.0 | 0.0 | 0.0 |
| hallucinated APIs per run | 0.08 | 0.00 | -0.08 |
| % runs with at least one hallucinated API | 8.3 | 0.0 | -8.3 |

### npm only

| metric | A (no tools) | B (Bright Data) | B minus A |
|---|---:|---:|---:|
| runs evaluated | 24 | 24 | 0 |
| deprecated calls per run (static match) | 0.62 | 0.88 | 0.25 |
| deprecation warnings + removed-API errors per run (runtime) | 0.12 | 0.25 | 0.12 |
| ground-truth items hit per run | 0.50 | 0.62 | 0.12 |
| % runs using any deprecated/removed API | 37.5 | 50.0 | 12.5 |
| % runs failing under -W error / --throw-deprecation because of a deprecation | 0.0 | 0.0 | 0.0 |
| hallucinated APIs per run | 0.00 | 0.00 | 0.00 |
| % runs with at least one hallucinated API | 0.0 | 0.0 | 0.0 |

## Every task

Counts are over the runs of each agent (deprecated runs = runs that used at least one deprecated or removed ground-truth API). Outcome compares the sum of failures (deprecated use, hallucination, code that does not run) across runs.

| task | package | deprecated runs A | deprecated runs B | hallucinated APIs A | hallucinated APIs B | runs OK A | runs OK B | B tool calls (mean) | outcome |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| py-pydantic-validators | pydantic | 0/3 | 0/3 | 0 | 0 | 3/3 | 3/3 | 4.0 | both clean |
| py-pydantic-serialize | pydantic | 0/3 | 0/3 | 0 | 0 | 3/3 | 3/3 | 3.0 | both clean |
| py-pandas-append | pandas | 0/3 | 0/3 | 0 | 0 | 3/3 | 3/3 | 3.0 | both clean |
| py-numpy-integrate | numpy | 0/3 | 0/3 | 0 | 0 | 3/3 | 3/3 | 4.0 | both clean |
| py-sqlalchemy-orm | sqlalchemy | 0/3 | 0/3 | 0 | 0 | 3/3 | 3/3 | 1.0 | both clean |
| py-pillow-text | pillow | 0/3 | 0/3 | 0 | 0 | 3/3 | 3/3 | 3.0 | both clean |
| py-sklearn-rmse | scikit-learn | 0/3 | 3/3 | 0 | 0 | 3/3 | 0/3 | 4.0 | B worse |
| py-scipy-integrate | scipy | 0/3 | 0/3 | 0 | 0 | 3/3 | 3/3 | 2.0 | both clean |
| py-matplotlib-cmap | matplotlib | 0/3 | 0/3 | 3 | 0 | 0/3 | 3/3 | 2.0 | B better |
| py-fastapi-lifespan | fastapi | 0/3 | 0/3 | 0 | 0 | 3/3 | 3/3 | 1.0 | both clean |
| py-polars-groupby | polars | 0/3 | 0/3 | 0 | 0 | 3/3 | 3/3 | 2.0 | both clean |
| py-httpx-wsgi | httpx | 0/3 | 0/3 | 0 | 0 | 3/3 | 3/3 | 6.0 | both clean |
| js-express-routes | express | 3/3 | 3/3 | 0 | 0 | 0/3 | 0/3 | 1.7 | no difference |
| js-zod-validate | zod | 3/3 | 3/3 | 0 | 0 | 3/3 | 3/3 | 1.0 | no difference |
| js-uuid | uuid | 0/3 | 0/3 | 0 | 0 | 3/3 | 3/3 | 1.0 | both clean |
| js-react-ssr-stream | react-dom | 0/3 | 0/3 | 0 | 0 | 3/3 | 3/3 | 1.0 | both clean |
| js-eslint-api | eslint | 0/3 | 0/3 | 0 | 0 | 0/3 | 0/3 | 3.0 | no difference |
| js-tanstack-query | @tanstack/query-core | 3/3 | 3/3 | 0 | 0 | 3/3 | 3/3 | 3.0 | no difference |
| js-lru-cache | lru-cache | 0/3 | 0/3 | 0 | 0 | 3/3 | 3/3 | 1.0 | both clean |
| js-nanoid | nanoid | 0/3 | 3/3 | 0 | 0 | 3/3 | 0/3 | 3.0 | B worse |

## Where B did not help

Outcomes: B better 1, B worse 2, both clean 13, no difference 4.

- `py-pydantic-validators`: both clean. A already avoided the deprecated APIs, so tools could only add cost.
- `py-pydantic-serialize`: both clean. A already avoided the deprecated APIs, so tools could only add cost.
- `py-pandas-append`: both clean. A already avoided the deprecated APIs, so tools could only add cost.
- `py-numpy-integrate`: both clean. A already avoided the deprecated APIs, so tools could only add cost.
- `py-sqlalchemy-orm`: both clean. A already avoided the deprecated APIs, so tools could only add cost.
- `py-pillow-text`: both clean. A already avoided the deprecated APIs, so tools could only add cost.
- `py-sklearn-rmse`: B worse. B still used mean_squared_error(..., squared=False); B errors: TypeError.
- `py-scipy-integrate`: both clean. A already avoided the deprecated APIs, so tools could only add cost.
- `py-fastapi-lifespan`: both clean. A already avoided the deprecated APIs, so tools could only add cost.
- `py-polars-groupby`: both clean. A already avoided the deprecated APIs, so tools could only add cost.
- `py-httpx-wsgi`: both clean. A already avoided the deprecated APIs, so tools could only add cost.
- `js-express-routes`: no difference. B still used unnamed wildcard route path '*'; B errors: TypeError.
- `js-zod-validate`: no difference. B still used ZodError.flatten(), z.string().email().
- `js-uuid`: both clean. A already avoided the deprecated APIs, so tools could only add cost.
- `js-react-ssr-stream`: both clean. A already avoided the deprecated APIs, so tools could only add cost.
- `js-eslint-api`: no difference. B errors: ESLintInvalidOptionsError.
- `js-tanstack-query`: no difference. B still used queryClient.fetchQuery / prefetchQuery / ensureQueryData.
- `js-lru-cache`: both clean. A already avoided the deprecated APIs, so tools could only add cost.
- `js-nanoid`: B worse. B still used nanoid/async; B errors: ERR_PACKAGE_PATH_NOT_EXPORTED.

## What agent B fetched

Tool calls across all B runs (refused = unknown tool or a dataset outside the three enabled ones):

| tool | calls | served from cache | errors or refused |
|---|---:|---:|---:|
| scrape_as_markdown | 47 | 29 | 0 |
| run_scraper (pypi) | 44 | 34 | 0 |
| run_scraper (npm) | 34 | 22 | 0 |
| discover | 15 | 0 | 15 |
| get_scraper_results | 6 | 0 | 6 |
| run_scraper (github_file) | 3 | 2 | 0 |

What the unique (cached) Bright Data responses contained:

| source | unique fetches | with version | with README / file content | empty record | mean chars |
|---|---:|---:|---:|---:|---:|
| github_file scraper | 2 | 0 | 2 | 0 | |
| npm scraper | 12 | 12 | 12 | 0 | |
| pypi scraper | 10 | 0 | 5 | 5 | |
| scrape_as_markdown | 24 | | | | 36,125 |
| search_engine | 1 | | | | 2,483 |

## Agent C: fetching the changelog in code

Agent B chose what to read and mostly read READMEs. Agent C removes the choice: the harness fetches the library's official changelog or migration guide, keeps only the lines announcing a deprecation, removal or rename, and puts them in the prompt. No tool loop, so the model cannot skip the page that matters. C2 reruns it with filter v2, one rule per way the replacement went missing under v1: strip markdown links before cutting a line (scikit-learn), keep the code block that follows a matched line (TanStack), and inject each named replacement as code (Express). See `exp/agent_c.py`.

Scoped to the 6 tasks agent C ran: `js-eslint-api`, `js-express-routes`, `js-nanoid`, `js-tanstack-query`, `js-zod-validate`, `py-sklearn-rmse`.

| metric | A (no tools) | B (Bright Data) | C (changelog injected) | C2 (filter v2) |
|---|---:|---:|---:|---:|
| runs evaluated | 18 | 18 | 18 | 18 |
| runs using an outdated API | 9 | 15 | 6 | 3 |
| runs where the code ran | 12 | 6 | 12 | 15 |
| hallucinated APIs, total | 0 | 0 | 0 | 0 |
| prompt tokens per run | 235 | 11267 | 1578 | 1782 |
| latency per run, mean (s) | 2.7 | 11.8 | 4.4 | 3.1 |
| Bright Data requests total | 0 | 18 | 0 | 0 |
| LLM cost total (USD) | 0.0162 | 0.0542 | 0.0189 | 0.0204 |

| task | outdated runs A | outdated runs B | outdated runs C | outdated runs C2 | ran A | ran B | ran C | ran C2 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| js-eslint-api | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| js-express-routes | 3/3 | 3/3 | 3/3 | 0/3 | 0/3 | 0/3 | 0/3 | 3/3 |
| js-nanoid | 0/3 | 3/3 | 0/3 | 0/3 | 3/3 | 0/3 | 3/3 | 3/3 |
| js-tanstack-query | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| js-zod-validate | 3/3 | 3/3 | 0/3 | 0/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| py-sklearn-rmse | 0/3 | 3/3 | 0/3 | 0/3 | 3/3 | 0/3 | 3/3 | 3/3 |

Where each changelog came from:

| task | fetched via | change lines kept (chars) | source |
|---|---|---:|---|
| js-eslint-api | `scrape_as_markdown` | 4,233 | https://eslint.org/docs/latest/use/migrate-to-8.0.0 |
| js-express-routes | `scrape_as_markdown` | 6,027 | https://expressjs.com/en/guide/migrating-5.html |
| js-nanoid | `run_scraper/github_file` | 738 | https://github.com/ai/nanoid/blob/main/CHANGELOG.md |
| js-tanstack-query | `scrape_as_markdown` | 6,108 | https://tanstack.com/query/latest/docs/framework/react/guides/migrating-to-v5 |
| js-zod-validate | `scrape_as_markdown` | 6,112 | https://zod.dev/v4/changelog |
| py-sklearn-rmse | `scrape_as_markdown` | 6,227 | https://scikit-learn.org/stable/whats_new/v1.4.html |

## Ground truth sources

| task | deprecated | replacement | source |
|---|---|---|---|
| py-pydantic-validators | `@validator` | `@field_validator` | [deprecated in 2.0](https://docs.pydantic.dev/latest/migration/) |
| py-pydantic-validators | `@root_validator` | `@model_validator` | [deprecated in 2.0](https://docs.pydantic.dev/latest/migration/) |
| py-pydantic-validators | `class Config inside a model` | `model_config = ConfigDict(...)` | [deprecated in 2.0](https://docs.pydantic.dev/latest/migration/) |
| py-pydantic-serialize | `Model.dict()` | `Model.model_dump()` | [deprecated in 2.0](https://docs.pydantic.dev/latest/migration/) |
| py-pydantic-serialize | `Model.json()` | `Model.model_dump_json()` | [deprecated in 2.0](https://docs.pydantic.dev/latest/migration/) |
| py-pydantic-serialize | `Model.parse_obj()` | `Model.model_validate()` | [deprecated in 2.0](https://docs.pydantic.dev/latest/migration/) |
| py-pydantic-serialize | `Model.parse_raw()` | `Model.model_validate_json()` | [deprecated in 2.0](https://docs.pydantic.dev/latest/migration/) |
| py-pydantic-serialize | `Model.copy()` | `Model.model_copy()` | [deprecated in 2.0](https://docs.pydantic.dev/latest/migration/) |
| py-pandas-append | `DataFrame.append` | `pandas.concat` | [removed in 2.0](https://pandas.pydata.org/docs/whatsnew/v2.0.0.html) |
| py-numpy-integrate | `np.trapz` | `np.trapezoid` | [deprecated in 2.0](https://numpy.org/doc/stable/release/2.0.0-notes.html) |
| py-numpy-integrate | `np.float_` | `np.float64` | [removed in 2.0](https://numpy.org/doc/stable/release/2.0.0-notes.html) |
| py-sqlalchemy-orm | `sqlalchemy.ext.declarative.declarative_base` | `sqlalchemy.orm.declarative_base / DeclarativeBase` | [moved in 2.0](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html) |
| py-sqlalchemy-orm | `Query.get()` | `Session.get()` | [legacy in 2.0 (LegacyAPIWarning)](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html) |
| py-sqlalchemy-orm | `Engine.execute()` | `Connection.execute() inside engine.connect()` | [removed in 2.0](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html) |
| py-pillow-text | `Image.ANTIALIAS` | `Image.Resampling.LANCZOS (or Image.LANCZOS)` | [removed in 10.0](https://pillow.readthedocs.io/en/stable/releasenotes/10.0.0.html) |
| py-pillow-text | `ImageDraw.textsize()` | `ImageDraw.textbbox() / ImageDraw.textlength()` | [removed in 10.0](https://pillow.readthedocs.io/en/stable/releasenotes/10.0.0.html) |
| py-pillow-text | `ImageFont.getsize() / FreeTypeFont.getsize()` | `getbbox() / getlength()` | [removed in 10.0](https://pillow.readthedocs.io/en/stable/releasenotes/10.0.0.html) |
| py-sklearn-rmse | `mean_squared_error(..., squared=False)` | `root_mean_squared_error` | [deprecated in 1.4, removed in 1.6](https://scikit-learn.org/stable/whats_new/v1.4.html) |
| py-scipy-integrate | `scipy.integrate.simps` | `scipy.integrate.simpson` | [removed in 1.14](https://docs.scipy.org/doc/scipy/release/1.14.0-notes.html) |
| py-scipy-integrate | `scipy.integrate.trapz` | `scipy.integrate.trapezoid` | [removed in 1.14](https://docs.scipy.org/doc/scipy/release/1.14.0-notes.html) |
| py-scipy-integrate | `scipy.integrate.cumtrapz` | `scipy.integrate.cumulative_trapezoid` | [removed in 1.14](https://docs.scipy.org/doc/scipy/release/1.14.0-notes.html) |
| py-matplotlib-cmap | `matplotlib.cm.get_cmap` | `matplotlib.colormaps[name]` | [removed in 3.9](https://matplotlib.org/stable/api/prev_api_changes/api_changes_3.9.0.html) |
| py-fastapi-lifespan | `@app.on_event('startup' / 'shutdown')` | `lifespan async context manager passed to FastAPI(lifespan=...)` | [deprecated](https://fastapi.tiangolo.com/advanced/events/) |
| py-polars-groupby | `DataFrame.groupby` | `DataFrame.group_by` | [renamed in 0.19 (old name since removed)](https://docs.pola.rs/releases/upgrade/0.19/) |
| py-polars-groupby | `Series/Expr.apply` | `map_elements` | [renamed in 0.19 (old name since removed)](https://docs.pola.rs/releases/upgrade/0.19/) |
| py-httpx-wsgi | `httpx.Client(app=...)` | `httpx.Client(transport=httpx.WSGITransport(app=...))` | [deprecated in 0.27, removed in 0.28](https://github.com/encode/httpx/blob/master/CHANGELOG.md) |
| js-express-routes | `app.del()` | `app.delete()` | [removed in 5.0](https://expressjs.com/en/guide/migrating-5.html) |
| js-express-routes | `req.param(name)` | `req.params / req.query / req.body` | [removed in 5.0](https://expressjs.com/en/guide/migrating-5.html) |
| js-express-routes | `res.send(status) / res.send(body, status)` | `res.sendStatus(status) / res.status(status).send(body)` | [removed in 5.0](https://expressjs.com/en/guide/migrating-5.html) |
| js-express-routes | `unnamed wildcard route path '*'` | `'/*splat' or '/{*splat}'` | [changed in 5.0 (path-to-regexp v8)](https://expressjs.com/en/guide/migrating-5.html) |
| js-zod-validate | `z.string().email()` | `z.email()` | [deprecated in 4.0](https://zod.dev/v4/changelog) |
| js-zod-validate | `ZodError.errors` | `ZodError.issues` | [removed in 4.0](https://zod.dev/v4/changelog) |
| js-zod-validate | `ZodError.flatten()` | `z.treeifyError()` | [deprecated in 4.0](https://zod.dev/v4/changelog) |
| js-zod-validate | `ZodError.format()` | `z.treeifyError()` | [deprecated in 4.0](https://zod.dev/v4/changelog) |
| js-zod-validate | `ZodObject.merge()` | `ZodObject.extend()` | [deprecated in 4.0](https://zod.dev/v4/changelog) |
| js-zod-validate | `{ message: ... } error parameter` | `{ error: ... }` | [deprecated in 4.0](https://zod.dev/v4/changelog) |
| js-uuid | `deep imports such as 'uuid/v4'` | `named exports: import { v4 } from 'uuid'` | [deprecated in 7, removed in 8.0](https://github.com/uuidjs/uuid/blob/main/CHANGELOG.md) |
| js-react-ssr-stream | `ReactDOMServer.renderToNodeStream` | `renderToPipeableStream` | [deprecated in 18.0 (absent from 19.x)](https://react.dev/blog/2022/03/08/react-18-upgrade-guide) |
| js-react-ssr-stream | `ReactDOMServer.renderToStaticNodeStream` | `none named in the changelog entry` | [removed in 19.0](https://github.com/facebook/react/blob/main/CHANGELOG.md) |
| js-eslint-api | `CLIEngine` | `ESLint class` | [removed in 8.0](https://eslint.org/docs/latest/use/migrate-to-8.0.0) |
| js-eslint-api | `FlatESLint / LegacyESLint` | `ESLint` | [removed in 10.0](https://eslint.org/docs/latest/use/migrate-to-10.0.0) |
| js-tanstack-query | `cacheTime option` | `gcTime` | [renamed in 5.0](https://tanstack.com/query/latest/docs/framework/react/guides/migrating-to-v5) |
| js-tanstack-query | `positional overloads fetchQuery(key, fn, options)` | `single object argument` | [removed in 5.0](https://tanstack.com/query/latest/docs/framework/react/guides/migrating-to-v5) |
| js-tanstack-query | `queryClient.fetchQuery / prefetchQuery / ensureQueryData` | `queryClient.query({...})` | [deprecated in 5.x, removal planned for v6](https://tanstack.com/query/latest/docs/framework/react/guides/migrating-to-v5) |
| js-lru-cache | `default export` | `named export { LRUCache }` | [removed in 9.0](https://github.com/isaacs/node-lru-cache/blob/main/CHANGELOG.md) |
| js-lru-cache | `maxAge option` | `ttl` | [deprecated in 7.0](https://github.com/isaacs/node-lru-cache/blob/main/CHANGELOG.md) |
| js-lru-cache | `del() method` | `delete()` | [deprecated in 7.0 (absent from 11.x)](https://github.com/isaacs/node-lru-cache/blob/main/CHANGELOG.md) |
| js-lru-cache | `reset() method` | `clear()` | [deprecated in 7.0 (absent from 11.x)](https://github.com/isaacs/node-lru-cache/blob/main/CHANGELOG.md) |
| js-nanoid | `nanoid/async` | `synchronous nanoid() / customAlphabet()` | [removed in 5.0](https://github.com/ai/nanoid/blob/main/CHANGELOG.md) |

## Versions tested against

Python: fastapi 0.143.0, httpx 0.28.1, matplotlib 3.11.2, numpy 2.4.6, pandas 3.0.6, pillow 12.3.0, polars 2.0.0, pydantic 2.14.1, scikit-learn 1.9.1, scipy 1.17.1, sqlalchemy 2.1.4, (interpreter) 3.11.10

npm: @tanstack/query-core 5.104.2, eslint 10.12.0, express 5.3.0, lru-cache 11.5.3, nanoid 6.0.2, react 19.3.0, react-dom 19.3.0, uuid 14.0.3, zod 4.6.6, (node) v22.16.0

## Caveats

- The Bright Data tool names in the brief (`web_data_npm_package`, `web_data_pypi_package`, the GitHub file tool) no longer exist. The MCP README of 2026-10-12 maps `groups=code,research` to the `scrapers` group, and npm, PyPI and GitHub file data come from `run_scraper` with the npmjs, pypi and GitHub repository dataset IDs (npm and PyPI take `package_name`, GitHub takes a file `url`). Agent B gets `run_scraper` (limited to those three datasets), `scrape_as_markdown` and `discover`. The hosted server left `discover` out for `groups=code,research`, so the URL also passes `tools=discover`.
- One B run (js-zod-validate run 1) was discarded and rerun: the first version of the tool description told the model to pass a URL to the npm scraper, which rejects it. No other run was rerun or dropped.
- Bright Data usage is counted in credits as the free tier bills them: 1 per scrape or search, 1 per scraper record (one per input URL). Polls of a slow scraper run and failed calls are also counted, so the figure is an upper bound.
- Fetches are cached on disk, so runs 2 and 3 of agent B usually cost no Bright Data requests. Live request counts are per run; cache hits are listed separately.
- The checks find deprecated and made-up APIs. They do not check that the output is correct.
- Left out of the ground truth on purpose: ESLint's `useEslintrc` option. The ESLint team blog (eslint.org/blog/2022/08/new-config-system-part-3) says "The useEslintrc option has been removed" from the flat-config class, but no changelog or migration guide names it, so runs that pass it count as code that does not run (ESLintInvalidOptionsError), not as deprecated use.
- NumPy's 2.0 notes call `np.trapz` deprecated; the installed 2.4 has removed it, so using it fails at runtime.
- Static patterns are regexes and can miss unusual spellings; the runtime checks cover the case where the API was removed.
- Generated code ran under macOS `sandbox-exec` with outbound network blocked except loopback, with a 60 s timeout.
- One model, 3 runs per cell. At temperature 0 the runs are often identical, so treat per-task differences as small samples.

## Per-run detail

| task | agent | run | runs | deprecated items hit | hallucinated symbols | error |
|---|---|---:|---|---|---|---|
| js-eslint-api | A | 1 | no | - | - | ESLintInvalidOptionsError: Invalid Options: |
| js-eslint-api | A | 2 | no | - | - | ESLintInvalidOptionsError: Invalid Options: |
| js-eslint-api | A | 3 | no | - | - | ESLintInvalidOptionsError: Invalid Options: |
| js-eslint-api | B | 1 | no | - | - | ESLintInvalidOptionsError: Invalid Options: |
| js-eslint-api | B | 2 | no | - | - | ESLintInvalidOptionsError: Invalid Options: |
| js-eslint-api | B | 3 | no | - | - | ESLintInvalidOptionsError: Invalid Options: |
| js-eslint-api | C | 1 | no | - | - | ESLintInvalidOptionsError: Invalid Options: |
| js-eslint-api | C | 2 | no | - | - | ESLintInvalidOptionsError: Invalid Options: |
| js-eslint-api | C | 3 | no | - | - | ESLintInvalidOptionsError: Invalid Options: |
| js-eslint-api | C2 | 1 | no | - | - | ESLintInvalidOptionsError: Invalid Options: |
| js-eslint-api | C2 | 2 | no | - | - | ESLintInvalidOptionsError: Invalid Options: |
| js-eslint-api | C2 | 3 | no | - | - | ESLintInvalidOptionsError: Invalid Options: |
| js-express-routes | A | 1 | no | unnamed wildcard route path '*' | - | TypeError: Missing parameter name at index 1: *; visit https://git.new/pathToRegexpError for info |
| js-express-routes | A | 2 | no | unnamed wildcard route path '*' | - | TypeError: Missing parameter name at index 1: *; visit https://git.new/pathToRegexpError for info |
| js-express-routes | A | 3 | no | unnamed wildcard route path '*' | - | TypeError: Missing parameter name at index 1: *; visit https://git.new/pathToRegexpError for info |
| js-express-routes | B | 1 | no | unnamed wildcard route path '*' | - | TypeError: Missing parameter name at index 1: *; visit https://git.new/pathToRegexpError for info |
| js-express-routes | B | 2 | no | unnamed wildcard route path '*' | - | TypeError: Missing parameter name at index 1: *; visit https://git.new/pathToRegexpError for info |
| js-express-routes | B | 3 | no | unnamed wildcard route path '*' | - | TypeError: Missing parameter name at index 1: *; visit https://git.new/pathToRegexpError for info |
| js-express-routes | C | 1 | no | unnamed wildcard route path '*' | - | TypeError: Missing parameter name at index 2: /*; visit https://git.new/pathToRegexpError for info |
| js-express-routes | C | 2 | no | unnamed wildcard route path '*' | - | TypeError: Missing parameter name at index 2: /*; visit https://git.new/pathToRegexpError for info |
| js-express-routes | C | 3 | no | unnamed wildcard route path '*' | - | TypeError: Missing parameter name at index 2: /*; visit https://git.new/pathToRegexpError for info |
| js-express-routes | C2 | 1 | yes | - | - |  |
| js-express-routes | C2 | 2 | yes | - | - |  |
| js-express-routes | C2 | 3 | yes | - | - |  |
| js-lru-cache | A | 1 | yes | - | - |  |
| js-lru-cache | A | 2 | yes | - | - |  |
| js-lru-cache | A | 3 | yes | - | - |  |
| js-lru-cache | B | 1 | yes | - | - |  |
| js-lru-cache | B | 2 | yes | - | - |  |
| js-lru-cache | B | 3 | yes | - | - |  |
| js-nanoid | A | 1 | yes | - | - |  |
| js-nanoid | A | 2 | yes | - | - |  |
| js-nanoid | A | 3 | yes | - | - |  |
| js-nanoid | B | 1 | no | nanoid/async | - | ERR_PACKAGE_PATH_NOT_EXPORTED: Package subpath './async' is not defined by "exports" in /Users/Admin/Documents/New projec |
| js-nanoid | B | 2 | no | nanoid/async | - | ERR_PACKAGE_PATH_NOT_EXPORTED: Package subpath './async' is not defined by "exports" in /Users/Admin/Documents/New projec |
| js-nanoid | B | 3 | no | nanoid/async | - | ERR_PACKAGE_PATH_NOT_EXPORTED: Package subpath './async' is not defined by "exports" in /Users/Admin/Documents/New projec |
| js-nanoid | C | 1 | yes | - | - |  |
| js-nanoid | C | 2 | yes | - | - |  |
| js-nanoid | C | 3 | yes | - | - |  |
| js-nanoid | C2 | 1 | yes | - | - |  |
| js-nanoid | C2 | 2 | yes | - | - |  |
| js-nanoid | C2 | 3 | yes | - | - |  |
| js-react-ssr-stream | A | 1 | yes | - | - |  |
| js-react-ssr-stream | A | 2 | yes | - | - |  |
| js-react-ssr-stream | A | 3 | yes | - | - |  |
| js-react-ssr-stream | B | 1 | yes | - | - |  |
| js-react-ssr-stream | B | 2 | yes | - | - |  |
| js-react-ssr-stream | B | 3 | yes | - | - |  |
| js-tanstack-query | A | 1 | yes | queryClient.fetchQuery / prefetchQuery / ensureQueryData | - |  |
| js-tanstack-query | A | 2 | yes | queryClient.fetchQuery / prefetchQuery / ensureQueryData | - |  |
| js-tanstack-query | A | 3 | yes | queryClient.fetchQuery / prefetchQuery / ensureQueryData | - |  |
| js-tanstack-query | B | 1 | yes | queryClient.fetchQuery / prefetchQuery / ensureQueryData | - |  |
| js-tanstack-query | B | 2 | yes | queryClient.fetchQuery / prefetchQuery / ensureQueryData | - |  |
| js-tanstack-query | B | 3 | yes | queryClient.fetchQuery / prefetchQuery / ensureQueryData | - |  |
| js-tanstack-query | C | 1 | yes | queryClient.fetchQuery / prefetchQuery / ensureQueryData | - |  |
| js-tanstack-query | C | 2 | yes | queryClient.fetchQuery / prefetchQuery / ensureQueryData | - |  |
| js-tanstack-query | C | 3 | yes | queryClient.fetchQuery / prefetchQuery / ensureQueryData | - |  |
| js-tanstack-query | C2 | 1 | yes | queryClient.fetchQuery / prefetchQuery / ensureQueryData | - |  |
| js-tanstack-query | C2 | 2 | yes | queryClient.fetchQuery / prefetchQuery / ensureQueryData | - |  |
| js-tanstack-query | C2 | 3 | yes | queryClient.fetchQuery / prefetchQuery / ensureQueryData | - |  |
| js-uuid | A | 1 | yes | - | - |  |
| js-uuid | A | 2 | yes | - | - |  |
| js-uuid | A | 3 | yes | - | - |  |
| js-uuid | B | 1 | yes | - | - |  |
| js-uuid | B | 2 | yes | - | - |  |
| js-uuid | B | 3 | yes | - | - |  |
| js-zod-validate | A | 1 | yes | ZodError.flatten(); z.string().email() | - |  |
| js-zod-validate | A | 2 | yes | ZodError.flatten(); z.string().email() | - |  |
| js-zod-validate | A | 3 | yes | ZodError.flatten(); z.string().email() | - |  |
| js-zod-validate | B | 1 | yes | ZodError.flatten(); z.string().email() | - |  |
| js-zod-validate | B | 2 | yes | ZodError.flatten(); z.string().email() | - |  |
| js-zod-validate | B | 3 | yes | ZodError.flatten(); z.string().email() | - |  |
| js-zod-validate | C | 1 | yes | - | - |  |
| js-zod-validate | C | 2 | yes | - | - |  |
| js-zod-validate | C | 3 | yes | - | - |  |
| js-zod-validate | C2 | 1 | yes | - | - |  |
| js-zod-validate | C2 | 2 | yes | - | - |  |
| js-zod-validate | C2 | 3 | yes | - | - |  |
| py-fastapi-lifespan | A | 1 | yes | - | - |  |
| py-fastapi-lifespan | A | 2 | yes | - | - |  |
| py-fastapi-lifespan | A | 3 | yes | - | - |  |
| py-fastapi-lifespan | B | 1 | yes | - | - |  |
| py-fastapi-lifespan | B | 2 | yes | - | - |  |
| py-fastapi-lifespan | B | 3 | yes | - | - |  |
| py-httpx-wsgi | A | 1 | yes | - | - |  |
| py-httpx-wsgi | A | 2 | yes | - | - |  |
| py-httpx-wsgi | A | 3 | yes | - | - |  |
| py-httpx-wsgi | B | 1 | yes | - | - |  |
| py-httpx-wsgi | B | 2 | yes | - | - |  |
| py-httpx-wsgi | B | 3 | yes | - | - |  |
| py-matplotlib-cmap | A | 1 | no | - | matplotlib.colormaps | ModuleNotFoundError: No module named 'matplotlib.colormaps' |
| py-matplotlib-cmap | A | 2 | no | - | matplotlib.colormaps | ModuleNotFoundError: No module named 'matplotlib.colormaps' |
| py-matplotlib-cmap | A | 3 | no | - | matplotlib.colormaps | ModuleNotFoundError: No module named 'matplotlib.colormaps' |
| py-matplotlib-cmap | B | 1 | yes | - | - |  |
| py-matplotlib-cmap | B | 2 | yes | - | - |  |
| py-matplotlib-cmap | B | 3 | yes | - | - |  |
| py-numpy-integrate | A | 1 | yes | - | - |  |
| py-numpy-integrate | A | 2 | yes | - | - |  |
| py-numpy-integrate | A | 3 | yes | - | - |  |
| py-numpy-integrate | B | 1 | yes | - | - |  |
| py-numpy-integrate | B | 2 | yes | - | - |  |
| py-numpy-integrate | B | 3 | yes | - | - |  |
| py-pandas-append | A | 1 | yes | - | - |  |
| py-pandas-append | A | 2 | yes | - | - |  |
| py-pandas-append | A | 3 | yes | - | - |  |
| py-pandas-append | B | 1 | yes | - | - |  |
| py-pandas-append | B | 2 | yes | - | - |  |
| py-pandas-append | B | 3 | yes | - | - |  |
| py-pillow-text | A | 1 | yes | - | - |  |
| py-pillow-text | A | 2 | yes | - | - |  |
| py-pillow-text | A | 3 | yes | - | - |  |
| py-pillow-text | B | 1 | yes | - | - |  |
| py-pillow-text | B | 2 | yes | - | - |  |
| py-pillow-text | B | 3 | yes | - | - |  |
| py-polars-groupby | A | 1 | yes | - | - |  |
| py-polars-groupby | A | 2 | yes | - | - |  |
| py-polars-groupby | A | 3 | yes | - | - |  |
| py-polars-groupby | B | 1 | yes | - | - |  |
| py-polars-groupby | B | 2 | yes | - | - |  |
| py-polars-groupby | B | 3 | yes | - | - |  |
| py-pydantic-serialize | A | 1 | yes | - | - |  |
| py-pydantic-serialize | A | 2 | yes | - | - |  |
| py-pydantic-serialize | A | 3 | yes | - | - |  |
| py-pydantic-serialize | B | 1 | yes | - | - |  |
| py-pydantic-serialize | B | 2 | yes | - | - |  |
| py-pydantic-serialize | B | 3 | yes | - | - |  |
| py-pydantic-validators | A | 1 | yes | - | - |  |
| py-pydantic-validators | A | 2 | yes | - | - |  |
| py-pydantic-validators | A | 3 | yes | - | - |  |
| py-pydantic-validators | B | 1 | yes | - | - |  |
| py-pydantic-validators | B | 2 | yes | - | - |  |
| py-pydantic-validators | B | 3 | yes | - | - |  |
| py-scipy-integrate | A | 1 | yes | - | - |  |
| py-scipy-integrate | A | 2 | yes | - | - |  |
| py-scipy-integrate | A | 3 | yes | - | - |  |
| py-scipy-integrate | B | 1 | yes | - | - |  |
| py-scipy-integrate | B | 2 | yes | - | - |  |
| py-scipy-integrate | B | 3 | yes | - | - |  |
| py-sklearn-rmse | A | 1 | yes | - | - |  |
| py-sklearn-rmse | A | 2 | yes | - | - |  |
| py-sklearn-rmse | A | 3 | yes | - | - |  |
| py-sklearn-rmse | B | 1 | no | mean_squared_error(..., squared=False) | - | TypeError: got an unexpected keyword argument 'squared' |
| py-sklearn-rmse | B | 2 | no | mean_squared_error(..., squared=False) | - | TypeError: got an unexpected keyword argument 'squared' |
| py-sklearn-rmse | B | 3 | no | mean_squared_error(..., squared=False) | - | TypeError: got an unexpected keyword argument 'squared' |
| py-sklearn-rmse | C | 1 | yes | - | - |  |
| py-sklearn-rmse | C | 2 | yes | - | - |  |
| py-sklearn-rmse | C | 3 | yes | - | - |  |
| py-sklearn-rmse | C2 | 1 | yes | - | - |  |
| py-sklearn-rmse | C2 | 2 | yes | - | - |  |
| py-sklearn-rmse | C2 | 3 | yes | - | - |  |
| py-sqlalchemy-orm | A | 1 | yes | - | - |  |
| py-sqlalchemy-orm | A | 2 | yes | - | - |  |
| py-sqlalchemy-orm | A | 3 | yes | - | - |  |
| py-sqlalchemy-orm | B | 1 | yes | - | - |  |
| py-sqlalchemy-orm | B | 2 | yes | - | - |  |
| py-sqlalchemy-orm | B | 3 | yes | - | - |  |

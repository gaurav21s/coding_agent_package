"""Run a generated script inside the sandbox venv and record every warning and the final exception.

Usage: python -I pyharness.py <script.py> <out.json>
"""
import json
import runpy
import sys
import traceback
import warnings

script, out_path = sys.argv[1], sys.argv[2]
records = []


def _hook(message, category, filename, lineno, file=None, line=None):
    records.append({"category": category.__name__,
                    "deprecation": issubclass(category, (DeprecationWarning, PendingDeprecationWarning, FutureWarning)),
                    "message": str(message)[:500], "filename": filename, "lineno": lineno,
                    "in_script": filename == script})


warnings.simplefilter("always")
warnings.showwarning = _hook
result = {"exit": "ok", "exception": None, "warnings": records}
sys.argv = [script]
try:
    runpy.run_path(script, run_name="__main__")
except SystemExit as e:
    if e.code not in (0, None):
        result["exit"] = "error"
        result["exception"] = {"type": "SystemExit", "message": str(e.code), "traceback": ""}
except BaseException as e:  # noqa: BLE001 - we want every failure recorded
    result["exit"] = "error"
    result["exception"] = {"type": type(e).__name__,
                           "mro": [c.__name__ for c in type(e).__mro__],
                           "name": getattr(e, "name", None),
                           "message": str(e)[:1000],
                           "traceback": "".join(traceback.format_exception(e))[-3000:]}
finally:
    sys.stdout.flush()
    with open(out_path, "w") as f:
        json.dump(result, f)

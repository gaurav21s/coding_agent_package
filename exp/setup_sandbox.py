"""Build clean sandboxes with the latest release of every library in tasks.json.

    python3.11 -m exp.setup_sandbox            # create if missing
    python3.11 -m exp.setup_sandbox --fresh    # delete and rebuild

Writes sandbox/versions.json so the report can say exactly what was tested against.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess

from . import config

EXTRA_PY = ["httpx"]                 # FastAPI's TestClient needs it
EXTRA_NPM = ["react"]                # react-dom needs its peer


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fresh", action="store_true")
    args = ap.parse_args()
    tasks = json.loads(config.TASKS_FILE.read_text())["tasks"]
    py_pkgs = sorted({t["package"] for t in tasks if t["ecosystem"] == "pypi"} | set(EXTRA_PY))
    npm_pkgs = sorted({t["package"] for t in tasks if t["ecosystem"] == "npm"} | set(EXTRA_NPM))

    if args.fresh:
        shutil.rmtree(config.PY_SANDBOX, ignore_errors=True)
        shutil.rmtree(config.NODE_SANDBOX, ignore_errors=True)

    env = {**os.environ, "UV_HTTP_TIMEOUT": "300"}
    if not config.SANDBOX_PYTHON.exists():
        subprocess.run(["uv", "venv", "-q", "-p", "python3.11", str(config.PY_SANDBOX)], check=True)
    subprocess.run(["uv", "pip", "install", "-q", "--upgrade", "-p", str(config.SANDBOX_PYTHON), *py_pkgs],
                   check=True, env=env)

    config.NODE_SANDBOX.mkdir(parents=True, exist_ok=True)
    pkg_json = config.NODE_SANDBOX / "package.json"
    if not pkg_json.exists():
        pkg_json.write_text(json.dumps({"name": "sandbox", "private": True, "type": "module"}))
    subprocess.run(["npm", "install", "--silent", *[f"{p}@latest" for p in npm_pkgs]],
                   cwd=config.NODE_SANDBOX, check=True)

    versions = {"python": {}, "npm": {}}
    out = subprocess.run([str(config.SANDBOX_PYTHON), "-c",
                          "import importlib.metadata as m, json, sys; "
                          f"print(json.dumps({{p: m.version(p) for p in {py_pkgs!r}}}))"],
                         capture_output=True, text=True, check=True)
    versions["python"] = json.loads(out.stdout)
    versions["python"]["(interpreter)"] = subprocess.run([str(config.SANDBOX_PYTHON), "--version"],
                                                         capture_output=True, text=True).stdout.split()[-1]
    for p in npm_pkgs:
        versions["npm"][p] = json.loads((config.NODE_SANDBOX / "node_modules" / p / "package.json").read_text())["version"]
    versions["npm"]["(node)"] = subprocess.run(["node", "--version"], capture_output=True, text=True).stdout.strip()
    (config.SANDBOX_DIR / "versions.json").write_text(json.dumps(versions, indent=2))
    print(json.dumps(versions, indent=2))


if __name__ == "__main__":
    main()

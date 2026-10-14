"""Statically check that every imported name and module-rooted attribute chain exists.

Imports libraries but never executes the generated script.
Usage: python -I pyresolve.py <script.py>   ->   JSON list of unresolved symbols on stdout
"""
import ast
import importlib
import json
import sys

src = open(sys.argv[1]).read()
tree = ast.parse(src)
aliases = {}        # local name -> dotted path of a module or object
unresolved = []
checked = set()


def resolve(dotted):
    parts = dotted.split(".")
    obj = None
    for i in range(len(parts), 0, -1):          # longest importable module prefix
        try:
            obj = importlib.import_module(".".join(parts[:i]))
            rest = parts[i:]
            break
        except Exception:
            continue
    if obj is None:
        return False, parts[0]
    for attr in rest:
        if not hasattr(obj, attr):
            try:                                 # lazily loaded submodule
                obj = importlib.import_module(f"{obj.__name__}.{attr}")
                continue
            except Exception:
                return False, attr
        obj = getattr(obj, attr)
    return True, None


def check(dotted, kind, lineno):
    if dotted in checked:
        return
    checked.add(dotted)
    ok, missing = resolve(dotted)
    if not ok:
        unresolved.append({"symbol": dotted, "missing": missing, "kind": kind, "line": lineno})


for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        for a in node.names:
            check(a.name, "import", node.lineno)
            aliases[a.asname or a.name.split(".")[0]] = a.name if a.asname else a.name.split(".")[0]
    elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
        for a in node.names:
            if a.name == "*":
                continue
            check(f"{node.module}.{a.name}", "from-import", node.lineno)
            aliases[a.asname or a.name] = f"{node.module}.{a.name}"

# Names rebound later in the script are not reliable roots.
assigned = {t.id for n in ast.walk(tree) if isinstance(n, (ast.Assign, ast.AnnAssign, ast.AugAssign))
            for t in ([n.target] if not isinstance(n, ast.Assign) else n.targets) if isinstance(t, ast.Name)}
assigned |= {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef))}

for node in ast.walk(tree):
    if isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Load):
        chain, cur = [], node
        while isinstance(cur, ast.Attribute):
            chain.append(cur.attr)
            cur = cur.value
        if isinstance(cur, ast.Name) and cur.id in aliases and cur.id not in assigned:
            root = aliases[cur.id]
            try:
                importlib.import_module(root)
                is_module = True
            except Exception:
                is_module = False
            if not is_module and "." in root:   # from-imported class or function: check attrs on it too
                is_module = True
            if is_module:
                check(".".join([root] + chain[::-1]), "attribute", node.lineno)

# Drop chains whose prefix is already reported, keep the shortest failing one.
syms = sorted(unresolved, key=lambda u: len(u["symbol"]))
kept = []
for u in syms:
    if not any(u["symbol"].startswith(k["symbol"] + ".") for k in kept):
        kept.append(u)
print(json.dumps(kept))

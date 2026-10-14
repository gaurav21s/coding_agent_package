// Statically check that every imported module, named export and member chain on an
// imported binding exists. Loads the libraries but never runs the generated script.
// Must sit next to the script inside sandbox/node so bare specifiers resolve there.
// Usage: node jsresolve.mjs <code file> <comment-free source file>  ->  JSON on stdout
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';

const [codeFile, srcFile] = process.argv.slice(2);
const src = readFileSync(srcFile, 'utf8');
const require = createRequire(codeFile);
const bindings = {};          // local identifier -> { spec, name }   name: 'default' | '*' | export name
const specs = new Map();      // spec -> 'esm' | 'cjs'
const unresolved = [];

const addNamed = (list, spec, sep) => {
  for (const part of list.split(',')) {
    const p = part.trim();
    if (!p || p.startsWith('type ')) continue;
    const [orig, local] = p.split(sep).map((s) => s.trim());
    bindings[local || orig] = { spec, name: orig };
  }
};

for (const m of src.matchAll(/import\s+([\w$\s{},*]+?)\s+from\s+['"]([^'"]+)['"]/g)) {
  const [, clause, spec] = m;
  specs.set(spec, 'esm');
  const ns = clause.match(/\*\s+as\s+([\w$]+)/);
  if (ns) bindings[ns[1]] = { spec, name: '*' };
  const named = clause.match(/\{([^}]*)\}/);
  if (named) addNamed(named[1], spec, /\s+as\s+/);
  const def = clause.replace(/\{[^}]*\}/, '').replace(/\*\s+as\s+[\w$]+/, '').replace(/,/g, ' ').trim();
  if (def) bindings[def] = { spec, name: 'default' };
}
for (const m of src.matchAll(/import\s+['"]([^'"]+)['"]/g)) specs.set(m[1], 'esm');
for (const m of src.matchAll(/(?:const|let|var)\s+\{([^}]*)\}\s*=\s*(?:await\s+)?(require|import)\(\s*['"]([^'"]+)['"]\s*\)/g)) {
  specs.set(m[3], m[2] === 'require' ? 'cjs' : 'esm');
  addNamed(m[1], m[3], ':');
}
for (const m of src.matchAll(/(?:const|let|var)\s+([\w$]+)\s*=\s*(?:await\s+)?(require|import)\(\s*['"]([^'"]+)['"]\s*\)/g)) {
  specs.set(m[3], m[2] === 'require' ? 'cjs' : 'esm');
  bindings[m[1]] = { spec: m[3], name: m[2] === 'require' ? '*' : '*' };
}
for (const m of src.matchAll(/(?:require|import)\(\s*['"]([^'"]+)['"]\s*\)/g)) if (!specs.has(m[1])) specs.set(m[1], 'esm');

const modules = {};
for (const [spec, kind] of specs) {
  try {
    modules[spec] = kind === 'cjs' ? { default: require(spec), ...require(spec) } : await import(spec);
  } catch (e) {
    unresolved.push({ symbol: spec, missing: spec, kind: 'module', error: `${e.code || e.name}: ${String(e.message).slice(0, 200)}` });
  }
}

const values = {};
for (const [local, { spec, name }] of Object.entries(bindings)) {
  const mod = modules[spec];
  if (!mod) continue;
  if (name === '*') { values[local] = mod; continue; }
  if (!(name in mod) || (name !== 'default' && mod[name] === undefined && !(mod.default && name in Object(mod.default)))) {
    unresolved.push({ symbol: `${spec}:${name}`, missing: name, kind: 'named-import' });
    continue;
  }
  values[local] = mod[name] ?? mod.default?.[name];
}

const seen = new Set();
for (const local of Object.keys(values)) {
  const re = new RegExp(`(?<![\\w$.])${local.replace(/\$/g, '\\$')}((?:\\??\\.[A-Za-z_$][\\w$]*)+)`, 'g');
  for (const m of src.matchAll(re)) {
    const chain = m[1].replace(/\?/g, '').split('.').filter(Boolean);
    let cur = values[local];
    const path = [local];
    for (const prop of chain) {
      path.push(prop);
      const key = path.join('.');
      if (cur === null || cur === undefined || (typeof cur !== 'object' && typeof cur !== 'function')) break;
      if (!(prop in Object(cur))) {
        if (!seen.has(key)) { seen.add(key); unresolved.push({ symbol: key, missing: prop, kind: 'member' }); }
        break;
      }
      cur = cur[prop];
    }
  }
}
console.log(JSON.stringify(unresolved));
process.exit(0);

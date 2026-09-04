#!/usr/bin/env node
// Every plugin's version must agree across its manifests and the marketplace.
// weed-harness: .claude-plugin/plugin.json, .codex-plugin/plugin.json, marketplace root + entry.
// each plugins/<name>: .claude-plugin/plugin.json, .codex-plugin/plugin.json, marketplace entry.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const read = (p) => JSON.parse(fs.readFileSync(path.join(root, p), "utf8"));

const seen = {}; // plugin -> [{file, version}]
const add = (plugin, file, version) => (seen[plugin] ||= []).push({ file, version });

add("weed-harness", ".claude-plugin/plugin.json", read(".claude-plugin/plugin.json").version);
add("weed-harness", ".codex-plugin/plugin.json", read(".codex-plugin/plugin.json").version);
const market = read(".claude-plugin/marketplace.json");
add("weed-harness", ".claude-plugin/marketplace.json (root)", market.version);
for (const entry of market.plugins) add(entry.name, ".claude-plugin/marketplace.json (plugins)", entry.version);

for (const name of fs.readdirSync(path.join(root, "plugins"))) {
  for (const manifest of [".claude-plugin/plugin.json", ".codex-plugin/plugin.json"]) {
    const file = path.join("plugins", name, manifest);
    if (fs.existsSync(path.join(root, file))) add(name, file, read(file).version);
  }
}

let bad = 0;
for (const [plugin, rows] of Object.entries(seen)) {
  const versions = new Set(rows.map((r) => r.version));
  if (versions.size === 1) {
    console.log(`  ✓ ${plugin} ${rows[0].version} (${rows.length} files)`);
    continue;
  }
  bad++;
  console.error(`  ✗ ${plugin} disagrees:`);
  for (const r of rows) console.error(`      ${r.version}  ${r.file}`);
}
process.exit(bad ? 1 : 0);

#!/usr/bin/env node
// Word-count caps for the skills a matt-auto run reads (harness-diet-b, goal 5 / D9).
// `wc -w` semantics: whitespace-separated tokens. Exit 1 when any cap is exceeded.
// The spec asked for 3,500 / 3,500 / 8,500; D6 (delete only rules that lost their basis)
// stopped the diet at the values below. Lower a cap when a future diet earns it, never raise one.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const CAPS = {
  "skills/model-routing/SKILL.md": 700,
  "skills/loop-gates/SKILL.md": 700,
  "plugins/matt-loop/skills/matt-auto/SKILL.md": 3800,
  "plugins/auto-loop/skills/autocode/SKILL.md": 4200,
};
const CHAIN = [
  "plugins/matt-loop/skills/matt-auto/SKILL.md",
  "plugins/matt-loop/skills/interview-report/SKILL.md",
  "skills/loop-report/SKILL.md",
  "skills/model-routing/SKILL.md",
  "skills/loop-gates/SKILL.md",
];
const CHAIN_CAP = 8700;

const words = (file) => fs.readFileSync(path.join(root, file), "utf8").split(/\s+/).filter(Boolean).length;

let bad = 0;
for (const [file, cap] of Object.entries(CAPS)) {
  const n = words(file);
  const ok = n <= cap;
  if (!ok) bad++;
  console.log(`  ${ok ? "✓" : "✗"} ${file} ${n} words (cap ${cap})`);
}
const chain = CHAIN.reduce((sum, f) => sum + words(f), 0);
const chainOk = chain <= CHAIN_CAP;
if (!chainOk) bad++;
console.log(`  ${chainOk ? "✓" : "✗"} matt-auto chain ${chain} words (cap ${CHAIN_CAP})`);
process.exit(bad ? 1 : 0);

#!/usr/bin/env node
// weed-plugins installer
// Copies skill packs from this repo into the skill directories of supported
// AI coding CLIs. Zero dependencies; Node >= 18.
//
//   npx github:weedmo/skills                 # interactive
//   npx github:weedmo/skills --yes           # everything, everywhere
//   npx github:weedmo/skills --platforms claude-code,codex --plugins super-loop
//
// weed-harness is always installed (required). Other plugins are opt-in.

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import process from "node:process";
import readline from "node:readline/promises";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

const PLATFORMS = {
  "claude-code": {
    dir: (home) => path.join(home, ".claude", "skills"),
    note: "native SKILL.md discovery. If you already installed these as Claude plugins (/plugin install), skip this platform to avoid duplicate skills.",
  },
  codex: {
    dir: (home) => path.join(home, ".codex", "skills"),
    note: "native SKILL.md discovery; restart Codex to pick up new skills.",
  },
  opencode: {
    dir: (home) => path.join(home, ".config", "opencode", "skill"),
    note: "native SKILL.md discovery (skill/ directory).",
  },
  "gemini-cli": {
    dir: (home) => path.join(home, ".gemini", "skills"),
    note: "no native skill discovery - reference the skill files from ~/.gemini/GEMINI.md yourself.",
  },
};

const PLUGINS = {
  "weed-harness": {
    required: true,
    src: path.join(ROOT, "skills"),
    desc: "core harness infra (setup, harness-sync, skill-subscribe, find-skills, workflow-plan)",
  },
  "matt-loop": {
    src: path.join(ROOT, "plugins", "matt-loop", "skills"),
    desc: "matt-auto + vendored Matt Pocock skills (human-in-the-loop conducted Matt flow)",
  },
  "auto-loop": {
    src: path.join(ROOT, "plugins", "auto-loop", "skills"),
    desc: "autocode + auto_research (autonomous improvement loops)",
  },
  "super-loop": {
    src: path.join(ROOT, "plugins", "super-loop", "skills"),
    desc: "superpowers-based gated development loop",
  },
};

// ---------- args ----------

const args = process.argv.slice(2);
const flag = (name) => args.includes(`--${name}`);
const opt = (name) => {
  const i = args.indexOf(`--${name}`);
  return i >= 0 && args[i + 1] && !args[i + 1].startsWith("--") ? args[i + 1] : null;
};

if (flag("help") || flag("h")) {
  console.log(`weed-plugins installer

Usage: npx github:weedmo/skills [options]

Options:
  --platforms <a,b|all>  Platforms to install to: ${Object.keys(PLATFORMS).join(", ")}
  --plugins <a,b|all|none>  Extra plugins besides weed-harness (always installed)
  --yes                  Non-interactive; defaults to all platforms + all plugins
  --dry-run              Show what would be installed without writing
  --home <dir>           Override home directory (mainly for testing)
  --help                 Show this help`);
  process.exit(0);
}

const HOME = opt("home") || os.homedir();
const DRY = flag("dry-run");

// ---------- selection ----------

function parseList(value, valid, label) {
  if (!value || value === "all") return [...valid];
  if (value === "none") return [];
  const picked = value.split(",").map((s) => s.trim()).filter(Boolean);
  for (const p of picked) {
    if (!valid.includes(p)) {
      console.error(`Unknown ${label}: ${p} (valid: ${valid.join(", ")})`);
      process.exit(1);
    }
  }
  return picked;
}

async function promptList(rl, title, items, descs) {
  console.log(`\n${title}`);
  items.forEach((name, i) => console.log(`  ${i + 1}) ${name}${descs[name] ? ` — ${descs[name]}` : ""}`));
  const answer = (await rl.question("Select (comma-separated numbers, empty = all): ")).trim();
  if (!answer) return [...items];
  const picked = [];
  for (const token of answer.split(",")) {
    const n = Number(token.trim());
    if (!Number.isInteger(n) || n < 1 || n > items.length) {
      console.error(`Invalid selection: ${token.trim()}`);
      process.exit(1);
    }
    picked.push(items[n - 1]);
  }
  return [...new Set(picked)];
}

const platformNames = Object.keys(PLATFORMS);
const optionalPlugins = Object.keys(PLUGINS).filter((p) => !PLUGINS[p].required);

let platforms;
let plugins;

if (flag("yes") || opt("platforms") || opt("plugins")) {
  platforms = parseList(opt("platforms"), platformNames, "platform");
  plugins = parseList(opt("plugins"), optionalPlugins, "plugin");
} else {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  platforms = await promptList(rl, "Install to which platforms?", platformNames, {});
  const descs = Object.fromEntries(optionalPlugins.map((p) => [p, PLUGINS[p].desc]));
  console.log("\nweed-harness is required and always installed.");
  plugins = await promptList(rl, "Install which additional plugins?", optionalPlugins, descs);
  rl.close();
}

plugins = ["weed-harness", ...plugins];

// ---------- install ----------

function skillDirs(src) {
  if (!fs.existsSync(src)) return [];
  return fs
    .readdirSync(src, { withFileTypes: true })
    .filter((e) => e.isDirectory() && fs.existsSync(path.join(src, e.name, "SKILL.md")))
    .map((e) => e.name);
}

console.log(`\n${DRY ? "[dry-run] " : ""}Installing ${plugins.join(", ")} → ${platforms.join(", ")}\n`);

let failures = 0;
for (const platform of platforms) {
  const dest = PLATFORMS[platform].dir(HOME);
  console.log(`[${platform}] ${dest}`);
  for (const plugin of plugins) {
    const { src } = PLUGINS[plugin];
    const skills = skillDirs(src);
    if (skills.length === 0) {
      console.log(`  ! ${plugin}: no skills found at ${src}`);
      failures++;
      continue;
    }
    for (const skill of skills) {
      const from = path.join(src, skill);
      const to = path.join(dest, skill);
      try {
        if (!DRY) {
          fs.mkdirSync(dest, { recursive: true });
          fs.rmSync(to, { recursive: true, force: true });
          fs.cpSync(from, to, { recursive: true });
        }
        console.log(`  ✓ ${plugin}/${skill}`);
      } catch (err) {
        console.log(`  ✗ ${plugin}/${skill}: ${err.message}`);
        failures++;
      }
    }
  }
  console.log(`  note: ${PLATFORMS[platform].note}\n`);
}

if (failures > 0) {
  console.error(`Done with ${failures} failure(s).`);
  process.exit(1);
}
console.log("Done. Restart each CLI so new skills are discovered.");

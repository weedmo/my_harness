#!/usr/bin/env node
// weed-plugins installer
// Copies skill packs from this repo into the skill directories of supported
// AI coding CLIs. Zero dependencies; Node >= 18.
//
//   npx github:weedmo/skills                 # interactive
//   npx github:weedmo/skills --yes           # everything, everywhere
//   npx github:weedmo/skills --platforms claude-code,codex --plugins auto-loop
//
// Claude Code setup is always installed when that platform is selected. Loop
// plugins are opt-in and available on every platform.

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
    dir: (home) => path.join(home, ".config", "opencode", "skills"),
    note: "native SKILL.md discovery (skills/ directory).",
  },
  "gemini-cli": {
    dir: (home) => path.join(home, ".gemini", "skills"),
    note: "no native skill discovery - reference the skill files from ~/.gemini/GEMINI.md yourself.",
  },
  orca: {
    dir: (home) => path.join(home, ".agents", "skills"),
    note: "universal agent-skills directory; Orca exposes these skills to every agent it drives. Orca also auto-discovers plugins installed via Claude (/plugin install) and Codex (codex plugin add) - skip this platform if you use those to avoid duplicate skills.",
  },
};

const PLUGINS = {
  "weed-harness": {
    required: true,
    src: path.join(ROOT, "skills"),
    desc: "Claude Code setup (HUD and hooks)",
    platforms: ["claude-code"],
  },
  "matt-loop": {
    src: path.join(ROOT, "plugins", "matt-loop", "skills"),
    desc: "matt-auto + vendored Matt Pocock skills (human-in-the-loop conducted Matt flow)",
  },
  "auto-loop": {
    src: path.join(ROOT, "plugins", "auto-loop", "skills"),
    desc: "autocode + auto_research (autonomous improvement loops)",
  },
};

const OPENCODE_ASSETS = {
  "matt-loop": [
    {
      src: path.join(ROOT, "plugins", "matt-loop", "opencode", "agents"),
      dir: (home) => path.join(home, ".config", "opencode", "agents"),
      desc: "model-routing agents",
    },
  ],
};

const LEGACY_SKILLS = [
  "find-skills",
  "harness-sync",
  "skill-subscribe",
  "super-loop",
  "workflow-plan",
];

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
  --plugins <a,b|all|none>  Optional loop plugins (Claude Code setup is automatic)
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
  console.log("\nClaude Code setup is installed automatically when that platform is selected.");
  plugins = await promptList(rl, "Install which additional plugins?", optionalPlugins, descs);
  rl.close();
}

// ---------- install ----------

function skillDirs(src) {
  if (!fs.existsSync(src)) return [];
  return fs
    .readdirSync(src, { withFileTypes: true })
    .filter((e) => e.isDirectory() && fs.existsSync(path.join(src, e.name, "SKILL.md")))
    .map((e) => e.name);
}

function installedSkillName(platform, skill) {
  if (platform !== "opencode") return skill;
  return skill.replaceAll("_", "-");
}

function normalizeOpenCodeSkill(skillDir, sourceName, installedName) {
  if (sourceName === installedName) return;
  const skillFile = path.join(skillDir, "SKILL.md");
  const content = fs.readFileSync(skillFile, "utf8");
  fs.writeFileSync(
    skillFile,
    content.replace(/^name:\s*.*$/m, `name: ${installedName}`),
  );
}

function installOpenCodeCommands(plugin, home) {
  if (plugin !== "matt-loop") return;
  const commandDir = path.join(home, ".config", "opencode", "command");
  const skills = skillDirs(PLUGINS[plugin].src);
  fs.mkdirSync(commandDir, { recursive: true });
  for (const skill of skills) {
    const command = `---\ndescription: Run the Matt Loop ${skill} workflow.\n---\n\nUse the \`${skill}\` skill to complete this request:\n\n$ARGUMENTS\n`;
    fs.writeFileSync(path.join(commandDir, `${skill}.md`), command);
  }
  console.log(`  ✓ ${plugin}/skill slash commands`);
}

function cleanupLegacyClaudeHook(home) {
  const settingsPath = path.join(home, ".claude", "settings.json");
  if (!fs.existsSync(settingsPath)) return;
  const data = JSON.parse(fs.readFileSync(settingsPath, "utf8"));
  const groups = data.hooks?.SessionStart;
  if (!Array.isArray(groups)) return;
  let changed = false;
  const cleanedGroups = [];
  for (const group of groups) {
    const hooks = Array.isArray(group.hooks) ? group.hooks : [];
    const cleanedHooks = hooks.filter((hook) => {
      const legacy = String(hook.command || "").includes("skill-subscribe/scripts/check.py");
      if (legacy) changed = true;
      return !legacy;
    });
    if (cleanedHooks.length > 0 || hooks.length === 0) {
      cleanedGroups.push(cleanedHooks.length === hooks.length ? group : { ...group, hooks: cleanedHooks });
    }
  }
  if (!changed) return;
  if (cleanedGroups.length > 0) data.hooks.SessionStart = cleanedGroups;
  else delete data.hooks.SessionStart;
  if (DRY) console.log("  - legacy skill-subscribe SessionStart hook");
  else fs.writeFileSync(settingsPath, `${JSON.stringify(data, null, 2)}\n`);
}

console.log(`\n${DRY ? "[dry-run] " : ""}Installing selected packages → ${platforms.join(", ")}\n`);

let failures = 0;
for (const platform of platforms) {
  const dest = PLATFORMS[platform].dir(HOME);
  const platformPlugins = platform === "claude-code"
    ? ["weed-harness", ...plugins]
    : plugins;
  console.log(`[${platform}] ${dest} (${platformPlugins.join(", ") || "cleanup only"})`);
  const legacySkills = platform === "claude-code"
    ? LEGACY_SKILLS
    : [...LEGACY_SKILLS, "setup"];
  const legacyDirs = platform === "opencode"
    ? [dest, path.join(HOME, ".config", "opencode", "skill")]
    : [dest];
  for (const legacyDir of legacyDirs) {
    for (const skill of legacySkills) {
      const legacyPath = path.join(legacyDir, skill);
      if (DRY) {
        console.log(`  - legacy ${legacyPath}`);
      } else {
        fs.rmSync(legacyPath, { recursive: true, force: true });
      }
    }
  }
  if (platform === "claude-code") {
    try {
      cleanupLegacyClaudeHook(HOME);
    } catch (err) {
      console.log(`  ✗ legacy hook cleanup: ${err.message}`);
      failures++;
    }
  }
  for (const plugin of platformPlugins) {
    const { src, platforms: supportedPlatforms } = PLUGINS[plugin];
    if (supportedPlatforms && !supportedPlatforms.includes(platform)) continue;
    const skills = skillDirs(src);
    if (skills.length === 0) {
      console.log(`  ! ${plugin}: no skills found at ${src}`);
      failures++;
      continue;
    }
    for (const skill of skills) {
      const installedName = installedSkillName(platform, skill);
      const from = path.join(src, skill);
      const to = path.join(dest, installedName);
      try {
        if (!DRY) {
          fs.mkdirSync(dest, { recursive: true });
          fs.rmSync(to, { recursive: true, force: true });
          fs.cpSync(from, to, { recursive: true });
          if (platform === "opencode") {
            normalizeOpenCodeSkill(to, skill, installedName);
          }
        }
        const renamed = skill === installedName ? "" : ` → ${installedName}`;
        console.log(`  ✓ ${plugin}/${skill}${renamed}`);
      } catch (err) {
        console.log(`  ✗ ${plugin}/${skill}: ${err.message}`);
        failures++;
      }
    }
  }
  if (platform === "opencode" && !DRY) {
    for (const plugin of platformPlugins) {
      for (const assets of OPENCODE_ASSETS[plugin] || []) {
        if (!fs.existsSync(assets.src)) continue;
        const assetDest = assets.dir(HOME);
        try {
          fs.mkdirSync(assetDest, { recursive: true });
          for (const entry of fs.readdirSync(assets.src, { withFileTypes: true })) {
            if (!entry.isFile()) continue;
            fs.cpSync(path.join(assets.src, entry.name), path.join(assetDest, entry.name));
          }
          console.log(`  ✓ ${plugin}/${assets.desc}`);
        } catch (err) {
          console.log(`  ✗ ${plugin}/${assets.desc}: ${err.message}`);
          failures++;
        }
      }
      try {
        installOpenCodeCommands(plugin, HOME);
      } catch (err) {
        console.log(`  ✗ ${plugin}/skill slash commands: ${err.message}`);
        failures++;
      }
    }
  } else if (platform === "opencode") {
    for (const plugin of platformPlugins) {
      for (const assets of OPENCODE_ASSETS[plugin] || []) {
        if (fs.existsSync(assets.src)) {
          console.log(`  ✓ ${plugin}/${assets.desc}`);
        }
      }
      if (plugin === "matt-loop") {
        console.log(`  ✓ ${plugin}/skill slash commands`);
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

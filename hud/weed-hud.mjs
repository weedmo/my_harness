#!/usr/bin/env node
/**
 * weed-hud - Statusline for Claude Code
 * Shows: [weed#version] | model effort | 5h% | wk% @dir | session | ctx% | tools
 *
 * 5h%/wk% come from Claude Code's official rate_limits payload (matches /usage).
 */

import { readFileSync, readdirSync, existsSync } from "node:fs";
import { homedir } from "node:os";
import { join, basename } from "node:path";
import { execSync } from "node:child_process";

const home = homedir();

function readStdin() {
  return new Promise((resolve) => {
    let data = "";
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (c) => (data += c));
    process.stdin.on("end", () => resolve(data));
    setTimeout(() => resolve(data), 1500);
  });
}

function findLatestPluginVersion(name) {
  const base = join(home, ".claude/plugins/cache/weed-plugins", name);
  if (!existsSync(base)) return null;
  const versions = readdirSync(base, { withFileTypes: true })
    .filter((d) => d.isDirectory() && /^\d/.test(d.name))
    .map((d) => d.name)
    .sort((a, b) => b.localeCompare(a, undefined, { numeric: true }));
  return versions[0] || null;
}

function parseTranscript(path) {
  const out = { tools: 0, sessionMin: 0 };
  if (!path || !existsSync(path)) return out;
  let tools = 0;
  let firstTs = null;
  const content = readFileSync(path, "utf8");
  for (const line of content.split("\n")) {
    if (!line) continue;
    let m;
    try {
      m = JSON.parse(line);
    } catch {
      continue;
    }
    const ts = m.timestamp;
    if (ts && !firstTs) firstTs = ts;
    const c = m.message?.content;
    if (Array.isArray(c)) {
      for (const b of c) if (b?.type === "tool_use") tools++;
    }
  }
  out.tools = tools;
  if (firstTs) {
    out.sessionMin = Math.max(
      0,
      Math.round((Date.now() - new Date(firstTs).getTime()) / 60000),
    );
  }
  return out;
}

function getGitInfo(cwd) {
  if (!cwd) return null;
  const opts = { cwd, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"], timeout: 200 };
  const tryRun = (cmd) => {
    try {
      return execSync(cmd, opts).trim();
    } catch {
      return "";
    }
  };
  const branch = tryRun("git --no-optional-locks rev-parse --abbrev-ref HEAD");
  if (!branch) return null;
  const displayBranch =
    branch === "HEAD"
      ? tryRun("git --no-optional-locks rev-parse --short HEAD") || "DETACHED"
      : branch;
  const gitDir = tryRun("git --no-optional-locks rev-parse --git-dir");
  const isWorktree = gitDir.includes("/worktrees/");
  return { branch: displayBranch, isWorktree };
}

function shortModel(data) {
  const id = data.model?.id || "";
  const display = data.model?.display_name || "";
  const fromId = id.match(/claude-(opus|sonnet|haiku|fable|mythos)-(\d+)-(\d+)/i);
  if (fromId) {
    const [, , major, minor] = fromId;
    return `${major}.${minor}`;
  }
  const fromDisplay = display.match(/(Opus|Sonnet|Haiku|Fable|Mythos)\s+(\d+)\.(\d+)/i);
  if (fromDisplay) {
    const [, , major, minor] = fromDisplay;
    return `${major}.${minor}`;
  }
  return display || "claude";
}

function levelColor(value, mid, high, C) {
  if (value < mid) return C.green;
  if (value < high) return C.yellow;
  return C.red;
}

function getTerminalCols() {
  if (process.stdout.columns) return process.stdout.columns;
  if (process.stderr.columns) return process.stderr.columns;
  if (process.env.COLUMNS) return parseInt(process.env.COLUMNS, 10) || 0;
  try {
    const out = execSync("stty size < /dev/tty 2>/dev/null || tput cols 2>/dev/null", {
      encoding: "utf8",
      stdio: ["pipe", "pipe", "ignore"],
    }).trim();
    const n = parseInt(out.split(/\s+/).pop(), 10);
    if (n > 0) return n;
  } catch {}
  return 0;
}

function formatRemaining(resetsAtSec) {
  if (!resetsAtSec) return "";
  const ms = resetsAtSec * 1000 - Date.now();
  if (ms <= 0) return "0m";
  const totalMin = Math.round(ms / 60000);
  const days = Math.floor(totalMin / 1440);
  const hours = Math.floor((totalMin % 1440) / 60);
  const mins = totalMin % 60;
  if (days > 0) return hours > 0 ? `${days}d${hours}h` : `${days}d`;
  if (hours > 0) return mins > 0 ? `${hours}h${mins}m` : `${hours}h`;
  return `${mins}m`;
}

function visibleLength(s) {
  const stripped = s.replace(/\x1b\[[0-9;]*m/g, "");
  let len = 0;
  for (const ch of stripped) {
    const cp = ch.codePointAt(0);
    len += cp > 0x1f000 ? 2 : 1;
  }
  return len;
}

async function main() {
  const raw = await readStdin();
  let data = {};
  try {
    data = JSON.parse(raw);
  } catch {}

  const model = shortModel(data);
  const effort = data.effort?.level || "";
  const cwd = data.cwd ? basename(data.cwd) : "";
  const gitInfo = getGitInfo(data.cwd);
  const version = findLatestPluginVersion("weed-harness") || "?";
  const { tools, sessionMin } = parseTranscript(data.transcript_path);
  const ctxPct = Math.round(data.context_window?.used_percentage ?? 0);
  const fiveHourPct = Math.round(data.rate_limits?.five_hour?.used_percentage ?? 0);
  const weekPct = Math.round(data.rate_limits?.seven_day?.used_percentage ?? 0);
  const fiveHourLeft = formatRemaining(data.rate_limits?.five_hour?.resets_at);
  const weekLeft = formatRemaining(data.rate_limits?.seven_day?.resets_at);

  const C = {
    reset: "\x1b[0m",
    dim: "\x1b[2m",
    cyan: "\x1b[36m",
    green: "\x1b[32m",
    yellow: "\x1b[33m",
    red: "\x1b[31m",
    magenta: "\x1b[35m",
  };
  const sessColor = levelColor(sessionMin, 120, 240, C);
  const ctxColor = levelColor(ctxPct, 50, 80, C);
  const fiveHourColor = levelColor(fiveHourPct, 50, 80, C);
  const weekColor = levelColor(weekPct, 50, 80, C);

  const modelPart = effort
    ? `${C.green}${model}${C.reset} ${C.magenta}${effort}${C.reset}`
    : `${C.green}${model}${C.reset}`;

  const head = [
    `${C.cyan}[weed#${version}]${C.reset}`,
    `${C.dim}|${C.reset}`,
    modelPart,
    `${C.dim}|${C.reset}`,
    `5h:${fiveHourColor}${fiveHourPct}%${C.reset}${fiveHourLeft ? `${C.dim}(${fiveHourLeft})${C.reset}` : ""}`,
    `${C.dim}|${C.reset}`,
    `wk:${weekColor}${weekPct}%${C.reset}${weekLeft ? `${C.dim}(${weekLeft})${C.reset}` : ""}`,
    cwd
      ? (() => {
          let s = `${C.dim}@${C.reset}${cwd}`;
          if (gitInfo) {
            const branchColor = gitInfo.isWorktree ? C.magenta : C.cyan;
            const wtMarker = gitInfo.isWorktree ? "⎇" : "";
            s += `${C.dim}:${C.reset}${branchColor}${gitInfo.branch}${wtMarker}${C.reset}`;
          }
          return s;
        })()
      : "",
  ]
    .filter(Boolean)
    .join(" ");
  const tail = [
    `session:${sessColor}${sessionMin}m${C.reset}`,
    `ctx:${ctxColor}${ctxPct}%${C.reset}`,
    `${C.yellow}🔧${tools}${C.reset}`,
  ].join(" ");
  const oneLine = `${head} ${C.dim}|${C.reset} ${tail}`;
  const cols = getTerminalCols();
  const output = cols > 0 && visibleLength(oneLine) > cols ? `${head}\n${tail}` : oneLine;
  process.stdout.write(output);
}

main();

---
name: setup
description: "weed-harness 사용자 환경 셋업 — 터미널 UI(statusLine HUD)와 기본 설정(custom hooks 등록: language-rule, auto-update)만 담당. 스킬/플러그인 설치는 하지 않음(skill-subscribe로 cherry-pick). 멱등(idempotent)이라 여러 번 실행해도 안전. 트리거: '/setup', 'setup hud', 'setup hooks', 'statusLine 등록'."
---

# weed-harness setup

플러그인을 처음 설치한 사용자가 weed-harness의 **사용자-레벨 기본 설정**을 한 번에 적용하기 위한 skill.

## 범위 (중요)

setup은 **터미널 UI와 기본 설정만** 다룬다:

- **`statusLine` HUD** — 터미널 하단 상태줄
- **custom hooks 등록** — language-rule(언어 규칙), auto-update(필수 스킬 자동 최신화)

**스킬/플러그인 설치는 setup의 책임이 아니다.** 각 loop 플러그인(super-loop, auto-loop, matt-loop 등)의 스킬은 통째로 플러그인을 설치하기보다 **skill-subscribe로 필요한 스킬만 cherry-pick**해서 등록하는 것이 효율적이다. 한 번 가져온 필수 스킬(graphify, matt-* 등)의 최신화는 auto-update.sh 훅이 세션 시작마다 수행한다.

## 왜 필요한가

Claude Code 플러그인은 `skills/`, `hooks/hooks.json` 등을 자동으로 등록하지만:

- **`statusLine`** 은 사용자의 `~/.claude/settings.json`에 직접 등록되어야 함
- 일부 hook (language-rule, auto-update) 은 의도적으로 plugin hooks.json에 안 넣음 → opt-in으로 사용자가 등록

## 사용법

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/setup/install.sh"          # 전체 (hud + hooks)
bash "${CLAUDE_PLUGIN_ROOT}/skills/setup/install.sh" hud      # HUD만
bash "${CLAUDE_PLUGIN_ROOT}/skills/setup/install.sh" hooks    # hook 등록만
bash "${CLAUDE_PLUGIN_ROOT}/skills/setup/install.sh" status   # 현재 상태만 보기 (변경 없음)
```

## skill이 호출되었을 때 Claude의 행동

1. 사용자의 의도를 파악:
   - "/setup", "setup all", "전부 설정해줘" → `install.sh all`
   - "setup hud", "statusLine 등록해줘" → `install.sh hud`
   - "setup hooks", "hook 등록" → `install.sh hooks`
   - "setup status", "뭐 설치되어 있어?" → `install.sh status`
   - 스킬 설치 요청("superpowers 설치", "matt skill 가져와" 등)이면 setup이 아니라
     **skill-subscribe**(cherry-pick) 또는 `/plugin install`로 안내

2. 해당 명령을 Bash 도구로 실행. 출력은 그대로 사용자에게 보여줌.

3. 결과 요약: 설치된 항목 / 이미 있던 항목 / 실패한 항목. statusLine·hook 적용에는 Claude Code 재시작 필요 안내.

## 셋업 항목 상세

### `hud`

- 플러그인의 `hud/weed-hud.mjs` → 사용자의 `~/.claude/hud/weed-hud.mjs` 로 복사
- `~/.claude/settings.json` 의 `statusLine` 을 `node ~/.claude/hud/weed-hud.mjs` 로 등록
- **버전 무관 안정 경로** 를 사용 → plugin 업데이트에도 statusLine 깨지지 않음
- statusLine이 비어 있거나 이미 weed-hud를 가리킬 때만 등록. **다른 도구(예: Orca)가 관리 중인 statusLine은 건드리지 않고 경고만 출력**

### `hooks`

다음 hook들을 `~/.claude/settings.json` 에 등록 (스크립트 자체는 plugin이 제공):

| Event | Matcher | Script |
|-------|---------|--------|
| UserPromptSubmit | (none) | language-rule.sh |
| SessionStart | (none) | auto-update.sh |

`auto-update.sh`는 세션 시작마다 이미 설치된 필수 스킬을 자동 최신화: graphifyy 신버전이 PyPI에 있으면 업그레이드 후 claude/codex 양쪽에 재설치, superpowers 플러그인 업데이트(best-effort), `~/.codex/skills`의 matt-* 스킬을 marketplace 클론과 재동기화.

각 hook script 가 사용자 `~/.claude/hooks/` 에 없으면 plugin에서 복사. 등록은 같은 matcher group에 합쳐짐.

## 멱등성 / 안전성

- 모든 단계가 "현재 상태 검사 → 필요하면 변경" 방식
- JSON 머지는 Python으로 수행 (수동 sed/awk 안 씀)
- 같은 hook script가 이미 등록되어 있으면 중복 추가 안 함
- 사용자 자체 설정(env, permissions)은 절대 건드리지 않음 — statusLine + hooks 만 다룸

## 적용 확인

`install.sh status` 로 현재 상태를 점검할 수 있음:
- HUD 파일 존재 여부, statusLine 등록 여부
- 각 hook 등록 여부

## 재시작 필요

statusLine, hooks 변경은 Claude Code 세션 재시작 후에 적용됩니다. 재시작 후 statusLine HUD에 `[weed#X.Y.Z]` 가 보이면 OK.

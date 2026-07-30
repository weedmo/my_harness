---
name: setup
description: "weed-harness 사용자 환경 셋업 — statusLine HUD 설치, understand-anything 플러그인 설치, 추가 hooks (language-rule 등) 등록. 멱등(idempotent)이라 여러 번 실행해도 안전. 트리거: '/setup', 'setup hud', 'plugin 설치 후 설정', 'statusLine 등록'."
---

# weed-harness setup

플러그인을 처음 설치한 사용자가 weed-harness가 제공하는 사용자-레벨 설정(statusLine, custom hook 등록)을 한 번에 적용하기 위한 skill.

## 왜 필요한가

Claude Code 플러그인은 `skills/`, `agents/`, `hooks/hooks.json`, MCP 서버는 자동으로 등록하지만:

- **`statusLine`** 은 사용자의 `~/.claude/settings.json`에 직접 등록되어야 함
- **외부 플러그인 의존성** (예: understand-anything) 은 별도 설치 필요
- 일부 hook (language-rule 등) 은 의도적으로 plugin hooks.json에 안 넣음 → opt-in으로 사용자가 등록

## 사용법

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/setup/install.sh"            # 전체 셋업
bash "${CLAUDE_PLUGIN_ROOT}/skills/setup/install.sh" hud        # HUD만
bash "${CLAUDE_PLUGIN_ROOT}/skills/setup/install.sh" understand # understand-anything 플러그인
bash "${CLAUDE_PLUGIN_ROOT}/skills/setup/install.sh" hooks      # 추가 hook 등록
bash "${CLAUDE_PLUGIN_ROOT}/skills/setup/install.sh" status     # 현재 상태만 보기 (변경 없음)
```

## skill이 호출되었을 때 Claude의 행동

1. 사용자의 의도를 파악:
   - "/setup", "setup all", "전부 설정해줘" → `install.sh all`
   - "setup hud", "statusLine 등록해줘" → `install.sh hud`
   - "setup understand", "understand-anything 설치" → `install.sh understand`
   - "setup hooks", "hook 등록" → `install.sh hooks`
   - "setup status", "뭐 설치되어 있어?" → `install.sh status`

2. 해당 명령을 Bash 도구로 실행. 출력은 그대로 사용자에게 보여줌.

3. 결과 요약:
   - 설치된 항목, 이미 있던 항목, 실패한 항목을 표로 정리
   - statusLine/hook 적용을 위해 Claude Code 재시작이 필요하면 안내

## 셋업 항목 상세

### `hud`

- 플러그인의 `hud/weed-hud.mjs` → 사용자의 `~/.claude/hud/weed-hud.mjs` 로 복사
- `~/.claude/settings.json` 의 `statusLine` 을 `node ~/.claude/hud/weed-hud.mjs` 로 등록
- **버전 무관 안정 경로** 를 사용 → 다음 plugin 업데이트(예: 2.1.9 → 2.2.0)에도 statusLine 깨지지 않음
- 사용자가 statusLine을 다른 명령으로 바꿔놨다면 덮어씀 (멱등성을 위해)

### `understand`

- `claude plugin marketplace add Lum1104/Understand-Anything` (이미 있으면 skip)
- `claude plugin install understand-anything` (이미 있으면 skip)
- codebase 이해/분석용 third-party 플러그인 (`/understand`, `/understand-explain`, `/understand-chat` 등 제공)
- 자동 트리거되지 않음 — 사용자가 명시적으로 해당 slash command를 호출해야 함

### `hooks`

다음 hook들을 `~/.claude/settings.json` 에 등록 (스크립트 자체는 plugin이 제공):

| Event | Matcher | Script |
|-------|---------|--------|
| UserPromptSubmit | (none) | language-rule.sh |

각 hook script 가 사용자 `~/.claude/hooks/` 에 없으면 plugin에서 복사. 등록은 같은 matcher group에 합쳐짐.

## 멱등성 / 안전성

- 모든 단계가 "현재 상태 검사 → 필요하면 변경" 방식
- JSON 머지는 Python으로 수행 (수동 sed/awk 안 씀)
- 같은 hook script가 이미 등록되어 있으면 중복 추가 안 함
- 사용자 자체 설정(env, permissions)은 절대 건드리지 않음 — statusLine + hooks 만 다룸

## 적용 확인

`install.sh status` 로 현재 상태를 점검할 수 있음:
- HUD 파일 존재 여부
- statusLine 등록 여부
- 각 hook 등록 여부

## 재시작 필요

statusLine, hooks 변경은 Claude Code 세션 재시작 후에 적용됩니다. 재시작 후 statusLine HUD에 `[weed#X.Y.Z]` 가 보이면 OK.

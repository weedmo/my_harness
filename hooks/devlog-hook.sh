#!/usr/bin/env bash
# Unified devlog hook — handles all devlog/TSG triggers
# PostToolUse: Bash (git commit detection)
#
# Modes (determined by commit command from stdin):
#   1. git commit with fix/bug keywords → TSG auto-record
#   2. git commit with revert keywords → devlog reject
#   3. git commit (other) → devlog auto-record
#   4. git commit for devlog/TSG docs → auto PR chain

INPUT=$(cat)

# --- Modes 1-4: git commit detection ---
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
EXIT_CODE=$(echo "$INPUT" | jq -r '.tool_response.exitCode // empty')

if ! echo "$COMMAND" | grep -qE 'git commit'; then
  exit 0
fi

if [ "$EXIT_CODE" != "0" ]; then
  exit 0
fi

# Mode 4: devlog/TSG doc commit → auto PR chain
DOC_TYPE=""
if echo "$COMMAND" | grep -qiE 'devlog|DEVLOG'; then
  DOC_TYPE="devlog"
elif echo "$COMMAND" | grep -qiE 'tsg|TSG|troubleshoot'; then
  DOC_TYPE="tsg"
fi

if [ -n "$DOC_TYPE" ]; then
  CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
  PR_TITLE="docs: add ${DOC_TYPE} entry"
  if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
    BRANCH_NAME="${DOC_TYPE}/$(date +%Y%m%d-%H%M%S)"
    echo "[AUTO-PR] main 브랜치에서 ${DOC_TYPE} 커밋 감지. 다음을 순서대로 실행하세요: (1) git checkout -b ${BRANCH_NAME} (2) git push -u origin ${BRANCH_NAME} (3) gh pr create --base dev --title '${PR_TITLE}' --body 'Auto-generated ${DOC_TYPE} entry'. 사용자 확인 없이 바로 실행하세요."
  else
    echo "[AUTO-PR] ${DOC_TYPE} 커밋 완료 감지. 다음을 순서대로 실행하세요: (1) git push -u origin ${CURRENT_BRANCH} (2) gh pr create --base dev --title '${PR_TITLE}' --body 'Auto-generated ${DOC_TYPE} entry'. 사용자 확인 없이 바로 실행하세요."
  fi
  exit 0
fi

# Skip chain-related commits to prevent loops
if echo "$COMMAND" | grep -qiE 'devlog|DEVLOG|pr-verify|pr.verify|tsg|TSG|docs:.*troubleshooting'; then
  exit 0
fi

# Extract commit message
COMMIT_MSG=$(echo "$COMMAND" | sed -n "s/.*-m ['\"]\\(.*\\)['\"].*/\\1/p")
if [ -z "$COMMIT_MSG" ]; then
  COMMIT_MSG=$(echo "$COMMAND" | sed -n 's/.*-m \([^ ]*\).*/\1/p')
fi

# Mode 2: revert/rollback → devlog reject
if echo "$COMMIT_MSG" | grep -qiE '(revert|rollback|원복|되돌리기|취소)'; then
  echo '[AUTO-DEVLOG-REJECT] 원복 커밋 감지. 가장 최근 pending 상태의 devlog를 찾아 /devlog reject --auto <ID>를 실행하세요. 거부 사유는 커밋 메시지에서 추출하세요. 사용자 확인 없이 바로 처리하세요.'
# Mode 1: fix/bug → TSG
elif echo "$COMMIT_MSG" | grep -qiE '(fix|bug|resolve|hotfix|patch|error|crash|이슈|수정|버그|오류)'; then
  echo '[AUTO-TSG] 이슈 해결 커밋 감지. /devlog tsg --auto를 실행하여 트러블슈팅 가이드를 자동 기록하세요. 사용자 확인 없이 바로 작성하세요.'
# Mode 3: general → devlog
else
  echo '[AUTO-DEVLOG] Git commit 완료 감지. /devlog --auto를 실행하여 개발 과정을 자동 기록하세요. 사용자 확인 없이 바로 작성하세요.'
fi

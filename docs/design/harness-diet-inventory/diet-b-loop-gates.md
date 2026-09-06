# loop-gates diet-b 대조표 (2026-09-06)

| 지운 규칙 | D-id | 남은 자리 |
|---|---|---|
| 단위 목록의 "a matt-auto ticket" | D4 | PR · autocode 실행 · matt-auto ship |
| "every previously completed unit's ledger is re-run then too" (티켓 간 재검증) | D4 | matt-auto 9단계의 "머지 뒤 먼저 끝난 티켓의 명령 재실행" |
| "A worker in its own worktree gets its own copy of the ledger and its own approval there" | D4 | 삭제 (워커 워크트리에 원장이 없다); "evidence is produced on the coordinator's machine"는 Orca 경계 항목에 유지 |
| description의 `merging-pr-queue` | D5 | pr-babysit · autocode · matt-auto ship |

## 문장만 줄인 곳 (규칙 유지, D6)

- Red flags 6개 → 4개: "CHECK: baking in a number"와 "dispatch/lease under Orca"는 본문 규칙의 반복이라 뺐다.
- 설치 경로 열거(`~/.agents/skills/unlazy`, per-CLI dirs)를 한 문장으로.
- `wc -w` 693 (목표 ≤ 700 충족).

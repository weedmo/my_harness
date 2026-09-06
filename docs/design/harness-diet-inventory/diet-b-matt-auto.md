# matt-auto diet-b 대조표 (2026-09-06)

지운 규칙 → 근거가 사라진 결정(D-id). 여기 없는 문장은 줄였을 뿐 규칙은 남아 있다.

| 지운 규칙 | D-id | 남은 자리 |
|---|---|---|
| 라우팅 표의 `matt-fast` · `matt-max` 행, `matt-large-context` "chunk via matt-max" | D1, D2 | `matt-default` / `matt-deep` 두 행, large-context는 "chunk via `matt-deep`" |
| Ship mode Routing "Opening the PR → matt-fast" | D1 | "Opening the PR → in-session" |
| 9단계: 티켓별 `.unlazy/matt-auto/<ticket>.GATES.md` 작성 · `gate-check.mjs --reverify` · "unmet gates … max two retries" | D4 | "Verification is yours" — 검증 명령을 프롬프트에, 반환 후 코디네이터가 워크트리/체크아웃에서 직접 실행, 재시도 ≤ 2, 그 뒤 에스컬레이션 |
| Parallel loop 2단계: 워커 워크트리에 원장 복사 · `CWD: ../..` · approve | D4 | 삭제 (워커 프롬프트가 검증 명령을 담는다) |
| Parallel loop 4단계: `--reverify` 원장, 머지 뒤 원장 복사 · `--approve --reverify` · 이전 티켓 원장 재검증 | D4 | 워커 워크트리에서 명령 직접 실행, 머지 뒤 먼저 끝난 티켓의 명령 재실행 |
| Parallel 마무리 "unlazy boundaries … one Solo ledger per ticket … Stop hook" | D4 | "Orca owns dispatch, waiting, and retry; you own verification" |
| 티켓 보드 Gates 열 (`met/total` from `--reverify`; `—` without unlazy) | D4 | Checks 열 (`passed/total` on your latest run) |
| 결정 로그 `gates_caught` 정의 "any of your --reverify runs … decides the future of the per-ticket ledger" | D4 | ship 원장 UNMET 건수 |
| PR 조건 "every ticket complete with its ledger ALL MET (or its verification passed without unlazy)" | D4 | "every ticket's verification commands pass on your own run" |
| Ship ledger G1 "every ticket ledger ALL MET (for f in …GATES.md …)" | D4 | "every ticket's verification commands pass on the PR branch tip (one gate per ticket)" |
| Red flag "trusting … instead of your own --reverify" | D4 | "your own run of its commands, before and after merge" |
| `orca-worker-prompt.md` "Done is defined by … GATES.md / 파일 없으면 ask / gate-check 실행" | D4 | "Done is the ticket's verification commands passing; the coordinator re-runs them" |
| 규칙 4 · Fallback "weed-harness 3.x required" | D8 | "4.x" |

## 문장만 줄인 곳 (규칙 유지, D6)

- Red flags 9개 → 7개: 각 항목의 "→ 이유" 절을 지우고 같은 뜻의 항목을 합쳤다. 모든 항목은 본문 규칙의 반복이다.
- Progress board 데이터 계약 문단: `blocked`/`blocker`/`estimateMin`/`startedAt` 등은 `$interview-report`의 계약이라 열거를 줄이고 참조로 남겼다.
- Ship ledger G4–G6: pr-babysit 원장의 세 게이트와 같은 명령이라 "pr-babysit's three gates with its commands"로 참조했다.
- 근거 설명 절 삭제: "DAG independence is not disk independence", "a results panel written before the work is verified is a guess", "the ledger exists because a confident report is not evidence" 등 — 규칙 문장은 그대로.
- 목표 ≤ 3,500 단어에는 못 미쳤다(3,790). 더 지울 D-id가 없어 `bin/check-words.mjs`의 상한은 3,800으로 둔다.

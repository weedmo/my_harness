# autocode diet-b 대조표 (2026-09-06)

| 지운 규칙 | D-id | 남은 자리 |
|---|---|---|
| 2C hard → `strategist-max` (fable/xhigh) | D3 | Codex: `strategist`를 `reasoning_effort: "max"`로 스폰; Claude Code · OpenCode: Deep `strategist` + `escalated = true` |
| 3C `auto-loop:strategist-max` 스폰 | D3 | `strategist` (Codex는 hard일 때 effort max) |
| 3E-2 `strategist-max` 재스폰 "the only automatic path to the Max tier" | D3 | Codex 재스폰(effort max) / 그 외 같은 `strategist`에 회고 전달; `escalated = true`; 실행당 한 번 |
| 3E-3 "If already on max" | D3 | "If already `escalated`" (종료 조건 동일) |
| 3H 표 Strategist(escalated)=Max, Experimenter fast 행 | D1, D2 | Strategist(escalated)="Deep, Codex effort `max`"; Experimenter default 행이 one-site 변경도 포함 |
| 3D-2 `beyond_scope` reroute "fast→default→deep" | D1 | "default→deep" |
| 3H "Max is reserved for the strategist" | D2 | "the Codex `max` retry is reserved for the strategist" |
| `reference.md` `experimenter-fast (haiku/low)` 예시 두 곳, `difficulty: "fast"`, routes `fast|default|deep` | D1 | `experimenter-default (opus/medium)`, `default|deep` |
| `validate.py` `DIFFICULTIES` `fast` | D1 | `{"default", "deep"}` |
| 서문 "weed-harness 3.x required" | D8 | "4.x" |

## 문장만 줄인 곳 (규칙 유지, D6)

- Anti-patterns 11개 → 7개: 같은 뜻의 항목을 합쳤다(배치 대기 + 전략가 재스폰, 노이즈 밴드 + worker_done 신뢰, 보드 stale + deliver.py, 체크아웃 + --no-ff + push + merge).
- 줄바꿈으로 나뉘어 있던 문단을 한 줄로 합쳤다(단어 수는 그대로, 읽기만 바뀜).
- 목표 ≤ 3,500 단어에는 못 미쳤다(4,182). 코드 블록과 명령 예시가 절반이라 더 지울 D-id가 없어 `bin/check-words.mjs`의 상한은 4,200으로 둔다.

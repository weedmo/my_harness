---
name: super-loop
description: "superpowers 기반 개발 루프 — brainstorming → writing-plans → 실행(subagent-driven/executing-plans) → verification → finishing을 하나의 게이트 루프로 실행. verification이 실패하면 원인 단계로 되돌아가 수렴할 때까지 반복. 트리거: '/super-loop', 'superpowers loop', 'superpowers 루프로 진행해줘'. superpowers 플러그인 필요 (/setup claude가 설치)."
---

# super-loop

superpowers 스킬들을 하나의 **게이트 루프**로 엮는 얇은 오케스트레이터.
각 단계는 해당 superpowers 스킬을 Skill 도구로 호출해 수행하고, 게이트를
통과해야 다음 단계로 넘어간다. 이 스킬 자체는 glue일 뿐 — 실제 방법론은
전부 superpowers가 소유한다.

## 전제

- superpowers 플러그인이 설치되어 있어야 한다 (`/setup claude`).
- 격리가 필요한 작업이면 시작 전에 `superpowers:using-git-worktrees`.

## 루프

```
[1] BRAINSTORM   superpowers:brainstorming
      gate: 사용자가 승인한 스펙 (HARD-GATE)
[2] PLAN         superpowers:writing-plans
      gate: 단계별 계획 + 각 단계의 검증 방법 명시
[3] EXECUTE      규모에 따라 택1
      - 같은 세션, 리뷰 중요 → superpowers:subagent-driven-development
      - 별도 세션            → superpowers:executing-plans
      gate: 계획의 모든 단계 완료
[4] VERIFY       superpowers:verification-before-completion
      gate: 검증 명령 실행 + 증거 확보 (주장 금지, 증거만)
      실패 시 루프백:
        - 구현 결함        → [3]으로
        - 계획 결함        → [2]로
        - 요구사항 오해    → [1]로
[5] FINISH       superpowers:finishing-a-development-branch
      gate: 테스트 통과 + 통합 방식 결정
```

## 규칙

- **단계를 건너뛰지 않는다.** 이미 승인된 스펙/계획이 있으면 해당 단계는
  "게이트 통과"로 처리하고 넘어간다 (다시 하지 않는다).
- **루프백은 원인 단계까지만.** 전체를 처음부터 다시 돌지 않는다.
- **3회 연속 같은 게이트에서 실패하면 멈추고 사용자에게 보고한다** —
  실패 내용, 시도한 것, 막힌 지점.
- trivial 작업에는 이 루프를 쓰지 않는다 (SKILL_MAP의 Golden rule).

## 사용자가 이 스킬을 호출했을 때

1. 현재 상태를 진단해 어느 단계에서 시작할지 정한다
   (스펙 있음 → [2], 계획 있음 → [3], 구현 끝 → [4]).
2. 각 단계 진입 시 "super-loop: [단계] 시작 — [superpowers 스킬]" 한 줄 보고.
3. 루프백이 발생하면 이유를 한 줄로 보고하고 되돌아간다.

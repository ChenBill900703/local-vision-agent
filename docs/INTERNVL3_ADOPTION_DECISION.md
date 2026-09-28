# InternVL3 Adoption Decision — 2026-09-28

PILOT / EXPLORATORY / NOT FORMAL THESIS RESULT

**ADOPT INTERNVL3-2B-INSTRUCT AS PRIMARY VLM CANDIDATE**

Evidence: [capability result](INTERNVL3_AGENT_CAPABILITY_RESULT.md), immutable initial
[feasibility report](INTERNVL3_2B_GPU_FEASIBILITY_REPORT.md), and frozen capability amendment.
Engineering safety, offline, five completed queries, placement and cleanup PASS.
Semantic/capability review is human-only and cannot be inferred from process exit0.

Human record (user statement, no AI semantic grading):

```json
{
  "reviewer_kind": "human_user",
  "reviewer": "project user",
  "recorded_at": "2026-09-28T14:34:52.064867+08:00",
  "run_id": "INTERNVL3_AGENT_CAPABILITY_PILOT_20260928",
  "raw_events_sha256": "0b520872d0b08de7c33bf191e8908be18fce213923941ba4a8cb6fb66e65f5d9",
  "all_capabilities_and_chinese_usable": true,
  "statement": "人工確認：全部可用，Verification 足以支持 claim",
  "method": "Post-run user review of all five unmodified raw outputs against prospective rubric; no GPT judge"
}
```

This is engineering/development adoption only; not RQ2–RQ4 success. Same-model verification is not ground truth. No third model, formal experiment, push or release. PUBLIC RELEASE RIGHTS remains UNKNOWN.

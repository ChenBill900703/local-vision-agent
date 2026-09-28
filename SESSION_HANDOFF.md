# Latest handoff — Adoption confirmed 2026-09-28

ADOPT INTERNVL3-2B-INSTRUCT AS PRIMARY VLM CANDIDATE. User human review confirms
all five raw capability outputs and Traditional Chinese usable. GPU session
INTERNVL3_AGENT_CAPABILITY_PILOT_20260928 consumed; safety/offline/cleanup PASS.
No further GPU load authorized by that allowance. No dependency/download changes.
See docs/INTERNVL3_ADOPTION_DECISION.md and docs/INTERNVL3_AGENT_CAPABILITY_RESULT.md.
Next: create local adopt-internvl3-2b-primary-vlm checkpoint, then authorized adapter/
persistent-worker/bounded-Agent development. No real images supplied; no extra GPU run.
The previous handoff below is historical, including its former pending authorization.

# Session handoff — 2026-09-28

**PILOT / EXPLORATORY / NOT FORMAL THESIS RESULT**

## Active state

InternVL3 Safe Migration + Full Local Feasibility phase ended with
**CONDITIONAL PASS — SMALL ENGINEERING BLOCKER**. Stop GPU work and integration.
Full [feasibility report](docs/INTERNVL3_2B_GPU_FEASIBILITY_REPORT.md),
[frozen amendment](docs/INTERNVL3_PILOT_AMENDMENT_2026-09-28.md),
[static review](docs/INTERNVL3_STATIC_REVIEW_2026-09-28.md).
RD-001/RQ1–4/same-model A–D/local8GB unchanged. Model implementation evaluation only.

Candidate: OpenGVLab/InternVL3-2B-Instruct, model/config/tokenizer/template revision
`f6c7b60375759170fd49f5e9e298e2178485c5ba`. Not adopted into active Agent adapter.
Official -hf is default/MPO-lineage conversion, not the same Instruct checkpoint.

Current Git HEAD: `cb171216dac7f7fd99aa6b9a2776de4bd1311af4`
(`checkpoint-moondream2-feasibility-complete`), created BEFORE InternVL acquisition.
No push. Working tree has this phase's code/docs/tests, deliberately uncommitted;
run-start exact dirty state/source hashes in run/provenance.json, completion state and
diff archived in evidence/. Do not discard dirty changes or rewrite checkpoint history.

## Assets / environment

Root: `artifacts/internvl3-20260928` (ignored).
One4,177,999,192-byte BF16 safetensors, no alternate weights or datasets.
Weights SHA256 `b69fcfb5cd97b91b52022642d88da91201487aa73750fa8b14a0e6591a5a9e2d`.
Payload ledger4,190,306,324 bytes; <=5GB acquisition ceiling.
Full receipts/allowlists/provenance, selected source/config/tokenizer and official rights
evidence retained. Hash-verified controlled code under `controlled/iv3_fixed`;
patch SHA256 `e9374e89a0a0668af5cdd56ebf43a170fd1ff47798a9027cbdc6223754654c95`.
Backup: `artifacts/internvl3-20260928-evidence-backup` (excludes duplicate large weights).
Dependencies changed: **NONE**. Existing Python3.11.9, torch2.7.1+cu126,
Transformers4.57.6. Use PYTHONPATH=src and PYTHONIOENCODING=utf-8 for CPU commands.
PUBLIC RELEASE RIGHTS = UNKNOWN; local bounded research usage supported by review.

## Runs and last PASS

One InternVL GPU run `INTERNVL3_INITIAL_GPU_PILOT`, 2026-09-28 02:48:53+08:00;
one persistent load, one original synthetic fixture, four real queries,82 output tokens.
English QA PASS; direct繁中 QA PASS;繁中caption PASS; English-to繁中 PASS on this fixture.
Offline/observed cuda:0 placement/resource bounds PASS. Peak allocated4429.578MiB,
peak reserved4688MiB, sampled whole-device peak5105MiB.
Cleanup0 allocated/0 reserved, process tree empty; after exit214used/7804freeMiB baseline.
No OOM/runtime failure. Last technical checkpoint: cleanup + process exit PASS.
Shared GPU memory spill: UNKNOWN / OBSERVABILITY LIMITATION, not zero-spill proof.

## Blocker and do-not-repeat

Scheduler's frozen lexical gate was overly restrictive (`left`, `right`, `了` rejected).
It skipped all four scene/object/detail/verification probes despite correct core outputs.
This is assistant-authored engineering incompleteness, not Chinese-model failure.
Keep raw gate=false and protocol unchanged; no post-result tuning of this gate.
The tokenizer warning is explained by local Transformers' null-version Mistral heuristic;
no regex correction or remote request occurred. Exact warning/review retained.

- Do not rerun initial pilot; exclusive run directory is a consumed authorization gate.
- Do not install/download a second model, quantize/offload, or delete Moondream assets.
- Do not resume Moondream prompt tuning. All initial/repair1/final runs consumed;
  Chinese blocker and historical raw evidence remain preserved.
- Do not integrate adapter, run A–D/formal data, or publish without separate approval.
- Do not reinterpret fixture success as general quality, research improvement or deadline guarantee.

## Exact next action

Read the report and original authorization; present conditional result for user decision.
If user authorizes completing missing probes: write a NEW prospective amendment defining
a sound non-GPT scheduling/acceptance mechanism and ONE bounded offline load/session for
the four already specified capabilities. Keep model/dtype/safety/image/token/deadline
limits and all negative evidence. No additional asset acquisition or dependency needed.
Obtain scoped authorization before GPU execution. Only after full feasibility and user
confirmation may real-adapter integration begin. No automatic continuation from this file.

CPU checks:75 tests passed, Ruff passed, strict Mypy21 modules passed.
Report can be regenerated CPU-only with `.venv/Scripts/python.exe scripts/internvl_report.py`.
Author must review code/raw answers and any AI-assisted claims; no advisor/institution
approval asserted.10/31 core and11/1 engineering acceptance remain targets only.

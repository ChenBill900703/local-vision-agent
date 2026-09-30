# CURRENT — Smartphone source input CPU ready, 2026-09-30

SMARTPHONE SOURCE INPUT = CPU READY.
VERIFICATION BUDGET REPAIR = CPU READY.
COMBINED GPU VALIDATION = PENDING AUTHORIZATION. No baseline READY.
Exact source HEAD: bdf9dd2cb3b5657cf2e33a0efa5829b5b614c694; branch main.
Final docs checkpoint contains same runtime/config; final SHA/clean status recorded in
artifacts/smartphone-source-repair-20260930/checkpoint.json after local commit. No push.

This phase CPU ONLY: no GPU query/import/init/load/inference or real indoor/outdoor run,
no dependencies/downloads, no model/precision/preprocessing/Agent verificationpolicy change.
110 CPU tests PASS(10.956s), Ruff PASS, strict Mypy29 PASS. Prior101-test repair retained.
Large synthetic JPEGs + explicit CPU fake worker prove source ingress wiring, not GPU results.

SourceImageLimits:32MiB compressed,32000000pixels,10000edge,JPEG/PNGsingleframe,strictdecode.
Conservative64bytes/pixel working estimate+64MiBcompressed+1GiBoverhead~=2.97GiB on32GB;
not measured/hardcapped. Reject oversized/malformed/truncated/bomb/unsupported beforeGPU.
Runtime config internvl-development-v2 requires separate source_image_limits; existing
limits image fields explicitly internal/model-facing <=10MiB/262144pixels/512edge.
Original path/hash/bytes/dimensions/format retained; CPU EXIFtranspose/RGB/LANCZOS<=512 then
ignored exclusive <run>-input/normalized.png with sourceprovenance, hash/dimensions recorded.
Original never modified; small fixtures keep originalpath/bytes/pixels. Model still one448tile,
aspect-ratio distortion and lost tiny/distant/OCR details remain development limitations.

Repair doc: docs/SMARTPHONE_SOURCE_INPUT_REPAIR.md.
Old VERIFICATION_BUDGET_REPAIR_OUTDOOR_20260930_V1 amendment frozen NOT EXECUTED, do not use.
New proposal: docs/SMARTPHONE_COMBINED_GPU_VALIDATION_AMENDMENT_2026-09-30.md.
Proposed exclusive ID SMARTPHONE_COMBINED_OUTDOOR_20260930_V1; NOT RUN.
Input MUST be original development_images/outdoor_scene_001.jpg, SHA256
adaf0193b5a16a49526347ea2cd0561d4cd6580fd038290dbacf4e4dbf76e736,3472x4624.
Application performs normalization; never supply manual edge512 as user input for that run.

Prior indoor partial TOOL_CALL_LIMIT/8claims/6checks/2unresolved/truncation/humanreview unchanged;
prior synthetic smoke PASS unchanged. All consumed runs remain non-repeatable; no rawrewrite.
Photos private/local/development only, no cloud/Git/publication/identity recognition.
Exact next action: obtain authorization for ONE original-phone-photo combined GPU validation
under NEW amendment, then prospective execution/humanreview. Do not execute from this handoff.
No engineeringbaselineREADY or formal experiment; no feature expansion/modelshopping.

Previous CURRENT preserved in artifacts/smartphone-source-repair-20260930/previous_handoff.md.
Historical handoffs below do not override CURRENT.

# Historical handoff — Real Agent development implementation, 2026-09-29

ADOPT INTERNVL3-2B-INSTRUCT AS PRIMARY VLM CANDIDATE, user HUMAN review recorded.
Model/tokenizer/config/template f6c7b60375759170fd49f5e9e298e2178485c5ba.
No dependencies/downloads changed; no model shopping or formal evaluation.

Adoption checkpoint: 580d0a92c529b0e4aca692b658ca77d675a4678c, clean before integration.
Current implementation is in the local `integrate-internvl-persistent-bounded-agent`
checkpoint containing this document (resolve exact HEAD with git rev-parse HEAD).
No push. Completion audit/dirty state/source hashes stored under
artifacts/internvl3-capability-20260928/evidence/integration-completion/.
Completion backup: artifacts/internvl3-integration-20260929-evidence-backup.
2026-09-29 closeout performed CPU checks only; no additional GPU session.

Completed code: typed real adapter, private pinned CUDA backend, JSON persistent worker,
independent watchdog, explicit versioned preprocessing, existing A–D controller connection,
Chinese report/normalized trace/evidence links. CPU fixtures only for new integration.
93 CPU tests PASS; Ruff src/tests/scripts PASS; strict Mypy28 modules PASS.
[Integration contract and limits](docs/REAL_INTERNVL_INTEGRATION.md).

GPU runs: exactly one capability session during the 2026-09-28 adoption phase, control+4probes, all user-reviewed
usable; engineering/offline/resource/placement/zero-cleanup/process exit PASS. Initial run
was not repeated. Both are under artifacts/internvl3-20260928/runs. Capability backup:
artifacts/internvl3-capability-20260928-evidence-backup. Human review in evidence/human_review.json.
All original Moondream evidence/weights retained. Last real GPU PASS: capability cleanup.

New RPC/adapter/Agent end-to-end GPU is NOT VERIFIED. Do not relabel pilot as integration
validation. No suitable real images supplied; optional real-image check not run.
No known model/hardware blocker; next verification gate remains pending scoped execution.
The development parser conservatively requires explicit verification labels; other wording
stays unresolved even when a human considers it a reasonable reply. No GPT runtime judge.

Exact next action: freeze and obtain scoped authorization for ONE adapter/Agent GPU smoke
on the existing synthetic fixture using this implementation. No dependency/model download.
Do not rerun initial/capability gates, test another VLM, change precision/offload, integrate
external detector/OCR/UI, or execute formal A–D evaluation. Final common preprocessing/
tiling, claims/triggers/data/metrics/statistics still need formal freeze.

Below are historical handoffs; their older pending/conditional states are not current.

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

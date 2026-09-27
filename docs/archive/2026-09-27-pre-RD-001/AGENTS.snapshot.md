# SUPERSEDED snapshot — 2026-09-27 before RD-001

Historical record only; not active instructions, requirements or execution authorization.
Original path: `AGENTS.md`. Original text follows unchanged (line endings may be normalized).
Active direction: [RD-001](../../RESEARCH_DIRECTION.md).

---

# Project instructions

## Current phase: requirements documentation only

The latest user request explicitly prohibits code changes, dependency installs,
model/data downloads, CUDA initialization, training and GitHub pushes.
Only inspect and edit requirements documentation in this turn. Previous setup
authorization does not carry forward. Do not run tests or GPU checks for doc edits.

Required scope now includes short Traditional Chinese image descriptions, in
addition to Pet breed and DTD texture classification. Captioning is mandatory,
but chat, OCR, detection boxes and segmentation remain out of scope.
See docs/REQUIREMENTS.md v1.1 for current contracts and proposed research design.
Do not silently omit captioning if no safe model fits: report the blocker.
Caption claims are not class ground truth; classification AURC does not validate
caption quality. No caption model has been selected or hardware-validated.

Updated: 2026-09-22. The user explicitly says NOT to start the project yet.
Only perform requested reviews and documentation edits. Do not implement fixes
or features, install dependencies, download data/models, train, infer, benchmark,
or push/publish to GitHub until the user explicitly authorizes the relevant phase.
Read-only inspection is allowed; diagnostic tests must be within the requested
review. README commands and earlier deadlines are not execution authorization.

Automatic decision-making is sufficient. An LLM-driven agent and Qwen are NOT
requirements. The project supports a master's thesis and publication submission;
do not guarantee graduation, novelty, ethics approval or publication acceptance.
Older roadmap entries about LLM decisions and schedules are historical proposals,
not prerequisites, authorization, or evidence of completed work.

## Requirements before implementation and formal evaluation

Track decisions as proposed, user-confirmed, or advisor/institution-confirmed;
never invent approval. Resolve these boundaries before freezing formal experiments:

- Research question, proposed contribution versus prior work, primary metric,
  comparison baseline, resource budget and success criterion.
- Input/output contract: known labels/dataset versus unknown-domain input,
  single/batch images, unsupported inputs, abstention and failure behavior.
- Required datasets and versions, usage rights, splitting and duplicate checks,
  calibration/validation/test roles, expected sample counts and label vocabulary.
- Minimum deliverables, available GPU time, experiment budget and dated milestones;
  clarify whether the deadline means code, thesis, submission or acceptance.
- Target venue/category, advisor expectations, applicable institutional review,
  authorship and AI disclosure rules. Confirm actual policies from their sources;
  public datasets alone do not establish an exemption from review.
- GitHub visibility, code license, distributable artifacts, report language and
  publication figure specifications.

Suggest concrete defaults but label them as proposals. Formal experiments need
a versioned protocol. Pilot work is exploratory and also requires authorization
to leave the current review-only phase.

### Decision register and phase gates

- Maintain a decision register in README.md with proposal, status, responsible
  confirmer, confirmation date and evidence/source. Missing evidence means
  unconfirmed; AI suggestions do not establish user or institutional approval.
- User-confirmed: automatic decisions suffice; no required LLM/Qwen; RTX 3070 Ti
  8 GiB and local-first execution; thesis/publication intent and GitHub-ready
  delivery; readable code/reports; experimental integrity; documentation-only phase.
  Pet/DTD, Chinese reports, public GitHub intent, 32GB RAM, approximately 500GB
  available disk, all-day GPU availability, October 31 code and December 31 draft
  targets are user-confirmed. Captioning is now mandatory. Scientific thresholds
  and institutional clearance remain unconfirmed.
- Before implementation: agree minimum scope, input/output and failure contracts,
  intended research question and baseline, engineering acceptance criteria,
  available resources and revised dates; obtain explicit implementation permission.
- Before a pilot: authorize scoped data/model acquisition and GPU work, establish
  applicable data-use/review requirements, and specify resource/stop limits and
  exploratory outputs. A pilot is not a retrospectively preregistered experiment.
- Before formal evaluation: version the complete protocol, resolve applicable
  advisor/institutional requirements with evidence, and record authorization.
  Fix the primary metric, comparator, coverage/resource constraint, acceptable
  tradeoff, repetitions and uncertainty analysis before inspecting test results.
- Before release/submission: check rights, authorship, AI disclosure, venue rules,
  traceability and presentation; obtain explicit release/submission permission.
  Code completion, thesis completion, submission and acceptance are distinct.
- Separate engineering acceptance from scientific hypotheses. Null/negative
  results must be preserved; never change metrics, data or stopping rules merely
  to manufacture success. Document post-result amendments as exploratory.
- Unresolved publication formatting need not block unrelated requested review
  work. No phase gate overrides the current prohibition on implementation.

## Outcome

Build a reproducible local visual-recognition agent suitable for a master's
thesis, publication submission and a GitHub-ready repository. The system must run on one NVIDIA RTX
3070 Ti with 8 GiB VRAM and must fail safely when a workload does not fit.

## Non-negotiable GPU safety rules

- Never use `device_map="auto"`, CPU offload, disk offload, an offload folder,
  or Windows shared GPU memory as a planned fallback.
- A model load must pass `GpuGuard.preflight` before importing or allocating the
  heavyweight model.
- The planning process ceiling is 6400 MiB (6.25 GiB). Preflight additionally
  requires 1536 MiB free AFTER estimated model use, beyond existing desktop use.
  This budget is not proof of an implemented allocator cap. Estimates must be
  labeled unmeasured until hardware tests establish them.
- Load at most one heavyweight model at a time. Explicitly release it before
  loading another model.
- Use inference mode for inference, not trainable forward passes. Bound image
  resolution, use batch size 1 by default and token bounds when relevant.
  Profile training and inference separately.
- If the budget cannot be satisfied, stop with a clear error. Do not silently
  move weights, KV cache, tensors, or optimizer state to CPU or disk.
- Model and dataset downloads require explicit user approval because they may be
  large, slow, or license-sensitive.

## Engineering quality

- Write reviewer-readable code: consistent names, explicit types and units,
  small modules, public input/output contracts and documented failure conditions.
  Explain research assumptions and method choices; map paper algorithms and
  experiment settings to implementation modules.
- Separate data preparation, model adapters, routing, evaluation and reporting.
  Avoid hidden thresholds, duplicate defaults and notebook-only execution.
  Document commands that reproduce every formal table and figure.

- Keep orchestration framework-independent and typed. Prefer small modules with
  explicit inputs and outputs over hidden global state.
- Add or update tests for every behavior change. Run the most relevant unit
  tests, then the full test suite when practical.
- Record experiment configuration, random seed, model revision, dataset split,
  latency, peak VRAM, and result metrics.
- Never commit datasets, model weights, secrets, caches, or generated runs.
- Preserve raw evidence outside Git with backups; ignored does not mean disposable.
  Publication-safe figures and summaries may be released separately only with
  provenance, rights checks and user authorization.
- Do not broaden the thesis scope beyond image classification, confidence-aware
  routing, verification, abstention, and short image descriptions unless the user
  explicitly approves further expansion. The classification research and caption
  engineering evaluation must remain separate.
- Do not add a dependency unless it has a concrete use and its license is
  compatible with a public research repository.

## Experimental protocol and research integrity

- Before formal evaluation, version hypotheses, baselines, data splits, seeds,
  training/tuning budgets, checkpoint selection, calibration, routing thresholds,
  metrics, statistical analysis, exclusions and stopping rules.
- Keep train, calibration, routing-validation and test roles distinct. Never tune
  prompts, preprocessing, thresholds or checkpoints from test outcomes. Check exact
  and near duplicates and related samples across splits. Document unknown overlap
  with foundation-model pretraining; do not claim its absence without evidence.
- Freeze test manifests and label vocabulary. Verify IDs, targets and counts for
  every method. Never silently omit OOMs, corrupt images, timeouts, abstentions or
  failed runs; report exclusions and denominators explicitly.
- Disclose supervision, pretrained weights, tuning budgets and hardware conditions
  for fair comparisons. Report coverage alongside selective accuracy. Distinguish
  cached decision replay from measured end-to-end latency and memory.
- Preserve run IDs, code commit and dirty state, dependency versions, dataset/split
  hashes, model revisions, all settings, seeds, per-sample predictions, errors,
  resource measurements and logs needed to reconstruct reported values.
- Never fabricate data, measurements, references, significance or approvals.
  Label synthetic fixtures, mock results and illustrative plots clearly and keep
  them separate from thesis evidence. Preserve negative and null results.
- Do not cherry-pick seeds, classes or examples. Define repetitions and uncertainty.
  Post-result changes need a dated amendment, rationale and exploratory label;
  retain earlier protocols and results rather than rewriting history.
- Verify citations against primary sources; credit papers, reused code, datasets
  and models and retain licenses/attributions.
- Keep an AI-assistance record of tools, tasks, substantial generated contributions
  and human verification. The author must understand and verify code and claims;
  AI output is not empirical evidence. Follow actual institution/venue disclosure
  rules, and never assert automatic ethics compliance.
- Document provenance, permissions and personal/sensitive information. Additional
  private images, scraping, human-subject collection or user studies need separate
  scope and applicable review/consent checks before proceeding.

## Publication-quality figures, tables and reports

- Generate formal results from traceable artifacts using versioned reporting code;
  never manually change measurements for appearance or a preferred conclusion.
- Use consistent names, colors, fonts, precision and ordering. Label axes, units,
  sample sizes, splits, seed aggregation, error bars and abbreviations accurately.
  Distinguish standard deviations from confidence intervals.
- Use legible, color-accessible and grayscale-distinguishable styles. Avoid 3D
  decoration and misleading scales or undisclosed axis truncation. Match venue
  dimensions and vector/raster format or DPI; retain underlying numeric tables.
- Every figure/table needs a caption with relevant limitations, run/configuration
  provenance and a regeneration command. Mark qualitative/synthetic examples.
- Render and inspect at intended publication size for clipping, overlap, illegible
  text and inconsistent legends. Formatting must not change underlying results.

## Definition of done for a code change

- Acceptance criteria are satisfied.
- Tests pass, or the exact unavailable dependency is reported.
- GPU-affecting changes include a memory-budget check and failure behavior.
- Public APIs and non-obvious safety decisions are documented.
- `git status` contains no secrets, data, weights, or unrelated files.
- Experimental/reporting changes require run-to-table/figure traceability and
  checks of completeness, split integrity, denominators and reproducibility.
  Unit-test success alone does not establish a scientific claim.
- During review-only work report what was examined/edited and what is unverified.
  Never describe plans as implemented or measured features.

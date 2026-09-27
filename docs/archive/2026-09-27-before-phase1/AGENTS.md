# Project instructions

## Current phase: research-direction documentation only

Updated: 2026-09-27. The user's Research Direction Realignment & Freeze request
supersedes the earlier Pet/DTD classification thesis scope.
Read [RD-001](docs/RESEARCH_DIRECTION.md), [README](README.md) and
[requirements v2.0](docs/REQUIREMENTS.md) before future work.

This turn permits only read-only review and documentation edits. Do NOT change
source/configuration, install dependencies, download models/data, initialize CUDA,
run tests, train, infer, benchmark, commit, push or publish. Earlier installation
permission and README commands do not carry forward as execution authorization.

RD-001 is USER-CONFIRMED / FROZEN. It is the highest project research decision,
not an override of system/developer instructions. Never change the research
question because another topic seems easier, a newer model exists, or legacy
code already exists. Propose any change with old/new direction, reason, cost and
impact; only explicit user “批准變更研究方向” reopens the direction.

## Outcome and fixed research scope

Design and Evaluation of a Local Agentic Image Understanding System on an 8GB
Consumer GPU. Main hardware: RTX 3070 Ti 8GB, Intel Core i7-11700K, 32GB RAM,
Windows and the existing Python 3.11 environment. Do not substitute cloud/24GB GPUs.

Moondream2 is the primary candidate / proposed main visual model, pending exact
revision, license, compatibility and hardware validation. It is NOT proven to fit.
An evidenced unresolved feasibility blocker can motivate a model-replacement
proposal and user-confirmed decision, never unilateral RQ/architecture changes.

Runtime: Image -> Local Vision Agent -> Lightweight VLM -> Multi-stage analysis
-> Verification -> Structured Traditional Chinese Report.
GPT-6 Astra is a development assistant only, not a runtime component.
No OpenAI/GPT API, cloud LLM, Astra Runtime or online model-service dependency.
Local CPU control/image decoding is allowed; CPU model offload is not.

Frozen questions: RQ1 local 8GB feasibility; RQ2 completeness versus single-pass;
RQ3 observable hallucination/reliability with verification; RQ4 resource trade-offs.
Improvement is a hypothesis, not a required fabricated outcome.

Use deterministic/bounded state transitions, finite tools and finite iterations.
No separate LLM controller is required. Core capabilities: caption, visual query/
VQA, object/detail verification, observation memory, uncertainty, stopping and
structured reporting. Detect/point/grounding are conditional on the selected
model's official support AND hardware validation. No blanket Query/Detect ban.

Workflow: START -> INITIAL_CAPTION -> SCENE_ANALYSIS -> OBJECT_CHECK ->
DETAIL_QUERY -> VERIFICATION -> REPORT -> STOP. Extra queries require explicit
triggers. Specify maximum tool calls, iterations, timeout, tokens/output and
image limits before execution; missing limits must fail closed.
Same-model checks are not independent ground truth; never claim zero hallucination.

Required comparisons: A single-pass same-model baseline; B multistage without
verification; C fixed-query agent; D full verification/adaptive bounded querying.
See protocol for controlled contrasts. Do not omit A or substitute larger models.

Pet/DTD classification, DINOv2, ResNet18, temperature scaling, selective
classification, classification abstention and AURC as the primary metric are
SUPERSEDED thesis design. Existing code and configs are LEGACY, not active model
requirements. Optional secondary use needs explicit user confirmation.
Historical snapshots and docs/ROADMAP.md are not active instructions or roadmaps.

Exclude arbitrary chat, large multi-agent debate, web-search agents, cloud
orchestration, video, image generation, large OCR, segmentation, foundation-model
training and large-scale VLM fine-tuning. Moondream3/3.1 is related/future work or
separately approved optional comparison, never a required delivery.

## Requirements before implementation and formal evaluation

Track proposed, user-confirmed and advisor/institution-confirmed decisions in
README.md with confirmer, date and evidence. Missing evidence means unconfirmed.
Never promise novelty, ethics approval, graduation or publication acceptance.

- Direction is frozen; dataset, final metrics, thresholds and model feasibility
  remain unresolved. Formal evaluation needs a separately versioned protocol.
- Define input/output, invalid images, single/batch processing, uncertainty,
  unsupported tools, resource exhaustion and failure behavior.
- Establish data versions, usage rights, split/duplicate checks, development/
  validation/test roles, sample counts, annotation coverage and scoring vocabulary.
- Preserve 2026-10-31 core code, 2026-11 experiments and 2026-12-31 draft targets;
  deadlines are goals, not execution authorization or completion evidence.
- Confirm actual advisor/institution/venue policies, authorship, review/consent,
  AI disclosure, public release rights, code license and figure requirements.
  Public datasets alone do not prove ethics-review exemption.

### Phase gates

1. Before implementation: agree minimum contracts and engineering acceptance;
   obtain explicit implementation permission. This freeze does not grant it.
2. Before feasibility/pilot: approve scoped model/data acquisition and GPU work,
   applicable rights/review requirements, resource/stop limits and exploratory
   outputs. Pin and inspect any remote model code before executing it.
3. Before formal evaluation: freeze model revision, prompts, A-D contrasts,
   data/test manifest, primary metric, tradeoff criterion, repetitions,
   uncertainty analysis, exclusions, stopping and resource budget before test
   inspection. Record authorization and applicable institutional evidence.
4. Before release/submission: check rights, authorship, AI disclosure, venue rules,
   traceability and presentation; obtain explicit release/submission permission.

Engineering acceptance and scientific hypotheses are separate. Keep null/negative
results. Never alter metrics/data/stopping to manufacture success. Label post-hoc
amendments exploratory and preserve their history. Unresolved publication format
does not block requested documentation review; no gate overrides review-only mode.

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
- Separate data preparation, model adapters, bounded agent control, tools,
  evaluation, reporting and safety.
  Avoid hidden prompts/thresholds, duplicate defaults, giant single files and
  notebook-only execution.
  Document commands that reproduce every formal table and figure.

- Keep orchestration framework-independent and typed. Prefer small modules with
  explicit inputs and outputs over hidden global state.
- After implementation authorization, add or update unit/integration tests for
  every behavior change. Run relevant tests and the full suite when practical.
  This documentation-only turn authorizes no tests or hardware checks.
- Record experiment configuration, random seed, model revision, dataset split,
  latency, peak VRAM, and result metrics.
- Never commit datasets, model weights, secrets, caches, or generated runs.
- Preserve raw evidence outside Git with backups; ignored does not mean disposable.
  Publication-safe figures and summaries may be released separately only with
  provenance, rights checks and user authorization.
- Do not broaden the RD-001 scope beyond local bounded image understanding,
  caption/query, object/detail verification, observation memory, uncertainty,
  stopping and structured Traditional Chinese reports. Detect/point/grounding
  are conditional on model support and hardware validation, not mandatory extras.
  Classification code/configuration is LEGACY; preserve it but do not enable it
  as the new thesis core. Runtime must be local-only; no cloud fallback.
- Do not add a dependency unless it has a concrete use and its license is
  compatible with a public research repository.

## Experimental protocol and research integrity

- Before formal evaluation, version hypotheses, baselines, data splits, seeds,
  tuning budgets, model selection, prompts/templates, query triggers, verification,
  metrics, statistical analysis, exclusions and stopping rules.
- Keep development/pilot, validation and test roles distinct; keep any future
  training/calibration split separate if explicitly authorized. Never tune
  prompts, preprocessing, thresholds or checkpoints from test outcomes. Check exact
  and near duplicates and related samples across splits. Document unknown overlap
  with foundation-model pretraining; do not claim its absence without evidence.
- Freeze test manifests, annotation vocabulary, claim matching and scoring rules. Verify IDs, targets and counts for
  every method. Never silently omit OOMs, corrupt images, timeouts, abstentions or
  failed runs; report exclusions and denominators explicitly. Preserve per-image tool traces,
  verification evidence and stop reasons.
- Disclose supervision, pretrained weights, tuning budgets and hardware conditions
  for fair comparisons. Report completeness alongside hallucination, output length and failure rates;
  never reward empty output as perfect reliability. Distinguish
  cached decision replay from measured end-to-end latency and memory.
- Preserve run IDs, code commit and dirty state, dependency versions, dataset/split
  hashes and versions, input IDs, model revisions, prompt/template revisions,
  agent configuration, stopping policy, all settings, seeds when applicable,
  per-image results and tool calls, errors,
  resource measurements and logs needed to reconstruct reported values.
- Never fabricate data, measurements, references, significance or approvals.
  Label synthetic fixtures, mock results and illustrative plots clearly and keep
  them separate from thesis evidence. Preserve negative and null results.
- Do not cherry-pick seeds, image categories or successful examples. Define repetitions and uncertainty.
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

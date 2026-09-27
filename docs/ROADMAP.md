# Historical roadmap — SUPERSEDED / NOT ACTIVE

Retained for historical traceability only. The whole plan below is SUPERSEDED,
including its scope, exclusions, model choices and dates. It grants no execution
permission and is not evidence that any milestone was completed.

Current frozen direction: [RD-001](RESEARCH_DIRECTION.md), 2026-09-27.
Current requirements: [v2.0](REQUIREMENTS.md).
The ONLY active roadmap is [DELIVERY_PLAN v2.0](DELIVERY_PLAN.md):
2026-10-31 code, 2026-11 experiments, 2026-12-31 thesis draft.

Local bounded caption/query/verification replaces the old classification thesis.
Detect/point are conditional capabilities under RD-001; the historical detection
exclusion below does not apply to the current design. No extra LLM controller
is required; Astra is development-only. Current phase: documentation only.

---

# Four-month delivery plan

## Scope freeze

The thesis implementation covers image classification, confidence-aware tool
routing, verification, abstention, and resource measurements. Detection,
segmentation, image generation, source-generator attribution, and multi-agent
debate are excluded from the initial scope.

## Milestones

### 2026-09-14 to 2026-09-27: reproducible baseline

- Install a project-owned Python environment and a stable CUDA-enabled PyTorch.
- Verify CUDA without downloading a model.
- Add dataset manifests and deterministic splits.
- Run a small CLIP smoke test only after download approval.

Exit criteria: tests pass, CUDA is verified, and one image can be classified
without CPU or disk offload.

### 2026-09-28 to 2026-10-18: baseline experiments

- Add CLIP zero-shot, ResNet18, and DINOv2-small adapters.
- Record metrics, latency, peak VRAM, seeds, and model revisions.
- Produce repeatable CSV/JSON experiment outputs.

Exit criteria: every baseline runs from a documented command and produces a
machine-readable result.

### 2026-10-19 to 2026-11-08: agent routing

- Connect the confidence router to real model adapters.
- Add verifier disagreement handling and abstention.
- Add a minimal local interface after the command-line path is stable.

Exit criteria: the agent chooses, verifies, or abstains deterministically from a
recorded configuration.

### 2026-11-09 to 2026-11-29: frozen experiments

- Compare fixed models, fixed ensemble, and the dynamic agent.
- Run two ablations: no routing and no verification.
- Freeze code, data splits, model revisions, and result tables.

Exit criteria: all thesis tables can be regenerated from committed code and
uncommitted local data.

### 2026-11-30 to 2026-12-20: thesis and defense material

- Write methods, implementation, experiments, limitations, and conclusions.
- Generate diagrams and tables from frozen experiment outputs.
- Reserve the final days for corrections rather than new features.

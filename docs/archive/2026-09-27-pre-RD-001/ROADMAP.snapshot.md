# SUPERSEDED snapshot — 2026-09-27 before RD-001

Historical record only; not active instructions, requirements or execution authorization.
Original path: `docs/ROADMAP.md`. Original text follows unchanged (line endings may be normalized).
Active direction: [RD-001](../../RESEARCH_DIRECTION.md).

---

# Historical roadmap — superseded

The schedule below is retained as history only. Current scope and deadlines are
in REQUIREMENTS.md v1.1 and DELIVERY_PLAN.md v1.1. Short Traditional Chinese image
descriptions are now mandatory; CLIP, EuroSAT and an LLM controller are not.
Current authorization is documentation only: no code, downloads or CUDA work.

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

# Formal experiment design v1 — 2026-10-01

**FORMAL EXPERIMENT DESIGN = DRAFT READY FOR AUTHOR REVIEW**

DESIGN/FREEZE ONLY. The choices below are the single prospectively selected v1 proposal,
locked within this draft; they are NOT author-approved execution authorization or a
completed preregistration. No formal images inspected/run or datasets downloaded this
phase. Author acceptance, materialized manifests, independent references and executable
scoring audit must precede formal execution. Changes require a dated v2 before test
outputs, never an overwritten v1 or post-result optimization.

## Package and fixed questions

[Methods/prompts/budgets](FORMAL_METHODS_ABCD.md), [data and human annotation](FORMAL_DATA_PROTOCOL.md),
[claim units and metrics](FORMAL_METRICS.md), [sample size/statistics](FORMAL_STATISTICAL_PLAN.md),
[blocking decisions](FORMAL_OPEN_QUESTIONS.md), [engineering baseline](ENGINEERING_BASELINE_DECISION.md).
These develop, rather than retroactively freeze, [protocol v0.3](EXPERIMENT_PROTOCOL.md).

| RQ (RD-001 unchanged) | Planned evidence |
|---|---|
| RQ1: lightweight VLM as fully local Agent core on RTX 3070 Ti 8GB? | Completion, safety, resource and cleanup fields across all planned invocations |
| RQ2: multistage improves salient information completeness vs single caption? | Paired image-level salient-object recall, D−A |
| RQ3: verification reduces observable hallucination / erroneous / unsupported claims? | Independent truth of full raw claims and verifier-endorsed claims; B−D errors, false acceptance and lost correct content |
| RQ4: quality vs latency, VRAM, calls and computation? | Paired resource differences, joint quality/cost tables, failures included |

Hypotheses may be null or negative. A−D is workflow effect with extra computation;
B−D is verification contribution; C−D is adaptive versus fixed querying under a common
ceiling. It is not an equal-actual-compute experiment. No baseline change or model shopping.

## Common preprocessing: selected P1

Select **P1: existing smartphone-source-v1 -> single RGB BICUBIC 448×448 ImageNet tile**
for ALL A/B/C/D. Source decode/EXIF/RGB, aspect-preserving <=512 LANCZOS normalization
when needed, then square resize; exact implementation/hash from source
`bdf9dd2cb3b5657cf2e33a0efa5829b5b614c694`. No dynamic tiles or thumbnail.
This is an explicit resource-constrained system study, NOT a measurement of maximum
InternVL capability or reproduction of its official benchmark scores.

| Candidate | Intended-use fidelity / detail | VRAM, latency, visual tokens | Fairness / reproducibility / decision |
|---|---|---|---|
| P1 current square | Uses model's 448 tile/normalization; differs from general dynamic route, warps aspect ratio, discards small details during <=512 reduction | 1 tile, 256 visual context tokens from pinned config; tested development memory only, not all future inputs | Same deterministic bytes/tensor for all methods; selected for bounded previously demonstrated path |
| P2 letterbox 448 | Preserves geometry, introduces padding absent from current path; non-square content uses fewer pixels, tiny objects may shrink further | 1 tile/256 tokens, similar tensor size, actual memory/time unmeasured | Common policy could be fair; fill color/interpolation would require new freeze and feasibility; not selected |
| P3 official dynamic tiling | Better matches official multi-tile route and may retain detail; not guaranteed more accurate | Variable tiles/visual tokens, extra encode/KV cost; no 8GB proof, can exceed current 1024 input-token bound | Requires exact grid/max_tiles/thumbnail and new resource study for all methods; not selected, not implemented |

Official example uses dynamic 448 crops and optional thumbnail; pinned config has
patch size 14 and downsample ratio .5: (448/14)^2×.5^2 = 256 tokens/tile.
This arithmetic is a configuration fact, not a new hardware measurement.
[Official model card](https://huggingface.co/OpenGVLab/InternVL3-2B-Instruct), also retained
locally at the pinned revision in `artifacts/internvl3-20260928/upstream/instruct/`.
No additional feasibility needed to choose the unchanged P1 operating point. If the
author instead requires P2/P3, STOP and propose a separately authorized bounded pilot;
never claim this draft has tested those alternatives. Independent annotation records
both original-visible and model-tile-visible objects to expose preprocessing loss.

## Common generation: selected G128

Select existing **128 new tokens/call**, **1024 total generated tokens/image/method**;
no prompt shortening, no resumption of truncated sentences, no translation/OpenCC.
Greedy do_sample=false, temperature=0, num_beams=1, use_cache=true, seed=0;
actual pinned EOS/pad/template and rendered token IDs retained. Same library for all methods.

| Candidate | Prospective trade-off | v1 decision |
|---|---|---|
| 128 | Known bounded path; truncation may penalize long descriptions and A completeness; limits claim volume and runtime | Selected, truncation is measured, never hidden |
| 192 | Could reduce truncation, but more latency/KV/claims, fewer affordable checks per content unit; not measured | Not selected; current runtime rejects >128 |
| 256 | More output capacity, potentially more hallucinated claims and verification backlog; not proven within timeout/resource path | Not selected |
| Shorter prompt | Could constrain content and change all contrasts; requires a new exact library | Not selected; no development-photo tuning |

Selection prioritizes a reproducible bounded engineering operating point, not the answer
quality of two development photos. Equal per-call ceilings do not equal equal total
opportunity: A has one response, B/C/D have more; report length, truncation and actual tokens.
No silent increase after viewing formal results. Conclusions apply to G128/P1 only.

## Formal RQ1/RQ4 measurement contract

Each image×method has fresh worker, one load, persistent model within its calls, no cross-
method/image memory or feature-cache reuse. Same sequential hardware, offline guards,
resource policy and clean recovery. Record Python/OS/driver/library/assets hashes,
source/config/manifest/protocol SHA, HEAD/dirty state, ordering, timestamps, run/input IDs.

Save source dimensions/bytes/hash, oriented dimensions, normalized hash/dimensions,
conversion and final tile policy; input rejection count; CPU source-preprocessing time
as a separate field when instrumentation exists (currently not separately measured).
Record wall-clock monotonic load, source preprocessing, model preprocessing, individual
calls, Agent time, cleanup, end-to-end through cleanup, total invocation through report
persistence. GPU-synchronized timing boundary must be identical for methods; do not add
unsynchronized GPU intervals or substitute replay time. Existing timing-boundary audit
and any missing CPU instrumentation are pre-execution blockers, not implemented here.

Record max allocated/reserved MiB after reset, sampled device total used/free/baseline,
sampling cadence and missed samples. Device use includes desktop; not process attribution.
Record all calls/tokens/truncation, OOM, timeout, parse/transport/input errors, safety
refusals, partial states and unattempted tasks. Completion = valid bounded report AND
safety/cleanup success; budget-unresolved completion counts but is separately tabulated.
Cleanup requires allocator allocated/reserved zero, worker exit0, Job empty and device
baseline-equivalent within existing64MiB tolerance. Stop the execution block on a safety
failure; no retries. Block approval is separate from this design; never erase denominators.

Formal feasibility is reported as observed rates/CIs and resource distributions, not a
universal guarantee or a new arbitrary success threshold. The prior development run
strongly supports tested-path feasibility but is never pooled into formal measurements.
No energy/FLOPs claim without instrumentation; calls/tokens/time are cost proxies.

## Freeze and authorship gate

400 paired formal images, 40 disjoint design/rubric images, one invocation/method/image;
see statistical plan for precision rationale and workload. All remain prospective.
Author must approve the six-document package, rights/splits, human rubric and practical
workload; then authorize acquisition/manifests and offline scoring preparation separately.
A final signed manifest/config/prompts/scoring-code hash bundle is required before any
formal run. No institutional/advisor/ethics approval inferred. No publication authorized.
AI assistance: Codex drafted this package and audited retained files on 2026-10-01;
author supplied the only development semantic judgment. AI is not a runtime or judge.
10/31 code, 11/1 engineering acceptance, November experiments, 12/31 draft remain goals,
not promises. Feature freeze and no-more-development-GPU remain in force.

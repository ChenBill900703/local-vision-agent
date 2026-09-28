# InternVL3 capability coverage — prospective amendment, 2026-09-28

**PILOT / EXPLORATORY / NOT FORMAL THESIS RESULT**

User authorization: resume / Adoption Gate / conditional Real Agent Integration request,
retained at artifacts/internvl3-capability-20260928/evidence/user_authorization.txt.
This permits ONE new bounded session. The initial run is immutable and never rerun.
No model shopping, download, dependency changes, quantization, offload or formal testing.

## Resume audit before modifications

Branch main; HEAD cb171216dac7f7fd99aa6b9a2776de4bd1311af4. Previous phase's dirty
source/docs/tests preserved.75 CPU tests PASS(3.216s), Ruff PASS, strict Mypy21 PASS.
22 pinned asset entries and134 backup entries hash-verified. Current21 source hashes
matched initial-run provenance. Only existing InternVL run: INTERNVL3_INITIAL_GPU_PILOT.
Audit JSON records full dirty state and initial file hashes; prior handoff/README/AGENTS saved.

## Execution safety and semantic evaluation are separate

Historical `internvl_policy.probe_gate` is unchanged. New `capability_gate` is a separate
contract. It accepts any wording/language/semantic content if the response decodes,
is a nonempty string, has a valid completed transport receipt, no exception, a healthy
worker, and respects input/output/call/image/session/time/memory limits. Invalid Unicode,
replacement characters and malformed schemas are rejected; raw data/errors still saved.
No whitelist of English/Chinese words, color/shape pairs, truth or phrase matching.
Incorrect or uncertain but valid text also passes execution safety and goes to human review.

Parent additionally checks worker PID, allowed event transitions, the exact five operations
and fixed prompts, deadlines, telemetry, and zero allocator cleanup. Worker and parent
both validate completion receipts. No semantic result controls further probes.
All five calls run in order unless an engineering/security/resource failure occurs.

Before GPU: tests cover left/right/了, varied and incorrect wording, empty/malformed
output, decode/model/worker failures, timeout, all budgets, unexpected transport and a
real Windows CPU persistent-worker five-call success / forced-timeout cleanup. Full CPU
suite, Ruff, strict Mypy must pass. CPU fixtures are never model-recognition evidence.

## Fixed runtime

OpenGVLab/InternVL3-2B-Instruct model/tokenizer/config/template revision
`f6c7b60375759170fd49f5e9e298e2178485c5ba`; weights SHA256
`b69fcfb5cd97b91b52022642d88da91201487aa73750fa8b14a0e6591a5a9e2d`.
Existing local assets and controlled patch reused, never fetched or modified.
Python3.11.9, torch2.7.1+cu126, torchvision0.22.1+cu126, Transformers4.57.6 unchanged.
Same worker / CUDA lifecycle / tokenizer / internvl2_5 system template and image path.
Batch1, BF16, eager, cuda:0, one heavyweight model, one load, no retry or fallback.
Offline flags + Python network-denial audit active before heavy imports, same observability
limitations (not OS firewall proof, shared-memory spill UNKNOWN).

Original384x256 synthetic fixture hash
`7a902b90e90b2c89ff91cd78a23f5a8b9d42bb4ca15a24775736ee9afb1d463f`.
One448x448 RGB BICUBIC tile and existing normalization; no thumbnail. Aspect ratio
distortion remains a declared limitation, unchanged for this coverage pilot.

Estimate6000MiB; process ceiling6400MiB; dedicated reserve1536MiB; allocator cap5400MiB.
GpuGuard preflight before heavy imports, same post-init check and dedicated-memory sampler.
Source limits512edge/262144pixels/10MiB; input<=1024tokens; output<=128tokens/call;
existing caps8calls/image,1024outputtokens/image,3images,24calls/session, but this protocol
allows exactly ONE image and at most FIVE calls. No real-image run is included here.
Load180s/call60s/image300s/cleanup10s/session1800s; no increase after a failure.
Greedy temperature0, do_sample=False,num_beams1,max_new_tokens128,use_cache=True;
same EOS/pad and model BOS defaults. Fresh KV per query; real visual extraction each call.

## Fixed prompts and order

1. control: `What shapes are in the image, and what color is each shape?`
2. scene: `這張圖片主要是什麼場景？`
3. objects: `請列出畫面中明顯可見的主要物件。`
4. detail: `背景中還有哪些明顯且可以確認的物件？`
5. verification: `敘述：圖片中有紅色正方形。請重新檢查圖片，這個敘述是否能由圖片直接支持？若不能確定，請明確說無法確定。`

No prompt variations, extra probes or post-output edits. No Chinese-output suffix added
to the four user-fixed prompts. Control correctness also goes to post-run human review.

## Post-run rubric and adoption

Researcher HUMAN review, not GPT/cloud judgement. Save unmodified text and a blank
review record to be completed by the user/researcher AFTER all calls and cleanup.

| Item | Usable criterion |
|---|---|
| Control | Correct red square / blue circle; confirms visible query route |
| Scene | Simple/geometric shape scene; no invented complex setting |
| Objects | At least red square and blue circle |
| Detail | No invented background objects; white background/no other obvious object reasonable |
| Verification | Reasonable support/yes for red-square claim |
| Chinese | Useful predominantly Traditional Chinese; wording need not match a template |

If human-reviewed capabilities/Chinese usable and technical gates/cleanup pass:
ADOPT INTERNVL3-2B-INSTRUCT AS PRIMARY VLM CANDIDATE (engineering/development only).
One small actual engineering blocker: CONDITIONAL PASS — ONE SMALL ENGINEERING BLOCKER.
Genuine model/hardware/security blocker: REJECT INTERNVL3-2B. Human review missing is
PENDING REVIEW, not an invented reject/conditional/adopt verdict. No human result fabricated.
Only after ADOPT may the authorized adapter/Agent implementation begin; local adoption
checkpoint first. No extra GPU session inferred from implementation permission.

## Evidence and cleanup

New exclusive run: INTERNVL3_AGENT_CAPABILITY_PILOT_20260928, under existing asset root
artifacts/internvl3-20260928/runs/. Old run path never reused. Preserve source snapshot,
model/tokenizer/config hashes, exact/rendered prompts, raw responses and token IDs/counts,
latency visual/generation/total, allocated/reserved peaks, CUDA/NVIDIA free, stop reason,
worker status, warnings, exceptions, parent trace and before/after hardware state.

Require references released, workspace/cache cleanup, allocated=reserved=0, worker exit,
Windows Job empty. Record device baseline and after-exit usage; baseline-equivalent means
within64MiB device-wide desktop fluctuation AND reserve maintained, with model process
gone; any larger unexplained residual is a blocker, not automatic acceptance. This does
not relax zero allocator requirements. No cleanup retries or lower acceptance after data.

Initial reports/amendment/raw data/old lexical gate preserved byte-for-byte; verify again
after run. Backup new evidence separately without copying large weights. No public release.
Real-image sanity awaits up to2 user-provided rights-confirmed nonsensitive development
images; no formal dataset or unapproved image acquisition. Final preprocessing/tiling
policy remains a research gate before A–D freeze, identical for all four methods.

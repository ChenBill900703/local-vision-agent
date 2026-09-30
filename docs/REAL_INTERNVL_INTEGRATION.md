# Verification update — 2026-09-30

The unchanged integration at c2ce0b24a61c257db9cdc232f45dd4c95e30521f now has one actual
Method D GPU end-to-end smoke PASS on the original synthetic fixture. Six actual calls,
linked trace/Chinese report, placement/offline/budget/zero-cleanup/process recovery PASS.
See [result](REAL_INTERNVL_AGENT_GPU_SMOKE_RESULT.md). No real-image sanity yet; this does
not validate RQ2–RQ4 or all conditional branches. GPU allowance consumed; no further run.
The implementation/CPU-stage record below is preserved as historical evidence; its NOT RUN
statements describe the state before this separately authorized smoke.

# Real InternVL adapter and bounded Agent — development implementation

Implemented 2026-09-28; CPU closeout 2026-09-29. **DEVELOPMENT ONLY / NOT FORMAL THESIS RESULT**.
Implementation starts AFTER human-confirmed [ADOPT](INTERNVL3_ADOPTION_DECISION.md) and
clean local adoption checkpoint `580d0a92c529b0e4aca692b658ca77d675a4678c`.
No push, new weights/dependencies, model shopping or formal experiment.

## What is implemented and what is measured

| Component | Implementation | Verification this phase |
|---|---|---|
| Pinned InternVL backend | Actual local CUDA model loader and inference, no mock fallback | Ported from reviewed pilot path; new wrapper not GPU-executed |
| Adapter | load/unload/caption/query/invoke/health, metadata/trace/errors | CPU unit + process integration fixtures |
| Persistent worker | One model load, one image, multiple bounded calls, explicit unload/exit | Windows CPU processes: success, failure, malformed reply, timeout and cleanup |
| Agent A–D | Existing decision flow connected through VisionAdapter/Executor | CPU fixtures for all four methods, adaptive branches and fresh memory |
| Chinese report/trace | Raw response preserved, literal candidate claims, status/evidence links | CPU fixtures; real model Chinese proven in two pilots only |
| Real capability pilot | One load, control + four fixed probes | GPU/offline/cleanup PASS; user HUMAN semantic review PASS |
| New adapter end-to-end GPU | Ready for a separately scoped smoke gate | NOT RUN; capability GPU allowance consumed |
| Real-image sanity | Optional <=2 rights-confirmed development images | NOT RUN; no suitable user images supplied |

The original and capability pilots remain immutable. New implementation tests are not
new GPU runs and cannot retroactively validate the new RPC/backend end-to-end path.

## Public boundary and lifecycle

`InternVLAdapter(asset_root, evidence_directory, RuntimeConfig)` implements the existing
VisionAdapter contract and serves as its bounded Executor. Explicit methods:

- `load()` starts one owned worker, performs guarded load and returns runtime metadata.
- `begin_image(ImageInput)` validates bytes/hash/size and logs versioned preprocessing.
- `caption()` / `query(prompt, prompt_id=...)` / `invoke(Request, ImageInfo, timeout_s)`
  return the typed Answer contract. Only caption/scene/object/detail/verify tool IDs.
- `health()` reports process state, loaded/failure state, calls and watchdog failure.
- `unload()` requires zero allocator cleanup, process exit, empty Job and device recovery.

No caller can transparently fall back to MockAdapter. Mock CLI/config remain explicitly
separate. Agent only uses public adapter identity/capabilities/invoke; model/tokenizer/KV
internals stay behind the adapter. All imports remain CPU-only until backend preflight.
Real Agent refuses a nonloaded or mismatched executor/config. Real adapter processes one
image only; use a fresh explicitly invoked lifecycle for another image, with fresh memory.

START WORKER → guarded load once → validated image → multiple bounded requests → report
→ unload/allocator check → worker exit. No per-query reload and no Moondream co-load.
JSON IPC contains finite operation names, sequence IDs and data; no pickle, arbitrary
class deserialization, shell/tool execution from model output or cloud calls.
Windows Job owns actual Python PID and descendants. Watchdog independently monitors
GPU reserve/ceiling/telemetry and request/image/session deadlines, including idle gaps.
Parent validates replies and forces process-tree termination on failures. Model exceptions
and failed cleanup produce partial/failed reports; process exit alone never proves zero
allocated/reserved. Recovery/error evidence remains available after forced termination.

## Safety settings and provenance

`configs/agent_internvl_development.toml` requires every runtime/Agent limit. Missing,
unknown, invalid or above-pilot bounds refuse execution; no permissive defaults/offload.
Same pinned model/tokenizer/config/template revision
`f6c7b60375759170fd49f5e9e298e2178485c5ba`, BF16/cuda:0/eager, batch1, greedy generation.
Guard before heavy imports,6000MiB planning estimate/6400MiB ceiling/1536MiB reserve/
5400MiB allocator cap. Source/weights/framework hashes verified; dependency-version drift
refused before importing model frameworks. No automatic install or corrective download.
Existing offline flags and Python network audit apply; native-network/firewall proof is
not claimed. Windows shared-memory spill remains UNKNOWN / OBSERVABILITY LIMITATION.

Input<=10MiB/512edge/262144pixels; input<=1024 actual rendered tokens, output<=128/call,
8 calls/iterations maximum,1024 total outputtokens, one image/worker, bounded memory.
Load<=180s,call<=60s,image<=300s,cleanup<=10s,session<=1800s. Failure never retries.
Request output allowance is reduced by Agent's remaining total budget; backend rechecks.
No fixed prompt-byte proxy for real inference: tokenizer counts full system/image/text.

Each run directory is exclusive and cannot overwrite an existing run. Save exact config,
commit/dirty/source hashes, all rendered prompts/settings/token IDs/raw text, measurements,
worker status/stop reasons, parent trace, failures, cleanup and device recovery.
`agent_report.json`/`.md` and `normalized_trace.json` link observations to raw call IDs.
Normalized trace explicitly contains observation_id/state/request/raw_model_response/
extracted_claims/evidence_links; raw text is never silently translated or repaired.

## Versioned preprocessing and semantic limitations

`internvl-single-tile-rgb-bicubic448-imagenet-v1`: EXIF transpose, RGB, single448x448
BICUBIC tile, ImageNet mean/std, no thumbnails. Decode uses bounded bytes checked against
the validated hash before preprocessing, preventing file-change substitution.
This retains the pilot's aspect-ratio distortion. Tile count/shape/policy are logged.
**RESEARCH GATE: decide and freeze final preprocessing/tiling identically for A/B/C/D
before any formal comparison.** Do not silently change it for one method.

`literal-sentence-claims-explicit-verdict-v1` keeps up to4 unique literal sentence clauses
as candidate claims per response. These are not independently grounded/atomic facts.
Uncertainty or explicit contradiction/missing-detail wording produces bounded investigation
signals. This semantic normalization is DEVELOPMENT Agent control, never the execution
safety gate or adoption judge. It does not score accuracy or understand all paraphrases.
Cross-observation semantic contradiction detection and final claim vocabulary remain
research-design work before formal protocol freeze.

Verifier status only parses an explicit leading supported/contradicted/unresolved label
without conflicting labels; otherwise unresolved. Thus the pilot's plain restatement can
be HUMAN-reviewed as usable interface evidence while this conservative runtime parser
keeps that same wording unresolved. No fabricated automatic agreement/ground truth.
Nonverified real claims start unresolved, not accepted truth.

## A–D and adaptive behavior

The existing finite prompt library/decision transitions were not redesigned:
A one response; B adaptive investigation without verification; C fixed investigation +
verification; D adaptive investigation +verification. B/D share investigation; C/D share
verification. Uncertain/missing signals trigger object/detail queries; duplicate claims
link observations; no new detail evidence stops expansion. One finite query library,
no second LLM controller. Same model, generation, preprocessing, failure and reporting
policy across methods. All branches are bounded by calls/tokens/time/memory limits.

CPU process tests demonstrate different D call sequences for uncertain vs clear fixtures,
A exactly one invocation, B/D investigation identity, C fixed questions, no-new-evidence
stop and per-run memory reset. This is implementation behavior, not A–D quality evidence.

## Tests and reproducible commands

93 CPU unit/integration tests PASS(9.229s), strict Mypy28 modules PASS. Ruff final check
covers src/tests/scripts. Tests use explicit fake process/model responses and mock NVIDIA
snapshots, never real GPU initialization. Test real subprocesses/Jobs with one-load/multi-
query, forced timeout, idle image timeout, failures, bad reply IDs, nonzero cleanup and
cleanup timeout. Also config/dependency drift, preprocessing/hash safety, conservative
normalization, immutable run protection, import safety and A–D boundary integration.

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
$env:PYTHONIOENCODING = 'utf-8'
.venv/Scripts/python.exe -m unittest discover -s tests
.venv/Scripts/python.exe -m ruff check src tests scripts
.venv/Scripts/python.exe -m mypy src
```

The explicit execution entry is `python -m local_vision_agent.real_agent`; `--help` is
CPU-only. It requires config/assets/image/input-id/evidence-dir/method and explicit
`--authorize-development-gpu`. A CLI flag does not replace scoped user authorization.
Do not run it under the consumed capability allowance.

Next smallest stage: separately authorize ONE new adapter/Agent GPU smoke session on
the existing synthetic fixture, freezing run ID/method/call limits first. No download or
environment changes needed. Only then consider optional rights-confirmed real images.
No formal datasets/statistics, hypothesis confirmation, publication-rights claims or push.
10/31 core /11/1 engineering acceptance remain targets, not guaranteed delivery.

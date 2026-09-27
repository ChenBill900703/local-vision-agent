# Phase 2 repair1 amendment — 2026-09-27

PILOT / EXPLORATORY / NOT FORMAL THESIS RESULT

## Authorization and immutable history

After receiving the initial FAIL report and the explanation that another GPU attempt
needs renewed permission, the user instructed:「請繼續進行 盡量解決掉問題」.
This continuation authorizes the bounded blocker repairs and one verification attempt
described here, not open-ended retries. Preserve initial-pilot and its backup unchanged.
New run ID: repair1-pilot; exclusive directory creation again prevents automatic retries.
RD-001, model/tokenizer revisions, A–D, data scope and all safety ceilings remain unchanged.
No new dependencies, downloads, model, dataset, offload, compilation, training or release.

## Pre-result engineering changes and hypotheses

1. Replace status-file replace/read polling with JSONL pipe events. Persist raw events
   independently; reader thread must not block deadlines. Failure/EOF stops the worker.
2. Worker announces its actual PID and waits for GO before validation or CUDA. Parent
   assigns it to a Windows Job Object with KILL_ON_JOB_CLOSE and no breakaway, then sends GO.
   This handles Windows venv launcher/worker PID differences. Kernel job covers descendants.
   [Microsoft Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects).
3. NVIDIA sampling moves to a separate thread; samples older than 2 seconds fail closed.
   Operation/image/load/cleanup deadlines remain independent of telemetry events.
4. After deleting model references, explicitly clear cuBLAS workspaces, then empty the
   CUDA allocator. Existing torch 2.7.1 exposes `_cuda_clearCublasWorkspaces` in its local
   stubs. [PyTorch CUDA notes](https://github.com/pytorch/docs/blob/site/stable/notes/cuda.md)
   describe persistent cuBLAS workspaces with default 2*4096+8*16 KiB = 8.125 MiB.
   This matches the initial residue, but is only a causal hypothesis before measurement.
   Record allocated bytes before/after this call; retain strict zero-allocation acceptance.
5. Fixed upstream non-reasoning query appends suffix [3] twice. A separate controlled
   package introduces a single Boolean switch, defaulting to the original behavior.
   Original package stays untouched. False removes only the second suffix. Preserve
   source diff/hash and validate all artifacts before import. This is an exploratory
   local patch to the same fixed model, not a new upstream release or proven fix.

## Frozen diagnostic sequence (before viewing new outputs)

Use only the original 384x256 synthetic development fixture, same weights, same model
instance, same encoded image. temperature=0, top_p=1, max output=128 per call.

1. Encode once.
2. Native normal caption, first and warm (two calls).
3. Original double-suffix English query: `What shapes and colors are in the image?`
4. Original double-suffix Chinese query: `請只用繁體中文回答：圖片中有哪些形狀？它們各是什麼顏色？`
5. Single-suffix English query, same text as step 3.
6. Single-suffix Chinese query, same text as step 4.

Total seven calls including encode; <=768 generated tokens if all six text calls hit
128 tokens. One load, one image; original ceilings remain <=3 images,24 calls,30 minutes;
load180s/call60s/image300s/cleanup10s; input1024 tokens/call, output1024/image;
image512 edge/262144 pixels/10 MiB. Estimated6000 MiB, ceiling6400, reserve1536,
allocator cap5400. OOM/budget/timeout/exception stops; no automatic further attempt.

Compare raw strings for actual shape/color answers vs question echo. Presence of CJK
alone does not establish language quality. Keep all outputs, including failures;
no statistical inference, no prompt search, no model fallback, no claims of general quality.
No English-to-Chinese template substitution presented as model-generated Chinese.

## CPU acceptance before new GPU work

Pipe Unicode/large-event delivery with status-file replace denied; malformed/EOF refusal;
load/call/image/cleanup deadline state; full supervisor success and timeout with CPU fixture
worker; actual Windows Job termination of worker and descendant; handshake refusal;
workspace clear ordering with mock torch; extract and run reviewed query function with
fake tensor backend to verify exact single/double suffix lists. These are engineering
tests and cannot establish GPU cleanup or language success. Full suite and strict types required.

## Result

The one repair1 attempt completed: technical minimal feasibility PASS, overall
CONDITIONAL PASS because useful direct Chinese remains unresolved. Windows supervision
and allocator cleanup passed. See [separate result](PHASE2_REPAIR1_RESULT.md).
Do not overwrite initial FAIL report or reuse either run gate.

# Final Moondream2 language diagnostic — 2026-09-27 (pre-result amendment)

**PILOT / EXPLORATORY / NOT FORMAL THESIS RESULT**

User explicitly authorizes the LAST Moondream2 language diagnostic, not open-ended
prompt tuning. Run ID: `language-final-20260927`. Preserve initial-pilot and repair1-pilot
and all negative evidence unchanged. This amendment is written before execution.

Purpose: determine whether an English instruction elicits a useful Traditional Chinese
visual answer. Same `synthetic-shapes-v1` development image and original manifest/hash.
Same model `9a7d4024050840e001defacec2b00727e89149e6`, tokenizer
`35192e10a54e36eabe0a7cc57a2c1aab371cafc5`, BF16 dense weights, explicit cuda:0.
Use original reviewed controlled package (not repair1 suffix patch): upstream/default
double-suffix query behavior. Repair1 pipe/Windows Job/workspace cleanup controls retained.

## Frozen sequence

One persistent load, one encode, then exactly TWO query calls:

1. English control:
   `What shapes are in the image, and what color is each shape?`
2. English instruction requesting Traditional Chinese:
   `Answer the following question in Traditional Chinese only. Do not repeat the question. What shapes are in the image, and what color is each shape?`

No caption or other prompt. Temperature=0, top_p=1, reasoning=false, output<=128 tokens
per query, input<=1024. Total calls=3 including encode; output<=256 (within1024/image).
No translation, OpenCC, second model, cloud service, post-output prompt changes or retries.
Original safety limits remain: estimate6000/ceiling6400/reserve1536/allocator5400 MiB;
batch1,512edge/262144pixels/10MiB; load180s/call60s/image300s/cleanup10s/session1800s;
one load. Preflight, placement, no offload, offline and fail-closed rules unchanged.

## Frozen interpretation and stopping

English control PASS only if it correctly describes red square and blue circle.
Traditional Chinese PASS only if useful shape/color content is correct and predominantly
Traditional Chinese (e.g. 紅色正方形、藍色圓形); CJK presence/echo/report labels do not count.
PARTIAL: correct but mainly Simplified Chinese, mixed English/Chinese, or understandable
Traditional Chinese with apparent instability. FAIL: English-only, instruction/question
echo, wrong/no visual answer, malformed/unusable. Keep raw output without corrections.
One sample cannot measure stability across repeats; do not invent a stability statistic.

PASS -> KEEP MOONDREAM2; stop language testing; real adapter/Agent integration is NEXT phase.
PARTIAL -> NEED MODEL DECISION; stop tuning, no converter/translator.
FAIL -> MOONDREAM2 DIRECT TRADITIONAL CHINESE OUTPUT = REPRODUCIBLE BLOCKER;
recommend EVALUATE FALLBACK VLM, prioritizing OpenGVLab/InternVL3-2B-Instruct for a later
authorized evaluation. Do NOT download/load/integrate it now. A hardware/control failure
must be reported as an invalid language test, not fabricated evidence of language failure.

Save prompts, raw answers, token IDs/counts, revisions, settings, VRAM, synchronized latency,
cleanup, commit/dirty state and run ID. Record actual start timestamp in run evidence.
Create separate dated result and same-disk evidence backup, retaining all previous runs.
No install/download/commit/push/release. No additional language tuning after completion.

# Formal methods A/B/C/D v1 — 2026-10-01

DRAFT READY FOR AUTHOR REVIEW / DESIGN ONLY. Selected parameters are prospective;
no runtime changes or formal execution. [Design](FORMAL_EXPERIMENT_DESIGN.md).

## Common core and limits

OpenGVLab/InternVL3-2B-Instruct model/tokenizer/template revision
`f6c7b60375759170fd49f5e9e298e2178485c5ba`; weights SHA256
`b69fcfb5cd97b91b52022642d88da91201487aa73750fa8b14a0e6591a5a9e2d`.
Recheck weights digest against retained manifest at final execution freeze.
Controlled code patch `e9374e89a0a0668af5cdd56ebf43a170fd1ff47798a9027cbdc6223754654c95`;
runtime source `bdf9dd2cb3b5657cf2e33a0efa5829b5b614c694`.
BF16/cuda:0/eager/inference_mode/batch1; P1/G128 per design. Pinned local assets only.
Same Chinese presentation, no translator, report formatting makes zero model calls.
Each visual query has the same image/template and no accumulated chat history.

| Limit | Common value |
|---|---|
| Tool/model calls, iterations, observations, candidate memory | 8 each; never a ninth call |
| Output/call; total/image/method; input/call | 128; 1024; 1024 including rendered image/template tokens |
| Response characters | 8192 (existing validation includes extracted claim text) |
| Timeouts seconds: load/call/image/cleanup/session | 180/60/300/10/1800 |
| Original source | JPEG/PNG single frame; 32 MiB compressed, 32M decoded pixels, edge<=10000 |
| Normalized/internal input | <=10 MiB, <=262144 pixels, edge<=512; final single448 tile |
| GPU guard | 6000MiB planning estimate,6400MiB ceiling,1536MiB post-estimate reserve,5400MiB allocator cap |

GpuGuard before heavyweight import; one model; no offload/auto mapping/shared-memory
fallback/quantization. Missing settings or drift refuses before load. Existing dependency
versions and runtime manifest stay pinned. Total ceilings are maxima, not targets.

## Exact prompt library (verbatim)

```text
caption: 以繁體中文描述圖片的場景、重要物件與可見細節；不確定時明示。
scene: 以繁體中文描述可見場景，不推測不可見的背景。
object: 以繁體中文檢查重要物件；看不清楚的物件請標示未確定。
detail: 以繁體中文描述可見細節；不要推測看不見的屬性。
verify: 檢查候選敘述，回報 supported、contradicted 或 unresolved；非獨立真值：
```

Labels above are prompt IDs, not sent text. verify sends its exact prefix immediately
followed by the exact candidate string, no inserted space. Pinned conversation template,
image tokens, special-token checks, EOS/pad and actual token IDs are part of the freeze.

| Method | Investigation | Verification |
|---|---|---|
| A | caption exactly once; SINGLE_PASS | None, no hidden refinement |
| B | caption, scene, conditional object, conditional detail | None |
| C | caption, scene, object, detail in this fixed order | FIFO remaining budget, same as D |
| D | Exactly B's investigation | FIFO remaining budget, no feedback to investigation |

## Exact triggers and termination

Use current source `agent.py` and `internvl_contract.py`, not an unstated semantic planner.
Uncertainty is case-insensitive substring presence of: 不確定, 無法, 可能, 不明, 看不清,
矛盾, 不一致, uncertain, cannot, maybe. On non-object answers uncertainty adds missing
object; on object answers adds missing detail. Any of 細節不明, 背景不明, 缺少細節,
矛盾, 不一致 adds missing detail. `似乎` alone is not a trigger in this frozen policy.
Object runs iff caption or scene is uncertain or missing object (always for C).
Detail runs iff caption/scene is missing detail OR executed object is uncertain/missing
detail (always for C). At most one call for each ID; no loop seeking better answers.
After detail, unchanged exact-deduplicated runtime candidate count -> NO_NEW_EVIDENCE;
otherwise QUERY_SET_DONE. No detail -> NO_TRIGGER. State visits alone are not model calls.

Runtime candidate extraction remains literal split `[。！？\n]+`, strip, exact-string
unique first four clauses per answer, global FIFO exact dedup with evidence links and
max8 candidate entries. New ninth unique candidate raises MEMORY_LIMIT, preserving partial
observations; it is not silently dropped to make C complete. Intro fragments/conjunctions
remain a known engineering limitation. Independent formal claim annotation is separate
and uncapped (see metrics); no parser repair disguised as this design.

For C/D, capacity=min(8model,8tool,8iterations,8observation-memory)−calls_used, floor0.
Freeze first min(candidate_count,capacity) candidates once; verify in FIFO order.
C normally leaves4 slots, D leaves4–6 if investigation completes. No reserved report calls.
Unselected candidates are unresolved/null verification_id/reason verification_budget_not_available.
Tokens/time remain hard gates; remaining-call slots do not promise successful checks.
Verifier normalization accepts a leading single unambiguous supported/contradicted/unresolved
label (whitespace or . : ： 。 delimiter) with no competing label; otherwise unresolved.
No rewriting or correction-generation stage. Budget-limited report may complete normally;
execution failures remain partial/failed. Preserve actual model text and stop/truncation.
No retry, limit relaxation, follow-up after verification or model-written report.

## Interpretation of controlled contrasts

B/D have identical investigation rules; independent greedy executions can still differ on
GPU. Log full prefix equality and divergence; never replace D's measured run with B replay.
B−D verification attribution is strongest on matching investigation prefixes; report this
subset as descriptive sensitivity, all images remain the primary paired denominator.
C/D differ in fixed/adaptive investigation; same total ceiling means verification capacity
also changes. This is the effect of adaptive allocation, not query-selection quality at
equal check count. Report pre-verification coverage plus post-verification coverage/cost.
A/D includes additional calls and content opportunity, not pure intelligence gain.

Full raw report includes all claims even when verifier rejects them. Thus current system
cannot be presumed to reduce raw hallucination by editing. Independently evaluate the
raw surface and an explicitly labeled offline endorsement view; never present that view
as a newly implemented report filter. All methods retain raw answers, not just candidates.
A/B have no endorsed-by-verifier claims; their comparison view is raw investigation.
C/D endorsement view contains only propositions linked to model-supported candidates;
this selective view must always be paired with coverage/retention/empty-view rates.

Failures include input/guard/OOM/timeout/transport/malformed/memory-limit/cleanup errors.
A safety failure stops the block and leaves later slots NOT_ATTEMPTED; no automatic retry.
Non-safety bounded reports retain their exact status. Future runner must prove conformance
on CPU fixtures before separate formal authorization; this task adds no runner/features.

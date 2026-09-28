# InternVL3 candidate selection, static review and first-load decision

PILOT / EXPLORATORY / NOT FORMAL THESIS RESULT

## Checkpoint and authorization

Before InternVL source/config/acquisition: 71 CPU tests passed (2.704s), Ruff passed after
three non-behavioral legacy lint fixes, strict Mypy passed all 19 modules. Git checkpoint
`cb171216dac7f7fd99aa6b9a2776de4bd1311af4` (`checkpoint-moondream2-feasibility-complete`),
no push; clean state after checkpoint. Reports/ignored backups preserved. Diff check noted
only three historical generated-report trailing blank lines; not rewritten. Assets/caches/
raw runs/private-development ignored. Precommit status saved in artifacts/moondream2-checkpoint-20260928.
New full user authorization retained in artifacts/internvl3-20260928/evidence/user_authorization.txt.
Implementation amendment only: RD-001/RQ1–4/A–D/local8GB unchanged. No Agent integration.

## Distribution decision

| Aspect | -hf | -Instruct (SELECTED) |
|---|---|---|
| Full SHA | cb57a075cb75a2e6d1b668b128d48bb00ae321d2 | f6c7b60375759170fd49f5e9e298e2178485c5ba |
| Official lineage | Conversion of InternVL3-2B; native Transformers | Multimodal pretrain + SFT, explicitly NOT MPO |
| Equivalence | Card intends equivalence to InternVL3-2B, not Instruct | Different post-training checkpoint from default/MPO release |
| Architecture | Native InternVLForConditionalGeneration / Qwen2 | InternVLChatModel / InternVisionModel / Qwen2ForCausalLM |
| Language / vision | Qwen2.5-1.5B initial language component; InternViT-300M | Same dimensions, distinct trained weights |
| Processor/template | Native processor, Jinja ChatML | Official README dynamic tiling + torchvision transform; internvl2_5 conversation.py |
| Custom Python | Not required for native path | Five pinned Python files reviewed, imported locally after preflight |
| Weights bytes | 4,178,013,768 (NOT downloaded) | 4,177,999,192 (only selected acquisition) |

Both are conversational multilingual image-text-to-text distributions; neither is a bare
untuned LLM. However, checkpoint equivalence is NOT established: Instruct explicitly lacks
MPO while hf maps the default release. User's non-equivalence rule therefore selects
Instruct, not hf merely for convenience. No quality ranking is inferred from metadata.
Official [hf card](https://huggingface.co/OpenGVLab/InternVL3-2B-hf/tree/cb57a075cb75a2e6d1b668b128d48bb00ae321d2),
[Instruct card](https://huggingface.co/OpenGVLab/InternVL3-2B-Instruct/tree/f6c7b60375759170fd49f5e9e298e2178485c5ba).

Config, tokenizer, processor description, generation config and model code all use the
selected repo SHA. Qwen2 tokenizer JSON/BPE vocabulary, no separate floating tokenizer.
Chat template is the pinned conversation.py internvl2_5 entry; tokenizer Jinja is not used
to format custom chat. Config's stale path strings (32B/6B) are historical metadata:
actual config dimensions are text28x1536/12heads/2KVheads, ViT24x1024/16heads; do not load
their named paths. Exact weights header is verified before execution.

## License / local-use decision

Instruct README body and Python headers declare MIT; README metadata lists Apache2.0 but
also carries a qwen name/link to 72B. Actual 1.5B language base is Apache2.0 per its official
[LICENSE](https://huggingface.co/Qwen/Qwen2.5-1.5B/blob/main/LICENSE). The selected card's
body also explicitly names Apache2.0 for Qwen2.5. Preserve this inconsistency, not silently
relicense it. Both Apache2.0 and the referenced Qwen agreement grant local use; this bounded
academic use is reasonably supported. No 100M-user commercial service is involved.
Tokenizer/config are supplied with the selected official release; same usage evidence,
not a claim that all packaging has one unambiguous redistribution license.

Pinned official MIT (OpenGVLab), Apache2.0 (Qwen1.5B/FastChat) and the linked Qwen72B
agreement are saved separately with SHA/receipts. No Qwen/base weights downloaded.
Conversation credits FastChat; keep provenance and Apache notice obligations. MIT copyright
and permission notice, Apache license/attributions/NOTICE if applicable, modification
notices, and any Qwen Notice obligations must be resolved before redistribution.
**PUBLIC RELEASE RIGHTS = UNKNOWN** pending harmonization of card/license metadata and
third-party notices; no public release is authorized. No missing local-use grant identified.

## Static execution review

Read all five pinned Python files in full: both configurations, modeling_intern_vit,
modeling_internvl_chat, conversation. No shell/subprocess/network/arbitrary output writes
in active model methods. Conversation's OpenAI message conversion is pure formatting,
not an API client; not called. Config.from_pretrained can resolve remote metadata, but
pilot constructs from pinned local JSON directly. No AutoModel remote code resolution.
Tokenizer is standard Qwen2 local-only, trust_remote_code=False.

Optional flash_attn/einops imports and apex substitution removed in a separately hashed
controlled copy. Eager attention is explicitly selected. timm.DropPath import replaced
by a rejecting stub; configured drop_path_rate=0 selects nn.Identity. No runtime change
to dense inference math, prompts, weights, vocabulary or generation algorithms. Reject
nonzero DropPath instead of quietly substituting behavior. Patch/diff/hash retained.
No dependency installation needed for this constrained active path; no flash kernels.

Existing transformers4.57.6 Qwen2 supplies GenerationMixin, DynamicCache, eager attention
and bounded generation. Local code path checked: no hub kernel plugin installed; no
kernel substitution requested. Installed framework code hashes recorded. The library's
general import closure is trusted installed code, not an exhaustive dependency audit.
Remote source never executes before guard. Inference_mode throughout, no training path.
Model state instantiated directly on cuda:0, BF16 default during constructor only;
safetensors loaded tensor-by-tensor onto cuda:0 then copied (no full duplicate state dict).
No pickle/torch.load, CPU/disk offload, automatic map, sharding or quantization.
Inspect every parameter/buffer and visual/KV/input states. Generation gets fresh cache per
call; no accumulated conversation. ExplicitEOS/max_new_tokens/timeout/call limits.
Delete all tensor/model refs; clear cuBLAS workspaces; empty cache; synchronize; require
allocator zero and kernel Job empty after exit. Python network audit and offline flags;
not an OS firewall proof. Windows shared-memory spill attribution remains UNKNOWN.

## Preprocessing and estimate

Official README resize/normalize pipeline is bounded to max_num=1, use_thumbnail=False:
exactly one 448x448 tile, 1025 ViT tokens -> 256 projected image tokens. Same input fixture
384x256; official one-tile path changes aspect ratio, recorded as a limitation (no image
content changes/extra files). RGB CPU decode/resize/normalization is not model offload.
Input<=512edge/262144pixels/10MiB, actual tile/tensor shape logged before GPU compute.
preprocessor_config's CLIPFeatureExtractor label is only historical processor metadata;
no CLIP model imported or loaded. Use explicit reviewed image transform.

**UNMEASURED PILOT VRAM ESTIMATE: 6000 MiB**, not measured proof or a general bound:

| Component | MiB |
|---|---:|
| Dense weights, vision+language+projector (4,177,999,192 bytes) | 3985 |
| Largest staged embedding/head tensor, ~444.4 MiB | 448 |
| KV: 28layers *2(K,V)*2heads*128dim*1152tokens*2bytes | 32 |
| Image, projected embeddings, masks and buffers | 16 |
| Eager attention/activation/generation workspaces, one tile, <=1024 input | 512 |
| Context, framework/libraries, allocator fragmentation allowance | 1007 |

Preflight needs free>=7536 MiB, process ceiling6400; extra allocator cap5400MiB. Post-init
CUDA free rechecked deducting context already consumed from estimate; if context>1007 or
remaining estimate+1536 does not fit, STOP. Boundary/parent telemetry enforce reserve.
Driver query before load showed 8192 total,214 used,7804 free, driver591.86; existing
VMware/permission-limited process entries retained. Requery at actual load mandatory.
No lower estimate, precision change or offload to manufacture a pass. Hardware test remains
pending until all hashes, bounded preprocessing, CPU tests and preflight pass.

## Operational notes

Small rights-metadata retrieval hit Windows cp950 decoding; changed to explicit UTF-8,
kept completed receipts, no model retry or environment change. Downloader refuses overwrite;
completed files reused, no duplicate weights. Asset ledger caps4.9GB payload (5GB approved,
transport overhead not packet-metered); new-disk cap12GB. Only one weight distribution.

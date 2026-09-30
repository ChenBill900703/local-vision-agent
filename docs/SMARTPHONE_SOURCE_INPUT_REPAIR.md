# Smartphone source input repair — 2026-09-30

SMARTPHONE SOURCE INPUT = CPU READY.
VERIFICATION BUDGET REPAIR = CPU READY.
COMBINED GPU VALIDATION = PENDING AUTHORIZATION.
No GPU queries/import/init/load/inference, natural-image inference, downloads or installs.

## Two independent policies

Runtime config schema internvl-development-v2 requires source_image_limits in addition to
limits (existing controller/internal model-input limits). Missing/unknown/invalid fields
refuse execution. Old v1 config is intentionally not silently upgraded. Existing mock config
and small fixture paths remain unchanged. Private backend still receives only bounded images.

Source: JPEG/PNG single frame; max_compressed_bytes33554432(32MiB),
max_decoded_pixels32000000(decimal32MP),max_source_edge_px10000. All finite, configurable
only downward. These conservative limits accept16,054,528-pixel originals without adopting
64MP/50MiB merely because those were suggested. No unbounded Pillow bomb bypass.
Source header bounds/format/frame count verified before full decode; bounded read, verify+
strict full load; corruption/truncation/bomb warnings reject. Unsafe Pillow truncated setting
is refused. Original bytes are never written. Malformed/unsupported input rejected before GPU.

RAM planning (estimate, NOT measured RSS or allocator cap): budget64bytes/sourcepixel for
simultaneous decoded surfaces, EXIF/RGB conversions, decoder scratch and working copies.
At32MP:2,048,000,000bytes=1.907GiB; two compressed32MiB buffers add64MiB; reserve1GiB for
Python/decoder/metadata overhead ->approximately2.97GiB task allowance (about9.3% of32GiB).
Normal Pillow images use substantially fewer bytes/pixel per surface; margin accommodates
several live copies. Normalization happens before model load, one source at a time. This is
conservative sizing for the32GB host, not a guarantee under arbitrary concurrent RAM pressure;
OS/decoder native allocations are not hard-capped, and low-memory conditions can still fail.
No CPU model offload involved. Downstream arrays stay tiny (3x448x448 float32 before BF16).

Model/controller limits unchanged: internal <=10MiB/262144pixels/512edge;8calls/iterations,
128output/call,1024input/call and totaloutput/image, all existing time/GPU limits.
Pinned InternVL model/BF16/cuda:0/batch1/eager/inference_mode and448x448single tile unchanged.
No full-resolution CUDA tensors, dynamic tiling,crops,quantization or second model.

## Automatic local path and provenance

Application real_agent accepts original ImageInput directly. CPU prepare_source records
original absolute path,inputID,SHA256,compressedbytes,width/height/format and oriented size;
EXIF transpose -> RGB -> LANCZOS aspect-preserving thumbnail <=512 -> metadata-free PNG.
Large input derivative goes to exclusive private run-directory sibling <run>-input/normalized.png
and source_provenance.json. Standard runs must use ignored artifacts storage; these photos
and derivatives must never be committed/uploaded/published. Original remains unmodified.
Record normalized SHA256/dimensions/format/path,conversion and source hash; runtime report
metadata source_input carries provenance, while report.image describes the model-facing input.
Small already-bounded images retain exact original path/bytes and existing downstream pixel
preprocessing. Hash checked again against adapter.begin_image to reject substitution.
Separate input directory is retained as evidence even if subsequent load refuses/fails.

Then existing InternVL preprocessing applies one448x448RGBBICUBIC/ImageNet tile. This still
changes aspect ratio at the model stage; no new high-resolution model experiment is implied.
Tiny text,distant objects,small signs,OCR details/tiny visual features may disappear. Accepting
phone originals validates usability, NOT preservation or understanding of all fine detail.
Final model preprocessing/tiling remains a FORMAL EXPERIMENT DESIGN FREEZE decision.

## Source changes and validation

source_input.py: typed SourceImageLimits and CPU normalization; internvl_contract.py/config:
required separate source policy; real_agent.py: pre-GPU preparation and report metadata;
internvl_rpc_worker.py: deserialize mandatory source policy only; reporting.py: source summary.
No backend/model-loader/math, Agent prompts/claim extraction/FIFO verification policy change.

110 CPU tests PASS(10.956s); Ruff src/tests/scripts PASS; strict Mypy29 source files PASS.
Tests include small fixture pixel equality/path identity; landscape4624x3472 andportrait3472x4624
synthetic JPEGs; aspect/512 bounds; EXIF orientation; original immutable/hash/metadata;
persisted normalized hash; pixel/edge/byte ceilings immediately exceeded; corrupt/truncatedJPEG,
unsupportedGIF,bomb/unsafe-decode setting,missing/invalid limits and framework-free import.
Actual application entry also exercised on synthetic phone dimensions via explicit CPU fake
worker/NVIDIA snapshots. No private-photo inference. Existing verification-budget/A-D/timeout/
malformedRPC/process/cleanup tests passed. Test success is not GPU feasibility evidence.
Evidence/logs: artifacts/smartphone-source-repair-20260930. Earlier101-test repair preserved.

## Next gate

Old VERIFICATION_BUDGET_REPAIR_OUTDOOR_20260930_V1 amendment remains frozen NOT EXECUTED;
do not use it. New combined proposal uses ORIGINAL outdoor_scene_001.jpg, never its manually
resized derivative as user input. One future explicitly authorized GPU run only, followed by
human development review. No baseline READY until future acceptance; no RQ improvement claim.
AI assistance: local source implementation/tests/reporting; no cloud image viewing or runtime judge.

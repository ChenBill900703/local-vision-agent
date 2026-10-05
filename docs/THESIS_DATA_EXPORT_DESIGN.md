# Thesis data export design — 2026-10-05

Application/data-layer completion only. Canonical atomic JSON is authoritative; CSV and
engineering_summary.json are deterministic derived exports. No model, prompt, Agent/FIFO,
normalization, source limits, GPU guard or CLI changes. No new dependency.

## Files and ownership

`*/result.json` remains the original report/metadata, schema windows-app-result-v1.
`*/review.json` is a separate atomic author assessment, default NOT_REVIEWED; allowed values
NOT_REVIEWED, USABLE, PARTIALLY_USABLE, UNUSABLE. UTF-8 note <=10000characters and UTC review
timestamp. Updating review never changes raw output, Agent status or canonical result bytes.
Review is qualitative engineering assessment, not truth, accuracy or human annotation study.
`*/session.json` records Webcam identity/backend, UTC start/end, frozen session limits,
captured/submitted frame IDs and counts, stop reason and cleanup evidence. `*/session_cleanup.json`
links subsequent runtime cleanup to each result without rewriting the original record.
App lifetime has one persistent model; an auto-capture session is a separate grouping.

`export-<UUID>/` contains selected CSVs, engineering_summary.json and export_audit.json.
Files remain under ignored application storage, exclusive export directory; no model-controlled
filenames or arbitrary export path. UI blocks export/review writes during active auto/analysis.
Each CSV is atomically replaced from a temp file; export bundle is complete only when audit
exists. Partial export on disk failure is not a complete bundle. No automatic file opening.
CSV generator uses Python standard library; no workbook engine or new installed package.

## Fixed column order

Column contracts in app_export_schema.py are versioned. Following lists are exact, in order.
Session schema appends camera_backend_type to the requested fields so FAKE cannot be confused
with QT_MULTIMEDIA_PHYSICAL. Summary/call record_schema_version suffix is REAL, MOCK or UNKNOWN.
Mock call rows describe executed mock invocations, not real model calls or thesis observations.

### analysis_summary.csv (43 columns)

```text
record_schema_version
timestamp
source_type
session_id
frame_id
input_id
source_width
source_height
source_format
source_bytes
source_sha256
normalized_width
normalized_height
normalized_sha256
status
completion_reason
stop_reason
agent_state_sequence
model_calls
input_tokens
output_tokens
total_tokens
truncated_call_count
candidate_claim_count
verification_attempted
verification_completed
verification_supported
verification_contradicted
verification_unresolved
verification_budget_unresolved
verification_coverage
analysis_latency_sec
total_latency_sec
peak_allocated_mib
peak_reserved_mib
peak_device_used_mib
cleanup_status
human_rating
human_note
human_review_timestamp
final_report
error_type
error_message
```

### model_calls.csv (16 columns)

```text
record_schema_version
session_id
frame_id
input_id
call_index
agent_state
prompt_id
input_tokens
output_tokens
latency_sec
generation_stop_reason
truncated
candidate_id
verification_candidate_text
verification_model_verdict
raw_response
```

### webcam_sessions.csv (32 columns)

```text
record_schema_version
session_id
camera_id
camera_display_name
session_start_timestamp
session_end_timestamp
configured_post_analysis_interval_sec
max_analysed_frames
max_session_duration_sec
captured_frames
analysis_attempts
completed_frames
partial_frames
failed_frames
total_model_calls
average_model_calls
total_output_tokens
average_output_tokens
mean_analysis_latency_sec
median_analysis_latency_sec
min_analysis_latency_sec
max_analysis_latency_sec
mean_verification_coverage
peak_allocated_mib
peak_reserved_mib
peak_device_used_mib
truncated_frame_count
session_stop_reason
camera_release_success
worker_cleanup_success
model_cleanup_success
camera_backend_type
```

## Mapping and missing data

Analysis row = one valid canonical IMAGE/WEBCAM analysis attempt, including failed/partial.
Source fields map unchanged source_input metadata; normalized fields map model_input, including
identity normalization. Per-image state sequence comes from report.states; it is a control trace,
not proof that every visited state issued a call. Candidate IDs claim-1..N are stable ordinal
identifiers within that canonical input; verification_id joins actual calls to candidates.

Real model_calls rows require backend call_start/call_done or retained frame_trace receipts.
Successful and started-but-failed calls are retained; missing answer/token/latency is blank.
Skipped queries and budget-unavailable verifications never receive fabricated rows.
Receipt reader filters exact input ID, joins start/done by call ID and retains read errors.
Mock rows use answered mock observations with explicit MOCK schema. They have no tokenized input
or measured model-call latency. Legacy records missing provenance/timing remain missing;
no retroactive rewrite or invented measurement. An absent trace is not proof of zero calls.

Blank CSV / null JSON = missing or not applicable; numeric0 remains a real recorded zero.
input/output totals require all constituent values; incomplete totals null. Total tokens require
both input and output totals. truncation count is unknown when any call truncation is unknown.
Supported/contradicted/unresolved counts use candidate status; budget-unresolved is separately
reported and is part of unresolved, so do not add it twice. Same-model support is not truth.

analysis_latency_sec spans session.analyze: source preparation, first lazy load if needed,
Agent and image-end reset. total_latency_sec spans worker ingress, capture-PNG save when needed,
analysis, report preparation and ephemeral cleanup; excludes final JSON flush, UI queue/display,
pre-capture wait and configured post-analysis interval. Neither is camera throughput.
Per-call latency is the existing model visual+generation receipt, never distributed from totals.
GPU values require REAL evidence; no GPU values from FakeCamera or mock. peak_device_used_mib is
maximum observed device-used snapshot, not continuously measured peak or per-process allocator.
UTC timestamps are recorded, not rewritten to match a desired development date.

Cleanup remains pending/unverified until a separate record supplies allocator-zero, worker exit,
empty job and baseline recovery evidence. Merely closing Qt objects is not verified physical
camera release; camera_release_success stays null unless independently documented. Fake session
hardware/model cleanup columns stay blank even if fake cleanup succeeds; raw mock evidence retained.

## CSV safety and determinism

UTF-8 BOM for Excel; standard CSV quoting, doubled quotes, CRLF row terminators, quoted embedded
commas/CR/LF intact. Spreadsheet-facing string cells with leading =,+,-,@ (also after leading
space/tab/CR/LF/BOM) receive a single leading apostrophe. This affects CSV only; raw JSON remains
byte-identical. Importers needing exact text must use canonical JSON, not strip guesses from CSV.
Numeric negatives would be numeric data, not formula text. Empty cells are intentional missing
values. No formulas, external links or executable model output are emitted by the app.
Analysis sort key: timestamp, session_id, input_id, record reference; calls follow analysis order
then receipt order; sessions sort start timestamp then session_id. CSV bytes are repeatable for
unchanged source/review/cleanup JSON. Exclusive export folder name is intentionally unique.

Corrupt records are reported in export_audit.json with references; no fake successful rows.
Corrupt review falls back to NOT_REVIEWED with audit error, retaining valid analysis. Corrupt
session metadata is audited; legacy webcam groups may have metadata-unavailable session rows.
Source SHA256 and exported CSV SHA256 are recorded for traceability. Never silently interpret
unreadable or missing records as successful attempts.

## Descriptive summary and denominators

engineering_summary.json contains requested attempt/status/review counts, completion rate,
call/token counts and means/medians, truncation counts/rate, verification coverage, analysis
latency mean/median/min/max and real-only GPU measurements/counts. REAL/MOCK/UNKNOWN partitions
are included; combined totals are inventory descriptions and must not be used as model efficacy.
No accuracy, hallucination rate, significance, confidence intervals or p-values are computed.

Completion denominator = valid parsed analysis attempts; partial/failed count in denominator.
Malformed records are excluded with audit counts, so report those exclusions with any summary.
Means/medians use available finite nonnegative measurements with *_known_count; missing is not0.
Truncation denominator = records with known truncation count, exposed separately. Coverage is a
macro mean across available per-analysis coverage, not pooled verified/claims and not accuracy.
Empty-population counts=0; rates/means=null. Incomplete numeric totals=null, not lower bounds
labelled totals. Session completed/partial/failed counts reflect persisted results; canonical
analysis_attempts counts submitted attempts. A mismatch leaves session totals null and exposes
missing results through counts rather than pretending they were completed. GPU means include
only REAL measured records and report their denominator. Review counts do not imply correctness.

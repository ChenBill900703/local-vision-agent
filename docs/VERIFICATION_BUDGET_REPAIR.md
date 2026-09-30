# Verification budget repair — 2026-09-30

VERIFICATION BUDGET REPAIR = CPU READY / GPU VALIDATION PENDING.
CPU-only authorization; no GPU query/load/inference, natural-image run, install or download.
Historical indoor TOOL_CALL_LIMIT/8claims/6checks/2unresolved/truncation/raw Chinese/human
review and synthetic/adoption/capability evidence remain immutable. This does not relabel them PASS.

## Policy and public contract

Source modules: agent.py (verification_slots/FIFO scheduling), contracts.py (v2 fields and
VerificationStop), internvl_adapter.py (generation receipt propagation), reporting.py (Chinese
coverage/truncation), real_agent.py (cleanup failure remains INCOMPLETE).
No prompt, trigger, claim extraction, model, config, generation limit or preprocessing change.

At entry to verification compute remaining model calls. Effective verification_budget is
max(0,min(max_model_calls,max_tool_calls,max_iterations,max_memory_entries)-calls_used).
No reserved calls: final report is non-model code. The stricter existing observation-memory
cap also limits slots. Candidate order is creation order, FIFO; schedule at most that many.
All excluded candidates become unresolved, verification_id=null,
verification_reason=verification_budget_not_available BEFORE any verification invocation.
No LLM/ranking/random/salience logic. C/D share scheduler; A/B do not verify.
Token/time/output constraints remain hard independent gates, not relaxed by the call planner.
A known exhausted verification budget is normal bounded completion; actual errors/timeouts/
malformed replies/cleanup failure remain incomplete failures. Hard call-limit backstop retained.

Report schema agent-report-v2; policy bounded-policy-v2-verification-fifo.
New fields: completion, typed verification_stop, candidate_claim_count, verification_budget,
verification_attempted, verification_completed, verification_unresolved_by_budget,
verification_coverage_ratio. Completed means a valid response including unresolved verdict,
NOT supported/correct. Coverage=completed/candidates; no candidates ->null, not perfect accuracy.
A/B report verification_stop NOT_APPLICABLE; C/D before stage NOT_REACHED; error INTERRUPTED.
Budget-limited normal result: status=complete, completion=COMPLETED_WITH_PARTIAL_VERIFICATION,
stop_reason and verification_stop=VERIFICATION_BUDGET_EXHAUSTED. Investigation_stop (e.g.
NO_TRIGGER) remains separate and does not mean all candidates verified.
Historical v1 files are not migrated or regenerated. Consumers must recognize the new v2
completion fields; status=complete alone says the bounded workflow finished, not full coverage.

CPU mock example:8candidates after2calls ->budget6/attempted6/completed6/unresolved_by_budget2,
coverage0.75 (75%),8total calls, no ninth attempt; two candidates remain unresolved.
Claim construction rejects supported/contradicted without verification_id. Agent assigns IDs
only after a validated response; schema evidence pointers alone are not truth assertions.

Answer generation_stop_reason and truncated are copied from real receipt: token_limit ->true,
eos ->false even at128tokens, unknown ->false (no assertion about truncation). Raw text unchanged.
Normalized trace includes these through serialized Answer. Markdown exposes tokens/stop/truncated.
No increase beyond128; same-model subjective over-acceptance remains a research limitation.

## Validation

101 CPU tests PASS(10.394s); Ruff src/tests/scripts PASS; strict Mypy28 source files PASS.
New tests:8claims/6slots/FIFO/75%, smaller/zero/exact candidate boundary, zero slots,
corrupt planner cannot bypass hard limit, real failure not masked, A/B/C/D behavior,
evidence-required statuses, generation-stop propagation including EOS at token ceiling.
Existing timeout/malformedRPC/cleanup/Windows process tests remain PASS. Explicit synthetic
CPU fixtures only; these are not repaired natural-image or GPU evidence.
Test files: tests/test_verification_budget.py; updated tests/test_agent.py and
 tests/test_internvl_adapter.py. Logs/preservation snapshot: artifacts/verification-budget-repair-20260930.

## Next gate

A separately authorized prospective outdoor GPU validation only; no indoor rerun.
See VERIFICATION_BUDGET_REPAIR_GPU_VALIDATION_AMENDMENT_2026-09-30.md after checkpoint.
Bounded partial verification is acceptable prospectively if explicit, safe and human-reviewed.
No baseline READY decision yet. AI assistance: implementation/tests/docs by development
assistant, no runtime judge or scientific correctness claim; author review remains required.

# Formal open questions and gates — 2026-10-01

**FORMAL EXPERIMENT DESIGN = DRAFT READY FOR AUTHOR REVIEW**

Engineering READY is narrow; NO formal execution/download/new development GPU is authorized.
A draft can be complete for review while exact acquired manifests and approvals remain absent.

| Class / ID | Item / selected v1 position | Evidence required / next owner action |
|---|---|---|
| DECISION REQUIRED D1 | P1 single448 square, no tiling, explicit distortion/detail limits | Author accepts restricted operating point; alternative requires prospective separate feasibility authorization |
| DECISION REQUIRED D2 | G128,1024 total, unchanged Chinese prompts | Author accepts truncation/fairness trade-off; no automatic192/256 or prompt search |
| DECISION REQUIRED D3 | Runtime literal FIFO unchanged; independent atomic human scoring of full raw text | Author accepts imperfect parser as evaluated system, not repaired using development failures |
| DECISION REQUIRED D4 | A/B/C/D exact library/triggers and8-call ceiling; C/D capacity differs | Author accepts adaptive-allocation estimand and raw vs endorsement distinction |
| DECISION REQUIRED D5 | Three primary endpoints, error taxonomy,0.05 practical scale,400 paired images/one repeat, bootstrap/Holm | Author statistical review and workload decision before outputs |
| BLOCKER B1 | Author approval of entire six-document package absent | Dated signoff and version/hash freeze, not implied by engineering review |
| BLOCKER B2 | Dataset acquisition not authorized; actual image IDs/license audit/archive/file hashes absent | Separately authorize bounded acquisition; rights review, deterministic selection and manifests before model execution |
| BLOCKER B3 | Independent salient references / Chinese synonyms / rubric not materialized | Two independent annotators plus adjudicator, training40 design images, locked reference/version hashes |
| BLOCKER B4 | Human staffing, approximately423 person-hours and institution/advisor policy unknown | Author confirms staffing/time, consent and required institutional/advisor review; do not infer exemption |
| BLOCKER B5 | Offline annotation linkage/scoring/paired statistics not implemented or CPU-validated | Separate scoped CPU evaluation tooling approval; fixtures for compound/truncated/duplicate/empty/failure/NA cases, exact commands/hash freeze |
| BLOCKER B6 | Formal runner/measurement mapping not certified | Audit lifecycle/timer boundaries, source timing, sampler cadence, prompts/settings/order; existing development evidence labels cannot be silently renamed formal |
| BLOCKER B7 | Formal execution safety/time budget and authorization absent | Explicit number of invocations, block schedule, overall resource budget, stop/resume rules and clean source/config/assets approval after B1–B6 |
| NON-BLOCKING LIMITATION L1 | Unknown foundation pretraining overlap, public validation-set familiarity | Disclose; no contamination-free claim |
| NON-BLOCKING LIMITATION L2 | P1 loss/distortion and128token truncation, max8 candidates and FIFO | Measure size/truncation/coverage strata and failures; no general maximum-model claim |
| NON-BLOCKING LIMITATION L3 | Same-model self-confirmation; verification only labels raw text | Independently score false acceptance and retained correct content; no automatic hallucination reduction |
| NON-BLOCKING LIMITATION L4 | One GPU/environment; greedy not bitwise guarantee; no repeat variance | Conditional inference only; preserve prefix divergence and balanced order |
| NON-BLOCKING LIMITATION L5 | Windows shared-memory UNKNOWN; Python audit not OS firewall; device sampling can miss peaks | Report measurement scope; never plan spill/offload |
| NON-BLOCKING LIMITATION L6 | Salience operational threshold, incomplete public labels, imperfect blinding/duplicate detection | Human adjudication and explicit denominator/limitations |

A DECISION REQUIRED is proposed concretely, not left as an unbounded option search; unresolved
items prevent B1. A NON-BLOCKING LIMITATION is disclosed, never silently treated as solved.
No item may be resolved by looking at formal outputs and tuning to them.

Exact next action: author reviews [design](FORMAL_EXPERIMENT_DESIGN.md),
[data/rubric](FORMAL_DATA_PROTOCOL.md), [metrics](FORMAL_METRICS.md),
[methods](FORMAL_METHODS_ABCD.md), [statistics](FORMAL_STATISTICAL_PLAN.md) and this gate list.
Then request only the scope necessary to resolve approved blockers. No run is queued.
No Webcam/GUI/OCR/detector/video/second-model/quantization/fine-tuning/cloud/runtime expansion.
No datasets, images, weights, raw runs or private annotation evidence committed or published.

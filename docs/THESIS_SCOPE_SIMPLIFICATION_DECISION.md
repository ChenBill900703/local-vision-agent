# Thesis scope simplification — user decision, 2026-10-01

USER-CONFIRMED scope change by the attached request retained in
`artifacts/windows-ui-20261001/evidence/user_authorization.txt`.
This explicit request supersedes the former GUI/Webcam exclusion and large formal-design
proposal only for the two input modes and local desktop application described here.
It does not authorize installations, physical camera inference, GPU execution or release.

Working title: **Design and Implementation of a Local Agentic Image Understanding System
on an 8GB Consumer GPU**. Engineering/system study: manual local still-image input,
Webcam repeated still-frame input, bounded Agent, same-model verification, Traditional
Chinese reports, Windows desktop interface, local resource/failure logging.

Preserve REAL LOCAL AGENT ENGINEERING BASELINE READY and all negative evidence. The
READY statement still describes the tested still-image path; new GUI and multi-image
persistent sessions are unverified extensions until their own acceptance gates pass.
No inference pipeline, model, prompts, precision, P1 normalization, FIFO or limits replaced.

The prior six FORMAL_* v1 documents are preserved as historical, unapproved proposals.
Their400-image COCO plan and large human annotation workload are not current requirements.
No dataset acquisition, formal benchmark or hundreds-of-images program. Historical RQ1–4
remain traceable research motivations, not mandatory large experiments or proven outcomes.
No SOTA/universal accuracy/zero hallucination/verification-correctness claim. Same-model
verification over-acceptance and all development hallucinations remain limitations.
A–D source interfaces remain preserved, without an obligation to execute formal comparisons.

This is the final major application feature scope: two input modes, one main window,
one existing local runtime, history and safe lifecycle. No accounts/server/REST/browser/
cloud/OCR/detector/tracking/temporal video/identity/biometrics/secondVLM/multi-agent/voice/
fine-tuning/quantization/dynamic tiling. Webcam provides independent still images;
there is no temporal understanding or cross-frame reasoning.

Trade-off: finish a usable, bounded local application and demonstrate engineering behavior,
instead of claiming a large independently annotated scientific comparison. Advisor/institution
acceptance of this thesis emphasis is UNKNOWN; no degree/publication promise.10/31 core,
11/1 acceptance and subsequent writing dates remain targets. User scope confirmation is
not institutional approval.

Implementation permission covers source/config/tests/docs and CPU/Fake testing after the
explicit missing-dependency gate. PySide6 is absent; stop before installation as requested.
See [UI design](WINDOWS_UI_DESIGN.md), [Webcam design](WEBCAM_SESSION_DESIGN.md),
[current implementation status](WINDOWS_UI_IMPLEMENTATION_RESULT.md).

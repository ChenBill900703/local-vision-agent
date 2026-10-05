# Known limitations

Engineering usability is not general semantic accuracy, novelty, SOTA or a proven thesis claim.
- Same-model verification is not independent ground truth; over-acceptance observed.
- Historical real-photo outputs included nonexistent cup and incorrect ornament/base/background
  attributes. Preserve all negative evidence and author qualifiers; never rewrite these as PASS.
-128output-token cap truncates responses. Budget8calls may leave verification unresolved; report
  coverage and bounded completion accurately, not false completeness.
- Single448 preprocessing after aspect512 ingress loses small detail; model capacity is limited.
- One target: Windows/i7-11700K/32GB/RTX3070Ti8GB. Other drivers/devices/hardware not validated.
- Webcam analyzes repeated independent still frames, not video, temporal reasoning or tracking.
  No identity/face tracking, OCR subsystem, detector, cloud fallback or conversation memory.
- Device readiness, capture and release depend on Qt/Windows permission/driver behavior; CPU
  stubs cannot establish physical compatibility. Final hardware status: PROJECT_FINAL_VALIDATION_RESULT.md.
- Real persistent multi-image CUDA must have real receipts before PASS; previous single-image
  engineering PASS does not imply multi-image cleanup/memory behavior.
- CSV is derived, formula-safe text differs from canonical JSON. Corrupt/missing data audited;
  means have explicit known denominators. Author usability review is qualitative, not accuracy.
- Repository license remains unresolved for publication. No redistribution of model/controlled
  third-party code, private images or raw evidence. No formal large benchmark completed.
- Model watchdog1800s persists across inputs; no hidden reload. Quit normally after bounded work.

Latest exact blocker and restart scope are in PROJECT_FINAL_VALIDATION_RESULT.md and CURRENT.

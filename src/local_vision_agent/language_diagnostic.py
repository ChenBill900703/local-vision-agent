"""Frozen final language diagnostic; no prompt search or response conversion."""

RUN_ID = "language-final-20260927"
CONTROL = "What shapes are in the image, and what color is each shape?"
TRADITIONAL_CHINESE = (
    "Answer the following question in Traditional Chinese only. Do not repeat the question. "
    "What shapes are in the image, and what color is each shape?"
)
OPERATIONS = (
    ("english_control", CONTROL, True),
    ("english_instruction_traditional_chinese", TRADITIONAL_CHINESE, True),
)

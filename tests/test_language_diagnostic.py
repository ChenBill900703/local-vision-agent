"""CPU-only checks for the final fixed-prompt diagnostic."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from local_vision_agent.language_diagnostic import CONTROL, OPERATIONS, TRADITIONAL_CHINESE
from local_vision_agent.pilot_policy import PilotRefusal
from local_vision_agent.pilot_worker import run


class LanguageDiagnosticTests(unittest.TestCase):
    def test_exact_two_prompts_and_original_suffix(self):
        self.assertEqual(CONTROL, "What shapes are in the image, and what color is each shape?")
        self.assertEqual(
            TRADITIONAL_CHINESE,
            "Answer the following question in Traditional Chinese only. Do not repeat the question. "
            "What shapes are in the image, and what color is each shape?",
        )
        self.assertEqual(len(OPERATIONS), 2)
        self.assertTrue(all(duplicate for _, _, duplicate in OPERATIONS))
        self.assertEqual([prompt for _, prompt, _ in OPERATIONS], [CONTROL, TRADITIONAL_CHINESE])

    def test_final_mode_validates_original_package_before_framework_import(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch(
                "local_vision_agent.pilot_worker.validate_assets",
                side_effect=PilotRefusal("CPU fixture"),
            ) as validate:
                self.assertEqual(run(root, root, final_language=True), 1)
                validate.assert_called_once_with(root, repair=False)

    def test_conflicting_modes_refused(self):
        with self.assertRaisesRegex(PilotRefusal, "CONFLICTING"):
            run(Path("missing"), Path("missing"), repair=True, final_language=True)

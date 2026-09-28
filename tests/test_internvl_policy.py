"""CPU-only gate tests; no pretrained model imports or simulated visual evidence."""

import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from local_vision_agent.internvl_policy import CORE, probe_gate, validate_assets
from local_vision_agent.pilot_policy import PilotRefusal


class InternvlPolicyTests(unittest.TestCase):
    def test_import_and_handshake_do_not_initialize_framework(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys; import local_vision_agent.internvl_worker; assert 'torch' not in sys.modules; assert 'transformers' not in sys.modules",
            ],
            check=False,
            capture_output=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "local_vision_agent.internvl_worker",
                "--root",
                ".",
                "--run-dir",
                ".",
            ],
            input="STOP\n",
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SUPERVISOR_HANDSHAKE_REQUIRED", result.stderr)

    def good(self) -> dict[str, str]:
        return {
            name: "圖片中有紅色正方形和藍色圓形。" if i else "A red square and a blue circle."
            for i, (name, _) in enumerate(CORE)
        }

    def test_fixed_claim_gate(self) -> None:
        self.assertTrue(probe_gate(self.good()))

    def test_missing_simplified_echo_wrong_or_uncertain_skip_probes(self) -> None:
        self.assertFalse(probe_gate({}))
        for raw in (
            "红色正方形和蓝色圆形",
            CORE[1][1],
            "A red square and blue circle",
            "圖片中有藍色正方形和紅色圓形。",
            "可能有紅色正方形和藍色圓形。",
            "圖片中有紅色正方形和藍色圓形及貓。",
        ):
            values = self.good()
            values["B_direct_zh"] = raw
            self.assertFalse(probe_gate(values), raw)

    def test_missing_manifest_refuses(self) -> None:
        with TemporaryDirectory() as name:
            root = Path(name)
            (root / "evidence").mkdir()
            (root / "evidence/runtime_manifest.json").write_text('{"revision":"main"}')
            with self.assertRaises(PilotRefusal):
                validate_assets(root, root)


if __name__ == "__main__":
    unittest.main()

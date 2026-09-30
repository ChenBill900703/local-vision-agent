"""CPU synthetic images only; smartphone dimensions, not private photo inference."""

import hashlib
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from PIL import Image, ImageFile

from local_vision_agent.contracts import AgentError, ImageInput
from local_vision_agent.internvl_contract import load_runtime_config, preprocess_array
from local_vision_agent.source_input import prepare_source


class SourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = load_runtime_config(
            Path(__file__).resolve().parents[1] / "configs/agent_internvl_development.toml"
        )

    def image(self, size=(8, 8), fmt="JPEG", orientation=None):
        p = self.root / "source.bin"
        with Image.new("RGB", size, "white") as im:
            exif = Image.Exif()
            if orientation:
                exif[274] = orientation
            im.save(p, format=fmt, **({"exif": exif} if fmt == "JPEG" else {}))
        return ImageInput("CPU-FIXTURE", p)

    def prepare(self, item, limits=None, name="normalized"):
        return prepare_source(
            item, limits or self.config.source_image_limits, self.config.limits, self.root / name
        )

    def test_small_path_identity_and_model_pixels_unchanged(self):
        item = self.image()
        sha = hashlib.sha256(item.path.read_bytes()).hexdigest()
        before = preprocess_array(item.path, sha, self.config.limits.max_input_bytes)
        bounded, m = self.prepare(item)
        self.assertEqual(item, bounded)
        self.assertFalse(m["normalized"])
        self.assertTrue(
            (
                before == preprocess_array(bounded.path, sha, self.config.limits.max_input_bytes)
            ).all()
        )

    def test_landscape_portrait_original_preserved_and_metadata(self):
        for size in ((4624, 3472), (3472, 4624)):
            item = self.image(size)
            original = item.path.read_bytes()
            bounded, m = self.prepare(item, name=str(size[0]))
            self.assertEqual(item.path.read_bytes(), original)
            self.assertEqual(m["source_sha256"], hashlib.sha256(original).hexdigest())
            self.assertEqual((m["source_width"], m["source_height"]), size)
            self.assertEqual(m["source_bytes"], len(original))
            self.assertEqual(m["source_format"], "JPEG")
            self.assertEqual(m["source_path"], str(item.path.resolve()))
            with Image.open(bounded.path) as im:
                self.assertLessEqual(max(im.size), 512)
                self.assertLessEqual(im.width * im.height, 262144)
                self.assertAlmostEqual(im.width / im.height, size[0] / size[1], delta=0.003)
                self.assertEqual(im.mode, "RGB")
                self.assertFalse(im.getexif())
            self.assertEqual(
                m["model_input"]["sha256"], hashlib.sha256(bounded.path.read_bytes()).hexdigest()
            )
            self.assertTrue((bounded.path.parent / "source_provenance.json").is_file())

    def test_exif_before_resize(self):
        item = self.image((1200, 800), orientation=6)
        _bounded, m = self.prepare(item)
        self.assertEqual((m["oriented_width"], m["oriented_height"]), (800, 1200))
        self.assertEqual((m["model_input"]["width"], m["model_input"]["height"]), (341, 512))

    def test_each_limit_immediately_exceeded(self):
        item = self.image()
        for field, value, code in (
            ("max_compressed_bytes", item.path.stat().st_size - 1, "SOURCE_BYTES_LIMIT"),
            ("max_decoded_pixels", 63, "SOURCE_PIXELS_LIMIT"),
            ("max_source_edge_px", 7, "SOURCE_EDGE_LIMIT"),
        ):
            with self.subTest(field=field), self.assertRaisesRegex(AgentError, code):
                self.prepare(item, replace(self.config.source_image_limits, **{field: value}))
        self.assertFalse((self.root / "normalized").exists())

    def test_corrupt_truncated_unsupported_and_unsafe_setting(self):
        item = self.image((100, 100))
        item.path.write_bytes(item.path.read_bytes()[:-25])
        with self.assertRaisesRegex(AgentError, "INVALID_IMAGE"):
            self.prepare(item)
        item = self.image(fmt="GIF")
        with self.assertRaisesRegex(AgentError, "UNSUPPORTED_IMAGE"):
            self.prepare(item)
        with (
            patch.object(ImageFile, "LOAD_TRUNCATED_IMAGES", True),
            self.assertRaisesRegex(AgentError, "UNSAFE_PILLOW"),
        ):
            self.prepare(item)

    def test_decompression_bomb_refuses_without_output(self):
        item = self.image()
        with (
            patch.object(Image, "MAX_IMAGE_PIXELS", 10),
            self.assertRaisesRegex(AgentError, "INVALID_IMAGE"),
        ):
            self.prepare(item)
        self.assertFalse((self.root / "normalized").exists())

    def test_missing_source_config_refuses(self):
        config = Path(__file__).resolve().parents[1] / "configs/agent_internvl_development.toml"
        p = self.root / "missing.toml"
        p.write_text(config.read_text().split("[source_image_limits]")[0])
        with self.assertRaises(AgentError):
            load_runtime_config(p)
        for value in (0, -1, True, 32000001):
            with self.assertRaises(AgentError):
                replace(self.config.source_image_limits, max_decoded_pixels=value)

    def test_import_has_no_framework_or_cuda(self):
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import local_vision_agent.source_input,sys; assert not {'torch','transformers','torchvision'} & set(sys.modules)",
            ],
            check=False,
            capture_output=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

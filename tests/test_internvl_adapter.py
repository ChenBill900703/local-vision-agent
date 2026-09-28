"""All model/process outputs here are explicit CPU fixtures, not GPU or VLM evidence."""

import hashlib
import os
import subprocess
import sys
import tempfile
import time
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from local_vision_agent.contracts import AgentError, ImageInfo, ImageInput, Method, Request
from local_vision_agent.gpu_guard import GpuSnapshot
from local_vision_agent.internvl_adapter import InternVLAdapter
from local_vision_agent.internvl_backend import InternVLBackend
from local_vision_agent.internvl_contract import (
    load_runtime_config,
    normalize_answer,
    preprocess_array,
    validate_environment,
)
from local_vision_agent.pilot_worker import Evidence
from local_vision_agent.real_agent import run_development

PROJECT = Path(__file__).resolve().parents[1]


def fixture_source(mode="success"):
    return (
        "MODE="
        + repr(mode)
        + "\n"
        + """
import os,sys,time,json,argparse
from pathlib import Path
from local_vision_agent.internvl_contract import RuntimeConfig
from local_vision_agent.internvl_policy import REVISION
from local_vision_agent.contracts import Limits,ImageInput
from local_vision_agent.image_input import inspect_image
from dataclasses import asdict
parser=argparse.ArgumentParser();parser.add_argument('--root');parser.add_argument('--run-dir');parser.add_argument('--configuration');a=parser.parse_args()
def emit(phase,**values):
 print(json.dumps(dict(phase=phase,pid=os.getpid(),monotonic=time.monotonic(),**values),ensure_ascii=False),flush=True)
def reply(n,op,payload):emit('response',id=n,op=op,payload=payload)
emit('ready');assert sys.stdin.readline().strip()=='GO'
c=json.loads(Path(a.configuration).read_text(encoding='utf8'));c['limits']=Limits(**c['limits']);config=RuntimeConfig(**c)
reply(0,'load',dict(model_id='OpenGVLab/InternVL3-2B-Instruct',revision=REVISION,device='cuda:0',fixture=True))
count=0
for line in sys.stdin:
 r=json.loads(line);op=r['op'];p=r['payload']
 if op=='begin_image':
  image=inspect_image(ImageInput(p['input_id'],Path(p['path'])),config.limits)
  reply(r['id'],op,dict(image=asdict(image),tile_count=1,preprocessing=config.preprocessing))
 elif op=='invoke':
  count+=1
  if MODE=='hang':time.sleep(30)
  if MODE=='failure':emit('failure',message='CPU fixture model failure');break
  raw={'caption':'模擬：可能有一個杯子。','scene':'模擬：室內。','object':'模擬：細節不明。','detail':'模擬：細節不明。','verify':'unresolved：模擬未決。'}[p['prompt_id']]
  if MODE=='clear':raw={'caption':'模擬：紅色正方形。','scene':'模擬：幾何圖形。','object':'模擬：圓形。','detail':'模擬：白色背景。','verify':'unresolved：模擬未決。'}[p['prompt_id']]
  reply(r['id']+(1 if MODE=='bad_id' else 0),op,dict(raw_response=raw,output_tokens=12,input_tokens=320,latency_s=.01,visual_s=.002,generation_s=.008,call_id=f'call-{count}',measurement={'peak_reserved_bytes':0}))
 elif op=='unload':
  if MODE=='slow_cleanup':time.sleep(1)
  reply(r['id'],op,dict(measurement={'allocated_bytes':1 if MODE=='bad_cleanup' else 0,'reserved_bytes':0}));break
"""
    )


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "synthetic.png"
        Image.new("RGB", (8, 8), "white").save(self.path)
        self.item = ImageInput("CPU-FIXTURE-NOT-VLM-EVIDENCE", self.path)
        self.config = load_runtime_config(PROJECT / "configs/agent_internvl_development.toml")

    def test_limits_missing_and_excessive_refuse(self):
        with self.assertRaises(AgentError):
            InternVLAdapter(self.root, self.root / "run", None)
        with self.assertRaises(AgentError):
            replace(self.config, limits=replace(self.config.limits, max_output_tokens=129))
        bad = self.root / "bad.toml"
        bad.write_text('schema="internvl-development-v1"\nadapter="internvl3-pinned"')
        with self.assertRaises(AgentError):
            load_runtime_config(bad)

    def test_adapter_direct_call_enforces_character_bound(self):
        adapter = InternVLAdapter(self.root, self.root / "no-process", self.config)
        adapter.loaded = True
        adapter.image = ImageInfo("fixture", 8, 8, "PNG")
        with (
            patch.object(adapter.transport, "request", return_value={"raw_response": "字" * 9000, "output_tokens": 1}),
            patch.object(adapter.transport, "abort"),
            self.assertRaisesRegex(AgentError, "OUTPUT_LIMIT"),
        ):
            adapter.invoke(Request("query", "scene", "CPU fixture", 128), adapter.image)
        self.assertTrue(adapter.failed)

    def test_dependency_drift_refuses_without_importing_model(self):
        with (
            patch("local_vision_agent.internvl_contract.importlib.metadata.version", return_value="changed"),
            self.assertRaisesRegex(AgentError, "DEPENDENCY_DRIFT"),
        ):
            validate_environment()

    def test_preprocessing_is_fixed_and_detects_changed_bytes(self):
        digest = hashlib.sha256(self.path.read_bytes()).hexdigest()
        result = preprocess_array(self.path, digest, 1024)
        self.assertEqual(result.shape, (3, 448, 448))
        self.assertAlmostEqual(float(result[0, 0, 0]), (1 - 0.485) / 0.229, places=5)
        with self.assertRaises(AgentError):
            preprocess_array(self.path, "wrong", 1024)
        with self.assertRaises(AgentError):
            preprocess_array(self.path, digest, 1)

    def test_literal_claims_uncertainty_and_verdict_are_conservative(self):
        query = Request("query", "object", "問題", 128)
        answer = normalize_answer("杯子可能是白色。細節不明。", 12, query)
        self.assertTrue(answer.uncertain)
        self.assertIn("detail", answer.missing)
        self.assertEqual(answer.text, "杯子可能是白色。細節不明。")
        verify = replace(query, prompt_id="verify")
        for raw, expected in (
            ("supported：可見", "supported"),
            ("contradicted。", "contradicted"),
            ("not supported", "unresolved"),
            ("supported or contradicted", "unresolved"),
            ("圖片中有紅色正方形。", "unresolved"),
        ):
            self.assertEqual(normalize_answer(raw, 10, verify).verdict, expected)

    def test_preflight_failure_precedes_framework_import(self):
        # A separate process proves imports do not accidentally initialize torch.
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys; import local_vision_agent.internvl_adapter; import local_vision_agent.internvl_rpc_worker; assert 'torch' not in sys.modules",
            ],
            capture_output=True,
            check=False,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        with (
            patch("local_vision_agent.internvl_backend.validate_assets"),
            patch("local_vision_agent.internvl_backend.deny_network"),
            patch(
                "local_vision_agent.internvl_backend.GpuGuard.preflight",
                side_effect=AgentError("PREFLIGHT_REFUSED"),
            ),
        ):
            backend = InternVLBackend(self.root, self.config, Evidence(self.root))
            with self.assertRaisesRegex(AgentError, "PREFLIGHT_REFUSED"):
                backend.load()
            self.assertIsNone(backend.torch)

    def _patch_transport(self, mode):
        real_popen = subprocess.Popen
        source = fixture_source(mode)

        def launch(command, **kwargs):
            if "local_vision_agent.internvl_rpc_worker" in command:
                tail = command[command.index("local_vision_agent.internvl_rpc_worker") + 1 :]
                command = [sys.executable, "-B", "-c", source, *tail]
            return real_popen(command, **kwargs)

        return patch("local_vision_agent.internvl_transport.subprocess.Popen", side_effect=launch)

    def test_existing_run_never_overwritten_and_invalid_image_never_loads(self):
        existing = self.root / "immutable-run"
        existing.mkdir()
        (existing / "agent_report.json").write_text("preserve")
        with self.assertRaisesRegex(AgentError, "RUN_DIRECTORY_EXISTS"):
            run_development(self.item, Method.A, self.root, existing, self.config)
        self.assertEqual((existing / "agent_report.json").read_text(), "preserve")
        with patch("local_vision_agent.internvl_transport.PersistentTransport.load") as load:
            result = run_development(
                ImageInput("missing", self.root / "absent"),
                Method.D,
                self.root,
                self.root / "bad-input",
                self.config,
            )
            load.assert_not_called()
            self.assertEqual(result.stop_reason, "IMAGE_IO_ERROR")

    @unittest.skipUnless(os.name == "nt", "Windows persistent Agent integration")
    def test_real_boundary_cpu_fixtures_keep_methods_separate_and_reset_memory(self):
        snapshot = GpuSnapshot("CPU fixture", 8192, 200, 7800)
        reports = {}
        for mode in ("success", "clear"):
            for method in Method:
                with (
                    self._patch_transport(mode),
                    patch(
                        "local_vision_agent.internvl_transport.query_gpu_snapshot",
                        return_value=snapshot,
                    ),
                    patch(
                        "local_vision_agent.pilot_supervisor_repair.query_gpu_snapshot",
                        return_value=snapshot,
                    ),
                ):
                    result = run_development(
                        self.item, method, self.root, self.root / f"{mode}-{method}", self.config
                    )
                self.assertEqual(result.stop_reason, "COMPLETED")
                self.assertTrue(result.runtime_metadata["cleanup"]["job_empty"])
                self.assertEqual(result.observations[0].call_id, "call-1")
                self.assertTrue(all("模擬" in o.answer.text for o in result.observations))
                self.assertTrue(result.runtime_metadata["observation_evidence"])
                self.assertTrue(all(c.status == "unresolved" for c in result.claims))
                reports[mode, method] = result
        self.assertEqual(len(reports["success", Method.A].observations), 1)
        b = reports["success", Method.B]
        d = reports["success", Method.D]
        self.assertEqual(
            b.observations, tuple(o for o in d.observations if o.request.prompt_id != "verify")
        )
        self.assertEqual(d.investigation_stop, "NO_NEW_EVIDENCE")
        self.assertLess(
            len(reports["clear", Method.D].observations),
            len(reports["clear", Method.C].observations),
        )
        self.assertEqual(reports["clear", Method.D].investigation_stop, "NO_TRIGGER")

    @unittest.skipUnless(os.name == "nt", "Windows watchdog between requests")
    def test_idle_image_timeout_kills_worker_without_another_request(self):
        snapshot = GpuSnapshot("CPU fixture", 8192, 200, 7800)
        config = replace(self.config, limits=replace(self.config.limits, per_image_timeout_s=0.2))
        with (
            self._patch_transport("success"),
            patch(
                "local_vision_agent.internvl_transport.query_gpu_snapshot", return_value=snapshot
            ),
            patch(
                "local_vision_agent.pilot_supervisor_repair.query_gpu_snapshot",
                return_value=snapshot,
            ),
        ):
            adapter = InternVLAdapter(self.root, self.root / "idle", config)
            try:
                adapter.load()
                adapter.begin_image(self.item)
                deadline = time.monotonic() + 3
                while adapter.transport.process.poll() is None and time.monotonic() < deadline:
                    time.sleep(0.02)
                self.assertIsNotNone(adapter.transport.process.poll())
                self.assertEqual(adapter.transport.failure, "IMAGE_TIMEOUT")
            finally:
                adapter.transport.abort()

    @unittest.skipUnless(os.name == "nt", "Windows process lifecycle")
    def test_persistent_queries_failures_timeout_and_cleanup(self):
        snapshot = GpuSnapshot("CPU fixture", 8192, 200, 7800)
        for mode in ("success", "hang", "failure", "bad_id", "bad_cleanup", "slow_cleanup"):
            with (
                self.subTest(mode=mode),
                self._patch_transport(mode),
                patch(
                    "local_vision_agent.internvl_transport.query_gpu_snapshot",
                    return_value=snapshot,
                ),
                patch(
                    "local_vision_agent.pilot_supervisor_repair.query_gpu_snapshot",
                    return_value=snapshot,
                ),
            ):
                config = (
                    replace(self.config, limits=replace(self.config.limits, cleanup_timeout_s=0.2))
                    if mode == "slow_cleanup"
                    else self.config
                )
                adapter = InternVLAdapter(self.root, self.root / mode, config)
                try:
                    adapter.load()
                    image = adapter.begin_image(self.item)
                    pid = adapter.transport.worker_pid
                    request = Request("query", "scene", "CPU fixture", 128)
                    if mode in ("hang", "failure", "bad_id"):
                        with self.assertRaises(AgentError):
                            adapter.invoke(request, image, 0.2)
                        self.assertIsNotNone(adapter.transport.process.poll())
                    else:
                        for _ in range(3):
                            self.assertIn("模擬", adapter.invoke(request, image).text)
                            self.assertEqual(adapter.transport.worker_pid, pid)
                        with self.assertRaises(AgentError):
                            adapter.load()
                        if mode in ("bad_cleanup", "slow_cleanup"):
                            with self.assertRaises(AgentError):
                                adapter.unload()
                        else:
                            self.assertTrue(adapter.unload()["job_empty"])
                finally:
                    adapter.transport.abort()


if __name__ == "__main__":
    unittest.main()

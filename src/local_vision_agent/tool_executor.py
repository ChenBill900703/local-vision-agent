"""Spawn-only mock worker with bounded waiting and explicit cleanup failure.

This is a CPU fixture executor, not a GPU model lifecycle implementation.
No arbitrary adapter classes or remotely supplied functions can be executed.
"""

import multiprocessing as mp
import time
from multiprocessing.connection import Connection

from .contracts import AgentError, Answer, ImageInfo, Request
from .mock_adapter import MockAdapter


def _worker(pipe: Connection, adapter: MockAdapter, request: Request, image: ImageInfo) -> None:
    try:
        pipe.send(adapter.invoke(request, image))
    except AgentError as exc:
        pipe.send(exc.code)
    except Exception:  # noqa: BLE001 -- worker boundary: parent needs a finite failure result.
        pipe.send("TOOL_FAILURE")
    finally:
        pipe.close()


class MockProcessExecutor:
    def __init__(self, adapter: MockAdapter, cleanup_timeout_s: float) -> None:
        if type(adapter) is not MockAdapter:
            raise AgentError("REAL_ADAPTER_NOT_ENABLED")
        self.adapter = adapter
        self.cleanup_timeout_s = cleanup_timeout_s

    def invoke(self, request: Request, image: ImageInfo, timeout_s: float) -> Answer:
        context = mp.get_context("spawn")
        reader, writer = context.Pipe(duplex=False)
        process = context.Process(target=_worker, args=(writer, self.adapter, request, image))
        started = False
        deadline = time.monotonic() + timeout_s
        try:
            process.start()
            started = True
            writer.close()
            if not reader.poll(max(0, deadline - time.monotonic())):
                raise AgentError("TOOL_TIMEOUT")
            result = reader.recv()
            if time.monotonic() >= deadline:
                raise AgentError("TOOL_TIMEOUT")
            if isinstance(result, str):
                raise AgentError(result)
            if not isinstance(result, Answer):
                raise AgentError("INVALID_TOOL_RESULT")
            return result
        except (EOFError, OSError) as exc:
            raise AgentError("TOOL_FAILURE") from exc
        finally:
            reader.close()
            writer.close()
            if started:
                # A timed-out worker must not continue after a partial report is returned.
                process.join(0)
                if process.is_alive():
                    process.terminate()
                    process.join(self.cleanup_timeout_s)
                if process.is_alive():
                    process.kill()
                    process.join(self.cleanup_timeout_s)
                if process.is_alive():
                    raise AgentError("CLEANUP_FAILED")
                process.close()

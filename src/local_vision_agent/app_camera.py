"""Qt camera and explicit fake. Preview never enters inference without capture()."""

from typing import Any

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtGui import QColor, QImage
from PySide6.QtMultimedia import QCamera, QImageCapture, QMediaCaptureSession, QMediaDevices
from PySide6.QtMultimediaWidgets import QVideoWidget


class CameraBase(QObject):
    frame = Signal(str, object)
    error = Signal(str)

    def devices(self) -> list[str]:
        raise NotImplementedError

    def identity(self) -> dict[str, Any]:
        raise NotImplementedError

    def ready(self) -> bool:
        raise NotImplementedError

    def open(self, index: int) -> None:
        raise NotImplementedError

    def capture(self, identifier: str) -> None:
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError


class QtCamera(CameraBase):
    def __init__(self, preview: QVideoWidget) -> None:
        super().__init__()
        self.preview = preview
        self.camera: QCamera | None = None
        self.session = QMediaCaptureSession(self)
        self.capture_device = QImageCapture(self)
        self.session.setImageCapture(self.capture_device)
        self.session.setVideoOutput(preview)
        self.capture_device.imageCaptured.connect(self._captured)
        self.capture_device.errorOccurred.connect(self._capture_error)
        self.pending: tuple[int, str] | None = None
        self.listed_ids: list[bytes] = []
        self.selected_identity: dict[str, Any] = {"camera_backend_type": "QT_MULTIMEDIA_PHYSICAL"}

    def devices(self) -> list[str]:
        devices = QMediaDevices.videoInputs()
        self.listed_ids = [bytes(d.id().data()) for d in devices]
        return [d.description() for d in devices]

    def identity(self) -> dict[str, Any]:
        return dict(self.selected_identity)

    def ready(self) -> bool:
        return (
            self.camera is not None
            and self.camera.isActive()
            and self.capture_device.isReadyForCapture()
        )

    def _capture_error(self, value: int, _code: Any, text: str) -> None:
        if self.camera is not None and (
            value == -1 or self.pending is not None and self.pending[0] == value
        ):
            self.error.emit(text)

    def open(self, index: int) -> None:
        self.close()
        devices = QMediaDevices.videoInputs()
        if not 0 <= index < len(devices):
            raise RuntimeError("CAMERA_UNAVAILABLE")
        if self.listed_ids and (
            index >= len(self.listed_ids)
            or bytes(devices[index].id().data()) != self.listed_ids[index]
        ):
            raise RuntimeError("CAMERA_DEVICE_LIST_CHANGED")
        self.camera = QCamera(devices[index], self)
        opened = self.camera
        opened.errorOccurred.connect(
            lambda _code, text: self.error.emit(text) if self.camera is opened else None
        )
        self.selected_identity = {
            "camera_backend_type": "QT_MULTIMEDIA_PHYSICAL",
            "camera_id": bytes(devices[index].id().data()).hex(),
            "camera_display_name": devices[index].description(),
        }
        self.session.setVideoOutput(self.preview)
        self.session.setCamera(opened)
        opened.start()

    def capture(self, identifier: str) -> None:
        if (
            self.pending is not None
            or self.camera is None
            or not self.capture_device.isReadyForCapture()
        ):
            raise RuntimeError("CAMERA_NOT_READY")
        value = self.capture_device.capture()
        if value < 0:
            raise RuntimeError("CAMERA_CAPTURE_FAILED")
        self.pending = (value, identifier)

    def _captured(self, value: int, image: QImage) -> None:
        if self.pending is not None and self.pending[0] == value:
            identifier = self.pending[1]
            self.pending = None
            self.frame.emit(identifier, image.copy())

    def close(self) -> None:
        self.pending = None
        if self.camera is not None:
            closing = self.camera
            self.camera = None
            closing.stop()
            self.session.setCamera(None)  # type: ignore[arg-type]  # Qt accepts null to detach
            closing.deleteLater()


class FakeCamera(CameraBase):
    """Synthetic pixels for CPU tests/demo, never physical camera evidence."""

    def __init__(self) -> None:
        super().__init__()
        self.opened = False
        self.captures = 0
        self.failure: str | None = None
        self.generation = 0

    def devices(self) -> list[str]:
        return ["FakeCamera（CPU 模擬，非影像辨識）"]

    def identity(self) -> dict[str, Any]:
        return {
            "camera_backend_type": "FAKE",
            "camera_id": "fake-camera-0",
            "camera_display_name": self.devices()[0],
        }

    def ready(self) -> bool:
        return self.opened and self.failure is None

    def open(self, index: int) -> None:
        if index != 0:
            raise RuntimeError("CAMERA_UNAVAILABLE")
        self.opened = True

    def capture(self, identifier: str) -> None:
        if not self.opened or self.failure:
            raise RuntimeError(self.failure or "CAMERA_DISCONNECTED")
        self.captures += 1
        image = QImage(64, 48, QImage.Format.Format_RGB32)
        image.fill(QColor("red" if self.captures % 2 else "blue"))
        generation = self.generation
        QTimer.singleShot(
            0,
            lambda: (
                self.frame.emit(identifier, image)
                if self.opened and generation == self.generation
                else None
            ),
        )

    def close(self) -> None:
        self.opened = False
        self.generation += 1

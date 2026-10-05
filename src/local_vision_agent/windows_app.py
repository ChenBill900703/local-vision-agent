"""Single-window native application. Default CPU demo cannot load the real model."""

import argparse
import json
import os
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any

from PySide6.QtCore import QLockFile, Qt, QThread, QTimer, Signal, Slot
from PySide6.QtGui import QCloseEvent, QFont, QFontDatabase, QImage, QPixmap
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .app_camera import CameraBase, FakeCamera, QtCamera
from .app_controller import AppController, AppState, SessionLimits
from .app_export import call_rows, export_bundle
from .app_export_schema import RATINGS
from .app_session import AnalysisSession, PersistentAnalysisSession, session_identity
from .app_storage import AppStorage
from .app_webcam_record import WebcamRecord
from .app_worker import AnalysisWorker, AppRequest, FakeAnalysisSession, timestamp
from .internvl_contract import RuntimeConfig, load_runtime_config

_font_family: str | None = None


def chinese_font() -> QFont:
    """Use an existing Windows font, including under Qt's offscreen test plugin."""
    global _font_family
    if _font_family is None:
        path = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts/msjh.ttc"
        if path.is_file():
            identifier = QFontDatabase.addApplicationFont(str(path))
            families = QFontDatabase.applicationFontFamilies(identifier)
            if families:
                _font_family = families[0]
        if _font_family is None:
            _font_family = "Microsoft JhengHei"
    return QFont(_font_family, 10)


class MainWindow(QMainWindow):
    analyze_requested = Signal(object)
    preview_requested = Signal(str, str)
    shutdown_requested = Signal()

    def __init__(
        self,
        session: AnalysisSession,
        storage: AppStorage,
        config: RuntimeConfig,
        *,
        camera: CameraBase | None = None,
        demo: bool = False,
        session_limits: SessionLimits | None = None,
    ) -> None:
        super().__init__()
        self.setFont(chinese_font())
        self.storage = storage
        self.storage_lock = QLockFile(str(storage.root / ".application.lock"))
        if not self.storage_lock.tryLock(0):
            raise RuntimeError("APPLICATION_STORAGE_ALREADY_IN_USE")
        self.storage.purge_ephemeral()
        self.session_limits = session_limits or SessionLimits()
        self.controller = AppController()
        self.config = config
        self.selected: Path | None = None
        self.preview_id: str | None = None
        self.preview_path: Path | None = None
        self.active_request: AppRequest | None = None
        self.webcam_record: WebcamRecord | None = None
        self.webcam_records: list[WebcamRecord] = []
        self.selected_record: str | None = None
        self.stop_reason = "USER_STOP"
        self.capture_started = 0.0
        self.dispatched = self.camera_open = self.shutdown_sent = self.shutdown_done = False
        self.setWindowTitle("本地影像理解 Agent" + (" — CPU 模擬／非辨識結果" if demo else ""))
        self.resize(1100, 800)
        self.image_preview = QLabel("選擇 JPG/PNG，或開啟 Webcam")
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setMinimumSize(400, 250)
        self.video_preview = QVideoWidget()
        self.video_preview.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
        self.preview_stack = QStackedWidget()
        self.preview_stack.addWidget(self.image_preview)
        self.preview_stack.addWidget(self.video_preview)
        self.camera = camera or QtCamera(self.video_preview)
        self.camera.frame.connect(self._frame)
        self.camera.error.connect(self._camera_error)
        self.open_image = QPushButton("開啟圖片")
        self.analyze_button = QPushButton("開始分析")
        self.devices = QComboBox()
        self.devices.addItems(self.camera.devices())
        self.open_camera = QPushButton("開啟 Webcam")
        self.start_auto = QPushButton("開始自動分析")
        self.stop_auto = QPushButton("停止自動分析")
        self.close_camera = QPushButton("關閉 Webcam")
        self.interval = QSpinBox()
        self.interval.setRange(3, 30)
        self.interval.setValue(self.session_limits.interval_s)
        self.interval.setSuffix(" 秒")
        self.save_frame = QCheckBox("保存已分析的 Webcam 影像")
        self.status = QLabel(
            f"IDLE；上限{self.session_limits.max_frames}張／"
            f"{self.session_limits.max_duration_s}秒；模型服務最長30分鐘，不自動重載。"
        )
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.details = QTextEdit()
        self.details.setReadOnly(True)
        self.review_rating = QComboBox()
        self.review_rating.addItems(list(RATINGS))
        self.review_note = QTextEdit()
        self.review_note.setMaximumHeight(75)
        self.review_note.setPlaceholderText("作者工程可用性評閱；非真值或正確率")
        self.review_save = QPushButton("儲存人工評閱")
        self.review_save.clicked.connect(self._save_review)
        self.open_record = QPushButton("開啟選取紀錄")

        self.export_buttons: list[QPushButton] = []
        self.history = QTableWidget(0, 10)
        self.open_record.clicked.connect(
            lambda: self._history_selected(self.history.currentRow(), 0)
        )
        self.history.setHorizontalHeaderLabels(
            ["時間", "來源", "ID", "狀態", "呼叫", "秒", "覆蓋", "紀錄", "人工評閱", "備註"]
        )
        self.history.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.history.cellClicked.connect(self._history_selected)
        layout = QVBoxLayout()
        layout.addWidget(self.preview_stack)
        for controls in (
            [self.open_image, self.analyze_button],
            [
                self.devices,
                self.open_camera,
                self.start_auto,
                self.stop_auto,
                self.close_camera,
                QLabel("分析完成後等待："),
                self.interval,
            ],
            [self.save_frame],
        ):
            row = QHBoxLayout()
            for control in controls:
                row.addWidget(control)
            layout.addLayout(row)
        for widget in (self.status, self.output):
            layout.addWidget(widget)
        analysis_view = QWidget()
        analysis_view.setLayout(layout)
        history_layout = QVBoxLayout()
        history_layout.addWidget(self.history)
        history_layout.addWidget(self.open_record)
        history_layout.addWidget(self.review_rating)
        history_layout.addWidget(self.review_note)
        history_layout.addWidget(self.review_save)
        export_row = QHBoxLayout()
        for label, kind in (
            ("匯出分析摘要 CSV", "analysis_summary"),
            ("匯出模型呼叫 CSV", "model_calls"),
            ("匯出 Webcam Session CSV", "webcam_sessions"),
            ("匯出全部 CSV", "all"),
        ):
            button = QPushButton(label)
            button.clicked.connect(lambda _checked=False, selected=kind: self._export(selected))
            self.export_buttons.append(button)
            export_row.addWidget(button)
        history_layout.addLayout(export_row)
        self.history_status = QLabel("JSON 為原始紀錄；CSV 是衍生資料。")
        self.history_status.setWordWrap(True)
        history_layout.addWidget(self.history_status)
        history_view = QWidget()
        history_view.setLayout(history_layout)
        self.tabs = QTabWidget()
        self.tabs.addTab(analysis_view, "分析")
        self.tabs.addTab(self.details, "詳細資料")
        self.tabs.addTab(history_view, "歷史紀錄")
        self.setCentralWidget(self.tabs)
        self.open_image.clicked.connect(self._choose)
        self.analyze_button.clicked.connect(self.analyze_manual)
        self.open_camera.clicked.connect(self._open_camera)
        self.start_auto.clicked.connect(self._start_auto)
        self.stop_auto.clicked.connect(self.stop_webcam)
        self.close_camera.clicked.connect(self.stop_webcam)
        self.analysis_thread = QThread(self)
        self.worker = AnalysisWorker(session, storage, config)
        self.worker.moveToThread(self.analysis_thread)
        self.analyze_requested.connect(self.worker.analyze, Qt.ConnectionType.QueuedConnection)
        self.preview_requested.connect(
            self.worker.prepare_preview, Qt.ConnectionType.QueuedConnection
        )
        self.shutdown_requested.connect(self.worker.close, Qt.ConnectionType.QueuedConnection)
        self.worker.result.connect(self._result)
        self.worker.preview.connect(self._preview)
        self.worker.error.connect(self._error)
        self.worker.closed.connect(self._worker_closed)
        self.worker.closed.connect(self.analysis_thread.quit)
        self.analysis_thread.finished.connect(self.worker.deleteLater)
        self.analysis_thread.finished.connect(self._thread_finished)
        self.analysis_thread.start()
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self._tick)
        self.timer.start()
        self._refresh_history()
        self._controls()

    def _controls(self) -> None:
        c = self.controller
        idle = not (c.busy or c.auto or c.closing or self.preview_id)
        self.open_image.setEnabled(idle)
        self.analyze_button.setEnabled(idle and self.selected is not None)
        self.open_camera.setEnabled(idle and self.devices.count() > 0)
        self.start_auto.setEnabled(idle and self.camera_open and self.camera.ready())
        self.devices.setEnabled(idle and not self.camera_open)
        self.interval.setEnabled(idle)
        self.save_frame.setEnabled(idle)
        self.stop_auto.setEnabled(self.camera_open and not c.closing)
        self.close_camera.setEnabled(self.camera_open and not c.closing)
        self.review_save.setEnabled(idle and self.selected_record is not None)
        for button in self.export_buttons:
            button.setEnabled(idle)

    def _choose(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "開啟圖片", "", "圖片 (*.jpg *.jpeg *.png)")
        if path:
            self.select_path(Path(path))

    def select_path(self, path: Path) -> None:
        if (
            self.controller.busy
            or self.controller.auto
            or self.preview_id
            or self.controller.closing
        ):
            return
        self.controller.recover()
        self.preview_id = "preview-" + session_identity()
        self.preview_path = path
        self.preview_requested.emit(self.preview_id, str(path))
        self._controls()

    @Slot(str, object)
    def _preview(self, identifier: str, data: bytes) -> None:
        if identifier != self.preview_id or self.controller.closing:
            return
        image = QImage.fromData(data)
        if image.isNull():
            self._error(identifier, "INVALID_PREVIEW")
            return
        self.selected = self.preview_path
        self.preview_id = None
        self.controller.select_image()
        self._show_image(image)
        self.status.setText("圖片已驗證，可開始分析。")
        self._controls()

    def _show_image(self, image: QImage) -> None:
        pixmap = QPixmap.fromImage(image)
        self.image_preview.setPixmap(
            pixmap.scaled(
                self.image_preview.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        self.preview_stack.setCurrentIndex(0)

    @Slot()
    def analyze_manual(self) -> None:
        if (
            self.selected is None
            or self.preview_id
            or self.controller.busy
            or self.controller.auto
            or self.controller.closing
        ):
            return
        self.controller.stopping = False
        self.controller.select_image()
        identifier = self.controller.request("IMAGE")
        if identifier:
            try:
                directory = self.storage.allocate(identifier)
            except (OSError, ValueError) as exc:
                self._error(identifier, "LOCAL_STORAGE_FAILED: " + str(exc))
                return
            self._submit(
                AppRequest(
                    identifier,
                    "IMAGE",
                    self.selected,
                    directory,
                    timestamp(),
                    self.controller.session_id,
                )
            )

    def _open_camera(self) -> None:
        try:
            self.controller.recover()
            self.camera.open(self.devices.currentIndex())
            self.camera_open = True
            self.controller.state = AppState.WEBCAM_PREVIEW
            self.preview_stack.setCurrentIndex(1)
            self.status.setText("Webcam 預覽；尚未送入分析。")
        except Exception as exc:  # noqa: BLE001 -- readable local hardware error
            self._camera_error(str(exc))
        self._controls()

    def _start_auto(self) -> None:
        if not self.camera_open:
            return
        self.controller.start_auto(
            SessionLimits(
                interval_s=self.interval.value(),
                max_frames=self.session_limits.max_frames,
                max_duration_s=self.session_limits.max_duration_s,
            )
        )
        try:
            self.webcam_record = WebcamRecord(
                self.storage,
                self.controller.session_id,
                self.camera.identity(),
                self.controller.limits,
            )
            self.webcam_records.append(self.webcam_record)
        except (OSError, ValueError) as exc:
            self._camera_error("SESSION_RECORD_FAILED: " + str(exc))
            return
        self.stop_reason = "USER_STOP"
        self._tick()

    def _tick(self) -> None:
        c = self.controller
        if c.auto and c.clock() >= c.deadline:
            self.stop_reason = "SESSION_DURATION_LIMIT"
            self.stop_webcam()
        if (
            c.busy
            and not self.dispatched
            and self.active_request is not None
            and c.clock() - self.capture_started >= self.config.limits.per_call_timeout_s
        ):
            self._camera_error("CAMERA_CAPTURE_TIMEOUT")
        if c.auto and not c.busy:
            identifier = c.request("WEBCAM")
            if identifier:
                try:
                    directory = self.storage.allocate(identifier)
                    self.active_request = AppRequest(
                        identifier,
                        "WEBCAM",
                        directory / "frame.png",
                        directory,
                        timestamp(),
                        c.session_id,
                        self.save_frame.isChecked(),
                    )
                    self.storage.save(
                        directory, {"save_frame": self.save_frame.isChecked()}, "retention.json"
                    )
                    self.dispatched = False
                    self.capture_started = c.clock()
                    self.camera.capture(identifier)
                except Exception as exc:  # noqa: BLE001 -- no storage/capture retry
                    self._camera_error(str(exc))
            elif c.stopping:
                self.stop_reason = (
                    "MAX_FRAME_LIMIT"
                    if c.frame_count >= c.limits.max_frames
                    else "SESSION_DURATION_LIMIT"
                )
                self.stop_webcam()
        self._controls()

    @Slot(str, object)
    def _frame(self, identifier: str, image: QImage) -> None:
        request = self.active_request
        if request is None or identifier != self.controller.pending or self.dispatched:
            return
        if (
            self.controller.stopping
            or self.controller.closing
            or self.controller.clock() >= self.controller.deadline
        ):
            self.stop_webcam()
            return
        try:
            if (
                image.isNull()
                or image.width() * image.height()
                > self.config.source_image_limits.max_decoded_pixels
            ):
                raise ValueError("INVALID_CAMERA_FRAME")
            if self.webcam_record is not None:
                self.webcam_record.captured(identifier)
            if isinstance(self.camera, FakeCamera):
                self._show_image(image)
            self._submit(replace(request, frame=image.copy(), captured_at=timestamp()))
        except Exception as exc:  # noqa: BLE001 -- preserve capture failure, no retry
            self._camera_error(str(exc))

    def _submit(self, request: AppRequest) -> None:
        if request.source == "WEBCAM" and self.webcam_record is not None:
            self.webcam_record.submitted(request.identifier)
        self.active_request = request
        self.dispatched = True
        self.status.setText("載入／分析中；可停止新工作，當次操作依既有上限完成。")
        self.analyze_requested.emit(request)
        self._controls()

    @Slot(str, object)
    def _result(self, identifier: str, data: dict[str, Any]) -> None:
        if not self.controller.complete(identifier, data["metadata"]["status"] == "complete"):
            return
        self.dispatched = False
        self.active_request = None
        self._display(data)
        self._refresh_history()
        if not self.controller.auto and self.controller.state in (AppState.ERROR, AppState.IDLE):
            self.stop_reason = data["metadata"].get("stop_reason", "ANALYSIS_FAILED")
            self.stop_webcam()
        if self.controller.auto:
            self.controller.next_due = self.controller.clock() + self.controller.limits.interval_s
        self._controls()

    def _display(self, data: dict[str, Any]) -> None:
        metadata = data["metadata"]
        fields = {
            "來源": "source",
            "狀態": "status",
            "ID": "input_id",
            "時間": "timestamp",
            "呼叫": "calls",
            "tokens": "tokens",
            "截斷": "truncated",
            "驗證覆蓋": "coverage",
            "停止原因": "stop_reason",
            "總延遲秒": "latency_s",
            "allocated MiB": "allocated_mib",
            "reserved MiB": "reserved_mib",
        }
        summary = "\n".join(
            f"{label}：{metadata[key] if metadata.get(key) is not None else 'N/A'}"
            for label, key in fields.items()
        )
        self.output.setPlainText(summary + "\n\n" + data["report_text"])
        self.status.setText(str(metadata.get("status", "N/A")))
        report = data.get("report", {})
        detail = {
            "Agent State Trace": report.get("states", []),
            "model_calls": call_rows(data),
            "candidate_claims": report.get("claims", []),
            "stop_reason": report.get("stop_reason", metadata.get("stop_reason")),
            "truncation": [x for x in call_rows(data) if x.get("truncated")],
            "raw_record": data,
        }
        self.details.setPlainText(json.dumps(detail, ensure_ascii=False, indent=2))

    def _refresh_history(self) -> None:
        records = self.storage.history()
        self.history.setRowCount(len(records))
        for row, (reference, data) in enumerate(records):
            m = data["metadata"] if data else {"status": "紀錄損壞"}
            for col, key in enumerate(
                ("timestamp", "source", "input_id", "status", "calls", "latency_s", "coverage")
            ):
                self.history.setItem(
                    row, col, QTableWidgetItem(str(m[key]) if m.get(key) is not None else "N/A")
                )
            self.history.setItem(row, 7, QTableWidgetItem(reference))
            try:
                review = self.storage.review(reference) if data else {}
            except (OSError, ValueError):
                review = {"human_rating": "REVIEW_READ_FAILED"}
            self.history.setItem(
                row, 8, QTableWidgetItem(str(review.get("human_rating", "NOT_REVIEWED")))
            )
            self.history.setItem(row, 9, QTableWidgetItem(str(review.get("human_note", ""))))

    def _history_selected(self, row: int, _column: int) -> None:
        item = self.history.item(row, 7)
        if item is not None:
            try:
                self._display(self.storage.load(item.text()))
                review = self.storage.review(item.text())
                self.selected_record = item.text()
                self.review_rating.setCurrentText(review["human_rating"])
                self.review_note.setPlainText(review["human_note"])
                self._controls()
            except (OSError, ValueError) as exc:
                self.status.setText("無法讀取紀錄：" + str(exc))

    @Slot()
    def _save_review(self) -> None:
        if self.selected_record is None or self.controller.busy or self.controller.auto:
            return
        try:
            self.storage.update_review(
                self.selected_record,
                self.review_rating.currentText(),
                self.review_note.toPlainText(),
            )
            self._refresh_history()
            self.history_status.setText("已儲存作者工程評閱；原始回答與 Agent 狀態保持不變。")
        except (OSError, ValueError) as exc:
            self.history_status.setText("評閱儲存失敗：" + str(exc))

    def _export(self, kind: str) -> None:
        if self.controller.busy or self.controller.auto or self.controller.closing:
            return
        try:
            target = export_bundle(self.storage, kind)
            self.history_status.setText("已匯出至：" + str(target))
        except (OSError, ValueError) as exc:
            self.history_status.setText("匯出失敗：" + str(exc))

    @Slot(str, str)
    def _error(self, identifier: str, message: str) -> None:
        if identifier == self.preview_id:
            self.preview_id = None
            self.selected = None
            self.controller.state = AppState.ERROR
        elif identifier == self.controller.pending:
            self.controller.complete(identifier, False)
            self.dispatched = False
            self.active_request = None
            self.stop_reason = message
            self.stop_webcam()
        else:
            return
        self.status.setText("操作失敗：" + message)
        self._controls()

    @Slot(str)
    def _camera_error(self, message: str) -> None:
        self.stop_reason = "CAMERA_ERROR: " + message
        try:
            directory = self.storage.allocate("camera-error-" + session_identity())
            self.storage.save(
                directory,
                {
                    "error": message,
                    "timestamp": timestamp(),
                    "session_id": self.controller.session_id,
                },
                "error.json",
            )
        except (OSError, ValueError) as exc:
            message += "; ERROR_LOG_WRITE_FAILED: " + str(exc)
        finally:
            self.stop_webcam()
            self.status.setText("Webcam 已停止：" + message)

    @Slot()
    def stop_webcam(self) -> None:
        self.controller.stop()
        self.camera.close()
        self.camera_open = False
        if self.webcam_record is not None:
            try:
                self.webcam_record.end("APP_CLOSE" if self.controller.closing else self.stop_reason)
            except (OSError, ValueError) as exc:
                self.status.setText("Session 紀錄儲存失敗：" + str(exc))
        if self.controller.pending and not self.dispatched:
            request = self.active_request
            self.controller.complete(self.controller.pending, True)
            if request is not None:
                try:
                    self.storage.remove_frame(request.directory)
                except (OSError, ValueError) as exc:
                    self.status.setText("暫存影像清理失敗：" + str(exc))
            self.active_request = None
        self._controls()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.shutdown_done:
            event.accept()
            return
        event.ignore()
        if not self.shutdown_sent:
            self.controller.close()
            self.stop_webcam()
            self.timer.stop()
            self.shutdown_sent = True
            self.shutdown_requested.emit()
            self.status.setText("正在安全關閉；等待當次有界操作與清理。")

    @Slot(object)
    def _worker_closed(self, cleanup: dict[str, Any]) -> None:
        for record in self.webcam_records:
            try:
                record.cleanup(cleanup)
            except (OSError, ValueError) as exc:
                cleanup["session_record_error"] = str(exc)
        self.status.setText("清理結果：" + json.dumps(cleanup, ensure_ascii=False))

    @Slot()
    def _thread_finished(self) -> None:
        self.storage_lock.unlock()
        self.shutdown_done = True
        self.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Local Windows application; default explicit CPU demo"
    )
    parser.add_argument("--authorize-development-gpu", action="store_true")
    parser.add_argument("--storage", type=Path, default=Path("artifacts/windows-app"))
    parser.add_argument("--max-frames", type=int, default=20)
    parser.add_argument("--max-session-seconds", type=int, default=1800)
    parser.add_argument("--interval-seconds", type=int, default=5)
    args = parser.parse_args()
    project = Path(__file__).resolve().parents[2]
    config = load_runtime_config(project / "configs/agent_internvl_development.toml")
    if not args.storage.resolve().is_relative_to((project / "artifacts").resolve()):
        raise ValueError("APPLICATION_STORAGE_MUST_BE_IGNORED_ARTIFACTS")
    storage = AppStorage(args.storage)
    session_limits = SessionLimits(args.interval_seconds, args.max_frames, args.max_session_seconds)
    session: AnalysisSession = (
        PersistentAnalysisSession(
            project / "artifacts/internvl3-20260928", storage.root / session_identity(), config
        )
        if args.authorize_development_gpu
        else FakeAnalysisSession(config)
    )
    app = QApplication(sys.argv[:1])
    window = MainWindow(
        session,
        storage,
        config,
        camera=None if args.authorize_development_gpu else FakeCamera(),
        demo=not args.authorize_development_gpu,
        session_limits=session_limits,
    )
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

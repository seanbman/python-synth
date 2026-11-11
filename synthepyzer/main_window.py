"""Main Synthepyzer desktop window."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QDockWidget,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .binding import StateController
from .panels import LayerPanel, MasterPanel, PresetBrowser
from .preset import PresetError, default_preset, load_preset, save_preset
from .state import default_layer


class SynthepyzerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.controller = StateController(default_preset(), self)
        self.preset_path: str | None = None
        self.preset_name = "Init Patch"
        self._build_workspace()
        self._build_menus()
        self.controller.dirtyChanged.connect(lambda _dirty: self._update_title())
        self._update_title()

    def _build_workspace(self) -> None:
        self.setMinimumSize(1000, 720)
        self.resize(1180, 820)
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(8, 8, 8, 8)

        intro = QLabel("Synthepyzer workspace · select a layer, shape its signal path, then save the patch")
        layout.addWidget(intro)
        self.tabs = QTabWidget()
        self.layer_panels: list[LayerPanel] = []
        for index, title in enumerate(("Layer A", "Layer B")):
            panel = LayerPanel(index, self.controller)
            self.layer_panels.append(panel)
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(panel)
            self.tabs.addTab(scroll, title)
        layout.addWidget(self.tabs, 1)
        layout.addWidget(MasterPanel(self.controller))
        self.setCentralWidget(central)

        self.browser = PresetBrowser()
        self.browser.loadRequested.connect(self._load_path)
        self.browser.folderRequested.connect(self._choose_preset_folder)
        self.preset_dock = QDockWidget("Preset Browser", self)
        self.preset_dock.setObjectName("PresetBrowserDock")
        self.preset_dock.setWidget(self.browser)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.preset_dock)

    def _action(self, menu, text: str, slot, shortcut: str | None = None, enabled: bool = True):
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        action.setEnabled(enabled)
        action.triggered.connect(slot)
        menu.addAction(action)
        return action

    def _build_menus(self) -> None:
        file_menu = self.menuBar().addMenu("File")
        self._action(file_menu, "New", self._new_preset, "Ctrl+N")
        self._action(file_menu, "Open…", self._open_preset, "Ctrl+O")
        self._action(file_menu, "Save", self._save_preset, "Ctrl+S")
        self._action(file_menu, "Save As…", self._save_as_preset, "Ctrl+Shift+S")
        file_menu.addSeparator()
        self._action(file_menu, "Quit", self.close, "Ctrl+Q")

        edit_menu = self.menuBar().addMenu("Edit")
        undo = self.controller.undo_stack.createUndoAction(self, "Undo")
        undo.setShortcut(QKeySequence.StandardKey.Undo)
        edit_menu.addAction(undo)
        redo = self.controller.undo_stack.createRedoAction(self, "Redo")
        redo.setShortcut(QKeySequence.StandardKey.Redo)
        edit_menu.addAction(redo)
        edit_menu.addSeparator()
        self._action(edit_menu, "Reset Active Layer", self._reset_active_layer)
        self._action(edit_menu, "Reset Patch", self._new_preset)

        view_menu = self.menuBar().addMenu("View")
        view_menu.addAction(self.preset_dock.toggleViewAction())
        view_menu.addSeparator()
        self._action(view_menu, "Expand All Sections", lambda: self._set_sections(True))
        self._action(view_menu, "Collapse All Sections", lambda: self._set_sections(False))

        audio_menu = self.menuBar().addMenu("Audio")
        self._action(audio_menu, "Output Device…", self._backend_unavailable, enabled=False)
        self._action(audio_menu, "Sample Rate", self._backend_unavailable, enabled=False)
        self._action(audio_menu, "Buffer Size", self._backend_unavailable, enabled=False)
        audio_menu.addSeparator()
        self._action(audio_menu, "Audio Status", self._backend_unavailable, enabled=False)

        midi_menu = self.menuBar().addMenu("MIDI")
        self._action(midi_menu, "Input Device…", self._backend_unavailable, enabled=False)
        midi_menu.addSeparator()
        self._action(midi_menu, "All Notes Off / Panic", self._panic)
        self._action(midi_menu, "MIDI Status", self._backend_unavailable, enabled=False)

        help_menu = self.menuBar().addMenu("Help")
        self._action(help_menu, "Open Manual", self._open_manual)
        self._action(help_menu, "About Synthepyzer", self._about)

    def _confirm_discard(self) -> bool:
        if not self.controller.dirty:
            return True
        answer = QMessageBox.question(
            self,
            "Unsaved changes",
            "The current patch has unsaved changes. Discard them?",
            QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        return answer == QMessageBox.StandardButton.Discard

    def _new_preset(self) -> None:
        if not self._confirm_discard():
            return
        self.controller.replace_state(default_preset())
        self.preset_path = None
        self.preset_name = "Init Patch"
        self.controller.mark_saved()

    def _open_preset(self) -> None:
        if not self._confirm_discard():
            return
        path, _ = QFileDialog.getOpenFileName(self, "Open Synthepyzer preset", "", "Synthepyzer presets (*.spyzr)")
        if path:
            self._load_path(path)

    def _load_path(self, path: str) -> None:
        try:
            payload = load_preset(path)
        except PresetError as exc:
            QMessageBox.warning(self, "Could not open preset", str(exc))
            return
        self.controller.replace_state(payload)
        self.preset_path = path
        self.preset_name = payload.get("meta", {}).get("name", Path(path).stem)
        self.controller.mark_saved()
        self.browser.set_directory(Path(path).parent)

    def _save_preset(self) -> None:
        if self.preset_path:
            self._save_path(self.preset_path)
        else:
            self._save_as_preset()

    def _save_as_preset(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save Synthepyzer preset", "Init Patch.spyzr", "Synthepyzer presets (*.spyzr)")
        if path:
            if not path.endswith(".spyzr"):
                path += ".spyzr"
            self._save_path(path)

    def _save_path(self, path: str) -> None:
        try:
            payload = self.controller.state
            payload.setdefault("meta", {})["name"] = self.preset_name
            save_preset(path, payload)
        except PresetError as exc:
            QMessageBox.warning(self, "Could not save preset", str(exc))
            return
        self.preset_path = path
        self.controller.mark_saved()
        self.browser.set_directory(Path(path).parent)

    def _choose_preset_folder(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Choose preset folder")
        if directory:
            self.browser.set_directory(directory)

    def _reset_active_layer(self) -> None:
        index = self.tabs.currentIndex()
        state = self.controller.state
        replacement = default_layer("A" if index == 0 else "B")
        current = state["layers"][index]
        for key, value in replacement.items():
            self.controller.set(("layers", str(index), key), value, "Reset active layer")

    def _set_sections(self, expanded: bool) -> None:
        for panel in self.layer_panels:
            panel.set_all_expanded(expanded)

    def _backend_unavailable(self) -> None:
        QMessageBox.information(self, "Backend not connected", "Audio and MIDI device support is not connected yet.")

    def _panic(self) -> None:
        self.statusBar().showMessage("All Notes Off requested; MIDI backend is not connected yet.", 5000)

    def _open_manual(self) -> None:
        manual = Path(__file__).resolve().parents[1] / "docs" / "index.html"
        try:
            subprocess.Popen(["xdg-open", str(manual)])
        except OSError:
            self.statusBar().showMessage(f"Manual: {manual}", 5000)

    def _about(self) -> None:
        QMessageBox.about(self, "About Synthepyzer", "Synthepyzer\nA two-layer MIDI-ready subtractive synth workspace.")

    def _update_title(self) -> None:
        marker = "*" if self.controller.dirty else ""
        self.setWindowTitle(f"{marker}{self.preset_name} · Synthepyzer")

    def closeEvent(self, event) -> None:
        if self._confirm_discard():
            event.accept()
        else:
            event.ignore()


def run() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    window = SynthepyzerWindow()
    window.show()
    return app.exec()

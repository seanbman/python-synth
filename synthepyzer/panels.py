"""Panels that compose the Synthepyzer workspace."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .binding import StateController
from .controls import CollapsibleSection, ParameterControl
from .parameters import AMP_ENVELOPE, FILTER, LFO, LAYER_UTILITY, MASTER, MIXER, OSCILLATOR, ParameterSpec


def add_control(layout, spec: ParameterSpec, controller: StateController, layer_index: int | None = None):
    control = ParameterControl(spec)
    controller.bind(spec.path(layer_index), control)
    control.resetRequested.connect(lambda c=control, s=spec, i=layer_index: c.set_value(s.default))
    # The reset action is a real state edit so it participates in undo/redo.
    control.resetRequested.connect(lambda s=spec, i=layer_index: controller.set(s.path(i), s.default, f"Reset {s.label}"))
    layout.addWidget(control)
    return control


class LayerPanel(QWidget):
    def __init__(self, layer_index: int, controller: StateController, parent: QWidget | None = None):
        super().__init__(parent)
        self.layer_index = layer_index
        self.controller = controller
        self.sections: list[CollapsibleSection] = []
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        utility = QGroupBox("Layer utility")
        utility_layout = QHBoxLayout(utility)
        for spec in LAYER_UTILITY:
            add_control(utility_layout, spec, controller, layer_index)
        root.addWidget(utility)

        oscillators = CollapsibleSection("Oscillators")
        self.sections.append(oscillators)
        for number, osc_id in ((1, "osc1"), (2, "osc2")):
            group = QGroupBox(f"Oscillator {number}")
            group_layout = QHBoxLayout(group)
            for spec in OSCILLATOR:
                scoped = ParameterSpec(
                    key=f"oscillators.{osc_id}.{spec.key}",
                    label=spec.label,
                    control=spec.control,
                    minimum=spec.minimum,
                    maximum=spec.maximum,
                    default=spec.default,
                    step=spec.step,
                    display=spec.display,
                    choices=spec.choices,
                )
                add_control(group_layout, scoped, controller, layer_index)
            oscillators.body_layout.addWidget(group)
        root.addWidget(oscillators)

        for title, specs in (("Mixer", MIXER), ("Filter", FILTER), ("Amp Envelope", AMP_ENVELOPE), ("LFO", LFO)):
            section = CollapsibleSection(title)
            self.sections.append(section)
            for spec in specs:
                add_control(section.body_layout, spec, controller, layer_index)
            root.addWidget(section)
        root.addStretch(1)

    def set_all_expanded(self, expanded: bool) -> None:
        for section in self.sections:
            section.set_expanded(expanded)


class MasterPanel(QGroupBox):
    def __init__(self, controller: StateController, parent: QWidget | None = None):
        super().__init__("Master output", parent)
        layout = QHBoxLayout(self)
        for spec in MASTER:
            add_control(layout, spec, controller)
        status = QLabel("Audio engine: not connected")
        status.setToolTip("Audio output will be connected in the audio backend milestone.")
        layout.addStretch(1)
        layout.addWidget(status)


class PresetBrowser(QWidget):
    loadRequested = pyqtSignal(str)
    folderRequested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.directory: Path | None = None
        layout = QVBoxLayout(self)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search presets")
        self.search.textChanged.connect(self._filter)
        layout.addWidget(self.search)
        self.list = QListWidget()
        self.list.itemDoubleClicked.connect(lambda item: self.loadRequested.emit(item.data(Qt.ItemDataRole.UserRole)))
        layout.addWidget(self.list)
        buttons = QHBoxLayout()
        self.open_folder = QPushButton("Open Folder")
        self.open_folder.clicked.connect(self.folderRequested)
        self.refresh = QPushButton("Refresh")
        self.refresh.clicked.connect(self.refresh_list)
        self.load = QPushButton("Load Selected")
        self.load.clicked.connect(self._load_selected)
        buttons.addWidget(self.open_folder)
        buttons.addWidget(self.refresh)
        buttons.addWidget(self.load)
        layout.addLayout(buttons)

    def set_directory(self, directory: str | Path | None) -> None:
        self.directory = Path(directory) if directory else None
        self.refresh_list()

    def refresh_list(self) -> None:
        self.list.clear()
        if not self.directory or not self.directory.exists():
            item = self.list.addItem("Choose a preset folder")
            self.list.item(0).setFlags(self.list.item(0).flags() & ~Qt.ItemFlag.ItemIsEnabled)
            return
        for path in sorted(self.directory.glob("*.spyzr")):
            item = self.list.addItem(path.stem)
            self.list.item(self.list.count() - 1).setData(Qt.ItemDataRole.UserRole, str(path))
        self._filter(self.search.text())

    def _filter(self, query: str) -> None:
        query = query.lower().strip()
        for row in range(self.list.count()):
            self.list.item(row).setHidden(bool(query) and query not in self.list.item(row).text().lower())

    def _load_selected(self) -> None:
        item = self.list.currentItem()
        if item and item.data(Qt.ItemDataRole.UserRole):
            self.loadRequested.emit(item.data(Qt.ItemDataRole.UserRole))

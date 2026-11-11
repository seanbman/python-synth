"""Panels that compose the Synthepyzer workspace."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
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
    """A compact 2-column instrument surface; every parameter stays on screen."""

    def __init__(self, layer_index: int, controller: StateController, parent: QWidget | None = None):
        super().__init__(parent)
        self.layer_index = layer_index
        self.controller = controller
        self.sections: list[CollapsibleSection] = []
        root = QGridLayout(self)
        root.setContentsMargins(5, 4, 5, 4)
        root.setHorizontalSpacing(8)
        root.setVerticalSpacing(5)
        root.setColumnStretch(0, 1)
        root.setColumnStretch(1, 1)

        utility = QGroupBox("Layer controls")
        utility_layout = QHBoxLayout(utility)
        utility_layout.setContentsMargins(5, 8, 5, 2)
        utility_layout.setSpacing(2)
        for spec in LAYER_UTILITY:
            add_control(utility_layout, spec, controller, layer_index)
        root.addWidget(utility, 0, 0, 1, 2)

        for number, osc_id in ((1, "osc1"), (2, "osc2")):
            section = CollapsibleSection(f"Oscillator {number}")
            self.sections.append(section)
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
                add_control(section.body_layout, scoped, controller, layer_index)
            root.addWidget(section, 1, number - 1)

        for row, column, title, specs in (
            (2, 0, "Filter", FILTER),
            (2, 1, "Amp envelope", AMP_ENVELOPE),
            (3, 0, "Mixer", MIXER),
            (3, 1, "LFO", LFO),
        ):
            section = CollapsibleSection(title)
            self.sections.append(section)
            for spec in specs:
                add_control(section.body_layout, spec, controller, layer_index)
            root.addWidget(section, row, column)

        for row in range(4):
            root.setRowStretch(row, 1)

    def set_all_expanded(self, expanded: bool) -> None:
        for section in self.sections:
            section.set_expanded(expanded)


class MasterPanel(QGroupBox):
    def __init__(self, controller: StateController, parent: QWidget | None = None):
        super().__init__("Master output", parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 2)
        layout.setSpacing(4)
        for spec in MASTER:
            add_control(layout, spec, controller)
        status = QLabel("Audio engine: not connected")
        status.setToolTip("Audio output will be connected in the audio backend milestone.")
        layout.addStretch(1)
        layout.addWidget(status)
        self.setMaximumHeight(116)


class PresetBrowser(QWidget):
    """Preset list with pages instead of hidden or visible scrolling."""

    loadRequested = pyqtSignal(str)
    folderRequested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.directory: Path | None = None
        self._presets: list[Path] = []
        self._matches: list[Path] = []
        self._page = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(5)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search presets")
        self.search.textChanged.connect(self._filter)
        layout.addWidget(self.search)

        self.list = QListWidget()
        self.list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list.itemDoubleClicked.connect(
            lambda item: self.loadRequested.emit(item.data(Qt.ItemDataRole.UserRole))
        )
        layout.addWidget(self.list, 1)

        pager = QHBoxLayout()
        self.previous_page = QPushButton("Previous")
        self.previous_page.clicked.connect(lambda: self._change_page(-1))
        self.page_label = QLabel()
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.next_page = QPushButton("Next")
        self.next_page.clicked.connect(lambda: self._change_page(1))
        pager.addWidget(self.previous_page)
        pager.addWidget(self.page_label, 1)
        pager.addWidget(self.next_page)
        layout.addLayout(pager)

        buttons = QHBoxLayout()
        self.open_folder = QPushButton("Open Folder")
        self.open_folder.clicked.connect(self.folderRequested)
        self.refresh = QPushButton("Refresh")
        self.refresh.clicked.connect(self.refresh_list)
        buttons.addWidget(self.open_folder, 1)
        buttons.addWidget(self.refresh, 1)
        layout.addLayout(buttons)
        self.load = QPushButton("Load Selected")
        self.load.clicked.connect(self._load_selected)
        layout.addWidget(self.load)
        self._show_page()

    def set_directory(self, directory: str | Path | None) -> None:
        self.directory = Path(directory) if directory else None
        self.refresh_list()

    def refresh_list(self) -> None:
        self._presets = (
            sorted(self.directory.glob("*.spyzr"))
            if self.directory and self.directory.exists()
            else []
        )
        self._filter(self.search.text())

    def _filter(self, query: str) -> None:
        query = query.lower().strip()
        self._matches = [
            path for path in self._presets if not query or query in path.stem.lower()
        ]
        self._page = 0
        self._show_page()

    def _page_size(self) -> int:
        row_height = max(30, self.list.fontMetrics().height() + 12, self.list.sizeHintForRow(0))
        return max(1, self.list.viewport().height() // row_height)

    def _show_page(self) -> None:
        page_size = self._page_size()
        count = len(self._matches)
        page_count = max(1, (count + page_size - 1) // page_size)
        self._page = max(0, min(self._page, page_count - 1))
        self.list.clear()

        for path in self._matches[self._page * page_size:(self._page + 1) * page_size]:
            item = QListWidgetItem(path.stem)
            item.setData(Qt.ItemDataRole.UserRole, str(path))
            item.setToolTip(str(path))
            self.list.addItem(item)

        if not self._matches:
            item = QListWidgetItem("Choose a preset folder" if not self.directory else "No matching presets")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            self.list.addItem(item)

        self.page_label.setText(f"{self._page + 1} / {page_count}")
        self.previous_page.setEnabled(self._page > 0)
        self.next_page.setEnabled(self._page + 1 < page_count)
        self.load.setEnabled(bool(self._matches))

    def _change_page(self, amount: int) -> None:
        self._page += amount
        self._show_page()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        QTimer.singleShot(0, self._show_page)

    def _load_selected(self) -> None:
        item = self.list.currentItem()
        if item and item.data(Qt.ItemDataRole.UserRole):
            self.loadRequested.emit(item.data(Qt.ItemDataRole.UserRole))

"""Small, accessible Qt controls used by the main synth workspace."""

from __future__ import annotations

from typing import Any

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QDial,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from .parameters import ParameterSpec, format_value


class ParameterControl(QWidget):
    valueChanged = pyqtSignal(object)
    resetRequested = pyqtSignal()

    def __init__(self, spec: ParameterSpec, parent: QWidget | None = None):
        super().__init__(parent)
        self.spec = spec
        self.parameter_label = spec.label
        self._updating = False

        root = QVBoxLayout(self)
        root.setContentsMargins(4, 4, 4, 4)
        root.setSpacing(2)
        title_row = QHBoxLayout()
        self.label = QLabel(spec.label)
        self.label.setToolTip(f"{spec.label}: adjust the current layer parameter")
        self.reset_button = QToolButton()
        self.reset_button.setText("↺")
        self.reset_button.setToolTip(f"Reset {spec.label}")
        self.reset_button.setAccessibleName(f"Reset {spec.label}")
        self.reset_button.clicked.connect(self.resetRequested)
        title_row.addWidget(self.label)
        title_row.addStretch(1)
        title_row.addWidget(self.reset_button)
        root.addLayout(title_row)

        if spec.control == "combo":
            self.editor = QComboBox()
            for value, label in spec.choices:
                self.editor.addItem(label, value)
            self.editor.currentIndexChanged.connect(self._emit_combo)
        elif spec.control == "spin":
            self.editor = QSpinBox()
            self.editor.setRange(int(spec.minimum), int(spec.maximum))
            self.editor.setSingleStep(int(spec.step))
            self.editor.valueChanged.connect(self._emit_value)
        elif spec.control == "toggle":
            self.editor = QPushButton()
            self.editor.setCheckable(True)
            self.editor.toggled.connect(self._emit_toggle)
        else:
            if spec.control == "slider":
                self.editor = QSlider(Qt.Orientation.Horizontal)
            else:
                self.editor = QDial()
                self.editor.setNotchesVisible(True)
            self._steps = max(1, round((spec.maximum - spec.minimum) / spec.step))
            self.editor.setRange(0, self._steps)
            self.editor.valueChanged.connect(self._emit_range)

        self.editor.setAccessibleName(spec.label)
        self.editor.setToolTip(self.label.toolTip())
        root.addWidget(self.editor)
        self.value_label = QLabel()
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.value_label)
        self.setMinimumWidth(86)

    def set_value(self, value: Any) -> None:
        self._updating = True
        try:
            if self.spec.control == "combo":
                index = self.editor.findData(value)
                self.editor.setCurrentIndex(max(0, index))
            elif self.spec.control == "spin":
                self.editor.setValue(int(value))
            elif self.spec.control == "toggle":
                self.editor.setChecked(bool(value))
                self.editor.setText("On" if value else "Off")
            else:
                position = round((float(value) - self.spec.minimum) / self.spec.step)
                self.editor.setValue(max(0, min(self._steps, position)))
            self.value_label.setText(format_value(value, self.spec))
        finally:
            self._updating = False

    def _emit_combo(self, _index: int) -> None:
        if not self._updating:
            value = self.editor.currentData()
            self.value_label.setText(format_value(value, self.spec))
            self.valueChanged.emit(value)

    def _emit_value(self, value: int) -> None:
        if not self._updating:
            self.value_label.setText(format_value(value, self.spec))
            self.valueChanged.emit(value)

    def _emit_toggle(self, checked: bool) -> None:
        self.editor.setText("On" if checked else "Off")
        self.value_label.setText(format_value(checked, self.spec))
        if not self._updating:
            self.valueChanged.emit(checked)

    def _emit_range(self, position: int) -> None:
        value = self.spec.minimum + position * self.spec.step
        self.value_label.setText(format_value(value, self.spec))
        if not self._updating:
            self.valueChanged.emit(value)


class CollapsibleSection(QWidget):
    def __init__(self, title: str, parent: QWidget | None = None, expanded: bool = True):
        super().__init__(parent)
        self.header = QToolButton()
        self.header.setText(title)
        self.header.setCheckable(True)
        self.header.setChecked(expanded)
        self.header.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.header.clicked.connect(self._toggle)
        self.body = QWidget()
        self.body_layout = QHBoxLayout(self.body)
        self.body_layout.setContentsMargins(8, 4, 8, 8)
        self.body_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.header)
        layout.addWidget(self.body)
        self._toggle(expanded)

    def _toggle(self, expanded: bool) -> None:
        self.header.setArrowType(Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow)
        self.body.setVisible(expanded)

    def set_expanded(self, expanded: bool) -> None:
        self.header.setChecked(expanded)
        self._toggle(expanded)

"""Small, accessible Qt controls used by the main synth workspace."""

from __future__ import annotations

from typing import Any

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QDial,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSizePolicy,
    QSpinBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from .parameters import ParameterSpec, format_value


COMPACT_LABELS = {
    "Enabled": "Enable",
    "Transpose": "Transp.",
    "Waveform": "Wave",
    "Semitone": "Semi",
    "Oscillator 1": "Osc 1",
    "Oscillator 2": "Osc 2",
    "Resonance": "Reson.",
    "Key Track": "Key Trk",
    "Env Amount": "Env Amt",
    "Destination": "Dest.",
}


class ParameterControl(QWidget):
    valueChanged = pyqtSignal(object)
    resetRequested = pyqtSignal()

    def __init__(self, spec: ParameterSpec, parent: QWidget | None = None):
        super().__init__(parent)
        self.spec = spec
        self.parameter_label = spec.label
        self._updating = False

        root = QVBoxLayout(self)
        root.setContentsMargins(1, 1, 1, 1)
        root.setSpacing(1)
        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(0)
        self.label = QLabel(COMPACT_LABELS.get(spec.label, spec.label))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setMinimumWidth(0)
        self.label.setToolTip(f"{spec.label}: adjust the current layer parameter")
        self.reset_button = QToolButton()
        self.reset_button.setText("↺")
        self.reset_button.setFixedSize(17, 17)
        self.reset_button.setToolTip(f"Reset {spec.label}")
        self.reset_button.setAccessibleName(f"Reset {spec.label}")
        self.reset_button.clicked.connect(self.resetRequested)
        title_row.addWidget(self.label, 1)
        title_row.addWidget(self.reset_button, 0)
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
        if isinstance(self.editor, QDial):
            self.editor.setFixedSize(48, 48)
            self.editor.setNotchesVisible(False)
        elif isinstance(self.editor, QSlider):
            self.editor.setMinimumWidth(48)
            self.editor.setFixedHeight(26)
        else:
            self.editor.setMinimumWidth(0)
            self.editor.setFixedHeight(25)
        editor_row = QVBoxLayout()
        editor_row.setContentsMargins(0, 0, 0, 0)
        editor_row.setSpacing(0)
        editor_row.addStretch(1)
        editor_row.addWidget(self.editor, 0, Qt.AlignmentFlag.AlignHCenter)
        editor_row.addStretch(1)
        root.addLayout(editor_row, 1)
        self.value_label = QLabel()
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.value_label)
        # The selected choice, spinbox value and toggle state are already visible
        # in the editor. Repeating them below wastes an entire line per control.
        self.value_label.setVisible(spec.control not in ("combo", "spin", "toggle"))
        self.setMinimumWidth(60)
        self.setMinimumHeight(91)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

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


class ControlGroup(QGroupBox):
    """A permanently visible, clearly bordered synth section."""

    def __init__(self, title: str, parent: QWidget | None = None):
        super().__init__(title, parent)
        self.setObjectName("synthControlGroup")
        self.setStyleSheet("""
            QGroupBox#synthControlGroup {
                background-color: #eef1f0;
                border: 1px solid #aeb9ba;
                border-radius: 6px;
                margin-top: 12px;
            }
            QGroupBox#synthControlGroup::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 9px;
                padding: 0 5px;
                color: #25343a;
                background-color: #eef1f0;
                font-size: 11px;
                font-weight: 600;
            }
        """)
        self.body_layout = QHBoxLayout(self)
        self.body_layout.setContentsMargins(6, 8, 6, 4)
        self.body_layout.setSpacing(3)

"""Qt state binding with undo/redo for the synth controls."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QUndoCommand, QUndoStack

from .state import clone_state


def _read_path(state: dict[str, Any], path: tuple[str, ...]) -> Any:
    value: Any = state
    for part in path:
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def _write_path(state: dict[str, Any], path: tuple[str, ...], value: Any) -> None:
    target: Any = state
    for part in path[:-1]:
        target = target[int(part)] if isinstance(target, list) else target[part]
    final = path[-1]
    if isinstance(target, list):
        target[int(final)] = value
    else:
        target[final] = value


class StateChangeCommand(QUndoCommand):
    def __init__(self, controller: "StateController", path: tuple[str, ...], before: Any, after: Any, label: str):
        super().__init__(label)
        self.controller = controller
        self.path = path
        self.before = deepcopy(before)
        self.after = deepcopy(after)

    def redo(self) -> None:
        self.controller._apply(self.path, self.after)

    def undo(self) -> None:
        self.controller._apply(self.path, self.before)


class StateController(QObject):
    valueChanged = pyqtSignal(object, object)
    stateReplaced = pyqtSignal()
    dirtyChanged = pyqtSignal(bool)

    def __init__(self, state: dict[str, Any], parent: QObject | None = None):
        super().__init__(parent)
        self.state = clone_state(state)
        self.undo_stack = QUndoStack(self)
        self.undo_stack.indexChanged.connect(self._on_stack_changed)
        self._saved_index = 0

    @property
    def dirty(self) -> bool:
        return self.undo_stack.index() != self._saved_index

    def get(self, path: tuple[str, ...]) -> Any:
        return _read_path(self.state, path)

    def set(self, path: tuple[str, ...], value: Any, label: str = "Change parameter") -> None:
        before = self.get(path)
        if before == value:
            return
        self.undo_stack.push(StateChangeCommand(self, path, before, value, label))

    def _apply(self, path: tuple[str, ...], value: Any) -> None:
        _write_path(self.state, path, deepcopy(value))
        self.valueChanged.emit(path, value)

    def bind(self, path: tuple[str, ...], widget: Any) -> None:
        widget.set_value(self.get(path))
        widget.valueChanged.connect(lambda value, p=path: self.set(p, value, f"Change {widget.parameter_label}"))
        self.valueChanged.connect(lambda changed_path, value, p=path, w=widget: w.set_value(value) if changed_path == p else None)
        self.stateReplaced.connect(lambda p=path, w=widget: w.set_value(self.get(p)))

    def replace_state(self, state: dict[str, Any]) -> None:
        self.state = clone_state(state)
        self.undo_stack.clear()
        self._saved_index = 0
        self.stateReplaced.emit()
        self.dirtyChanged.emit(False)

    def mark_saved(self) -> None:
        self._saved_index = self.undo_stack.index()
        self.dirtyChanged.emit(self.dirty)

    def _on_stack_changed(self, _index: int) -> None:
        self.dirtyChanged.emit(self.dirty)

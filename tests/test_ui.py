import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from synthepyzer.controls import ParameterControl
from synthepyzer.main_window import SynthepyzerWindow
from synthepyzer.preset import default_preset


class UiSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_workspace_exposes_navigation_and_bound_layer_controls(self):
        window = SynthepyzerWindow()
        self.addCleanup(window.close)
        self.assertEqual([window.tabs.tabText(i) for i in range(2)], ["Layer A", "Layer B"])
        self.assertEqual([action.text() for action in window.menuBar().actions()], ["File", "Edit", "View", "Audio", "MIDI", "Help"])
        cutoff = next(control for control in window.layer_panels[0].findChildren(ParameterControl) if control.parameter_label == "Cutoff")
        cutoff.editor.setValue(cutoff.editor.value() + 1)
        self.app.processEvents()
        self.assertTrue(window.controller.dirty)
        self.assertGreater(window.controller.state["layers"][0]["filter"]["cutoff"], 0.72)
        window.controller.undo_stack.undo()
        self.assertFalse(window.controller.dirty)
        self.assertEqual(window.controller.state["layers"][0]["filter"]["cutoff"], 0.72)

    def test_replacing_a_preset_refreshes_bound_controls(self):
        window = SynthepyzerWindow()
        self.addCleanup(window.close)
        payload = default_preset("Loaded")
        payload["layers"][0]["filter"]["cutoff"] = 0.18
        window.controller.replace_state(payload)
        self.app.processEvents()
        cutoff = next(control for control in window.layer_panels[0].findChildren(ParameterControl) if control.parameter_label == "Cutoff")
        self.assertEqual(cutoff.value_label.text(), "18%")


if __name__ == "__main__":
    unittest.main()

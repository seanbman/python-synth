import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtWidgets import QApplication, QScrollArea

from synthepyzer.controls import ControlGroup, ParameterControl
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

    def test_every_control_fits_at_minimum_supported_window_size(self):
        window = SynthepyzerWindow()
        self.addCleanup(window.close)
        window.resize(1000, 680)
        window.show()
        self.app.processEvents()

        self.assertFalse(window.findChildren(QScrollArea))
        for index in (0, 1):
            window.tabs.setCurrentIndex(index)
            self.app.processEvents()
            panel = window.layer_panels[index]
            controls = panel.findChildren(ParameterControl)
            self.assertEqual(len(controls), 32)
            for control in controls:
                top_left = control.mapTo(panel, QPoint(0, 0))
                with self.subTest(layer=index, parameter=control.parameter_label):
                    self.assertGreaterEqual(top_left.x(), 0)
                    self.assertGreaterEqual(top_left.y(), 0)
                    self.assertLessEqual(top_left.x() + control.width(), panel.width())
                    self.assertLessEqual(top_left.y() + control.height(), panel.height())

    def test_sections_are_permanent_bordered_groups_and_have_no_collapse_actions(self):
        window = SynthepyzerWindow()
        self.addCleanup(window.close)
        window.resize(1000, 680)
        window.show()
        self.app.processEvents()

        view = next(action.menu() for action in window.menuBar().actions() if action.text() == "View")
        self.assertEqual([action.text() for action in view.actions()], ["Preset Browser"])
        for index, panel in enumerate(window.layer_panels):
            window.tabs.setCurrentIndex(index)
            self.app.processEvents()
            groups = panel.findChildren(ControlGroup)
            self.assertEqual(len(groups), 7)
            self.assertEqual(
                [group.title() for group in groups],
                ["Layer settings", "Oscillator 1", "Oscillator 2",
                 "Filter", "Amp envelope", "Mixer", "LFO"],
            )
            for group in groups:
                with self.subTest(layer=index, group=group.title()):
                    self.assertTrue(group.isVisible())
                    self.assertFalse(group.isCheckable())
                    self.assertIn("border:", group.styleSheet())
                    self.assertGreater(len(group.findChildren(ParameterControl)), 0)

        self.assertTrue(window.centralWidget().findChildren(ControlGroup))
        self.assertFalse(window.findChildren(QScrollArea))

    def test_choice_spin_and_toggle_values_have_no_redundant_caption(self):
        window = SynthepyzerWindow()
        self.addCleanup(window.close)
        panel = window.layer_panels[0]
        for control in panel.findChildren(ParameterControl):
            with self.subTest(parameter=control.parameter_label):
                if control.spec.control in ("combo", "spin", "toggle"):
                    self.assertTrue(control.value_label.isHidden())
                else:
                    self.assertFalse(control.value_label.isHidden())
                self.assertTrue(control.label.text())

    def test_preset_browser_uses_pages_with_no_scrollbars(self):
        window = SynthepyzerWindow()
        self.addCleanup(window.close)
        window.show()
        self.app.processEvents()
        browser = window.browser
        self.assertEqual(browser.list.verticalScrollBarPolicy(), Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.assertEqual(browser.list.horizontalScrollBarPolicy(), Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        with tempfile.TemporaryDirectory() as directory:
            for index in range(70):
                (Path(directory) / f"patch-{index:03d}.spyzr").touch()
            browser.set_directory(directory)
            self.app.processEvents()
            self.assertLess(browser.list.count(), 70)
            self.assertTrue(browser.next_page.isEnabled())
            first_page = browser.list.item(0).text()
            browser.next_page.click()
            self.assertTrue(browser.previous_page.isEnabled())
            self.assertNotEqual(browser.list.item(0).text(), first_page)
            self.assertLessEqual(browser.list.count(), browser._page_size())


if __name__ == "__main__":
    unittest.main()

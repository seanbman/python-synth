import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from synthepyzer.preset import (
    CURRENT_FORMAT_VERSION,
    PresetFormatError,
    PresetVersionError,
    default_preset,
    load_preset,
    save_preset,
)


class PresetContractTests(unittest.TestCase):
    def test_default_preset_has_two_layers_with_layer_b_disabled(self):
        preset = default_preset()

        self.assertEqual(preset["format"], "spyzr")
        self.assertEqual([layer["id"] for layer in preset["layers"]], ["A", "B"])
        self.assertTrue(preset["layers"][0]["enabled"])
        self.assertFalse(preset["layers"][1]["enabled"])

    def test_round_trip_preserves_layer_values_and_unknown_fields(self):
        preset = default_preset("Layered Glass")
        preset["layers"][0]["filter"]["cutoff"] = 0.41
        preset["layers"][1]["enabled"] = True
        preset["layers"][1]["transpose"] = -12
        preset["future_feature"] = {"enabled": True, "amount": 0.75}
        preset["layers"][0]["future_control"] = {"mode": "spectral"}

        with TemporaryDirectory() as directory:
            path = Path(directory) / "layered-glass.spyzr"
            save_preset(path, preset)
            loaded = load_preset(path)

        self.assertEqual(loaded["meta"]["name"], "Layered Glass")
        self.assertEqual(loaded["layers"][0]["filter"]["cutoff"], 0.41)
        self.assertEqual(loaded["layers"][1]["transpose"], -12)
        self.assertEqual(loaded["future_feature"]["amount"], 0.75)
        self.assertEqual(loaded["layers"][0]["future_control"]["mode"], "spectral")

    def test_v0_single_layer_preset_migrates_to_two_layers(self):
        legacy = default_preset()
        legacy.pop("format_version")
        legacy["format"] = "spyzr"
        legacy["layer"] = legacy.pop("layers")[0]

        with TemporaryDirectory() as directory:
            path = Path(directory) / "legacy.spyzr"
            path.write_text(json.dumps(legacy), encoding="utf-8")
            migrated = load_preset(path)

        self.assertEqual(migrated["format_version"], CURRENT_FORMAT_VERSION)
        self.assertEqual([layer["id"] for layer in migrated["layers"]], ["A", "B"])
        self.assertTrue(migrated["layers"][0]["enabled"])
        self.assertFalse(migrated["layers"][1]["enabled"])

    def test_future_format_is_rejected_without_touching_current_file(self):
        preset = default_preset()
        preset["format_version"] = CURRENT_FORMAT_VERSION + 1

        with TemporaryDirectory() as directory:
            path = Path(directory) / "future.spyzr"
            path.write_text(json.dumps(preset), encoding="utf-8")
            with self.assertRaises(PresetVersionError):
                load_preset(path)

    def test_malformed_json_raises_a_preset_error(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "broken.spyzr"
            path.write_text("{not json", encoding="utf-8")
            with self.assertRaises(PresetFormatError):
                load_preset(path)

    def test_missing_required_layer_is_rejected(self):
        preset = default_preset()
        preset["layers"] = [preset["layers"][0]]

        with TemporaryDirectory() as directory:
            with self.assertRaises(PresetFormatError):
                save_preset(Path(directory) / "should-not-be-written.spyzr", preset)


if __name__ == "__main__":
    unittest.main()

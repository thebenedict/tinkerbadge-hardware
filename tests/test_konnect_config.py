"""Configuration checks only; never starts Konnect or edits hardware."""
import importlib.util
import os
from pathlib import Path
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / "tools/konnect_call.py"

def load_config(env, platform="darwin", installed=False, executable=None):
    spec = importlib.util.spec_from_file_location("konnect_config_under_test", SOURCE)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(os.environ, env, clear=True), patch("sys.platform", platform), patch("pathlib.Path.home", return_value=Path("/home/example")), patch("pathlib.Path.is_file", return_value=installed), patch("shutil.which", return_value=executable):
        spec.loader.exec_module(module)
    return module

class ConfigurationTests(unittest.TestCase):
    def test_existing_macos_defaults(self):
        module = load_config({}, installed=True)
        self.assertEqual(module.BIN, "/home/example/Documents/KiCad/10.0/3rdparty/plugins/com_github_mixelpixx_konnect/bin/konnect")
        self.assertEqual(module.CONFIG, "/home/example/Library/Application Support/konnect/codex.toml")
    def test_explicit_overrides(self):
        module = load_config({"KONNECT_BIN": "custom/konnect", "KONNECT_CONFIG": "local/config.toml"})
        self.assertEqual(module.BIN, "custom/konnect")
        self.assertEqual(module.CONFIG, "local/config.toml")
    def test_linux_path_and_xdg(self):
        module = load_config({"XDG_CONFIG_HOME": "/tmp/config"}, "linux", executable="/usr/bin/konnect")
        self.assertEqual(module.BIN, "/usr/bin/konnect")
        self.assertEqual(module.CONFIG, "/tmp/config/konnect/codex.toml")
    def test_linux_home_fallback(self):
        module = load_config({}, "linux")
        self.assertEqual(module.BIN, "konnect")
        self.assertEqual(module.CONFIG, "/home/example/.config/konnect/codex.toml")
    def test_callers_can_override_config(self):
        module = load_config({})
        module.CONFIG = "local/pcb.toml"
        self.assertEqual(module.CONFIG, "local/pcb.toml")

if __name__ == "__main__":
    unittest.main()

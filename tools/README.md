# Hardware tools

These scripts record the design and review workflow used for the current badge. Read the hardware specification and applicable review guides before running scripts that change native KiCad files. Some tools require a running KiCad editor and the optional Konnect MCP integration.

## Konnect configuration

`konnect_call.py` uses `KONNECT_BIN` and `KONNECT_CONFIG` when set. Otherwise it finds the existing KiCad 10 macOS plugin under the current user's home directory, then looks for `konnect` on `PATH`.

The default configuration is `~/Library/Application Support/konnect/codex.toml` on macOS and `$XDG_CONFIG_HOME/konnect/codex.toml` on Linux, falling back to `~/.config/konnect/codex.toml`. Keep your machine-specific configuration outside the repository. PCB helpers can select a generated `.build/pcb_konnect.toml` configuration.

```sh
export KONNECT_BIN="$(command -v konnect)"
export KONNECT_CONFIG="$HOME/.config/konnect/codex.toml"
python3 tools/konnect_call.py --catalog
```

Choose the configuration that matches your installation before running the catalog command. The helper creates `.build/` for local logs. It does not install Konnect or configure KiCad access.

Run configuration-only checks without opening KiCad or starting Konnect:

```sh
python3 tests/test_konnect_config.py
```

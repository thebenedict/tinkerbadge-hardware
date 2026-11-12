# Hardware tools

These scripts record the design and review workflow used for the current badge. Read the hardware specification and applicable review guides before running scripts that change native KiCad files. Some tools require a running KiCad editor and the optional Konnect MCP integration.

## Current publication snapshot

Run `python3 tools/refresh_publication.py --cad-python /path/to/cad-environment/bin/python` with KiCad 10.0.8 and the enclosure requirements installed. It runs ERC, DRC with in-memory zone refill and schematic parity, contract/property checks, manufacturing exports, mechanical interface extraction, CAD generation and native enclosure fit checks. The native KiCad inputs must remain unchanged. Evidence is written to `exports/publication/manifest.json`.

`python3 tools/check_export_chain.py` checks that the electrical evidence, manufacturing package, enclosure and archived CAD still match. Warnings remain recorded; passing this consistency check does not close physical prototype gates.

Commit the hardware snapshot, then run the web repository's badge exporter against that commit, regenerate feature/enclosure renders and run `npm run check`. Update its explicit source pins when selecting a new hardware revision. The web exporter rejects changed or uncommitted selected inputs and includes the publication evidence and manufacturing downloads.

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

## Design-review tools (10 November 2026)

These need only `kicad-cli` and KiCad's bundled Python, not Konnect. See `docs/design/design_review_2026-11-10.md`.

- `schlib.py`, `apply_design_review_schematic.py`, `apply_design_review_contracts.py`: one-shot schematic and contract edits.
- `create_review_footprints.py`: dock pads, front SAO socket and rear NFC coil footprints.
- `sync_board_design_review.py`, `pcb_dump.py`, `route_remaining.py`, `pcb_apply_routes.py`, `pcb_prune_dangling.py`, `finish_board_review.py`: board sync, grid router and finishing.
- `rebuild_review.sh`, `export_design_review.sh`, `drc_summary.py`: replay, evidence export and a compact DRC summary.
- `check_power_paths.py`: narrowest link on each main power path.
- `assign_jlc_parts.py`, `apply_jlc_release.py`, `export_jlc.py`: LCSC part assignment, JLCPCB rule and silkscreen fixes, and the order package in `production/jlcpcb/`.

## Review fixes, 11 November 2026

See `docs/review/response_2026-11-11.md`.

- `apply_review_2026_11_11_schematic.py`, `apply_review_2026_11_11_board.py`: one-shot schematic, contract and board edits. Do not rerun on the current files.
- `check_nfc_window.py` (KiCad Python) and `check_nfc_gerbers.py`: fail when copper other than the coil and its feed is inside the NFC window, in the board file and in the exported Gerbers. `export_jlc.py` runs both.
- `write_display_pinout.py`, `write_pcb_placement.py`: regenerate `docs/design/display_pinout.md` from the display contract and `docs/design/pcb_placement.json` from the board.
- `renumber_power_symbols.py`: unique power-symbol references across sheets.
- `pcb_strip_stubs.py`: removes dead-end track chains and duplicate segments, each verified by DRC.
- `route_remaining.py` gained protected windows, a pocket test that names where a net is walled in, and a flood-guided search.

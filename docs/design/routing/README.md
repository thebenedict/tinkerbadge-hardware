# Routing inputs and outputs

The native board file is authoritative. These files record how the review's copper was produced, in the order applied with `tools/pcb_apply_routes.py`.

| Step | File | Content |
|---|---|---|
| 1 | `manual_switch_nodes.json` | Hand-routed TPS63802 switch nodes and ground via |
| 2 | `manual_usb_display.json` | USB-C front end through the ESD array, display-connector via lattice, charger EN1 escape |
| 3 | `router_output.json` | Main router run (`router_config.json`) |
| 4 | `router_output_nfc.json`, `router_output_rgb7.json` | NFC coil terminals and one re-routed LED link |
| 5 | verified dangling-copper prune (`tools/pcb_prune_dangling.py`), silkscreen (`tools/finish_board_review.py`) | |
| 6 | `manual_finish.json`, `router_output_finish.json` | Lattice entries for display pins 13/14; display clock/data, NFC field detect, dock 5 V, 3.3 V islands |
| 7 | `manual_finish2.json`, `router_output_finish2.json` | Pockets opened at the charger CHG pad, accelerometer and NFC tag; affected nets re-routed |
| 8 | `manual_finish3.json`, `router_output_finish3.json` | MCU pad 25 and accelerometer pad 4 cleared; last nets routed |
| 9 | prune and silkscreen again | |

Steps 1 and 2 are replayed by `tools/rebuild_review.sh`. Steps 6 to 8 used the router with `--via 0.48 0.25 --hweight 3 --budget 12000000 --retries 0`. `router_config_finish.json` records an automatic rip-up attempt that was abandoned.

## 11 November 2026 review fixes

Applied to the board from checkpoint `3120d6e`, in this order.

| Step | File | Content |
|---|---|---|
| 1 | `tools/apply_review_2026_11_11_board.py` | New and moved footprints, the `NFC_WINDOW` rule area and design rule, display-connector via lattice; rips the nets that crossed the window or met moved parts |
| 2 | `router_output_2026-11-11.json` (`router_config_2026-11-11.json`) | First router run |
| 3 | `manual_2026-11-11_a.json`, `router_output_2026-11-11_b.json` | Expansion I²C ripped to open the display fan-out; rerouted |
| 4 | `manual_2026-11-11_b.json`, `router_output_2026-11-11_c.json` | Display nets ripped whole; straight escapes from the connector alternating between B.Cu and In2.Cu |
| 5 | `manual_2026-11-11_c.json`, `router_output_2026-11-11_d.json` | NFC tag area laid by hand with the coil ends swapped (inner end LA); C507, C508, C303 moved; I²C, field-detect and two display nets rerouted |
| 6 | `router_output_2026-11-11_e.json` | Internal I²C and expansion SDA, routed with the flood-guided search |
| 7 | `tools/pcb_prune_dangling.py`, `tools/pcb_strip_stubs.py` | Verified removal of dangling copper and one 23-segment dead-end chain |
| 8 | `manual_2026-11-11_d.json`, `tools/finish_board_review.py`, `tools/apply_jlc_release.py board` | SAO footprint reloaded for its moved labels; silkscreen, references and fabrication fields |

Router runs used `--via 0.48 0.25 --hweight 3 --retries 0`. Step 6 needed the guide added to `tools/route_remaining.py` that day: the search follows a flood from the target, so long winding routes no longer exhaust the budget.

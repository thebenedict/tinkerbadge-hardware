# Routing inputs and outputs, design review 10 November 2026

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

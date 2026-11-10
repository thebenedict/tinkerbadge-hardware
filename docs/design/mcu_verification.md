# MCU schematic implementation checks

Temporary review artifacts below are identified by filename only; these intermediate files are not distributed. Published source outputs and repeatable checks are linked from the [current verification record](verification.md).

2026-11-09. **PASS for the MCU sheet's reviewed electrical contract and local connectivity.** The complete badge is not yet ERC- or manufacturing-released. This implementation was confined to `mcu.kicad_sch`; all native changes used the installed official Konnect MCP server. No shared symbol library, main PCB, routing or manufacturing file was modified.

## Evidence and scope

- Original-source review: `review_mcu.md`; contract SHA-256 `c9603c23ce6b0a902d29ba0c00a2ccd5c10c8b32814e0eff10f720ad48c01a19`.
- Source→symbol→footprint acceptance: `../components/ESP32-S3-WROOM-1-N16R8.library_acceptance.md`. Disposable symbol and footprint were placed, queried, rendered and visually compared to the original drawings before main implementation. Standard two-terminal passives and one-pad test points are generic associations, not approval of an unspecified procurement MPN.
- Queried actual placed pin coordinates before wiring. USB resistor pin 2 faces the module and pin 1 faces the connector nets, matching the contract exactly. GND1/40/41 all appear in the exported netlist despite hidden co-located symbol pins.
- `tools/check_schematic_contracts.py path/to/export.net --blocks mcu`: **17 components, 67 physical endpoints, 4 intentional NC, no mismatch**. Every reference's value, footprint and library ID also agrees with the contract. Machine-readable results and pinned hashes are in `mcu_verification.json`.
- Konnect validators: **0 floating wire ends, 0 unconnected pins, 0 shorted named nets, 0 orphans**. No electrical exception or suppression was used.
- Inspected `mcu-v1.png`, corrected resistor field/body overlap, a decoupling note/GND overlap and a local strap-label/global-label overlap, then inspected `mcu-v2.png`. The second rendering is readable with direct nearby RC/bypass/USB wiring, an explicit EN branch junction, proper power symbols, global cross-sheet signals, and local recovery/strap nets. Standard passives use 1.27 mm half-grid placement where necessary for their 7.62 mm terminal spacing; the functional layout and wiring otherwise follow the 2.54 mm grid.

## Root ERC is interim, not waived

Root `tinkerbadge.kicad_sch` was checked after MCU completion while other sheets were still being populated. It reported 15 isolated peripheral signal labels and 3 power-input-not-driven errors (U101 IN1, U101 IN2 and a display GND symbol). These are documented in `mcu-integration-erc.json` and sent to the integration/power owners. No same-local/global-label warning or MCU endpoint error occurred. Run ERC again on the completed root, not the standalone child; this interim result is not an acceptance of the remaining violations.

## Historical MCP procedure

Placement/query: `mcu_place.json` and results; orientation/field adjustments: `mcu_adjust.json`; wiring: `mcu_wire.json`; visual corrections and validators: `mcu_cleanup.json`. Each corresponding JSONL result links the complete individual MCP response. Exported netlist `mcu.net`; final inspected image `mcu-v2.png`. The native sheet is atomically saved by schematic mutation tools; the PCB-only `save_project` operation was not misrepresented as a schematic save.

## Remaining gates

Independent integration-owner review, completed-root ERC and human visual acceptance remain required. No PCB placement or routing was performed. Antenna keepout, module ground/thermal-pad process, USB geometry/placement, effective capacitance, 3.3 V peak current/transients, reset/ramp behavior, RTC wake firmware and ROM-recovery effects require subsequent PCB/prototype work. GPIO40 may intentionally power the display in USB-OTG ROM recovery; R207 only defines its high-impedance state.

Native sheet SHA-256 at handoff: `78cf64f1287d4627792265044955fe1d02be1b42636e134f4ee26c646edaddc9`.

## Hidden traceability annotation

Added MPN and Contract properties to all17 references through individual Konnect edit calls, explicitly hidden. Fresh `mcu-final.net` readback verifies every property: exact U201 MPN, explicit TBD specification-level passives, and PCB-pad-only test points. The original placement batch had never requested these custom properties, so this was an addition rather than a retry of a silently failed batch. Endpoint check remains17/67/4NC PASS. `mcu-v3.png` is byte-for-byte identical to the accepted v2 rendering. No electrical or visible change.

Current native SHA-256: `29e7598143e36c0ba33b1ea5875f514755eb59f60cc515947e747fa4303c45b3`.
Current netlist SHA-256: `54e12ee149a68e8647cb052f91a4b870ffd62f323cf6b95284078ccad8cd38eb`.
Unchanged PNG SHA-256: `bbae74a5e4f6c42ec3d6890e01b966257746cdf6c7efc4d2bd317a6fe2cea4a8`.

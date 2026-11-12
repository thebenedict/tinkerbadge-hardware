# Design review, 10 November 2026

> **Superseded in part.** An independent review on 11 November found a layout defect in this pass (ground planes under the NFC coil) and several fit problems. Board revision 0.3 fixes them; see [the response to that review](../review/response_2026-11-11.md). Statements below describe revision 0.2 unless marked.

Reviewer: Claude (agent), at the project owner's request, with authority to change the design, BOM and schematic. Baseline: commit `3c8a60e` (first routing pass, 179 schematic components, 48 unconnected board items, nine parts without footprints). After this pass: 155 components, no unconnected items, no missing footprints.

This review covers usability, manufacturability, BOM and cost, placement, routing and appearance. Findings are ranked by how much they affect someone wearing, charging, building or hacking the badge. The second half records what was changed in this pass, what was checked, and what is still open.

## Summary

The electrical design was careful and well documented, and the source-first process caught real problems (the display pin names, the MOSFET lifecycle notice, the LED supply margin). The same caution had also left the badge unable to do several things a badge has to do, and had added parts to guard against cases that cannot occur in this circuit.

The most important findings:

1. **The badge could not charge its own battery.** Charge enable was strapped off pending a temperature-sensing design. A loaner fleet that must be opened to charge is not usable.
2. **USB input was limited to 100 mA.** Even with charging enabled, a USB port would have taken more than ten hours to fill the cell, and a battery-free badge might not boot from USB.
3. **The board could not be built.** Nine parts had no footprint, including the battery connector, display connector, both inductors and USB ESD protection.
4. **The SAO socket was on the back.** Add-ons are decorative and meant to be seen; the rear position under the battery lead made the port close to pointless.
5. **The battery connector sat mid-board under the display** on the front, with the cell on the rear and no path for the lead.
6. **About 20 parts protected against conditions the circuit cannot reach**, including a 14-pin analog switch for one battery divider and a 20-pin buffer for five display signals.
7. **Routing was incomplete**, with 48 open connections and no path to completion while footprints were missing.

All seven are addressed in this pass. The board is fully connected and passes DRC apart from five unchanged baseline items and four T-junction reports. The largest remaining risks are physical and need hardware in hand: display flex orientation, radio performance with the glass 3.5 mm from the antenna, NFC tuning, and the optical stack.

## Usability

### Charging (changed)

`R120` held BQ24074 `CE` high, so the charger never ran. The stated blocker was that the charger's native thermistor window (about 0–50 °C with a 10 kΩ B3435 part) is 5 °C wider on the hot side than a typical pouch cell's 0–45 °C charge rating, and that a two-resistor network can only widen the window.

That is true, and the answer is to choose the thermistor rather than to disable charging. A 10 kΩ **B3950** NTC moves the nominal window to about 3–47 °C (cold trip at 28 kΩ, hot trip at 4.0 kΩ, from the 75 µA bias and 2.1 V / 0.3 V thresholds). Threshold and bias tolerance add roughly ±3 °C. The charge current is 270 mA, about 0.25 C for the 1000–1200 mAh cells this badge can carry, and the cell has its own protection circuit. This is ordinary practice for a 1S consumer charger and is safer than the common hobby shortcut of a fixed 10 kΩ resistor, which the earlier notes rightly rejected.

`RT101` is now a board-mounted NTC inside the cell footprint, next to the charger, so that it follows cell temperature through the board when the pack is taped down. `CE` is tied low. The separate thermistor connector (`J104`) is removed; a two-wire pack needs no third lead.

Still to verify on a prototype: thermal coupling between cell and `RT101`, actual trip temperatures, and charge termination with the system running.

### USB charge rate (changed)

`EN1`/`EN2` selected the 100 mA input limit for USB and 500 mA for the dock, switched by a MOSFET inverter on the mux status pin. A Type-C sink with 5.1 kΩ pull-downs may draw 500 mA from any compliant source, and the ESP32-S3 enumerates as a USB device. `EN1` is now pulled high permanently: 500 mA for both inputs. `Q103` and `R110` are removed and the mux status pin is unused.

### SAO socket (changed)

Moved from the rear to the front top edge, between role LEDs D402 and D403, where an add-on stands above the display and is visible when the badge is worn. The socket has its own footprint with the SAO v1.69bis host pin order drawn explicitly (top row 3V3, SDA, GPIO1; bottom row GND, SCL, GPIO2) and labelled on silkscreen. An add-on will overhang the top edge and may shade D402/D403; check this with the role-bar diffuser.

### Battery connection (changed)

`J102` is now a through-hole JST PH side-entry header on the **rear**, beside the cell and 17 mm from the charger. PH is the connector fitted to most small protected pouch cells sold individually, so replacement packs are easy to find. Polarity is not standardised across vendors: pin 1 is battery positive, the silkscreen says so, and every new pack type must be checked with a meter before it is plugged in.

### Recovery access (recommended, not changed)

EN and BOOT exist only as 1 mm pads on the rear, behind the enclosure. Native USB handles normal flashing, but a badge in deep sleep or with broken firmware needs both. For a badge meant to be reprogrammed by attendees, I recommend moving button B to GPIO0 so that it doubles as BOOT, and adding a recessed reset pinhole or a third small button on EN. This changes the button wiring and enclosure, so it is left as a decision.

### Status while charging (noted)

By specification the status LED is dark in deep sleep, including while charging in the dock. Someone collecting badges from a dock has no way to see which are full. If that matters, the charger's `CHG` output can drive the red die directly through a resistor, independent of firmware. Not changed.

### LED supply (recommended, not changed)

The WS2812C-2020 minimum supply is 3.3 V and the shared rail is 3.3 V ±1.3 % before load steps. The accepted prototype experiment stands. If it misbehaves, the cheapest fix is to power the eight LEDs from `VSYS` (3.3–4.4 V) instead of `+3V3`. Battery current is about the same either way, the LED load steps come off the logic rail, and the data-high threshold (0.55 × 4.4 V = 2.42 V) still sits below the MCU's 2.64 V minimum output. This is a net change on eight parts and one trunk.

## BOM and cost

### Parts removed

| Removed | Why it was there | Why it is not needed |
|---|---|---|
| U107 TMUX1511 (TSSOP-14), C115, R129, R130 | Isolate the battery divider from an unpowered MCU pin | The 3.3 V regulator is enabled whenever `VSYS` exists, so the MCU is powered whenever the battery has voltage. A 1 MΩ / 1 MΩ divider with 100 nF draws 2 µA and cannot inject meaningful current. The ADC now reads VBAT / 2. |
| U301 SN74LVC541 (TSSOP-20), C312, R303–R307 | Stop MCU pins back-powering the display when its rail is off | Firmware drives the five outputs low before dropping `EPD_EN`, as every reference design for this panel does. During reset the pins are high-impedance. A stuck-high pin leaks a few milliamps through the panel's input diodes and does no damage. |
| Q103, R110 | Select USB100 vs USB500 from the mux status | Both inputs now use USB500. |
| R103–R106 | Mux over-voltage supervisors at 5.75 V | The mux tolerates 22 V, the charger behind it tolerates 28 V and has its own 10.5 V cut-off, and each input has a TVS. TI specifies grounding OV1/OV2 when unused. |
| R120 | Charge disable strap | Charging is enabled. |
| R115 | Pull-up for charger PGOOD | PGOOD duplicates the separate USB and dock presence signals and its QFN pin had no escape route. The pin and expander input P1 are left unconnected. |
| R514–R517 | Pull-downs on four unused expander pins | Firmware drives unused expander pins low after reset. The resistors sat in the most congested part of the board. |
| J104 | Connector for an external thermistor | Replaced by on-board `RT101`. |

Net change: 179 → 155 schematic components, two fewer ICs (both in leaded TSSOP packages that dominated their areas), 25 fewer placements. Firmware must configure TCA9534 P1 and P4–P7 as outputs driven low.

### Values consolidated

Seven 0.1 % resistors and several E96 values were used where 1 % E24 parts do the same job. Each distinct non-stock value is a separate reel and, at JLCPCB, a separate extended-part loading fee.

| Ref | Was | Now | Effect |
|---|---|---|---|
| R107 / R108 | 31.6 k / 10.0 k 0.1 % | 30 k / 10 k 1 % | USB-priority threshold 4.04–4.40 V |
| R109 | 80.6 k | 82 k | Mux current limit about 1.45 A |
| R112 | 4.32 k | 4.3 k | Unused ILIM setting |
| R113 | 3.32 k | 3.3 k | Charge current about 270 mA |
| R114 | 47.5 k | 47 k | Charge timer about 6.3 h |
| R117 / R118 | 56.0 k / 10.0 k 0.1 % | 56 k / 10 k 1 % | 3.3 V ±2.4 % static |
| R127 / R128 | 100 k 0.1 % | 1 M 1 % | ADC divider, calibrate in firmware |
| R508 | 210 k | 200 k | Accessory limit about 115–160 mA |

The wider 3.3 V tolerance (3.22–3.38 V) makes the LED supply experiment slightly harder; see the `VSYS` fallback above.

### Parts kept after review

- **TPS2121 source mux.** Two Schottky diodes would be cheaper, but the diode drop puts a weak USB source close to the charger's 4.5 V input-regulation threshold. The mux gives clean priority and reverse blocking and is already placed.
- **TPS63802 buck-boost.** A plain buck would drop out below about 3.5 V of battery and waste a third of the cell with Wi-Fi peaks.
- **TPS22918 display switch.** The panel sleeps at microamps, but a hard power cycle is the reliable recovery from a hung controller.
- **TPS2553 accessory switch.** Qwiic and SAO ports invite shorts; a current-limited rail keeps a bad add-on from browning out the badge.
- **TCA9534 expander.** With the buffer gone the MCU still has no spare GPIO. Removing the expander means giving up accessory fault sensing or charger status; not worth it at this stage.

### Sourcing notes

- Display connector: the panel document names Panasonic AYF532435, which had zero stock. The footprint is now Hirose FH12-24S-0.5SH(55), which was stocked. See the open item on flex orientation.
- L101: Sunlord SWPA4020SR47NT (0.47 µH, 7 A saturation), chosen because JLCPCB stocks it; the Coilcraft XFL4015 first selected is not in their library. L301: Bourns SRN4018-680M, 1.8 mm tall. The earlier 1 A saturation target for L301 was a project guess; the panel's reference board uses a part of this class. Scope the boost current on the prototype.
- Part numbers, stock and prices were added afterwards; see the [JLCPCB release note](jlcpcb_release.md). L101 changed to a Sunlord part that JLCPCB stocks.

## Design for manufacturing

- **One SMT side.** All surface-mount parts stay on the front. The rear carries only bare pads (dock, test points), the NFC coil, and the two through-hole parts (`J102`, and the SAO socket inserted from the front and soldered on the rear). Both through-hole parts are hand-fit after reflow, along with the display and cell.
- **Every schematic part now has a footprint.** The remaining "confirm against the drawing" items are standard library patterns for exact catalogue parts.
- **DNP is now native.** `C508` (NFC trim) carries KiCad's DNP and exclude-from-BOM flags, so a generated BOM and placement file are correct without reading custom fields. `J103` and `AE501` are PCB features and are excluded from the BOM.
- **Fine-pitch clearance.** The `EPD_HV` net class required 0.25 mm, which a 0.5 mm-pitch FPC connector cannot meet (0.2 mm between pads). `EPD_HV`, `USB_HOLD` and `AnalogSense` are now 0.15 mm, the board minimum, which is adequate for ±20 V under solder mask. `PowerBranch` and `Switching_HOLD` stay at 0.2 mm.
- **Small vias.** 82 vias are 0.48 mm / 0.25 mm: 26 hand-placed at the display connector, USB data pairing and charger, the rest added by the finishing passes in congested areas. The others are 0.6 / 0.3 mm or larger. Confirm the fabricator's minimum before ordering; JLCPCB's standard 4-layer process accepts this size.
- **USB ESD array uses flow-through routing.** The four unused pads of the TPD4E05U06 are tied to their lines in the schematic so each trace runs straight through the package, as TI's layout guidance intends. Channels are assigned in connector order (CC2, D+, D−, CC1).
- **USB connector hole-to-pad clearance.** Four existing warnings (0.19 mm vs 0.25 mm) come from the manufacturer's own land pattern for USB4105 and are expected.
- **Assembly tier.** The ESP32-S3 module and LIS2DW12 still require JLCPCB Standard assembly with X-ray. If Economic assembly matters, the accelerometer is the part to change (a leaded or QFN alternative), not the module.

## Placement and routing

### What was already good

The fixed anchors are sensible: buttons on the left edge, USB and Qwiic on the right, role LEDs along the top, affinity LEDs evenly spaced along the bottom, passive optics grouped below the glass. Inner layers are unbroken ground planes. Decoupling is close to its pins and the converter feedback is Kelvin-routed.

### Findings

- **Antenna.** The module antenna overhangs a notch at the top left, which is right, but the display glass and its ITO layers sit 3.5 mm in front of it and the cell is behind the board nearby. Expect reduced range. Measure RSSI against a bare dev board before committing to this outline; the fallback is to move the module so the antenna clears the glass corner.
- **Power chain is spread out.** USB enters at the right edge, the charger is 25 mm in, the regulator is a further 40 mm left, and the display switch and boost are back toward the right. It works, and the trunks are wide, but `VSYS` and `+3V3` cross the board twice. If the board is re-placed for any other reason, put the regulator next to the charger.
- **USB data runs 95 mm** from the connector to the module's series resistors on the far left. At full speed (12 Mbit/s) this is acceptable without impedance control. The pair is routed together where the board allows.
- **Empty areas.** Removing U107 and U301 opened space left of centre and above the display connector. I left it open rather than re-spreading parts, to preserve the approved arrangement.

### Changes in this pass

- New footprints placed: `U105` at the USB connector, `L101` beside the regulator with switch nodes facing the IC, `L301` above the boost MOSFET, `J301` at the right edge with its opening toward the edge, `J102` on the rear beside the cell, dock pads at the rear bottom left, `RT101` in the cell footprint beside the charger, the SAO socket on the front top edge.
- NFC coil drawn on the rear: 10 turns, 0.2 mm track and gap, 18 × 13 mm, estimated 1.7 µH (modified Wheeler). With the tag's 50 pF this needs about 30 pF more to resonate at 13.56 MHz; `C507` is fitted at 27 pF and `C508` is the trim position. The estimate is ±20 %, so tuning on an assembled badge is required.
- The regulator switch nodes, the USB-C front end and the display-connector via lattice are hand-designed (`docs/design/routing/manual_*.json`).
- Other open connections were routed with a grid router written for this board (`tools/route_remaining.py`): 45° geometry, through vias, no copper in the antenna shoulder. **Correction, 11 November:** this line originally also claimed no copper under the coil. That was wrong. The router kept its own tracks out of inner layer 2 there, but the board had lost the rule area that kept the ground planes out, so both inner planes covered the coil and a front LED trace crossed it. The [11 November review](../review/design_review_2026-11-11.md) found this; the fix and a regression check are in [the response](../review/response_2026-11-11.md). Inner layer 2 now carries some long signal runs; inner layer 1 remains an unbroken ground plane. `C512` and `R102` moved a few millimetres to make room for the display fan-out and to sit beside the CC2 row.

Routing results and check output are in the next section.

## Checks performed

Native checks, KiCad 10.0.8, on the files in this commit. Outputs are in `exports/design-review-2026-11-10/`.

| Check | Result |
|---|---|
| Contract endpoint check (`check_schematic_contracts.py`) | Pass: 155 components plus test pads, 499 physical pins against the updated contracts |
| Property check (`check_schematic_properties.py`) | Pass; no unassigned footprints (was 9) |
| Checker regression tests | Pass (contract, property, Alps button) |
| ERC | 0 errors; the one documented LIS2DW12 address-strap warning |
| DRC, clearance and shorts | 0 |
| DRC, schematic parity | 0 issues (was 9 missing footprints) |
| DRC, other | 4 USB4105 hole-to-pad warnings from the manufacturer land pattern (unchanged); 1 module silkscreen at the notch edge (unchanged); 4 "dangling track" reports that are T-junction joins, kept because removing any of them opens a connection |
| **Unconnected items** | **0 (was 48)** |
| Narrowest link on each main power path (`check_power_paths.py`) | 0.20–0.30 mm, in short necks at fine-pitch pads; see below |

### How the last connections were closed

A first router pass left ten connections open. A reachability check showed that five were routable and had only run out of search budget; a greedier search closed them. The other five were single pads boxed in by neighbouring copper. Each pocket was opened by hand, the pad's net routed first, and the displaced nets re-routed:

- **Charger CHG (U102 pad 9).** The OUT-to-C105 link moved 0.4 mm outward so CHG can drop to a via beside the pad.
- **Accelerometer SDA (U502 pad 4)** and **NFC tag SDA and LA (U503 pads 5 and 1).** Neighbouring +3V3, field-detect and LB segments were cleared and re-routed around the pads.
- **MCU NFC field detect (U201 pad 25).** SAO_GPIO2 had been routed under the pad; it now takes another path.

The step-by-step inputs are in `docs/design/routing/`.

### What the routing looks like

- 2,672 track segments and 435 vias. 82 vias are the small 0.48 / 0.25 mm size (26 hand-placed, the rest from the finishing passes).
- Inner layer 1 is one unbroken ground region. Inner layer 2 carries 354 signal and power segments and its ground fill is now in four pieces; treat it as a routing layer.
- Main power paths are 0.5 mm or wider except for necks at fine-pitch pads: 1–5 mm on the 5 V, battery and `VSYS` paths. The 3.3 V feed to the module has 27 mm at 0.3 mm in an 87 mm path, mostly from the first routing pass; with the module's local 22 µF this is acceptable for a prototype and worth widening in a clean-up.
- The router optimises for completion, not appearance. Expect extra vias and some wandering paths, particularly around the display connector and charger. A tidy-up pass in KiCad's interactive router would improve it; nothing electrical depends on that.

I have not looked at this board in the KiCad GUI, and no person has reviewed the new routing. Images inspected: front copper and silkscreen, rear 3D render, and close-ups of the regulator, charger/USB and display-connector areas.

## Open items

Ordered by risk.

1. **Display flex orientation.** `J301` is a bottom-contact connector with pin 1 toward the bottom of the board. Whether the folded tail presents its contacts and pin order that way must be checked with a real panel before fabrication. If it is reversed, rotate the connector 180° or use the top-contact FH12 variant; the routing fan-out is local.
2. **Radio range** with glass and cell in place.
3. **NFC tuning** and read range through the enclosure; an 18 × 13 mm coil gives a short range.
4. **Charging qualification**: trip temperatures at the cell, termination under load, behaviour with no battery.
5. **LED supply margin** at 3.3 V; fall back to `VSYS` if needed.
6. **Human visual review of the routing.** The project process asks for placement approval before routing and a visual review before release. This pass added and moved parts and completed routing under a general grant of authority; the result should be looked at in KiCad before any order.
8. **Enclosure, diffuser and dock mechanics**, including the SAO overhang and the dock pad contact design.
9. **Recovery buttons** decision.

## Files

- Schematic changes: `tools/apply_design_review_schematic.py` (uses `tools/schlib.py`).
- Contract changes: `tools/apply_design_review_contracts.py`.
- New footprints: `tools/create_review_footprints.py` → `Tinkerbadge.pretty/`.
- Power-path check: `tools/check_power_paths.py`.
- Board sync and routing: `tools/sync_board_design_review.py`, `tools/pcb_dump.py`, `tools/route_remaining.py`, `tools/pcb_apply_routes.py`, `tools/pcb_prune_dangling.py`, `tools/finish_board_review.py`. `tools/rebuild_review.sh` replays the schematic and board changes from the baseline commit up to the router run; router outputs and hand-routed geometry are in `docs/design/routing/`.
- Evidence export: `tools/export_design_review.sh` → `exports/design-review-2026-11-10/`.

Component records for the removed parts (TMUX1511, SN74LVC541, TPS3700) and the earlier placement and capture reviews are kept as history; `implementation_status.md` and the block contracts describe the current design.

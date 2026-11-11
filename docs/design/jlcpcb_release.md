# JLCPCB release package, 10 November 2026

Board revision 0.2. Order files are in [`production/jlcpcb/`](../../production/jlcpcb/), rebuilt with `python3 tools/export_jlc.py`. This note records what was checked against JLCPCB's published limits, the order settings, the part choices, and what still has to happen before money is spent.

## Before ordering

The files are complete and pass the checks below. Three things cannot be closed from the CAD side:

1. **Display flex orientation.** `J301` is a bottom-contact Hirose FH12 with pin 1 toward the bottom edge. Confirm contact side and pin-1 end against a real panel. A reversed flex means a dead display on every board.
2. **Placement rotations.** `cpl-jlcpcb.csv` carries KiCad's rotations. JLCPCB's reel orientation differs for some packages, so check every polarised part in their placement preview before confirming: the eight RGB LEDs, the status LED, diodes, SOT-23 and SOT-23-6 parts, the QFNs, the LGA accelerometer, the module and the connectors.
3. **A person has not looked at the routing in KiCad.** It is router output: correct by DRC, not tidy.

Order a small first batch (JLCPCB's minimum is 2 assembled, 5 bare) and bring up one board before building a fleet. Charging, radio range, NFC tuning and the LED supply margin are unmeasured.

## Order settings

| Setting | Value | Note |
|---|---|---|
| Layers | 4 | |
| Dimensions | 110 × 80 mm | Above the 100 × 100 mm size that gets JLCPCB's lowest 4-layer price. The display glass is 93.3 mm wide, so the board cannot drop under 100 mm without a different panel. |
| Thickness | 1.6 mm | |
| Stackup | JLC04161H-7628 (default) | No impedance control needed; USB is full speed. |
| Outer / inner copper | 1 oz / 0.5 oz | Defaults. |
| Surface finish | Lead-free HASL | No surcharge. ENIG is the better finish for the dock contact pads and the 0.5 mm-pitch parts and is worth paying for on a fleet build. |
| Via covering | Tented | Default. |
| Min via hole / diameter | 0.25 mm / 0.48 mm | Inside the no-surcharge range (0.2–0.25 mm holes cost more only when the via diameter is under 0.45 mm). |
| Mark on PCB | Order number at a specified location, or remove | Their default placement may land on the visible rear. |
| Assembly | Standard PCBA, top side only | The ESP32-S3 module and LIS2DW12 are Standard-only, which rules out Economic PCBA. |
| Edge rails and fiducials | Added by JLCPCB | Required for Standard PCBA. The board also carries three 1 mm fiducials. |
| Hand-soldered parts | None | `J102` (battery header) and `J502` (SAO socket) are through-hole and are left off the BOM to avoid the manual-solder charge. Fit them by hand; they are listed in `bom-hand-fit.csv`. |

Upload `tinkerbadge-gerbers.zip`, `bom-jlcpcb.csv` and `cpl-jlcpcb.csv`.

## Capability check

Limits read from JLCPCB's [PCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) and [assembly capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities) pages on 10 November 2026. The project's KiCad design rules are set to these values or tighter, so DRC enforces them.

| Item | JLCPCB limit (multilayer, 1 oz) | Board |
|---|---|---|
| Track width / spacing | 0.09 / 0.09 mm | 0.15 / 0.15 mm minimum |
| Via hole / diameter without surcharge | hole ≥ 0.3 mm, or 0.2–0.25 mm with diameter ≥ 0.45 mm | 0.3 / 0.6 (322), 0.25 / 0.48 (82), 0.4 / 0.8 (31) |
| Via hole-to-hole | 0.2 mm | 0.25 mm rule |
| Via hole to track | 0.2 mm | ≥ 0.265 mm (0.15 mm clearance plus ring) |
| Inner-layer via hole to copper | 0.2 mm | ≥ 0.315 mm (0.2 mm zone clearance plus ring) |
| Plated through-hole annular ring | 0.20 mm recommended, 0.15 mm minimum | 0.2–0.3 mm |
| Non-plated hole | ≥ 0.5 mm; 0.2 mm to copper | 0.65 mm smallest; ≥ 0.2 mm to copper |
| Plated slot width | ≥ 0.35 mm | 0.6 mm (USB shell) |
| Copper to board edge | 0.2 mm | 0.5 mm rule |
| Pad-to-pad, different nets | 0.15 mm | 0.2 mm (FPC and USB-C pads) |
| Soldermask web | 0.10 mm | 0.10 mm at the 0.5 mm-pitch pads (0.05 mm expansion) |
| Trace coil under mask | 0.15 / 0.15 mm | 0.2 / 0.2 mm (NFC coil) |
| Legend | 1.0 mm text height, 0.15 mm line | All silkscreen raised to these minimums |
| Assembly, Standard | 0.35 mm pin pitch, 01005 | 0.5 mm pitch, 0402 smallest |

Changes made to get there:

- **ESP32 module footprint.** The library footprint's twelve thermal vias were 0.2 mm holes in small pads, which falls in the surcharge range. They are now 0.3 mm. KiCad reports the footprint as differing from its library copy; that is intended.
- **USB connector ground pads.** The manufacturer's land pattern put four pad ends 0.19 mm from the locating holes. They are trimmed by 0.05 mm at that end, giving 0.24 mm.
- **Silkscreen.** All text is at least 1.0 mm high with 0.15 mm strokes, and footprint outlines thinner than 0.15 mm are widened.
- **Design rules.** Hole clearance 0.2 mm, legend minimums, 0.15 mm silk-to-pad, 0.25 mm minimum drill.

## DRC and ERC

KiCad 10.0.8, with schematic parity. Output in `exports/design-review-2026-11-10/`.

| Result | Count | Disposition |
|---|---|---|
| Unconnected, clearance, short, hole, parity | 0 | |
| Dangling track | 4 | T-junction joins; removing any of them opens a connection |
| Silkscreen over board edge | 3 | The module's outline where its antenna overhangs the notch; clipped at fabrication |
| Silkscreen overlap | 2 | U105 and Q101 outlines touch; cosmetic |
| Library footprint mismatch | 1 | The module thermal-via change above |
| ERC | 0 errors, 1 warning | The documented LIS2DW12 address strap |

## Parts

Every fitted part has an LCSC number in the schematic (`LCSC` field), read from JLCPCB's assembly parts search on 10 November 2026. Stock and prices at that time are in [jlcpcb_parts_check_2026-11-10.csv](jlcpcb_parts_check_2026-11-10.csv).

- 59 BOM lines, 145 placements: 31 Basic, 2 Preferred Extended, 26 Extended. Extended parts carry JLCPCB's per-line loading fee; the 26 are the ICs, connectors, LEDs, buttons, inductors and three passives with no Basic equivalent.
- Component cost is about **$19.3 per badge** at JLCPCB's single-unit prices, before the display, cell, PCB, assembly and loading fees. The module ($4.95) and charger ($2.12) are the largest lines.
- Lowest stock: HSMF-C165 status LED (3,165), FH12 display connector (3,334), SWPA4020S inductor (3,475), BQ24074 (4,710). Recheck before a large order.

Substitutions made for sourcing:

| Ref | Was | Now | Why |
|---|---|---|---|
| L101 | Coilcraft XFL4015-471MEB | Sunlord SWPA4020SR47NT, C98415 (0.47 µH, 7 A sat, 29 mΩ) | Coilcraft part is not in JLCPCB's library. Footprint changed to the NR4020-style land (`L_Changjiang_FNR4020S`); **check it against the Sunlord drawing**. |
| R112 | 4.3 kΩ | 4.7 kΩ | Unused charger ILIM setting; shares the Basic 4.7 kΩ line. |
| C105–C107, C114, C505, C512, C513 | 10 µF X7R 0805 | CL21A106KAYNNNE, 10 µF 25 V X5R | Basic part; X5R is adequate for an indoor badge and the 25 V rating loses less capacitance under bias. |
| C113 | 1 nF C0G | CL10B102KB8NNNC, 1 nF 50 V X7R | Basic part; it only sets the display switch slew rate. |
| C203, C511, C515, C509, C201, C409 | X7R as drawn | Basic X5R parts of equal or higher voltage | Decoupling and RC duty only. |
| 1 µF 0805 (11 places) | 6.3–50 V ratings | CL21B105KBFNNNE, 1 µF 50 V X7R | One Basic line covers all of them. |
| D101, D102 | Littelfuse SMF6.0A | C19077499 SMF6.0A (same ratings, Preferred Extended) | No loading fee, deep stock. |
| RT101 | 10 kΩ B3950 NTC (unspecified) | KNTC0603/10KF3950, C2892547 | |

Not from JLCPCB: the display panel (Waveshare 3.7-inch raw panel), the cell (protected 1S pouch with JST PH, at least 300 mA charge rating; **check polarity**), enclosure and dock.

## After the boards arrive

1. Solder `J102` on the rear and `J502` on the front.
2. Before fitting a cell: power from USB, check 3.3 V, flash over native USB.
3. Fit the display flex, then the cell, checking polarity at `J102` with a meter first.
4. Firmware must drive the display signals low before switching its rail off, and set TCA9534 P1 and P4–P7 as outputs driven low.
5. Tune the NFC coil (`C507` 27 pF fitted, `C508` trim position) with the display and cell in place.

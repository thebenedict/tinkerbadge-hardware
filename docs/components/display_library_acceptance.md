# Display library acceptance

Temporary review artifacts below are identified by filename only; these intermediate files are not distributed. Published source outputs and repeatable checks are linked from the [current verification record](../design/verification.md).

2026-11-09. Accepted schematic symbol/pad correspondence for the exact parts below. Source diagrams, symbol readback, disposable native schematic and footprint placement, and fresh renders were inspected. Main-board physical layout and manufacturing acceptance remain open.

The three disposable footprints were placed through Konnect MCP on `check.kicad_pcb`, queried using `get_component_pads`, and exported as SVG. The inspected derived view is `display_footprints_crop.svg.png`. Pin1 markers, cathode marking and non-mirrored top views agree with the original manufacturer diagrams. No main-board placement was performed.

## SI1308EDL-T1-GE3

Footprint: `Package_TO_SOT_SMD:SOT-323_SC-70`. Source: Vishay 63399 Rev C p1 top view; package outline in same PDF.

| Source pin | Function | Symbol pin | Footprint pad | Local X,Y mm |
|---|---|---|---|---|
| 1 | G | 1 | 1 | -0.8875, -0.6500 |
| 2 | S | 2 | 2 | -0.8875, 0.6500 |
| 3 | D | 3 | 3 | 0.8875, 0.0000 |

All electrical leads are represented exactly once; no exposed pad or mounting holes.

## MBR0530T1G

Footprint: `Diode_SMD:D_SOD-123`. Source: onsemi MBR0530T1/D Rev9 p4 CASE425 STYLE1.

| Source pin | Function | Symbol pin | Footprint pad | Local X,Y mm |
|---|---|---|---|---|
| 1 | K | 1 | 1 | -1.6500, 0.0000 |
| 2 | A | 2 | 2 | 1.6500, 0.0000 |

All electrical leads are represented exactly once; no exposed pad or mounting holes.

## SN74LVC541APWR

Footprint: `Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm`. Source: TI SCAS298O p4 PW top-view pin drawing and PW0020A outline.

| Source pin | Function | Symbol pin | Footprint pad | Local X,Y mm |
|---|---|---|---|---|
| 1 | OE1# | 1 | 1 | -2.8625, -2.9250 |
| 2 | A1 | 2 | 2 | -2.8625, -2.2750 |
| 3 | A2 | 3 | 3 | -2.8625, -1.6250 |
| 4 | A3 | 4 | 4 | -2.8625, -0.9750 |
| 5 | A4 | 5 | 5 | -2.8625, -0.3250 |
| 6 | A5 | 6 | 6 | -2.8625, 0.3250 |
| 7 | A6 | 7 | 7 | -2.8625, 0.9750 |
| 8 | A7 | 8 | 8 | -2.8625, 1.6250 |
| 9 | A8 | 9 | 9 | -2.8625, 2.2750 |
| 10 | GND | 10 | 10 | -2.8625, 2.9250 |
| 11 | Y8 | 11 | 11 | 2.8625, 2.9250 |
| 12 | Y7 | 12 | 12 | 2.8625, 2.2750 |
| 13 | Y6 | 13 | 13 | 2.8625, 1.6250 |
| 14 | Y5 | 14 | 14 | 2.8625, 0.9750 |
| 15 | Y4 | 15 | 15 | 2.8625, 0.3250 |
| 16 | Y3 | 16 | 16 | 2.8625, -0.3250 |
| 17 | Y2 | 17 | 17 | 2.8625, -0.9750 |
| 18 | Y1 | 18 | 18 | 2.8625, -1.6250 |
| 19 | OE2# | 19 | 19 | 2.8625, -2.2750 |
| 20 | VCC | 20 | 20 | 2.8625, -2.9250 |

All electrical leads are represented exactly once; no exposed pad or mounting holes.

## Unresolved physical work

J301 remains an explicitly numbered panel interface, with no assigned connector footprint. AYF532435 is a candidate only; panel purchase SKU/revision, contact side, flex route, fold and pin1-to-pad1 mating remain blocked pending actual mechanical evidence. L301 requires an exact 68 µH inductor with qualified saturation/DCR and footprint. Generic passive package associations require exact MPN/DC-bias/voltage/thermal qualification.

The library check establishes numbering and package correspondence. It does not establish assembled switching performance, bias overshoot, display-current budget or antenna/mechanical compatibility.

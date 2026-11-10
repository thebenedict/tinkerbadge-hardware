# SN74LVC541APWR

Display off-state isolation for the five MCU outputs. Power from +3V3_EPD, ground both enables and unused inputs, and mark unused outputs NC. Add 100 nF at pins 20/10. The exact PW package has no exposed pad. Inputs accept 5.5 V and Ioff disables outputs at VCC = 0 V, with 10 µA maximum leakage under its specified test. MCU-side pulls define startup; BUSY uses a ground pulldown and no always-on pullup. Pixel review covered the PW pin drawing, Ioff description, and package outline.

See [display circuit decisions](../design/display.md) for voltage margins, support values, boot/off-state behavior, and release gates.

## Physical pin facts

Source: [SN74LVC541APWR.pdf](https://www.ti.com/lit/ds/symlink/sn74lvc541a.pdf). SCAS298O; June 2026; packaging addendum October 2026; 47 PDF pages. Machine-readable source: [SN74LVC541APWR.pins.json](SN74LVC541APWR.pins.json).

| Pin | Manufacturer function | Type | PDF page |
|---|---|---|---|
| 1 | OE1#: Active-low enable | input | 4 |
| 2 | A1: Channel input | input | 4 |
| 3 | A2: Channel input | input | 4 |
| 4 | A3: Channel input | input | 4 |
| 5 | A4: Channel input | input | 4 |
| 6 | A5: Channel input | input | 4 |
| 7 | A6: Channel input | input | 4 |
| 8 | A7: Channel input | input | 4 |
| 9 | A8: Channel input | input | 4 |
| 10 | GND: Ground | power_in | 4 |
| 11 | Y8: Channel output | tri_state | 4 |
| 12 | Y7: Channel output | tri_state | 4 |
| 13 | Y6: Channel output | tri_state | 4 |
| 14 | Y5: Channel output | tri_state | 4 |
| 15 | Y4: Channel output | tri_state | 4 |
| 16 | Y3: Channel output | tri_state | 4 |
| 17 | Y2: Channel output | tri_state | 4 |
| 18 | Y1: Channel output | tri_state | 4 |
| 19 | OE2#: Active-low enable | input | 4 |
| 20 | VCC: Supply | power_in | 4 |

Status: source facts and electrical assignments independently reviewed; see [display review](../design/review_display.md). Physical and prototype gates are listed in [library acceptance](display_library_acceptance.md).

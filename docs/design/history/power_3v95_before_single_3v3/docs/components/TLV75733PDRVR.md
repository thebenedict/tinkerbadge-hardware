# TLV75733PDRVR

Status: extracted; independent review pending

Package: DRV0006A WSON6 + EP, 2x2mm

Source: [TLV75733PDRVR.pdf](https://www.ti.com/lit/ds/symlink/tlv757p.pdf). Critical PDF pages: 3, 4, 5, 6, 18, 20, 21, 38, 39, 40.

Pin facts are generated from `power_facts.json`. Project assignments are separate in `../design/power_contract.json`.

| Physical pin/pad | Manufacturer function | Meaning |
|---|---|---|
| 1 | OUT | 3.3V regulated output |
| 2 | NC | No internal connection |
| 3 | GND | Ground |
| 4 | EN | Active-high enable |
| 5 | NC | No internal connection |
| 6 | IN | Supply input |
| 7 | EP | Exposed thermal pad, internally connected to GND |

## Design-relevant facts

- Page 3 Figure 4-3 is the selected DRV pinout, which differs from DBV. Original pixels were inspected. Package pages 38–40 explicitly number the exposed pad 7.
- Pages 4–6: input range is 1.45–5.5 V and output is nominally 3.3 V. DRV dropout at 1 A is at most 425 mV through 85°C and 475 mV through 125°C. Output accuracy is ±1% through 85°C and ±1.5% over the full temperature range; observe the table’s test conditions.
- Pages 18–21: effective input and output capacitors must exceed 0.47 µF; use 10 µF nominal each. The device does not block reverse current. Do not externally drive +3V3 while its input is off.
- DRV JEDEC thermal resistance is 100.2°C/W. Solder the thermal pad to the ground plane. At a 0.65 V drop and 0.6 A, 0.39 W would produce about a 39°C rise on that reference board. Validate the actual enclosure and copper layout.

Project circuit and power-state decisions: [power.md](../design/power.md).

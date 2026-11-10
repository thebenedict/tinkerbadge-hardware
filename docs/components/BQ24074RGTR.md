# BQ24074RGTR

Status: extracted; independent review pending

Package: RGT0016C VQFN-16 + exposed pad, 3 × 3 mm

Source: [BQ24074RGTR.pdf](https://www.ti.com/lit/ds/symlink/bq24074.pdf). Critical PDF pages: 7, 8, 9, 10, 12, 13, 14, 27, 28, 29, 30, 33, 34, 52.

Pin facts are generated from `power_facts.json`. Project assignments are separate in `../design/power_contract.json`.

| Physical pin/pad | Manufacturer function | Meaning |
|---|---|---|
| 1 | TS | Battery thermistor input |
| 2 | BAT | Protected battery positive |
| 3 | BAT | Protected battery positive |
| 4 | CE_N | Active-low charge enable |
| 5 | EN2 | Input-current mode bit 2 |
| 6 | EN1 | Input-current mode bit 1 |
| 7 | PGOOD_N | Open-drain valid-input indication |
| 8 | VSS | Ground |
| 9 | CHG_N | Open-drain charging/fault indication |
| 10 | OUT | System power output |
| 11 | OUT | System power output |
| 12 | ILIM | Adapter-current resistor |
| 13 | IN | External supply input |
| 14 | TMR | Safety timer resistor |
| 15 | ITERM | Termination-current programming |
| 16 | ISET | Charge-current programming |
| 17 | EP | Exposed thermal pad, must share VSS potential |

## Design-relevant facts

- Use the lower BQ24074 diagram on page 7, not the BQ24075 SYSOFF variant. The thermal pad uses project symbol/footprint number 17; the source names it Thermal Pad. Connect VSS pin 8 as well. The saved PDF package appendix on page 52 is RGT0016C.
- Pages 10–14: recommended input is 4.35–10.2 V, system output 4.3–4.5 V and battery regulation 4.16–4.23 V. BAT and OUT each require 4.7–47 µF bypass. IN requires 1–10 µF.
- EN2/EN1 modes: 00 gives 100 mA maximum, 01 gives 500 mA maximum, 10 selects ILIM, and 11 suspends input. CE high disables charging while preserving the power path and battery supplement.
- Page 13: TS bias is 72–78 µA, cold threshold 2.0–2.2 V and hot threshold 270–330 mV. Page 30 says the passive Rs/Rp network can widen but cannot narrow the temperature window. Direct B3435 sensing does not guarantee the present pack’s 0–45°C charging window.
- Pages 28–30: CHG can remain low during a temperature fault, so it is not a safe-to-charge signal. Timers slow proportionally during DPPM, input-DPM and thermal charge reduction.

Project circuit and power-state decisions: [power.md](../design/power.md).

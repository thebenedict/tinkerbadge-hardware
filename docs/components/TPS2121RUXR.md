# TPS2121RUXR

Status: extracted; independent review pending

Package: RUX0012A VQFN-HR 12, 2.0x2.5mm

Source: [TPS2121RUXR.pdf](https://www.ti.com/lit/ds/symlink/tps2121.pdf). Critical PDF pages: 4, 5, 6, 8, 13, 19, 21, 39, 40.

Pin facts are generated from `power_facts.json`. Project assignments are separate in `../design/power_contract.json`.

| Physical pin/pad | Manufacturer function | Meaning |
|---|---|---|
| 1 | OUT | Power output |
| 2 | IN2 | Source 2 power input |
| 3 | CP2 | Comparator-mode reference input |
| 4 | OV2 | Source 2 overvoltage supervisor |
| 5 | OV1 | Source 1 overvoltage supervisor |
| 6 | PR1 | Source 1 priority supervisor |
| 7 | IN1 | Source 1 power input |
| 8 | OUT | Power output |
| 9 | ST | Open-drain source status: high/Hi-Z IN1; low IN2 |
| 10 | ILM | Current-limit programming resistor |
| 11 | SS | Soft-start/settling capacitor |
| 12 | GND | Ground |

## Design-relevant facts

- Page 4 Figure 6-2 is a BOTTOM view. The large power pads are numbered 1, 2, 7 and 8. There is no additional exposed ground pad or pin 13.
- Pages 5–8: operating inputs are 2.8–22 V, absolute maximum 24 V. Control pins operate at 0–5.5 V, absolute maximum 6 V. RILM is 18–100 kΩ. The ST pull-up is 6–20 kΩ.
- Pages 13–21: both channels block reverse current, with finite detection current and response time. Measure hot-plug and backfeed behavior. VREF rising threshold is 1.01–1.10 V and control leakage is ±0.1 µA.

Project circuit and power-state decisions: [power.md](../design/power.md).

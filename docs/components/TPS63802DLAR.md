# TPS63802DLAR

Status: extracted; independent review pending

Package: DLA0010A VSON-HR10, 3x2mm

Source: [TPS63802DLAR.pdf](https://www.ti.com/lit/ds/symlink/tps63802.pdf). Critical PDF pages: 4, 5, 6, 11, 12, 18, 19, 20, 35, 36.

Pin facts are generated from `power_facts.json`. Project assignments are separate in `../design/power_contract.json`.

| Physical pin/pad | Manufacturer function | Meaning |
|---|---|---|
| 1 | EN | Active-high converter enable |
| 2 | MODE | Low = power-save mode; high = forced PWM |
| 3 | AGND | Analog ground |
| 4 | FB | Feedback sense |
| 5 | PG | Open-drain power good |
| 6 | VOUT | Regulated output |
| 7 | L2 | Inductor output-side switching node |
| 8 | GND | Power ground |
| 9 | L1 | Inductor input-side switching node |
| 10 | VIN | System input |

## Design-relevant facts

- Pages 4 and 35 show all ten physical pads. The larger functional pads are 6–10. There is no additional exposed pad or ground pin 11.
- Pages 5–6: VIN operates at 1.3–5.5 V, with startup above 1.8 V and 6 V absolute maximum. Output range is 1.8–5.2 V. Converter UVLO is not a safe lithium-ion discharge endpoint.
- Pages 6 and 18: feedback voltage is 0.500 V ±1% in PWM; bias-current magnitude is at most 100 nA. The lower feedback resistor must be at most 100 kΩ. MODE and EN must not float.
- Pages 18–20: nominal inductance is 0.47 µH with effective range 0.37–0.57 µH. Above 3.6 V output use two nominal 22 µF capacitors. Minimum effective output capacitance is 7 µF; the project target is at least 8.2 µF. Minimum effective input capacitance is 4 µF; the project target is at least 5 µF. Boost peak current limit can reach 5.75 A; verify inductor saturation.
- Pages 1 and 6: 2 A at VIN ≥ 2.3 V, VOUT = 3.3 V is the headline capability; the 2.3 V VIN;LOAD entry is in the MAX column for the minimum input needed for 2 A, once started, TJ = 25°C, not an unconditional full-temperature or whole-board current guarantee. Layout, input path, thermal and magnetic limits still apply.
- Page 19: one nominal 22 µF is recommended for outputs ≤3.6 V; increasing output capacitance is permitted without a stated upper limit. The revised shared-3.3 V project retains two 22 µF capacitors for transient margin; actual DC-bias capacitance and startup must be checked.

Project circuit and power-state decisions: [power.md](../design/power.md).

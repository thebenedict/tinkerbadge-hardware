# TMUX1511PWR

Status: extracted; independent review pending

Package: PW TSSOP14

Source: [TMUX1511PWR.pdf](https://www.ti.com/lit/ds/symlink/tmux1511.pdf). Critical PDF pages: 3, 4, 6, 7, 21, 22.

Pin facts are generated from `power_facts.json`. Project assignments are separate in `../design/power_contract.json`.

| Physical pin/pad | Manufacturer function | Meaning |
|---|---|---|
| 1 | SEL1 | Channel 1 enable high |
| 2 | S1 | Channel 1 source |
| 3 | D1 | Channel 1 drain |
| 4 | SEL2 | Channel 2 enable high |
| 5 | S2 | Channel 2 source |
| 6 | D2 | Channel 2 drain |
| 7 | GND | Ground |
| 8 | D3 | Channel 3 drain |
| 9 | S3 | Channel 3 source |
| 10 | SEL3 | Channel 3 enable high |
| 11 | D4 | Channel 4 drain |
| 12 | S4 | Channel 4 source |
| 13 | SEL4 | Channel 4 enable high |
| 14 | VDD | Supply |

## Design-relevant facts

- Page 3 shows the selected 14-pin PW package, with no exposed pad. Active-high SEL inputs have internal 6 MΩ pulldowns.
- Pages 4, 6 and 7: VDD operates at 1.5–5.5 V. Source/drain voltage may reach 3.6 V with VDD below 1.5 V. Powered-off leakage is ±2 µA over the full temperature range; the 10 nA figure applies at 25°C.
- On resistance is at most 4.5 Ω and on leakage is ±50 nA. Operating supply current is 37 µA typical, 70 µA maximum. SEL1 tied to +3V3 connects the ADC automatically without a GPIO.
- Maximum power-off transition time is 4 µs under the specified 1 µs supply-fall test. This is not an unconditional MCU injection-current guarantee for arbitrary ramps. Measure brownout and decay waveforms. The static off-state ADC bound is 0.2 V with its 100 kΩ pulldown.

Project circuit and power-state decisions: [power.md](../design/power.md).

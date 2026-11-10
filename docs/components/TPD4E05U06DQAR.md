# TPD4E05U06DQAR

Status: extracted; independent review pending

Package: DQA USON10, 2.5x1mm

Source: [TPD4E05U06DQAR.pdf](https://www.ti.com/lit/ds/symlink/tpd4e05u06.pdf). Critical PDF pages: 4, 6, 7, 13, 16, 23.

Pin facts are generated from `power_facts.json`. Project assignments are separate in `../design/power_contract.json`.

| Physical pin/pad | Manufacturer function | Meaning |
|---|---|---|
| 1 | D1+ | ESD channel 1 |
| 2 | D1- | ESD channel 2 |
| 3 | GND | Ground |
| 4 | D2+ | ESD channel 3 |
| 5 | D2- | ESD channel 4 |
| 6 | NC | No internal connection |
| 7 | NC | No internal connection |
| 8 | GND | Ground |
| 9 | NC | No internal connection |
| 10 | NC | No internal connection |

## Design-relevant facts

- Page 4 DQA top view was inspected. There is no exposed pad. NC pins 6, 7, 9 and 10 can float or connect to ground; the project leaves them floating.
- Pages 6–7: four independent channels discharge to ground, without a VCC clamp rail. Use them for USB D+, D−, CC1 and CC2, not VBUS. Operating signal maximum is 5.5 V, capacitance 0.5 pF typical and DC breakdown at least 6.5 V. This does not protect sustained CC-to-VBUS shorts.

Project circuit and power-state decisions: [power.md](../design/power.md).

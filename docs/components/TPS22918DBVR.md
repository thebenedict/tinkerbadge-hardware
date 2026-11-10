# TPS22918DBVR

Status: extracted; independent review pending

Package: DBV SOT23-6

Source: [TPS22918DBVR.pdf](https://www.ti.com/lit/ds/symlink/tps22918.pdf). Critical PDF pages: 3, 4, 5, 14, 16, 17, 20.

Pin facts are generated from `power_facts.json`. Project assignments are separate in `../design/power_contract.json`.

| Physical pin/pad | Manufacturer function | Meaning |
|---|---|---|
| 1 | VIN | Supply input |
| 2 | GND | Ground |
| 3 | ON | Active-high enable, never floating |
| 4 | CT | Slew-time capacitor |
| 5 | QOD | Quick-output-discharge connection |
| 6 | VOUT | Switched output |

## Design-relevant facts

- Pages 3–5: VIN operates at 1–5.5 V. ON accepts 3.3 V logic and must not float. The 2 A maximum switch current is not a current limiter. There is no exposed pad.
- Pages 14–17: QOD can connect directly to VOUT, through a resistor, or remain floating to disable discharge. QOD is not GND.
- Isolate panel signal paths separately when the output is off. A series resistor alone does not provide that isolation.

Project circuit and power-state decisions: [power.md](../design/power.md).

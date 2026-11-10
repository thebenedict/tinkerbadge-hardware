# SMF6.0A

Status: extracted; independent review pending

Package: SOD-123FL, two-lead unidirectional TVS

Source: [SMF6.0A.pdf](https://datasheet.octopart.com/SMF6.0A-Littelfuse-datasheet-14426042.pdf). Critical PDF pages: 1, 2, 4, 5.

Pin facts are generated from `power_facts.json`. Project assignments are separate in `../design/power_contract.json`.

| Physical pin/pad | Manufacturer function | Meaning |
|---|---|---|
| 1 | K | Cathode stripe; project pad1 convention |
| 2 | A | Anode; project pad2 convention |

## Design-relevant facts

- Page 5 marks physical polarity rather than numbered leads. Project convention is pin 1 = cathode, pin 2 = anode. Verify the footprint stripe against the drawing.
- Page 2: standoff is 6.0 V, breakdown 6.67–7.37 V at 10 mA, and maximum clamp 10.3 V at 19.4 A for a 10/1000 µs pulse at 25°C. Nonrepetitive pulse rating is 200 W. Reverse leakage is at most 400 µA at 6 V. Apply temperature derating.
- This is an input hot-plug/ESD TVS. Its rated clamp is below the mux’s 24 V and charger’s 28 V absolute maxima. It is not a 5.5 V rail clamp or sustained-overvoltage protection. Source current limiting and surge/thermal qualification are required.

Project circuit and power-state decisions: [power.md](../design/power.md).

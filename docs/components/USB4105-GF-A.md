# USB4105-GF-A

Status: extracted; independent review pending

Package: 16-contact USB-C USB2 receptacle, four shell anchors

Source: [USB4105-GF-A.pdf](https://s3.amazonaws.com/snapeda/datasheet/USB4105-GF-A_GCT.pdf). Critical PDF pages: 1, 2.

Pin facts are generated from `power_facts.json`. Project assignments are separate in `../design/power_contract.json`.

| Physical pin/pad | Manufacturer function | Meaning |
|---|---|---|
| A1 | GND | USB-C contact |
| A4 | VBUS | USB-C contact |
| A5 | CC1 | USB-C contact |
| A6 | Dp1 | USB-C contact |
| A7 | Dn1 | USB-C contact |
| A8 | SBU1 | USB-C contact |
| A9 | VBUS | USB-C contact |
| A12 | GND | USB-C contact |
| B1 | GND | USB-C contact |
| B4 | VBUS | USB-C contact |
| B5 | CC2 | USB-C contact |
| B6 | Dp2 | USB-C contact |
| B7 | Dn2 | USB-C contact |
| B8 | SBU2 | USB-C contact |
| B9 | VBUS | USB-C contact |
| B12 | GND | USB-C contact |
| S1 | SHELL | Unnumbered shell anchor; S1–S4 are project identifiers, not printed manufacturer pin numbers |
| S2 | SHELL | Unnumbered shell anchor; S1–S4 are project identifiers, not printed manufacturer pin numbers |
| S3 | SHELL | Unnumbered shell anchor; S1–S4 are project identifiers, not printed manufacturer pin numbers |
| S4 | SHELL | Unnumbered shell anchor; S1–S4 are project identifiers, not printed manufacturer pin numbers |

## Design-relevant facts

- The saved manufacturer drawing A1 comes from a SnapEDA mirror. The current GCT URL returned HTTP 403. Reconcile the latest drawing before footprint release.
- Page 1 component-side pad order, left to right: A1, B12, A4, B9, B8, A5, B7, A6, A7, B6, A8, B5, B4, A9, B1, A12. In the front mating view A1 is top left, A12 top right, B12 bottom left and B1 bottom right.
- All four shell anchors connect to GND. S1–S4 are project identifiers for unnumbered anchors. A library may repeat pad S1 for the four anchors only after physical verification. The drawing rates collective VBUS at 5 A and 20 V DC; these are connector ratings, not authorization to draw USB current.

Project circuit and power-state decisions: [power.md](../design/power.md).

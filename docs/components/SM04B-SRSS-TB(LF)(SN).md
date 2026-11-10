# SM04B-SRSS-TB(LF)(SN) component facts

## Source and physical package

[SM04B-SRSS-TB.pdf](https://static.maritex.eu/file/display/V4fDhAsiKnBEyPCW56dCheFp9nEKP1kk/SM04B-SRSS-TB.pdf), JST SH catalog extract,printed pages2–3, no visible date/revision. [Source](https://www.jst-mfg.com/product/pdf/eng/eSH.pdf). URL, retrieval route and SHA256 are in `SM04B-SRSS-TB(LF)(SN).source.json` under datasheets.

Side-entry SH four-contact1mm pitch SMT header with two solder retention tabs. Four electrical contacts plus two unnumbered retention tabs. Tabs are not a signal pin or EP; use unnumbered mechanical pads in footprint.

Inspected actual PDF p1 component-side land pattern and p2 side-entry drawing. First circuit is explicitly marked in side-entry mating view. Qwiic reference schematic J3/J4 independently confirms project numbering; archived Qwiic-reference.png.

| Physical pin | Name | Function | PDF page |
|---|---|---|---|
| 1 | CONTACT_1 | First circuit, manufacturer marked CircuitNo.1 | 2 |
| 2 | CONTACT_2 | Second circuit | 2 |
| 3 | CONTACT_3 | Third circuit | 2 |
| 4 | CONTACT_4 | Fourth circuit | 2 |
| MP1 | RETENTION_1 | Unnumbered solder retention tab, mechanical only | 1 |
| MP2 | RETENTION_2 | Unnumbered solder retention tab, mechanical only | 1 |

## Ratings and Qwiic contract

JST rates1A with28AWG,50VAC/DC,−25…85°C including temperature rise. Four-circuit dimensionA3.0mm, B6.0mm, side-entry height2.9mm. Use side-entry land pattern, not BM vertical-header pattern. Official direct download returned403; archived manufacturer-authored catalog obtained from distributor mirror.

Qwiic electrical pin assignment:1GND,2regulated3.3V,3SDA,4SCL, verified against SparkFun Qwiic Motor Driver schematic v10(26 August2019), J3/J4. J501 uses1GND,2ACC_3V3,3EXT_SDA,4EXT_SCL. https://www.sparkfun.com/qwiic defines cable blackGND, red3.3V, blueSDA, yellowSCL. The separately archived cable drawing's numbers are its housing view convention; do not transfer those numbers onto the PCB header blindly. Manufacturer CircuitNo.1 orientation plus actual cable continuity is the physical release check.

Shared50mA normal budget with SAO/IR RX, nominal3.3V only. ExternalI2C is separate from onboard bus,100kHz initial speed,4.7kΩ host pulls to switchedACC_3V3. Qualify cable capacitance/rise time and remove excessive parallel accessory pull-ups. No live insertion or independently powered add-ons in baseline.

## Review state

Extracted 2026-11-09. Electrical source facts and assignments passed [independent review](../design/review_peripherals.md). Connections are maintained in [the peripheral contract](../design/peripherals_contract.json); physical mating, footprints and prototype checks remain separate gates.

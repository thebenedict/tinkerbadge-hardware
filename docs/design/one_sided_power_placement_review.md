# Front-side power and display placement proposal

9 November 2026. Candidate for a 110 × 80 mm PCB, y=100–180 mm. Glass occupies x109.35–202.65/y110–164.9 with a proposed underside 4.5 mm above the front surface. This report supplies coordinates; the PCB owner performs the only CAD edits.

## Arrangement

- USB F(206.325,126),90° faces right, with its archived GCT mating face at x210 and contact row at x202.645. Its protection and input capacitor remain immediately west/north of the front FPC corridor.
- Mux U101(183.5,124), disabled charger U102(177,124), converter U103(165,130), and 6 × 6 mm L101 reservation (170.5,130) form the main power block.
- Battery ADC U107(151,136) remains in a quiet central-left area. Final parent I²C-pull placement near (163.5,128) conflicts with the converter/input-capacitor candidate and must be reconciled during merge.
- Display buffer U301(186,141) directs outputs toward front FPC reserve x195–209/y136–154. Display switch U104(154,146), boost L301 reservation (167,152), and local boost network occupy central lower space. Rail capacitors end at y164.18 and x181.4, clear of the parent's accessory/NFC support area.
- Dock protection and sensing follow the shorter outline and clear LEDs at y174. The dock connector remains a separate mechanical definition.

## Verification

The JSON companion `.build/one_sided_power_plan.json` contains all 83 coordinates, rotations, native transformed pad positions, courtyard bounds, package heights and source gates. No PCB object was moved; calculations transform only numeric geometry. No SaveBoard, schematic, project, footprint or model edits were performed. Source-board hash is recorded in the JSON and checked unchanged.

Conservative courtyard rectangles are screened among these 83 references and against the front FPC corridor. They do not replace a merged-board DRC or support/fastener/optical/RF check. Courtyard line thickness is not added to centerline bounds. Inductor reserve rotations do not establish unknown terminal locations.

## Electrical gates

**Initial allocation, superseded by the input-capacitor amendment below.** C101 stays near USB and C102 near the dock, so neither establishes local input decoupling at U101. TI's supply recommendations call for capacitors close to IN1/IN2/OUT. Before routing, either add local input bypass through a reviewed schematic change or revise allocation of the existing capacitors, then recheck USB inrush/source transitions. This coordinate proposal preserves nets and adds no electrical parts.

C103 is shared by mux output and charger input. Its pad-center distances are recorded below. Keep the complete supply/return loops short; the final escape may require a local bypass revision. C107 is local converter input bypass; C108 is the first output capacitor, and C109 adds shared-rail transient bulk. Keep feedback west of U103 and switching nodes east.

- R120 remains fitted 0 Ω from VSYS to CHARGE_DISABLE. Charging stays disabled. J104 is still optional/DNP.
- Preserve U102 grounded pad17/pin8 and qualified thermal/current-return geometry. Power-path heating still matters with charging off.
- Preserve the exact U103 DLA0010A asymmetric pads, pad8 GND and split paste windows. There is no pad11.
- L101 and L301 have no exact MPN, land pattern, installed height or accepted terminal orientation. No switching-loop closure can be claimed from their padless reservations.
- U105 still has the DQA0010A/B package/land-pattern gate. Keep its reservation close to USB and do not assign generic USON copper.
- FPC contact face, pin order, opening, insertion and fold remain unqualified. Do not treat the drawing reserve as an approved connector.
- Quiet BAT_DIV_PRE/BAT_ADC wiring must avoid the converter/boost switches and high-current returns.

## Height evidence

Source maxima: U101/U102/U103 ≤1.0 mm; U104 ≤1.45; U107/U301 ≤1.2; Q101–Q103 ≤1.25; Q301 ≤1.10; D101/D102 ≤1.10; D301–D303 ≤1.35; USB ≤3.31. Power-package evidence comes from the existing independent source review. This pass inspected actual original-package image pixels for Q301 (SI1308EDL PDF p7), display diodes (MBR0530T1G PDF p4), and buffer (SN74LVC541APWR PDF p27).

Exact capacitor/resistor MPNs and both inductors remain unknown. A 4.0 mm part-height constraint is provisional, not an approved magnetic component. At 4.5 mm glass underside it leaves only 0.5 mm for installed-height tolerance, solder, warp, insulation and shock clearance. Qualify exact parts and the final display supports before assembly release.

## Sources

- AGENTS.md; docs/spec.md; docs/style_guide/routing.md
- docs/design/power_contract.json; docs/design/display_contract.json
- docs/design/pcb_power_footprint_review.md; pcb_final_footprint_review.md
- docs/design/power.md; display.md; single_sided_assembly_assessment.md
- Archived TPS63802 §12, BQ24074 §12, TPS2121 §§11–12; SI1308EDL p7; MBR0530T1G p4; SN74LVC541APWR p27

Source board SHA256: 99158950ecce21da92f8c0e9343ecf60316f321255fd496f790517ac7717f49f

## Pad-center distances

| Connection | Distance mm |
|---|---:|
| C107.1 to U103.10 | 2.11 |
| C107.2 to U103.2 | 2.6 |
| C108.1 to U103.6 | 2.832 |
| C103.1 to U102.13 | 2.762 |
| C103.1 to U101.1 | 2.701 |
| C105.1 to U102.10 | 2.503 |
| C106.1 to U102.2 | 1.607 |
| C312.1 to U301.20 | 1.867 |
| Q301.2 to R301.1 | 1.64 |
| Q301.1 to R302.1 | 1.727 |
| C101.1 to U101.7 | 18.729 |
| C102.1 to U101.2 | 75.824 |

## Coordinate schedule

All entries are F.Cu; RES_ entries remain padless.

| Reference | X | Y | Rotation | Group |
|---|---:|---:|---:|---|
| J101 | 206.325 | 126 | 90 | USB connector and protection |
| RES_U105 | 199 | 126 | 0 | USB connector and protection |
| D101 | 198.9 | 131.8 | 180 | USB connector and protection |
| C101 | 198.9 | 134.6 | 180 | USB connector and protection |
| R101 | 198.7 | 128.4 | 180 | USB connector and protection |
| R102 | 195.6 | 128.4 | 180 | USB connector and protection |
| Q101 | 195.5 | 122.5 | 0 | USB connector and protection |
| R121 | 199.2 | 121.8 | 180 | USB connector and protection |
| R122 | 195.5 | 119.8 | 0 | USB connector and protection |
| R123 | 192.5 | 119 | 0 | USB connector and protection |
| U101 | 183.5 | 124 | 0 | Mux and disabled charger |
| C103 | 180.5 | 120.8 | 90 | Mux and disabled charger |
| C104 | 183.3 | 120.2 | 90 | Mux and disabled charger |
| R109 | 186.2 | 121 | 90 | Mux and disabled charger |
| R103 | 184.7 | 127.2 | 270 | Mux and disabled charger |
| R104 | 184.7 | 130.2 | 270 | Mux and disabled charger |
| R105 | 187.8 | 127.2 | 270 | Mux and disabled charger |
| R106 | 187.8 | 130.2 | 270 | Mux and disabled charger |
| R107 | 190.9 | 127.2 | 270 | Mux and disabled charger |
| R108 | 190.9 | 130.2 | 270 | Mux and disabled charger |
| U102 | 177 | 124 | 0 | Mux and disabled charger |
| C105 | 180.3 | 125 | 90 | Mux and disabled charger |
| C106 | 173 | 124 | 180 | Mux and disabled charger |
| R120 | 174 | 121 | 0 | Mux and disabled charger |
| Q103 | 168.8 | 125 | 0 | Mux and disabled charger |
| R110 | 168.8 | 122 | 0 | Mux and disabled charger |
| R111 | 175.5 | 130.5 | 0 | Mux and disabled charger |
| R112 | 180.2 | 128.6 | 0 | Mux and disabled charger |
| R113 | 177 | 120 | 0 | Mux and disabled charger |
| R114 | 177 | 117.9 | 0 | Mux and disabled charger |
| R115 | 177 | 127.6 | 0 | Mux and disabled charger |
| R116 | 182.9 | 128.5 | 90 | Mux and disabled charger |
| U103 | 165 | 130 | 0 | Main 3V3 converter |
| RES_L101 | 170.5 | 130 | 90 | Main 3V3 converter |
| C107 | 165 | 126.9 | 180 | Main 3V3 converter |
| C108 | 164.7 | 133.8 | 180 | Main 3V3 converter |
| C109 | 164.7 | 137.5 | 180 | Main 3V3 converter |
| R117 | 161.6 | 131.2 | 180 | Main 3V3 converter |
| R118 | 161.6 | 129.1 | 0 | Main 3V3 converter |
| U107 | 151 | 136 | 0 | Quiet battery ADC |
| C115 | 154.7 | 132.3 | 0 | Quiet battery ADC |
| R127 | 145 | 133 | 0 | Quiet battery ADC |
| R128 | 145 | 135 | 180 | Quiet battery ADC |
| R130 | 145 | 137 | 180 | Quiet battery ADC |
| C116 | 141.5 | 135.1 | 180 | Quiet battery ADC |
| R129 | 141.5 | 137.2 | 180 | Quiet battery ADC |
| Q102 | 121 | 166 | 0 | Dock protection and sensing |
| R124 | 117.4 | 163 | 0 | Dock protection and sensing |
| R125 | 117.4 | 165.1 | 0 | Dock protection and sensing |
| R126 | 124.5 | 166 | 0 | Dock protection and sensing |
| D102 | 119 | 175 | 180 | Dock protection and sensing |
| C102 | 124 | 171 | 0 | Dock protection and sensing |
| U104 | 154 | 146 | 0 | Display load switch and signal isolation |
| C112 | 150.7 | 145.2 | 90 | Display load switch and signal isolation |
| C113 | 154.8 | 149.1 | 0 | Display load switch and signal isolation |
| C114 | 157.1 | 143.8 | 90 | Display load switch and signal isolation |
| R119 | 158 | 148.6 | 180 | Display load switch and signal isolation |
| U301 | 186 | 141 | 0 | Display load switch and signal isolation |
| C312 | 191.5 | 138.2 | 0 | Display load switch and signal isolation |
| R303 | 179.7 | 137.4 | 180 | Display load switch and signal isolation |
| R304 | 179.7 | 139.5 | 180 | Display load switch and signal isolation |
| R305 | 179.7 | 141.6 | 180 | Display load switch and signal isolation |
| R306 | 179.7 | 143.7 | 180 | Display load switch and signal isolation |
| R307 | 179.7 | 145.8 | 180 | Display load switch and signal isolation |
| R308 | 188 | 145.9 | 0 | Display load switch and signal isolation |
| C303 | 192 | 145.5 | 90 | Display load switch and signal isolation |
| RES_L301 | 167 | 152 | 90 | Display boost and panel rail capacitors |
| C301 | 162.5 | 147.9 | 180 | Display boost and panel rail capacitors |
| Q301 | 167 | 156.4 | 90 | Display boost and panel rail capacitors |
| R301 | 170.2 | 157.2 | 0 | Display boost and panel rail capacitors |
| R302 | 163.8 | 157.2 | 180 | Display boost and panel rail capacitors |
| C302 | 171.8 | 153.5 | 90 | Display boost and panel rail capacitors |
| D301 | 175.5 | 149.3 | 180 | Display boost and panel rail capacitors |
| D302 | 175.5 | 152.5 | 0 | Display boost and panel rail capacitors |
| D303 | 171.8 | 160 | 180 | Display boost and panel rail capacitors |
| C304 | 179.7 | 149.5 | 0 | Display boost and panel rail capacitors |
| C305 | 175.5 | 163.2 | 0 | Display boost and panel rail capacitors |
| C306 | 179.7 | 163.2 | 0 | Display boost and panel rail capacitors |
| C307 | 176.1 | 160 | 0 | Display boost and panel rail capacitors |
| C308 | 179.7 | 160 | 0 | Display boost and panel rail capacitors |
| C309 | 179.7 | 152.5 | 0 | Display boost and panel rail capacitors |
| C310 | 175.5 | 156.5 | 0 | Display boost and panel rail capacitors |
| C311 | 179.7 | 156.5 | 0 | Display boost and panel rail capacitors |

## Input-capacitor allocation amendment

This amendment supersedes the initial connector-local C101/C102 positions and the local-mux-bypass blocker above. All component values and nets remain unchanged. The six coordinate changes are in .build/one_sided_mux_bypass_amendment.json; native CAD and source schematics were not edited.

Use the existing C101 and C102 as local TPS2121 input bypass, retaining D101/D102 and USB ESD at the connectors. TI SLVSEA3F section11, PDF p33, explicitly says bypass capacitors on IN1/IN2/OUT should be as close as possible to the device; sections10.7/12 discuss hotplug TVS protection and short wide current paths. C101 is already 1 uF/25 V X7R from USB_VBUS to GND, exactly U101 pin7 to GND. C102 has the same value from DOCK_5V to GND, exactly U101 pin2 to GND. No substitution or additional electrical component is needed for this allocation.

The archived GCT connector and Littelfuse TVS sources contain no requirement for a second, connector-local capacitor. Moving the existing bypass to the mux therefore does not establish a need to add parts. C101 remains directly connected to USB VBUS and still counts toward plug-in capacitance/inrush. The contract phrase Connector-side capacitor should be reconciled to local TPS2121 USB input bypass; that is a placement-description update, not a net/value change.

| Reference | X mm | Y mm | Front rotation |
|---|---:|---:|---:|
| C101 | 187 | 124.4 | 0 degrees |
| C102 | 180.8 | 125.2 | 270 degrees |
| C105 | 177.4 | 127.5 | 180 degrees |
| R115 | 177.4 | 130.2 | 0 degrees |
| R112 | 180.5 | 129.6 | 0 degrees |
| R111 | 175.5 | 133.5 | 0 degrees |

The changed positive-pad distances are 1.876 mm from C101 to USB input pin7 and 2.027 mm from C102 to dock input pin2. C105 remains 3.252 mm from charger OUT; C103 remains 2.762 mm from charger IN and 2.701 mm from nearest mux OUT. Numerical geometry checking finds no courtyard rectangle overlaps among the original 83 proposals after these six changes. Ground vias/plane and actual trace escape still determine complete bypass loops.

Remaining qualification: exact capacitor effective capacitance at bias/temperature; total USB plug-in current and capacitance; input-pin ringing and overshoot with intended cables during hotplug/source switching; TVS energy/current coordination and source current limits. This pass did not independently qualify the board against normative USB electrical specifications. Additional capacitance or damping may be justified by those requirements or measurements later, but it is not currently mandated by the reviewed sources and should not be introduced merely to compensate for remote bypass placement.

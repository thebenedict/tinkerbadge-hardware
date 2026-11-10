# Power symbol capture map

Temporary review artifacts below are identified by filename only; these intermediate files are not distributed. Published source outputs and repeatable checks are linked from the [current verification record](verification.md).

Electrical symbol mapping is accepted against the source review in [review_power.md](review_power.md). This is not a complete symbol-to-PCB pad acceptance record. Instance footprints are blank; pad geometry, paste and assembly orientation remain blocked before PCB use.

Custom symbols were created only through Konnect in `power_symbols.kicad_sym`, registered as `Tinkerbadge_Power`, queried back and placed in a disposable project. The rendered inspection is `symbols_final.png`. Every queried electrical pin number matches the source contract. The converter symbol was adjusted after its first render to eliminate a pin-name collision.

The machine-readable rows are in `power_symbol_map.json`. AO3400A numbering is explicitly project-assigned from the manufacturer’s indexed G/S/D physical view. USB shell aliases preserve four separate physical anchors under one SH electrical pin.

## TPS2121RUXR (U101)

Symbol: `Tinkerbadge_Power:TPS2121RUXR`. Source: `docs/datasheets/TPS2121RUXR.pdf`, pages 4, 5, 6, 8, 13, 19, 21, 39, 40.

| Physical lead | Manufacturer function | Symbol pin / name / type | Net |
|---|---|---|---|
| 1 | OUT | 1 / OUT / power_out | VEXT_5V |
| 2 | IN2 | 2 / IN2 / power_in | DOCK_5V |
| 3 | CP2 | 3 / CP2 / input | GND |
| 4 | OV2 | 4 / OV2 / input | MUX_OV_DOCK |
| 5 | OV1 | 5 / OV1 / input | MUX_OV_USB |
| 6 | PR1 | 6 / PR1 / input | MUX_PRIORITY_USB |
| 7 | IN1 | 7 / IN1 / power_in | USB_VBUS |
| 8 | OUT | 8 / OUT / passive | VEXT_5V |
| 9 | ST | 9 / ST / open_collector | MUX_USB_SELECTED |
| 10 | ILM | 10 / ILM / passive | MUX_ILM |
| 11 | SS | 11 / SS / passive | MUX_SS |
| 12 | GND | 12 / GND / power_in | GND |

## BQ24074RGTR (U102)

Symbol: `Battery_Management:BQ24074RGT`. Source: `docs/datasheets/BQ24074RGTR.pdf`, pages 7, 8, 9, 10, 12, 13, 14, 27, 28, 29, 30, 33, 34, 52.

| Physical lead | Manufacturer function | Symbol pin / name / type | Net |
|---|---|---|---|
| 1 | TS | 1 / TS / passive | BATT_NTC_OPTIONAL |
| 2 | BAT | 2 / BAT / power_out | VBAT_PROTECTED |
| 3 | BAT | 3 / BAT / passive | VBAT_PROTECTED |
| 4 | CE_N | 4 / ~{CE} / input | CHARGE_DISABLE |
| 5 | EN2 | 5 / EN2 / input | GND |
| 6 | EN1 | 6 / EN1 / input | CHARGER_EN1 |
| 7 | PGOOD_N | 7 / ~{PGOOD} / open_collector | CHARGER_PGOOD_N |
| 8 | VSS | 8 / VSS / power_in | GND |
| 9 | CHG_N | 9 / ~{CHG} / open_collector | CHARGER_CHG_N |
| 10 | OUT | 10 / OUT / power_out | VSYS |
| 11 | OUT | 11 / OUT / passive | VSYS |
| 12 | ILIM | 12 / ILIM / passive | CHARGER_ILIM |
| 13 | IN | 13 / IN / power_in | VEXT_5V |
| 14 | TMR | 14 / TMR / input | CHARGER_TMR |
| 15 | ITERM | 15 / ITERM / input | NC |
| 16 | ISET | 16 / ISET / passive | CHARGER_ISET |
| 17 | EP | 17 / VSS / passive | GND |

## TPS63802DLAR (U103)

Symbol: `Tinkerbadge_Power:TPS63802DLAR`. Source: `docs/datasheets/TPS63802DLAR.pdf`, pages 4, 5, 6, 11, 12, 18, 19, 20, 35, 36.

| Physical lead | Manufacturer function | Symbol pin / name / type | Net |
|---|---|---|---|
| 1 | EN | 1 / EN / input | VSYS |
| 2 | MODE | 2 / MODE / input | GND |
| 3 | AGND | 3 / AGND / power_in | GND |
| 4 | FB | 4 / FB / input | PRIMARY_FB |
| 5 | PG | 5 / PG / open_collector | NC |
| 6 | VOUT | 6 / VOUT / power_out | +3V3 |
| 7 | L2 | 7 / L2 / passive | PRIMARY_L2 |
| 8 | GND | 8 / GND / power_in | GND |
| 9 | L1 | 9 / L1 / passive | PRIMARY_L1 |
| 10 | VIN | 10 / VIN / power_in | VSYS |

## TPS22918DBVR (U104)

Symbol: `Tinkerbadge_Power:TPS22918DBVR`. Source: `docs/datasheets/TPS22918DBVR.pdf`, pages 3, 4, 5, 14, 16, 17, 20.

| Physical lead | Manufacturer function | Symbol pin / name / type | Net |
|---|---|---|---|
| 1 | VIN | 1 / VIN / power_in | +3V3 |
| 2 | GND | 2 / GND / power_in | GND |
| 3 | ON | 3 / ON / input | EPD_EN |
| 4 | CT | 4 / CT / passive | EPD_CT |
| 5 | QOD | 5 / QOD / passive | EPD_QOD |
| 6 | VOUT | 6 / VOUT / power_out | +3V3_EPD |

## TPD4E05U06DQAR (U105)

Symbol: `Power_Protection:TPD4E05U06DQA`. Source: `docs/datasheets/TPD4E05U06DQAR.pdf`, pages 4, 6, 7, 13, 16, 23.

| Physical lead | Manufacturer function | Symbol pin / name / type | Net |
|---|---|---|---|
| 1 | D1+ | 1 / D1+ / passive | USB_DP |
| 2 | D1- | 2 / D1- / passive | USB_DM |
| 3 | GND | 3 / GND / power_in | GND |
| 4 | D2+ | 4 / D2+ / passive | USB_CC1 |
| 5 | D2- | 5 / D2- / passive | USB_CC2 |
| 6 | NC | 6 / NC / free | NC |
| 7 | NC | 7 / NC / free | NC |
| 8 | GND | 8 / GND / passive | GND |
| 9 | NC | 9 / NC / free | NC |
| 10 | NC | 10 / NC / free | NC |

## TMUX1511PWR (U107)

Symbol: `Tinkerbadge_Power:TMUX1511PWR`. Source: `docs/datasheets/TMUX1511PWR.pdf`, pages 3, 4, 6, 7, 21, 22.

| Physical lead | Manufacturer function | Symbol pin / name / type | Net |
|---|---|---|---|
| 1 | SEL1 | 1 / SEL1 / input | +3V3 |
| 2 | S1 | 2 / S1 / passive | BAT_DIV_PRE |
| 3 | D1 | 3 / D1 / passive | BAT_SENSE_ISOLATED |
| 4 | SEL2 | 4 / SEL2 / input | GND |
| 5 | S2 | 5 / S2 / passive | NC |
| 6 | D2 | 6 / D2 / passive | NC |
| 7 | GND | 7 / GND / power_in | GND |
| 8 | D3 | 8 / D3 / passive | NC |
| 9 | S3 | 9 / S3 / passive | NC |
| 10 | SEL3 | 10 / SEL3 / input | GND |
| 11 | D4 | 11 / D4 / passive | NC |
| 12 | S4 | 12 / S4 / passive | NC |
| 13 | SEL4 | 13 / SEL4 / input | GND |
| 14 | VDD | 14 / VDD / power_in | +3V3 |

## USB4105-GF-A (J101)

Symbol: `Connector:USB_C_Receptacle_USB2.0_16P`. Source: `docs/datasheets/USB4105-GF-A.pdf`, pages 1, 2.

| Physical lead | Manufacturer function | Symbol pin / name / type | Net |
|---|---|---|---|
| A1 | GND | A1 / GND / passive | GND |
| A4 | VBUS | A4 / VBUS / passive | USB_VBUS |
| A5 | CC1 | A5 / CC1 / bidirectional | USB_CC1 |
| A6 | Dp1 | A6 / D+ / bidirectional | USB_DP |
| A7 | Dn1 | A7 / D- / bidirectional | USB_DM |
| A8 | SBU1 | A8 / SBU1 / bidirectional | NC |
| A9 | VBUS | A9 / VBUS / passive | USB_VBUS |
| A12 | GND | A12 / GND / passive | GND |
| B1 | GND | B1 / GND / passive | GND |
| B4 | VBUS | B4 / VBUS / passive | USB_VBUS |
| B5 | CC2 | B5 / CC2 / bidirectional | USB_CC2 |
| B6 | Dp2 | B6 / D+ / bidirectional | USB_DP |
| B7 | Dn2 | B7 / D- / bidirectional | USB_DM |
| B8 | SBU2 | B8 / SBU2 / bidirectional | NC |
| B9 | VBUS | B9 / VBUS / passive | USB_VBUS |
| B12 | GND | B12 / GND / passive | GND |
| S1 | SHELL | SH / SHIELD / passive | GND |
| S2 | SHELL | SH / SHIELD / passive | GND |
| S3 | SHELL | SH / SHIELD / passive | GND |
| S4 | SHELL | SH / SHIELD / passive | GND |

## AO3400A (Q101)

Symbol: `Transistor_FET:AO3400A`. Source: `docs/datasheets/AO3400A.pdf`, pages 1.

| Physical lead | Manufacturer function | Symbol pin / name / type | Net |
|---|---|---|---|
| 1 | G | 1 / G / input | USB_PRESENT_GATE |
| 2 | S | 2 / S / passive | GND |
| 3 | D | 3 / D / passive | USB_PRESENT_N |

## Remaining interfaces and discrete parts

D101/D102 use `Device:D_Zener`: symbol pin 1 is K and pin 2 is A, matching the explicitly project-numbered SMF6.0A cathode/anode map. Their final 270° symbol rotation puts K above A; both exported nets were rechecked after rotation. J102/J103/J104 use the two-terminal logical connector symbol, with unassigned physical parts and footprints. J104 is marked `NTC (DNP)` and carries `Populate=DNP`. The installed MCP has no native DNP-attribute operation, so downstream assembly/BOM tooling must honor the contract’s fitted=false entry and not infer population from a missing native flag.

Standard footprint queries are retained under `power_footprint_query_*.json`. They informed orientation checks, not blanket acceptance. In particular, the BQ symbol’s default EP1.6 footprint was not accepted in place of the saved RGT0016C drawing’s EP1.68 dimensions; the instance footprint is blank. AOS recommended land geometry differs from the standard SOT-23 candidate and remains a physical review gate.

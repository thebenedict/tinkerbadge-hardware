# Power project pin assignments

Generated from `power_contract.json`. Manufacturer facts remain in `../components/power_facts.json`; shared AO3400A facts are in `../components/AO3400A.pins.json`.

A null net means intentional NC on a reviewed component. On a blocked component, null means unresolved and no CAD connection is permitted.

Review status: reviewed electrical capture; physical footprint acceptance remains pending

## U101 — TPS2121RUXR

Status: ready_for_independent_review

| Physical pin/pad | Project net |
|---|---|
| 1 | VEXT_5V |
| 2 | DOCK_5V |
| 3 | GND |
| 4 | MUX_OV_DOCK |
| 5 | MUX_OV_USB |
| 6 | MUX_PRIORITY_USB |
| 7 | USB_VBUS |
| 8 | VEXT_5V |
| 9 | MUX_USB_SELECTED |
| 10 | MUX_ILM |
| 11 | MUX_SS |
| 12 | GND |

## U102 — BQ24074RGTR

Status: ready_for_independent_review

| Physical pin/pad | Project net |
|---|---|
| 1 | BATT_NTC_OPTIONAL |
| 2 | VBAT_PROTECTED |
| 3 | VBAT_PROTECTED |
| 4 | CHARGE_DISABLE |
| 5 | GND |
| 6 | CHARGER_EN1 |
| 7 | CHARGER_PGOOD_N |
| 8 | GND |
| 9 | CHARGER_CHG_N |
| 10 | VSYS |
| 11 | VSYS |
| 12 | CHARGER_ILIM |
| 13 | VEXT_5V |
| 14 | CHARGER_TMR |
| 15 | NC / blocked as status states |
| 16 | CHARGER_ISET |
| 17 | GND |

## U103 — TPS63802DLAR

Status: ready_for_independent_review

| Physical pin/pad | Project net |
|---|---|
| 1 | VSYS |
| 2 | GND |
| 3 | GND |
| 4 | PRIMARY_FB |
| 5 | NC / blocked as status states |
| 6 | VLED_3V9 |
| 7 | PRIMARY_L2 |
| 8 | GND |
| 9 | PRIMARY_L1 |
| 10 | VSYS |

## U104 — TPS22918DBVR

Status: ready_for_independent_review

| Physical pin/pad | Project net |
|---|---|
| 1 | +3V3 |
| 2 | GND |
| 3 | EPD_EN |
| 4 | EPD_CT |
| 5 | EPD_QOD |
| 6 | +3V3_EPD |

## U105 — TPD4E05U06DQAR

Status: ready_for_independent_review

| Physical pin/pad | Project net |
|---|---|
| 1 | USB_DP |
| 2 | USB_DM |
| 3 | GND |
| 4 | USB_CC1 |
| 5 | USB_CC2 |
| 6 | NC / blocked as status states |
| 7 | NC / blocked as status states |
| 8 | GND |
| 9 | NC / blocked as status states |
| 10 | NC / blocked as status states |

## U106 — TLV75733PDRVR

Status: ready_for_independent_review

| Physical pin/pad | Project net |
|---|---|
| 1 | +3V3 |
| 2 | NC / blocked as status states |
| 3 | GND |
| 4 | VLED_3V9 |
| 5 | NC / blocked as status states |
| 6 | VLED_3V9 |
| 7 | GND |

## U107 — TMUX1511PWR

Status: ready_for_independent_review

| Physical pin/pad | Project net |
|---|---|
| 1 | +3V3 |
| 2 | BAT_DIV_PRE |
| 3 | BAT_SENSE_ISOLATED |
| 4 | GND |
| 5 | NC / blocked as status states |
| 6 | NC / blocked as status states |
| 7 | GND |
| 8 | NC / blocked as status states |
| 9 | NC / blocked as status states |
| 10 | GND |
| 11 | NC / blocked as status states |
| 12 | NC / blocked as status states |
| 13 | GND |
| 14 | +3V3 |

## Q101 — AO3400A

Status: ready_for_independent_review

| Physical pin/pad | Project net |
|---|---|
| 1 | USB_PRESENT_GATE |
| 2 | GND |
| 3 | USB_PRESENT_N |

## Q102 — AO3400A

Status: ready_for_independent_review

| Physical pin/pad | Project net |
|---|---|
| 1 | DOCK_PRESENT_GATE |
| 2 | GND |
| 3 | DOCK_PRESENT_N |

## Q103 — AO3400A

Status: ready_for_independent_review

| Physical pin/pad | Project net |
|---|---|
| 1 | MUX_USB_SELECTED |
| 2 | GND |
| 3 | CHARGER_EN1 |

## D101 — SMF6.0A

Status: ready_for_independent_review

| Physical pin/pad | Project net |
|---|---|
| 1 | USB_VBUS |
| 2 | GND |

## D102 — SMF6.0A

Status: ready_for_independent_review

| Physical pin/pad | Project net |
|---|---|
| 1 | DOCK_5V |
| 2 | GND |

## J101 — USB4105-GF-A

Status: ready_for_independent_review

| Physical pin/pad | Project net |
|---|---|
| A1 | GND |
| A4 | USB_VBUS |
| A5 | USB_CC1 |
| A6 | USB_DP |
| A7 | USB_DM |
| A8 | NC / blocked as status states |
| A9 | USB_VBUS |
| A12 | GND |
| B1 | GND |
| B4 | USB_VBUS |
| B5 | USB_CC2 |
| B6 | USB_DP |
| B7 | USB_DM |
| B8 | NC / blocked as status states |
| B9 | USB_VBUS |
| B12 | GND |
| SH | GND |

## J102 — Logical interface

Status: logical_two_wire_interface_exact_mating_connector_pending

| Physical pin/pad | Project net |
|---|---|
| 1 | VBAT_PROTECTED |
| 2 | GND |

## J103 — Logical interface

Status: logical_only_mechanical_contact_design_pending

| Physical pin/pad | Project net |
|---|---|
| 1 | DOCK_5V |
| 2 | GND |

## J104 — Logical interface

Status: optional_DNP_thermistor_interface_exact_part_pending

| Physical pin/pad | Project net |
|---|---|
| 1 | BATT_NTC_OPTIONAL |
| 2 | GND |

## Support parts

| Ref | Value | Pin 1 net | Pin 2 net | Notes |
|---|---|---|---|---|
| R101 | 5.1k 1% | USB_CC1 | GND | Independent USB-C sink Rd. No PD negotiation or source-current advertisement measurement. |
| R102 | 5.1k 1% | USB_CC2 | GND | Independent USB-C sink Rd. |
| R103 | 44.2k 0.1% | USB_VBUS | MUX_OV_USB |  |
| R104 | 10.0k 0.1% | MUX_OV_USB | GND |  |
| R105 | 44.2k 0.1% | DOCK_5V | MUX_OV_DOCK |  |
| R106 | 10.0k 0.1% | MUX_OV_DOCK | GND |  |
| R107 | 31.6k 0.1% | USB_VBUS | MUX_PRIORITY_USB |  |
| R108 | 10.0k 0.1% | MUX_PRIORITY_USB | GND |  |
| R109 | 80.6k 1% | MUX_ILM | GND |  |
| R110 | 10k 1% | VSYS | MUX_USB_SELECTED |  |
| R111 | 100k 1% | VSYS | CHARGER_EN1 |  |
| R112 | 4.32k 1% | CHARGER_ILIM | GND |  |
| R113 | 3.32k 1% | CHARGER_ISET | GND |  |
| R114 | 47.5k 1% | CHARGER_TMR | GND |  |
| R115 | 100k 1% | +3V3 | CHARGER_PGOOD_N |  |
| R116 | 100k 1% | +3V3 | CHARGER_CHG_N |  |
| R117 | 69.0k 0.1% | VLED_3V9 | PRIMARY_FB |  |
| R118 | 10.0k 0.1% | PRIMARY_FB | GND |  |
| R119 | 1k 1% | +3V3_EPD | EPD_QOD |  |
| R120 | 0 | VSYS | CHARGE_DISABLE | FITTED hard disable: charging remains off until an autonomous temperature-safety circuit is reviewed. Do not replace with a ground strap. |
| R121 | 100k 1% | USB_VBUS | USB_PRESENT_GATE |  |
| R122 | 470k 1% | USB_PRESENT_GATE | GND |  |
| R123 | 100k 1% | +3V3 | USB_PRESENT_N |  |
| R124 | 100k 1% | DOCK_5V | DOCK_PRESENT_GATE |  |
| R125 | 470k 1% | DOCK_PRESENT_GATE | GND |  |
| R126 | 100k 1% | +3V3 | DOCK_PRESENT_N |  |
| R127 | 100k 0.1% | VBAT_PROTECTED | BAT_DIV_PRE |  |
| R128 | 100k 0.1% | BAT_DIV_PRE | GND |  |
| R129 | 100k 0.1% | BAT_ADC | GND |  |
| R130 | 10k 0.1% | BAT_SENSE_ISOLATED | BAT_ADC | Limits transient current during switch supply removal. Operating ADC transfer is VBAT/3.2, including R127/R128/R129/R130. |
| C101 | 1uF 25V X7R | USB_VBUS | GND | Connector-side capacitor; include in the USB plug-in capacitance budget. |
| C102 | 1uF 25V X7R | DOCK_5V | GND | Exposed-input capacitor, rated 25 V. |
| C103 | 4.7uF 25V X7R | VEXT_5V | GND | Also provides charger IN bypass. |
| C104 | 100nF 16V X7R | MUX_SS | GND | Estimated 6.4 ms ramp to 5 V; verify startup and inrush. |
| C105 | 10uF 10V X7R | VSYS | GND | Charger OUT bypass. |
| C106 | 10uF 10V X7R | VBAT_PROTECTED | GND | Charger BAT bypass, on the protected pack node only. |
| C107 | 10uF 10V X7R | VSYS | GND | Local TPS63802 input bypass; effective capacitance at least 5 µF. |
| C108 | 22uF 10V X7R | VLED_3V9 | GND | Local converter output. The parallel pair must retain at least 8.2 µF effective capacitance. |
| C109 | 22uF 10V X7R | VLED_3V9 | GND | Second output capacitor required above 3.6 V output. |
| C110 | 10uF 10V X7R | VLED_3V9 | GND | Local LDO input bypass. |
| C111 | 10uF 6.3V X7R | +3V3 | GND | Local LDO output; effective capacitance must exceed 0.47 µF. |
| C112 | 1uF 6.3V X7R | +3V3 | GND | Display load-switch input bypass. |
| C113 | 1nF 16V C0G | EPD_CT | GND | Typical rise time about 1.68 ms at 3.3 V. Measure peak display inrush. |
| C114 | 10uF 6.3V X7R | +3V3_EPD | GND | Display load-switch output bypass. The display block includes further local panel capacitors. |
| C115 | 100nF 6.3V X7R | +3V3 | GND | Local TMUX supply bypass. |
| C116 | 10nF 6.3V X7R | BAT_DIV_PRE | GND | ADC filter is upstream of isolation, avoiding a charged filter capacitor directly on an unpowered MCU pin. Wait at least 5 ms after startup. |
| L101 | 0.47uH | PRIMARY_L1 | PRIMARY_L2 | Select exact MPN before footprint release. Required effective inductance 0.37–0.57 µH, saturation-current target at least 7 A and DCR at most 40 mΩ. No magnetic MPN is approved. |

## Unresolved gates

- J102 is a logical two-wire battery interface, not an approved mating pinout. Select an ordinary protected 1S 4.2 V LiPo pack and verify its connector rating and polarity before assigning the footprint. J104 is an optional unpopulated separate cell-contact thermistor interface.
- Charging is hard disabled by fitted R120. J104 is DNP. Fitting a thermistor alone does not enable or qualify charging; an independently reviewed autonomous temperature window is still required.
- L101 exact MPN and footprint are not selected. Verify effective inductance, saturation current and DCR.
- The 3.95 V primary envelope, including power-save mode and transients, plus LDO headroom and thermal behavior require prototype qualification.
- The two-wire battery pack and connector are not selected. Their ratings must cover measured peak loads, or firmware and hardware limits must constrain those loads. The prior 1 A candidate cannot support unqualified simultaneous maxima.
- USB100 mode limits charger input, not total USB load. USB enumeration, suspend, current advertisement, inrush and upstream fault coordination remain unqualified.

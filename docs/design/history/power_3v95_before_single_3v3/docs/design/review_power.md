# Independent power source review

Temporary review artifacts below are identified by filename only; these intermediate files are not distributed. Published source outputs and repeatable checks are linked from the [current verification record](../../../../verification.md).

2026-11-09. Reviewer: display/MCU circuit reviewer, independent of the power author.

**PASS for development schematic capture with charging hard-disabled and J102 unconnected.** No power CAD was modified. This is not approval for battery hookup, charging, PCB release, thermal/current performance or USB compliance. Later battery/charger redesign requires a new review.

## Original evidence

Inspected original-source rendered pin diagrams: TPS2121 p4 bottom view; BQ24074 p7 lower top-view diagram and p52 package; TPS63802 p4/35; TPS22918 p3; TPD4E05U06 p4; TLV757P p3/38; TMUX1511 p3. Inspected GCT USB4105 p1, AO3400A p1, SMF6.0A p2/5. Independently re-extracted all eight selected IC/MOSFET PDFs into `review_power_*.txt`, then compared critical electrical tables and formulas to these originals, not only component summaries. Independently transcribed all seven IC maps and machine-compared them to facts. All inventory hashes match. Reviewed15 primary components and47 support elements.

## Physical map results

- U101 TPS2121RUXR all12 pads pass. OUT1/8, IN2=2, CP2=3, OV2=4, OV1=5, PR1=6, IN1=7, ST9, ILM10, SS11, GND12. The source is bottom view. No extra ground EP13 exists.
- U102 BQ24074 all16 signal pads pass. ITERM15 is specific to this variant; do not use another variant's SYSOFF/TD. Thermal pad is VSS and uses project number17. VSS8 must also ground. BAT2/3 and OUT10/11 both connect. Source p7 names RGT0016B but the current included package appendix p52 is RGT0016C; exact footprint dimensions need that current appendix.
- U103 TPS63802 all10 pads pass. EN1/VIN10=VSYS, MODE2 grounded, AGND3/GND8 grounded, FB4 divider, PG5 NC, VOUT6, L2=7, L1=9. Large functional power pads are not a separate EP.
- U104 TPS22918 VIN1/GND2/ON3/CT4/QOD5/VOUT6 pass. QOD connects through1 kohm to output, not ground. ON must not float.
- U105 TPD4E05U06 channels1/2/4/5, GND3/8, NC6/7/9/10 pass. Opposite NC pads are not internally routed signal outputs. Not sustained CC-to-VBUS protection.
- U106 TLV75733PDRVR uses the DRV map OUT1,NC2,GND3,EN4,NC5,IN6,EP7. The package drawing explicitly identifies EP7. EN-to-input and10 uF local bypass are correct. Effective input/output capacitance must exceed0.47 uF.
- U107 TMUX1511PWR14-pin PW map passes, including SEL4=13 and VDD14. SEL1/VDD=+3V3, other selects grounded, unused channels NC. Channel1 switches S2→D3. Powered-off protection is essential; a generic analog switch is not equivalent.
- Q101–103 AO3400A source p1 gives physical G/S/D and index geometry, not printed numbers. Accept **project-assigned**1=markedG,2=adjacentS,3=oppositeD only when footprint XY matches the source top view. No manufacturer-numbered pin claim is made. Source p5 is switching waveforms, not a package drawing; shared component citation correction and official AOS-SOT23.pdf are being maintained by the peripheral author. Footprint acceptance is separate from these electrical endpoints.
- D101/102 SMF6.0A banded cathodes go to input supplies, anodes ground. Project1=K/2=A is explicitly a project convention for unnumbered physical leads.6 V standoff and10.3 V rated-pulse clamp are correct, not a5.5 V rail clamp or sustained-fault protection.
- USB4105 contact functions, duplicated D+/D− pairs, VBUS/GND contacts, separate5.1 kohm CC pull-downs and NC SBU contacts agree. S1–S4 are project IDs for unnumbered shell anchors. J102 all-null contact nets and no footprint remain blocked. J103 is a logical dock interface only.

## Independent calculations and behavior

- TPS2121 ILIM=65.2/R(kohm)^0.861 gives1.488995 A typical at80.6 kohm. Source1–2 A limits are characterized at80 kohm, not exactly80.6 kohm. This is protection, not a USB current allowance.
- Divider0.1% extrema give priority4.19522–4.58296 V and OVP5.46528–5.97173 V rising thresholds before leakage. Control100 nA leakage adds only a few millivolts input-referred.5.25 V is below minimum OVP. Below the priority threshold, a higher dock voltage can win as the source truth table specifies.
- ST high/Hi-Z means IN1 or no valid source; LOW means IN2. R110 pull-up and Q103 inversion select EN2/EN1=00 (USB100) for USB,01 (USB500) for dock. BQ logic high1.4 V and maximum10 uA input current with100 kohm pull-up require VSYS>=2.4 V, met in the stated range. Use this bound rather than only approximate285 kohm internal pull-down. Test actual switching transitions and total USB current.
- Fitted R1200 ohm VSYS→CE disables charging at a valid system rail; BQ source explicitly preserves OUT/battery supplement with CE high. Unknown/open TS is not bypassed. No battery connection or charge enable is approved.
- Prospective3.32 kohm charge resistor gives237.68–296.64 mA including source factor797–975 Aohm and1% tolerance.47.5 kohm timer gives6.333 h typical,4.7025–7.9958 h extrema; precharge one tenth. ITERM open uses default. These calculations do not authorize charging an unspecified pack.
-69.0k/10.0k feedback gives3.95 V nominal. Including±1% feedback,0.1% resistor extrema and conservative±100 nA bias gives3.89677–4.00338 V in PWM. MODE=0 permits PFM, so this is not an all-load transient envelope. Two22 uF output caps above3.6 V agree with TI; actual effective output>=8.2 uF/input>=5 uF and L1010.37–0.57 uH remain selection checks. Exact magnetic MPN is not approved.
- LDO maximum3.3×1.015=3.3495 V plus475 mV maximum1 A dropout is3.8245 V. Calculated primary minimum leaves72.27 mV before transient/routing loss. Thermal and line/load regulation tests remain required; a1 A nameplate is not a qualified sustained system load. LED logic margin depends on separately reviewed exact pixel limits.
- Updated ADC C116 is upstream of the isolator; R13010 kohm is after it. Loaded ratio is VBAT/3.2, nominal1.328125 V at4.25 V. Off upstream voltage about2.13 V is under the3.6 V powered-off rating. Full-temperature2 uA leakage into100 kohm bounds static MCU input near0.20 V.4 us switch-off is conditional on TI's1 us supply-fall test, not arbitrary brownout. Calibration, acquisition and settling need measurement.

## Integration corrections and remaining gates

- Power/display rail is now standardized to+3V3_EPD. Initial EPD_3V3 spelling would have left them disconnected.
- Missing EPD_EN pull-down was added as R207100 kohm on MCU under integration-owner instruction, with amended source review in review_mcu.md. It handles MCU high impedance, not the intentional USB-OTG ROM HIGH state.
- Preserve disabled charging, unknown pack contact order/NTC qualification, exact inductor/capacitor requirements, protected battery node, thermal limits and current-limited bench supplies. Battery connector1 A cannot be protected by a2–4.5 A PCM trip. Simultaneous full loads are not qualified.
- USB100 with no battery may not boot. Enumeration/suspend/Type-C advertisement/inrush and total upstream current are not certified. TVS/source-fault coordination, backfeed, actual source transitions, startup/brownout, storage current and low-voltage restart remain full-system tests.
- No routing, manufacturing release or approval of future changes follows from this review.

## Reviewed SHA-256

- `docs/design/power_contract.json`: `f8dbda080d3aac1f34a2c0e43e9e91642410b47810c32536697ffb16d33dbc66`
- `docs/components/power_facts.json`: `fa07343ff2c170149ebfc668ac3c1c740363b7454ec155d8b6e27d1f7a1532cf`
- `docs/datasheets/power_inventory.json`: `796d015764af33298cc4377bb50fddd4075547b504bb3fb39fb8821f35db0319`
- `docs/datasheets/TPS2121RUXR.pdf`: `b2f5950f596dc2c4ca33e4ebac27fd35e4dcc68ea63e173466123e1118e91a06`
- `docs/datasheets/BQ24074RGTR.pdf`: `4fe4e4f9855501f83b400c6932e3098439e51c50539e40dc45b44a8d509e8db1`
- `docs/datasheets/TPS63802DLAR.pdf`: `be07deca1231c5493957bc64c2dc1cad5543bff330e49ae41caf3286fd80dca6`
- `docs/datasheets/TPS22918DBVR.pdf`: `1b28eb58003d28b18bf919a15734056f296a499bebee2bd493a1e4358c4dfb1c`
- `docs/datasheets/TPD4E05U06DQAR.pdf`: `c167cf1e72a5473a4d2c59b6a3c0251498701da05b7785919b9ceaae3b3e02c6`
- `docs/datasheets/LP603450.pdf`: `46d1f33d6de0c5ff81b80471a1f5973744574150349fc1152e5967f51f017052`
- `docs/datasheets/USB4105-GF-A.pdf`: `1077a88a61449995ed13bf7dba2585fcadf629aa071a4052691e2fd12759219b`
- `docs/datasheets/TPS3700DDCR.pdf`: `3bb7daed20b154bf22ded78e23269c6437eb587400b89bce0f543813df94ebf0`
- `docs/datasheets/TLV75733PDRVR.pdf`: `239d1f1e9bce270377e9af29bd06a5f99fe45f489878612d249d88cf9f2dd7a1`
- `docs/datasheets/TMUX1511PWR.pdf`: `04291b41a68347fedbbb0776aa44f500eaca65f2ca3af0e022ee60d41c7b1e9f`
- `docs/datasheets/SMF6.0A.pdf`: `543ea7413424eddda26798f6cb121c71ca701630dc936363818dbba00a3c27f5`
- `docs/datasheets/532610371-product.pdf`: `6ec8cb03a0d6fddc78d45dc98dc09baf6dd69abc526a632cbe8943e03ca38d20`
- `docs/datasheets/AO3400A.pdf`: `9c60d0b6c1ddc7609a4b788a91181468d8ffe6c3e9ba425c3d8ffc5ba88c5033`
- `docs/datasheets/AO3400A.pdf`: `9c60d0b6c1ddc7609a4b788a91181468d8ffe6c3e9ba425c3d8ffc5ba88c5033`

## Two-wire battery amendment

Contract v2 reviewed 2026-11-09, SHA-256 `44f8f76475c92147f8b7bf5bcd6607a5ff9673e2e4a582a1368c61b141a89d34`. J102 now represents a logical two-wire pack interface with project1=VBAT_PROTECTED,2=GND; this does not assign a real connector’s mating polarity. J104 is a separate DNP optional thermistor interface to BATT_NTC_OPTIONAL/GND, and U102 TS uses BATT_NTC_OPTIONAL. Fitted R120 still forces CE high; no charge-enable path was added. **PASS for schematic-only logical interfaces with exact mating connector/pack polarity still blocked.** Fitting a thermistor alone neither enables nor thermally qualifies charging. Source safety/charge-window gates above remain unchanged. This amendment follows the user's authorized two-wire/optional-unpopulated-sensor decision conveyed by the integration team.

## USB shell alias amendment and MOSFET geometry

2026-11-09. Reviewed power-contract SHA-256 `e6117b29bcaa7d7c11b527b3b0ae852f057ef4d57d010c1c6cd636974148bccb`. Reopened the original GCT USB4105-GF-A p1 drawing and its contact table. J101 retains all 16 original A/B contact endpoints; its four physical shell anchors S1–S4 now explicitly alias one electrical SH pin, grounded. The drawing's table identifies SHELL as GND, and the component-side land drawing has four shell slots and two mechanical locating holes. **PASS for this electrical alias amendment.** The aliases preserve the previously reviewed physical contacts; they are not a claim that GCT numbers its shell anchors S1–S4. Exact footprint assembly acceptance remains separate.

Also reopened original AO3400A p1 top/bottom views and the official AOS SOT23 outline PO-00001 version N (`AOS-SOT23.pdf`, SHA-256 `b6fac64d55f133ce74dd85ddddc618c3d5408e9531cb21e660f6a8ef3d8c5408`). The former identifies G at the indexed end of the paired-lead side, S adjacent, and D opposite. Neither source prints electrical pin numbers. Standard symbol query `power_symbol_AO3400A.json` has project 1=G, 2=S, 3=D. The footprint query `power_footprint_query_3.json` has pin1(-0.9375,-0.95), pin2(-0.9375,+0.95), pin3(+0.9375,0) mm; rotating the original top view to put the paired leads on the left agrees without mirroring. **PASS for this explicitly project-numbered function-to-position correspondence**, not a manufacturer-numbering claim or manufacture release. The standard footprint's land shape differs from AOS's recommended 0.8 mm square pads and still needs assembly/physical validation before release. Power implementation currently leaves unreleased footprint fields blank.

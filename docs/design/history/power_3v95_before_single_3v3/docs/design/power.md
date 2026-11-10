# Power circuit decisions

Date: 9 November 2026. Author: power design worker. Status: reviewed electrical development design with charging disabled. Exact two-wire battery connector and PCB footprints remain release gates.

The maintained electrical assignment source is [power_contract.json](power_contract.json). [power_pinouts.md](power_pinouts.md) is generated from it. Manufacturer facts are separate in [power_facts.json](../components/power_facts.json); the saved PDF revisions and hashes are in [power_inventory.json](../datasheets/power_inventory.json). Physical pin diagrams were inspected as images, not inferred from extracted text.

## Selected development architecture

USB 5 V or dock 5 V → individual input TVS → TPS2121 source selector → BQ24074 power path → TPS63802 at nominal 3.95 V → TLV75733 at 3.3 V for MCU, display, sensors and accessories.

The eight WS2812C-2020-V6 pixels use the shared 3.95 V primary directly. Its net name is `VLED_3V9`; it also supplies the LDO and therefore is not a dedicated LED boost converter. The MCU sends 3.3 V data directly. The accessory power and logic contract remains 3.3 V. No GPIO, MCU supply, display, sensor or accessory power pin connects directly to 3.95 V.

This replaces the insufficiently qualified nominal 3.3 V LED supply. A 3.45 V primary followed by a 3.3 V accessory LDO was rejected because guaranteed dropout, regulator tolerance and dynamic margin did not fit. Typical dropout was not used as a guarantee.

**Default assembled variant:** R120 is a fitted 0 Ω link from VSYS to charger CE. It disables charging in hardware. It is not a firmware override and there is no populated or approved ground strap that enables charging. The BQ24074 still provides its input-to-system and battery-to-system power paths. J102 is a logical two-wire interface with no approved mating footprint. Verify the selected pack’s actual polarity and current budget before connecting it.

A battery-free badge cannot be assumed to boot or run its full feature set on the USB 100 mA setting. Dock operation offers a 500 mA charger-input limit, subject to actual load and startup tests.

## Source selection, input protection and USB

- J101 is the exact GCT USB4105-GF-A receptacle. Both CC contacts have separate 5.1 kΩ, 1% sink resistors. Connect both D+ contacts together and both D− contacts together. All four VBUS contacts join USB_VBUS; all four ground contacts and all four shell anchors join GND. SBU1/SBU2 remain NC. Connector-side ESD is TPD4E05U06, with all four channels used for D+, D−, CC1 and CC2. Its opposite NC pads are not extra protected channels.
- U101 IN1 is USB_VBUS and IN2 is DOCK_5V. PR1 uses 31.6 kΩ over 10.0 kΩ, both 0.1%. CP2 is grounded, selecting the internal-reference priority scheme. USB takes priority when its voltage is valid, including when both sources are connected. With the specified 1.01–1.10 V priority reference, the rising switch threshold is approximately 4.20–4.58 V before the small resistor/leakage corrections. This is intentionally not the fastest comparator mode. Source interruption is buffered by the charger system/battery path where available.
- Each OV input uses 44.2 kΩ over 10.0 kΩ, 0.1%. Nominal trip is 5.745 V; reference limits give roughly 5.47–5.96 V, plus resistor and leakage error. Valid 5.25 V input is below the minimum threshold. This supervision prevents sustained higher input voltages from reaching the charger through the mux, within its timing and absolute maximum limits.
- R109 = 80.6 kΩ programs about 1.49 A typical mux limiting. The nearby characterized 80 kΩ setting is 1–2 A over temperature. This is a mux protection limit, not a USB allowance, dock allowance or battery current limit. C104 = 100 nF gives about 6.4 ms for a 5 V ramp from the data-sheet typical slew curve. C101/C102 are 1 µF each, and C103 is 4.7 µF, all 25 V rated.
- D101 and D102 are Littelfuse SMF6.0A, cathodes to their input supplies and anodes to GND. Its 6 V standoff tolerates normal 5 V inputs; the 10.3 V maximum clamp at the rated 19.4 A, 10/1000 µs pulse is below the mux's 24 V absolute maximum and the charger's input absolute maximum. This is a substantial improvement over relying on a 5.5 V-limited device upstream of a high-clamp TVS. The TVS is not a precise 5 V clamp and is not protection against arbitrary sustained high-voltage sources. Temperature derating, interconnect overshoot, pulse energy, failed-short behavior and upstream fault-current coordination need testing. Use current-limited, regulated 5 V sources during bench work. Final fuse/eFuse coordination remains a release gate.
- U101 ST is high impedance for USB/IN1 selection and low for dock/IN2 selection (TI p21). R110 pulls it to VSYS through 10 kΩ. Q103 AO3400A inverts that status: high/Hi-Z ST grounds BQ EN1 and selects USB100; low ST releases EN1 to its 100 kΩ VSYS pull-up and selects USB500. EN2 is permanently grounded. The default high/Hi-Z status therefore selects the conservative mode. The charger's internal EN1 pulldown does not defeat the external pull-up: at VSYS = 2.75 V, 100 kΩ against the approximately 285 kΩ internal pulldown still gives about 2.04 V, above the logic-high requirement.
- The BQ100 and BQ500 figures are maxima into its IN pin. Mux quiescent current, sensing dividers, TVS leakage and connector-side charging current are additional USB loads. This is not a claim of USB-IF enumeration, suspend, inrush or Type-C current-advertisement compliance. There is no higher-current USB mode without the required policy. Test the source-selection/current-mode transition, especially both-present insertion/removal, and ensure a transient status change does not overload USB.

## Charger and pack safety

BQ24074 references: PDF pp7–14 for pins and electrical limits, pp27–30 for timers and temperature behavior.

- C106 = 10 µF at BAT. C105 = 10 µF at OUT, plus the local 10 µF regulator input capacitor. C103 also supplies the required charger IN bypass. All are within the specified local bypass ranges; place them at the appropriate pins.
- R113 = 3.32 kΩ, 1% would program 268 mA nominal charge current. Using the 797–975 AΩ current factor and resistor tolerance gives about 238–297 mA, safely below the documented 550 mA pack limit. This does not enable charging. R112 = 4.32 kΩ is a conservative approximately 353 mA nominal adapter setting if EN2 were deliberately redesigned high; it is unused with EN2 grounded.
- R114 = 47.5 kΩ sets a nominal 6.33 hour fast-charge timer and 38 minute precharge timer. The 36–60 s/kΩ factor and resistor tolerance give the bounds; timers slow in proportion to charge-current reduction during DPPM/input-DPM/thermal limiting. Do not ground TMR, which disables the timers. ITERM is intentionally left floating for the data-sheet default termination behavior.
- CHG_N and PGOOD_N have 100 kΩ pull-ups to +3V3 and go to available status inputs, for example the expander. They do not identify which source is present, and CHG_N may remain low during a temperature fault. They must not drive the low-battery indicator directly.
- The former LP603450 candidate is retained as source evidence for the temperature mismatch, not as the selected battery. Its source gives 1100 mAh minimum, maximum charge 550 mA, maximum continuous discharge 1100 mA, charge 0–45°C and discharge −20 to 60°C. The Molex candidate remains limited to 1 A/contact. The PCM's 2–4.5 A overcurrent trip does not enforce that connector rating.
- The former pack drawing does not provide a numbered mating-contact map. The revised J102 is a logical two-wire interface: project terminal 1 is protected battery positive and terminal 2 is ground. These are board design identifiers, not an assertion about any vendor’s mating polarity. Its footprint remains unassigned until the stock pack, connector rating and polarity are verified.
- The BQ TS bias is 72–78 µA; hot trip is 270–330 mV and cold trip 2.0–2.2 V. For nominal B3435, R(0°C) is about 28.7 kΩ and R(45°C) about 4.85 kΩ. A direct connection does not guarantee the pack's 0–45°C window. TI p30 explicitly says its two-resistor TS network can only widen the native window, not narrow it. A fixed 10 kΩ substitute would defeat cell temperature sensing and is prohibited here.
- An external autonomous window detector is the plausible next design. TPS3700DDCR was researched and its original PDF saved, but it is not a selected populated part and has no approved schematic mapping. A future design must close NTC curve/B tolerance, comparator loading, threshold and bias tolerances, hysteresis, startup, lost-NTC, shorted-NTC and CE fail-safe behavior. Firmware must not be the cell-temperature safety mechanism. R120 remains fitted until the temperature-safety circuit and selected pack are independently reviewed.

## Primary rail and 3.3 V LDO

TPS63802 references: PDF pp4–6, 11–12 and 18–20. TLV75733 references: pp3–6 and 18–21.

- R117 = 69.0 kΩ and R118 = 10.0 kΩ, both 0.1%, select 0.5 × (1 + 69/10) = 3.95 V. Using ±1% feedback voltage, resistor extrema and a conservative ±100 nA feedback-bias contribution gives approximately 3.897–4.003 V in PWM before dynamic/routing effects. This is a design calculation, not a measured envelope in power-save mode.
- EN ties to VSYS and MODE to GND. The converter remains available in storage deep sleep. Never disable the only MCU supply and expect MCU firmware to restore it. Its roughly 1.3 V UVLO is not a safe battery cutoff. Controlled low-voltage sleep and restart must occur before the pack discharge endpoint, and a hardware cutoff may be needed after storage testing.
- L101 is nominal 0.47 µH, with effective 0.37–0.57 µH, saturation-current target at least 7 A and DCR at most 40 mΩ. The exact magnetic part and footprint are not selected. This is a schematic-value contract only; choosing an arbitrary 0.47 µH footprint is prohibited. The source's recommended example is a starting point, not permission to ignore saturation at maximum current limit.
- Above 3.6 V output the TPS63802 data sheet recommends two 22 µF output capacitors. C108/C109 meet that nominal requirement; select actual parts and sizes for at least 8.2 µF combined effective capacitance at DC bias and temperature. C107 must retain at least 5 µF effective input capacitance. Keep both switch loops short, join AGND to quiet ground, sense output at the capacitors and keep FB away from switching copper.
- U106 is specifically TLV75733PDRVR, WSON-6 with pad7 grounded. It is always enabled from VLED_3V9. C110/C111 = 10 µF are local input/output bypass; verify the required >0.47 µF effective capacitance. NC2/NC5 remain NC.
- Full-temperature LDO maximum output is 3.3495 V and maximum dropout at 1 A is 475 mV. Their sum is 3.8245 V. With the calculated approximately 3.897 V primary minimum, about 72 mV remains for all primary droop, trace losses and headroom margin. Adopt a preliminary 30 mV combined droop/routing allowance, leaving about 42 mV margin. This is why 3.8 V was rejected. The LDO's line-regulation test condition also requires 0.5 V nominal headroom; measure the actual output envelope rather than treating the accuracy number as an unconditional transient guarantee.
- At 0.6 A logic load, a 0.65 V drop dissipates about 0.39 W. The data-sheet JEDEC DRV thermal resistance of 100.2°C/W suggests about 39°C rise on that test board, not on this enclosure. Use ground copper/thermal vias and measure temperatures at worst ambient and simultaneous operating loads. Sustained 1 A is not approved by its nameplate alone.
- VLED maximum must be measured. A preliminary upper acceptance bound of 4.10 V gives LED VIH = 0.55 × 4.10 = 2.255 V. Even using a conservative MCU VOH of 0.8 × 3.2505 = 2.600 V leaves about 0.345 V high-level margin. Peripheral/MCU owners must verify the exact source guarantees and timing. No LED level shifter is required by these bounds. Lowest LED pin voltage must remain at least 3.3 V through disturbances. Use direct shared-rail pixels, keep DIN low during boot and black during storage, and qualify LED supply-before-MCU sequencing. Last DOUT is NC.

## Display switch and off-state behavior

U104 TPS22918 takes +3V3 and produces +3V3_EPD. EPD_EN has the MCU-sheet R207 100 kΩ pulldown. C113 = 1 nF gives about 1.68 ms typical rise at 3.3 V; actual panel inrush and rail sag require measurement. R119 = 1 kΩ joins output to QOD for controlled discharge. Input/output bypass is C112/C114. This switch has no current-limit function.

Signal isolation is owned by the display block and must keep all driven SPI/reset/data pins from back-powering the panel when +3V3_EPD is off. The switch alone does not solve that. ROM recovery can drive the selected enable GPIO high; this may power the display during recovery and is acceptable only with safe signal levels.

The LDO and this load switch do not provide reverse-current isolation. Accessories must not drive power back into +3V3. Accessory ports use the separately reviewed switched/protected 3.3 V branch and firmware-controlled signal high-impedance states; default them off until firmware intentionally enables them.

## Independent presence sensing

Q101 and Q102 are sourced AO3400A MOSFETs, not unsourced substitutes. Each source is grounded; each drain has a 100 kΩ pull-up to +3V3 and goes to USB_PRESENT_N or DOCK_PRESENT_N. Each gate is driven from its own pre-mux supply by 100 kΩ over 470 kΩ. At 4.35 V input, the nominal gate is 3.59 V, above the characterized 2.5 V gate drive. At the TVS's rated 10.3 V clamp, nominal gate is 8.49 V, below the ±12 V gate limit. Parasitic spike margin still needs layout and test verification.

The MCU sees only its own pulled-up logic rail, including when unpowered. Both-present status is independent of mux selection. These are presence signals, not precision valid-5-V comparators: a partially collapsed source can still assert them. Firmware must combine source presence with charger/system status as needed. Optional insertion wake is not required; at least one direct button remains the guaranteed wake path.

## Protected battery ADC

U107 is TMUX1511PWR, TSSOP-14. Its supplied-voltage-independent analog-pin limits and powered-off isolation are essential; a generic analog switch with ESD diodes to VDD is not an equivalent substitution.

VBAT_PROTECTED → R127 (100 kΩ) → BAT_DIV_PRE. R128 (100 kΩ) and C116 (10 nF) connect BAT_DIV_PRE to GND. The switch connects BAT_DIV_PRE to BAT_SENSE_ISOLATED when +3V3 is available. R130 (10 kΩ) then feeds BAT_ADC, with R129 (100 kΩ) from BAT_ADC to GND. All four resistors are 0.1%. SEL1 and VDD tie to +3V3; GND is grounded; other SEL pins are grounded and unused source/drain pins are NC. C115 = 100 nF bypasses the switch.

- With the switch on, the complete loaded divider gives BAT_ADC = VBAT / 3.2, not VBAT / 2. Allow for 4.5 Ω maximum switch resistance, leakage, resistor tolerance and MCU input error. At 4.25 V battery, nominal ADC voltage is 1.328 V. Use calibrated ADC1 acquisition and wait at least 5 ms after startup before valid readings. ADC sampling impedance and settling must be measured with the actual ESP32 settings.
- With the switch off, BAT_DIV_PRE rises only to VBAT / 2, at most about 2.13 V with tolerances, below the switch's 3.6 V powered-off signal rating. Full-temperature ±2 µA maximum off leakage into the 100 kΩ MCU-side pulldown bounds the static MCU pin near 0.20 V. Do not use the much smaller 25°C leakage figure for this proof.
- The filter capacitor is upstream of the isolation switch, so it is not a charged capacitor directly connected to an unpowered MCU pin. R130 limits the transient during the specified turn-off delay. The data sheet gives 4 µs maximum turn-off only for its stated supply-fall test. Measure actual brownout and abrupt power-removal waveforms; do not claim a universal zero-injection transient guarantee.
- The sensing divider draws about 29 µA at 4.2 V in operation and 21 µA with isolation off. TMUX supply current is 37 µA typical, 70 µA maximum. These and regulator/charger quiescent loads belong in the complete storage budget. The ADC path never bypasses battery protection or a future isolation switch: it starts at the protected pack node.

## Current budget and prototype gates

Use at most 1 A battery current as a provisional conservative design target. The new two-wire J102 connector and stock pack are not yet selected, so 1 A is not an established rating of that interface. The former Molex candidate was rated 1 A/contact. Even if the nominal 3.3 V loads total 0.60 A, the primary/LDO architecture needs approximately 3.95 × 0.60 /(0.85 × 3.2) = 0.87 A from a 3.2 V battery at an assumed 85% conversion efficiency, before LEDs. At 2.75 V that is about 1.01 A. Efficiency is an assumption to test, not a guaranteed minimum. Eight full-white LEDs add about 120 mA on the primary and make simultaneous maxima clearly unsuitable.

Default accessories off, LEDs black during high-current radio/display operations, use modest brightness, and restrict accessory budget to 50 mA aggregate until measured. Do not permit full-white pixels, radio peak, display refresh and maximum accessories simultaneously within the provisional battery-current target. Neither software scheduling nor these provisional values establishes fault safety or a finished connector-current proof. Before battery release, measure battery current across voltage/temperature and enforce a bounded peak envelope, or select a higher-rated pack/connector and re-review it.

Required tests before enabling charging or release:

1. Reopen original PDFs independently and review pin/net maps, support values and startup states. Record hashes and reviewer results.
2. Select a readily available protected two-wire 1S pack. Verify actual mating polarity, connector current rating, mechanical drawing, charge limits and protection behavior. Qualify the separate thermistor curve and attachment before enabling charging.
3. Complete autonomous thermal qualification; test missing/shorted thermistor, cold/hot limits, resets and firmware failure. Keep charging disabled until then.
4. Test USB only, dock only, both sources, absent/dead battery, source changes, reverse leakage, inrush and faults. Measure total USB current, not only charger current.
5. Measure both supply rails and LED pins during cold startup, radio/display/LED steps, PFM operation and low-battery boost. Keep +3V3 within every consumer's allowed range and preserve LDO headroom.
6. Test ADC calibration and steady/transient powered-off behavior, all peripheral backfeed paths, wake, low-voltage sleep/restart and complete storage current.
7. Select the inductor and capacitor MPNs, verify thermal/layout requirements and rerun the independent schematic netlist/ERC checks after those choices. No board routing or production readiness is established here.

## Two-wire battery decision, 2026-11-09

The user selected an ordinary two-wire protected 1S LiPo pouch pack, with provision for a separate thermistor that is not populated initially. J102 is therefore a logical two-terminal battery interface with no assigned connector footprint. The previous three-wire LP603450/Molex combination is no longer the selected build choice. Its source documents remain reference evidence for the charging-temperature issue.

J104 provides an optional, initially DNP, separate cell-contact thermistor connection: project terminal 1 is BATT_NTC_OPTIONAL and terminal 2 is GND. It connects to the charger TS input, but no fixed resistor is fitted in place of the sensor. Select its exact resistance curve and mechanical attachment as part of the future temperature-safety circuit. Do not sense only PCB air temperature.

R120 remains a fitted 0 Ω connection from VSYS to CE, so the initial build cannot charge. The charger’s input power path and battery supplement remain available. Populating J104 alone does not remove the disable or qualify the temperature window. Charging requires a separately reviewed hardware change after the exact pack limits, thermal sensing, fault handling and charge current are established.

The accessory block does not include a populated hardware signal isolator. Its separate MCU I²C bus uses pull-ups to switched ACC_3V3, and firmware must make external pins high impedance with internal pulls disabled when accessory power is off. Self-powered accessories and live insertion are prohibited in this development baseline.

## USB connector library mapping

The standard USB-C 16-contact symbol is used. Its single SH pin aliases all four unnumbered shell anchors, each connected to GND. Manufacturer contact facts retain separate S1–S4 physical identifiers; the project contract records their SH alias explicitly. The exact GCT footprint has 16 numbered contact-pad primitives, with A1/B12, A4/B9, B4/A9 and B1/A12 overlapping at four shared power lands. There are therefore 12 distinct contact-land positions, four plated shell-anchor slots and two unnumbered NPTH locating holes. Count these separately when comparing physical features to electrical pins.

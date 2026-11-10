# Peripheral design decisions

9 November 2026. PDFs and hashes: `docs/datasheets/peripheral_inventory.json`. Source pin maps are separate from `peripherals_contract.json`. Source facts and original assignments passed independent review. The later user-approved shared-3.3-V mapping delta was independently accepted before native capture. The earlier contract is preserved under `docs/design/revisions/`.

## Power and interfaces

Eight exact WS2812C-2020-V6 pixels now share nominal **3.3 V** with the MCU, sensors, NFC, status LED and IR transmitter. This supersedes the 3.95 V primary rail plus 3.3 V LDO proposal. The power contract owns the final calculated DC tolerance and load/transient limits; nominal 3.3 V is not a guarantee that every LED sees at least 3.3 V.

The manufacturer specifies **3.3–5.3 V** for this exact V6. The user explicitly accepted a prototype experiment whose tolerance, wiring loss or transients can place the LEDs below that minimum. Function, color/current, timing and input thresholds below the rated range are **not guaranteed**. Within the rated range, a shared supply makes the LED VIH requirement (0.55 times supply) track the MCU high-level output (at least 0.8 times supply); retain the LED VIL maximum of 0.7 V. No level shifter or separate LED rail is fitted.

Measure the supply at the most distant LED and the MCU during startup, low battery, Wi-Fi activity and simultaneous full-white LED transitions. Verify enough shared peak-current capacity and effective local capacitance; test data timing, startup state, recovery from rail dips and storage darkness. Eight 100 nF local capacitors plus 22 uF LED bulk remain fitted. Brightness and simultaneous-load limits remain firmware requirements. Revisit the rail architecture if these tests show unreliable behavior.

Live onboardI2C uses4.7kΩ pulls and100kHz initial clock. BH1730=0x29; LIS SA0high=0x19; NTAG=0x55; TCA9534(non-A)=0x20. Ambient interrupt is NC/polled, motionINT1 and NFCFD direct to MCU. All share live3.3V to avoid unproved off-state I2C leakage paths.

U506 P0/P1 read CHARGER_CHG_N/CHARGER_PGOOD_N; P2 drives ACC_EN; P3 reads ACC_FAULT_N. P4–7 have100kΩ pulldowns, INT NC/polled. Firmware writes output latch0 before direction0xFB. MCU-only reset does not reset the expander; restore safe state explicitly.

One TPS2553DBVR feeds Qwiic, SAO and IR RX.210kΩ1% ILIM gives calculated109.18–152.25mA bounds; reserve155mA upstream fault current. Publish50mA NORMAL COMBINED accessory budget, including IR receiver and pull-ups, until power testing allows more. Hardware current limit is not the normal allowance. This supersedes two proposed EXP-03 instances in draft BOM. A fault removes both ports and receiver.

Dedicated externalI2C has4.7kΩ pull-ups to switchedACC_3V3; SAO GPIO is3.3V only. Before disabling, stop bus, disable internal pulls, releaseI2C, setGPIO low/highZ and IR RX input/no pulls, then ACC_EN low. No independently powered add-ons and no live insertion.100kΩ output bleed with10µF gives1s nominal discharge constant, longer with accessories; measure discharge before promising a fixed delay. External ESD/hot-plug qualification remains open.

## Lighting and controls

D401–408 are one chain: first3 role pixels, last5 affinity pixels. Each100nF, chain22µF bulk, firstDIN330Ω/100kΩ, finalDO NC. Send black at startup and before storage; hold data low. Nominal fullwhite120mA is not a worst-case guaranteed current. Enforce brightness and simultaneous-load limits, scope exact V6 bit/reset timing and test black leakage.

D409 HSMF-C165 is two separate dies:1greenA,2redA,3greenK,4redK. Both cathodesGND; each anode fed through2.2kΩ by its own MCU output, each GPIO100kΩ down. Approx0.64mA typical. Preserve specification's power-status meaning and storage darkness.

SW401/SW402 use user-selected Alps SKSCLBE010/C115361, side-push2.2 N with guide bosses. Each has FOUR physical terminals:1/2 permanently common on the switch signal;3/4 permanently common onGND. Pressing joins the two pairs. Each closes through330 Ω to GPIO with100 kΩ pull-up/100 nF ground capacitor. About10 ms releaseRC, initial contact discharge≈10 mA, held current33 µA. Software debounce starts20 ms; BTN_A_N retains storagewake with no boot-strap function. See [source/mechanical record](../components/SKSCLBE010.md) and [independent source review](review_alps_buttons.md). Footprint remains blank. Verify4.85 mm terminal span, twoØ0.8 mm locating holes, board-edge/half-mount geometry and final case actuation. The capacitive-load and continuous-bias cautions require prototype/manufacturer qualification.

## Sensors and NFC

BH1730 VCC/DVI each have100nF; use register power-down, wait>2ms at startup. LIS CS/SA0 high; GND6/7/8, allowedNC5 grounded; INT2NC;100nF at each supply plus10µF bulk. Motion wake disabled for transport. See source records for logic limits, including archived ST Rev4 stricter thresholds versus Rev9 web text.

NTAG has100nF,10kΩ FD pull-up, VOUTNC. Center metal MUST NOT SOLDER. Keep powered because live shared bus withVCC0 lacks a verified Ioff guarantee. Typical195µA idle is material storage cost:1000mAh/0.195mA≈214days from this device alone, excluding other loads/derating/self-discharge. Storage runtime remains unproved.

NTAG Rev4.1 errata is mandatory: STOP/START spacing≥50µs, both-edge FD capture/RF guards, EEPROM busy timeout/readback, session-register lock/recovery, quiet bus≥1ms at power-up. No irreversible configuration lock during prototype. No independent NTAG reset means recovery can need board restart. AE501 is a13.56MHz PCB loop, twoDNP C0G tuning pads;2.75µH with50pF is only a starting calculation. Tune loaded assembly.

## IR working option

IR67-21C/TR8 plus AO3400A low-side driver uses100Ω0.25W LED resistor for≈21mA typical, gate100Ω and100kΩ down. Use38kHz one-third duty and bounded packets. Do not use1A pulse rating for high-duty carrier. AO source citation corrected: p1 labels G/S/D with gate index dot; official separate PO-00001N supplies package geometry. Numeric1G/2S/3D is explicitly conventional SOT23 derivation requiring reviewer acceptance.

IRM-H638T/TR2 pins1/2GND,3OUT,4VCC. Source-required filter100Ω fromACC_3V3 plus4.7µF/100nF local; no always-on output pull-up.0.4mA typical/0.7mA max idle. Minimum burst12cycles/gap16cycles. Validate AGC/protocol, startup false pulses, sunlight/collisions and optical range. It powers off with accessories.

## Physical interface gates

JST SH side-entry uses manufacturer CircuitNo.1 and SparkFun reference schematic1GND/2VCC/3SDA/4SCL. Two solder tabs are mechanical. Cable drawing housing-view numbers must not be blindly transferred to PCB header; verify cable continuity against pin1 marker.

SAO author host top view: odd1,3,5 upper row; even2,4,6 lower row. Factory Sullins drawing has no contact numbers, so project numbering explicitly follows this convention:1ACC_3V3/2GND/3SDA/4SCL/5GPIO1/6GPIO2. Independently verify female key and mirrored male mating before footprint release. Through-hole assembly/retention still needs manufacturing review.

## Checks performed

Archived PDF hashes verified. Package/pin pixels reviewed; AO3400A citation corrected and numeric derivation explicitly documented for review. Contract parser checked unique references and every assigned electrical pin against source maps. The original native capture passed all 215 endpoints across 75 components against an exported root netlist. The shared-3.3-V revision passed a fresh exported215-endpoint check. The subsequent Alps button replacement passed219 endpoints across the same75 components, with four physical pins per switch. Root ERC has zero errors and the documented intentional LIS2DW12 SA0 address-strap warning. See [capture evidence](peripherals_capture_review.md). Physical fit, runtime, antenna and lab tests remain unperformed; see the native-capture report for the final export evidence.

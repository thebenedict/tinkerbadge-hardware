# Historical peripheral-source review

**Superseded selections: this preserved review body is not current approval for the former 3.95 V LED rail or two-terminal Xunpu switches.** Later reviewed amendments govern both changes; unchanged component-source findings remain supporting evidence.

Current shared-rail decision and limits: [single nominal 3.3 V review](review_power_single_3v3.md) and [peripheral decisions](peripherals.md). Current switch source/symbol review: [Alps button amendment](review_alps_buttons.md), including four physical terminals, unassigned footprints and the unresolved continuous-bias application warning. Current native switch capture and complete-sheet visual acceptance are in the [independent final capture review](peripherals_independent_capture_review.md). Do not substitute this historical PASS for that current evidence.

The original evidence below is preserved unchanged. Its SHA-256 before this supersession header is `fedf05bc99c9beb6af17b1467ed59941f8759e271ed8c77883e0947a8e7928a0`.

---

# Independent peripheral source and assignment review

Reviewed 9 November 2026 by the integrating schematic worker, independently of the source extractor. Contract SHA-256: `7c2255b353729eb2224e37685db379b598e1021d2ca95386573d9cc492554699`.

## Outcome

PASS for electrical schematic capture of the 75-component contract. This does not approve PCB footprints, procurement substitutions, manufacturing or prototype performance. CAD pin queryback, disposable symbol/footprint checks and exported-netlist comparison remain separate requirements.

## Original source checks

Original PDF page images, not merely another worker's summary, were inspected:

- Worldsemi WS2812C-2020-V6 p. 2: top/back views and table prove 1 DO, 2 GND, 3 DI, 4 VDD. Eight devices chain output to next input; final output is NC. Minimum supply 3.3 V excludes a nominal 3.3 V rail without margin. The 3.95 V rail and 4.10 V acceptance ceiling give 2.255 V input-high requirement, below the MCU guaranteed high level.
- Broadcom HSMF-C165 p. 2: two independent dies, 1/3 green anode/cathode and 2/4 red anode/cathode, not a common-anode or three-pin device. Separate 2.2 kΩ resistors and grounded cathodes are consistent.
- TI TPS2553 p. 4: DBV mapping differs from DRV. Contract uses 1 IN, 2 GND, 3 active-high EN, 4 open-drain FAULT, 5 ILIM, 6 OUT. The source table specifies 110–150 mA at 210 kΩ; equation/tolerance budget is conservatively 109.18–152.25 mA. The published 50 mA normal combined budget is distinct from this fault limit.
- TI TCA9534 p. 4: all 16 pins match; address straps are grounded. P2 controls the accessory switch with external pulldown; startup defaults to input. P0/P1/P3 read status; INT is intentionally unused and polled. Firmware must reset the output latch before enabling output direction, including after MCU-only resets.
- Everlight IRM-H6XXT p. 1: two separate ground pins, pin 3 OUT and pin 4 VCC. The switched-supply filter and absence of an always-on output pullup prevent an obvious off-state back-power path. IR67-21C p. 2 proves 1 anode and 2 cathode; its high pulse rating is not permission for high-duty carrier. The 100 Ω resistor keeps continuous current below the device rating even during a stuck-on output.
- Xunpu TS-1088 p. 2 shows exactly two interchangeable electrical terminals. The two numbered schematic contacts are project identifiers for an unpolarized switch, not an invented four-pin package.
- ROHM BH1730 p. 2: 1 VCC, 2 optional INT, 3 GND, 4 SDA, 5 DVI, 6 SCL. Both supplies are 3.3 V; INT may be open.
- ST LIS2DW12 Rev. 4 p. 9: bottom-view pin numbering, I²C straps, grounded reserved pin 7, ground pins 6/8, allowed grounding of NC pin 5, VDD 9 and VDD_IO 10 all match. INT1 uses pin 12; INT2 pin 11 is unused.
- NXP NT3H2111 Rev. 3.6 p. 8: transparent top view matches all eight leads. Center metal is explicitly not for soldering. VOUT is left unused; separate antenna terminals and DNP tuning capacitors are correct. Always-on supply avoids assuming an undocumented Ioff property on the shared bus.
- AOS AO3400A Rev. 3.1 p. 1: original top and bottom images prove the index-side terminal is G, the other paired terminal S, and the single opposite terminal D. Numeric 1/2/3 are a documented project/conventional SOT23 mapping, not a printed AOS numbered table. Accept only when the chosen footprint's pad 1/index, 2 and 3 coincide with this physical view. No claim that p. 5 is a package drawing.
- JST SH header and housing diagrams identify Circuit No. 1. The cable drawing uses its own housing view and must not be transferred blindly to the PCB header. Sullins SFH11 drawing establishes geometry but not electrical numbering. Qwiic and SAO logical interfaces remain separate from the physical mating acceptance.

## Electrical review

Reviewed every component and support-part endpoint in the JSON. Local 100 nF bypassing, LED bulk capacitance, defined DIN/enable/gate defaults, active-low buttons with 100 kΩ/100 nF debounce, pullups to the correct powered domain, NFC tuning placeholders and the IR low-side circuit are coherent. Onboard I²C devices remain powered at 3.3 V; the dedicated external bus pulls to switched ACC_3V3. Firmware must disable pulls and release external pins before cutting accessory power. No independently powered add-ons or hot plugging are qualified.

The NTAG typical 195 µA idle current materially limits storage life. Full-white LED current is typical, not a guaranteed system maximum. Firmware scheduling, radio/display peaks, current-limit interactions, optical range, antenna tuning and every footprint/mating view require prototype or later physical verification.

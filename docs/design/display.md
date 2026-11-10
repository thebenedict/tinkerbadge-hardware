# Display circuit decisions

Revision 1, 9 November 2026. Source extraction complete; independent electrical review is pending. This is a schematic candidate, not a manufacturing release.

## Implemented candidate and authority

Implement the raw Waveshare 3.7-inch, 480 × 280 monochrome/four-gray panel described by the **19-page Rev 1.0 specification dated 29 May 2020**. ED037TC1 / SSD1677 is the working identity. Supplier SKU 18381 alone does not prove the glass, flex, controller revision, or waveform of the next shipment. Verify received markings and a working sample before assembly release.

The source inventory is [display_inventory.json](../datasheets/display_inventory.json). It records the actual downloaded PDF bytes, revisions, URLs, and SHA-256 hashes. Electrical assignments are maintained in [display_contract.json](display_contract.json), with a generated [pinout view](display_pinout.md). The panel controller is already integrated; no standalone SSD1677 is fitted.

## Physical pins and discrepancies

The exact panel table, PDF page 6 / printed page 3, controls physical flex numbering. Its mechanical detail A on PDF page 5 marks terminals 1 and 24. The [component record](../components/ED037TC1.md) captures all 24 positions.

- Pins 1 and 4 are **NC**, and remain unconnected with explicit schematic NC flags. The HAT's names HLT_CTL and VGL at these positions are not inherited.
- Pin 5 is **VSH2**, a reserved nominal 5 V source-rail node, not the HAT's generically named VGH. Keep the HAT's 1 µF ground bypass here. The SSD1677 application circuit, page 45, independently places a capacitor on FPC pin 5 / VSH2. Do not drive this node from the board.
- Pin 21 is **VGH**, nominal +20 V; pin 23 is **VGL**, nominal −20 V. The HAT calls the corresponding boost nets PREVGH/PREVGL.
- Pins 6 and 7 are temperature-sensor clock/data, unused and open. SSD1677 page 9 permits open unused pins. Do not join these to the badge I²C bus.
- Pin 18 is the internal **1.8 V VDD** regulator node, bypassed only. It is not the badge 3.3 V supply. Pin 19 / VPP is bypassed without an external OTP-programming supply.
- The panel table's I/O letters for RESE and SCL contradict their function descriptions. The descriptions and SSD1677 pages 9–10 establish them as current-sense and clock **inputs**. The facts explicitly record this correction rather than misclassifying their ERC types.
- Pin 8 / BS1 is tied to ground for 4-wire SPI. BUSY is active high. The MCU-to-panel data path is write-only in this schematic; no readback/MISO channel is implemented.

### Connector and flex gate

Panasonic's official September 2023 Y5B catalogue names AYF532435 and gives the dual top/bottom contacts, 0.5 mm pitch, 0.30 ± 0.03 mm FPC thickness, dimensional drawings, and recommended PCB pattern (PDF pages 2–5 and 8). Both sides of the contact tongue can make contact. This does not remove the possibility of reversing terminal order by flipping or folding the flex.

The catalogue drawing does not label numbered terminals. The two official standalone CAD-PDF links redirected to an HTML download page, so no purported PDF was retained. **J301 represents the panel's electrical flex positions, with AYF532435 as the physical connector candidate. Its footprint remains unassigned.** Before layout, establish the top-view footprint numbering, opening direction, actual contact face, flex fold, and continuity from panel 1 to board 1. Use the original panel detail, not an assumed generic FPC pin-1 convention. The bottom-contact Hirose alternative is not approved by this record.

## Boost and rail support

Use the actual Waveshare 3.7-inch HAT schematic, PDF page 1, for the loading-specific support network. The SSD1677 generic application circuit has 47 µH and 2.2 Ω, and explicitly says values depend on panel loading. Those generic values do not override the panel HAT's **68 µH and 0.47 Ω**. The HAT supply regulator, level translation, Pi header, and reset-driven power circuit are not copied.

Project component references are deliberately different from HAT references:

- L301: 68 µH between +3V3_EPD and EPD_SW.
- Q301: gate pin 1 to EPD_GDR; source pin 2 to EPD_RESE; drain pin 3 to EPD_SW. R301 = 0.47 Ω from RESE to ground; R302 = 10 kΩ from GDR to ground. Sense RESE at the MOSFET source and resistor terminal, with a short quiet return.
- C302 = 4.7 µF / 50 V between EPD_SW and EPD_PUMP. It is a nonpolar ceramic flying capacitor, not a ground bypass.
- D301: cathode pin 1 to ground, anode pin 2 to EPD_PUMP. This clamps the pump's positive swing.
- D302: cathode pin 1 to EPD_PUMP, anode pin 2 to EPD_VGL. This rectifies the negative rail.
- D303: cathode pin 1 to EPD_VGH, anode pin 2 to EPD_SW. This rectifies the positive rail.
- C301 = 4.7 µF / 50 V and C303 = 100 nF / 10 V bypass +3V3_EPD. Place the bulk capacitor at the boost inductor and 100 nF near FPC supply pins.
- C304–C311 provide separate 1 µF bypasses for VDD, VPP, VSH1, VGH, VSL, VGL, VCOM, and VSH2. All are nonpolar ceramics. The contract gives 50 V for high-voltage rails, 25 V for VPP/VSH2, and 10 V for VDD. The HAT leaves most capacitor ratings unspecified; these ratings are project engineering choices.

Use X7R, ±10% capacitors, and qualify **effective capacitance under DC bias**, not just the printed capacitance. HAT values are nominal and are not an effective-capacitance guarantee. Exact passive MPNs and package sizes remain to be chosen before PCB release. L301's initial selection requirements are shielded construction, ±20%, saturation current at least 1 A, RMS rating at least 0.5 A, and DCR at most 1 Ω. These are project screening targets, not measured or manufacturer-stated HAT current limits. Check actual switching peak current and saturation/temperature curves before approving a specific part; the panel's average current is not the inductor peak current.

### MOSFET lifecycle decision

Select **SI1308EDL-T1-GE3**, replacing the BOM's reference-only -BE3 suffix. Vishay termination notice PTN-SIL-029-2026 Rev 0, page 3 row 1, explicitly names -GE3 as the replacement. Datasheet 63399 Rev C, page 1, already specifies that exact ordering suffix. Its 30 V rating, 0.185 Ω maximum at VGS = 2.5 V, typical 1.4 nC gate charge, and G/S/D = 1/2/3 are verified. This closes the choice of schematic candidate without assuming a different MOSFET is equivalent. Exact -GE3 stock/assembly sourcing and prototype boost validation remain open.

### Diode polarity and stress

Use three **MBR0530T1G** parts. The onsemi Rev 9 PDF page 4, CASE 425 STYLE 1, explicitly identifies pin 1 as cathode and pin 2 as anode, with the package band at pin 1. Their 30 V reverse rating is above the nominal approximately 20 V applied in each rectifier branch. Verify ringing and reverse stress at operating extremes before accepting the margin. The page 1 discontinued ordering row refers to NRVB0530T3G, not the selected MBR0530T1G.

## Supply, isolation, and default states

The power block owns U104 and +3V3_EPD. Use a switched branch of the same regulated **3.3 V** used by the MCU. The exact panel permits 2.4–3.6 V logic supply (PDF page 8). The separate 1.8 V FPC node must not be confused with the supply table's overloaded VDD name.

U301 is **SN74LVC541APWR**, powered from +3V3_EPD. Pin 20 is VCC and pin 10 is ground; both active-low enables, pins 1 and 19, are grounded. Map A1/Y1 to MOSI, A2/Y2 to SCK, A3/Y3 to CS_N, A4/Y4 to DC, A5/Y5 to RST_N. Ground unused A6–A8 and explicitly NC unused Y6–Y8. C312 = 100 nF at the supply pins. The exact PW package has no exposed pad.

The buffer accepts 5.5 V inputs and has Ioff isolation at VCC = 0 V. It prevents an MCU output left high from powering the disabled display through its signal pins. The published Ioff limit is 10 µA per output under its test condition, not zero leakage; the switch must discharge the rail, and behavior during rail ramp/brownout still needs validation. Input defaults are 100 kΩ on the **MCU side**: CS_N pulled to +3V3, MOSI/SCK/DC/RST_N pulled to ground. These define states while the MCU resets without applying an always-on pullup to the panel.

BUSY goes directly from the panel to the MCU, with a 100 kΩ pulldown to ground. Do not enable an MCU pullup on BUSY while the panel is off. At 3.3 V, that pulldown draws 33 µA, within the panel's 400 µA output test condition. At common upstream supply V and switch droop d, panel guaranteed VOH is 0.8(V−d); an MCU VIH requirement of 0.75V is met when **d < 0.0625V**, approximately 0.206 V at 3.3 V. This ratio cancels shared regulator tolerance. Verify the final MCU VIH, load-switch resistance, trace loss, and update transient against that budget. Nominal switch loss alone is not proof of a transient margin.

At 100 µA loading, the buffer's guaranteed high level is at least VCC − 0.3 V across its full temperature specification (TI PDF page 7), which exceeds the panel's 0.8 VCC threshold at 3.3 V. Its output-low limit of 0.3 V is below the panel's 0.2 VCC threshold. Keep panel input and any added pulls within that test load. Start firmware SPI at 4 MHz; characterize higher speeds on the assembled board rather than using the 20 MHz panel maximum immediately.

## Sequencing and firmware requirements

The panel sequence diagram, PDF page 13, requires reset low for more than 20 ms after VCI rises, then more than 20 ms after reset release before initialization. Establish upstream default pins before EPD_EN, enable the supply, wait for rail settling, release reset, and run the exact panel initialization/waveform. Use an active-high BUSY timeout so a failed panel cannot hang housekeeping forever.

Finish the panel's controller-managed high-voltage shutdown, illustrated on PDF page 14, and command sleep before dropping EPD_EN. E-paper image retention does not require leaving the supply on. Return/reset firmware must clear the visible image before reporting a completed loaner checkout. Abrupt battery failure cannot guarantee image clearing and must not be treated as successful return.

## Required prototype and release checks

1. Record the actual glass/flex identity and panel waveform/firmware revision. Compare full, partial, and gray updates against the supplied reference board, including temperature limits and ghosting cleanup.
2. Scope +3V3_EPD, GDR, RESE, SW, PUMP, VGH, VGL, VSH1, VSL, and VCOM during power-up, heavy-pattern refresh, sleep, power removal, and brownout. Measure overshoot against 30 V MOSFET/diode limits and capacitor ratings.
3. Measure switching current, inductor saturation and temperature, sense-resistor pulse dissipation, and effective capacitance under bias. Revise passives from measurements before routing release.
4. Test MCU-held-high outputs with EPD_EN low, MCU reset, buffer brownout, stuck BUSY, and repeated power cycles. Measure off-state display-rail voltage/leakage and confirm safe shutdown.
5. Measure BUSY logic margin at maximum display load and MCU supply extremes. Verify no output exceeds either receiving rail during power transitions.
6. Independently review source diagrams and contract hashes, then compare exported KiCad physical-pin endpoint sets with the contract and run ERC. Keep the J301 mating/footprint gate explicit until resolved.

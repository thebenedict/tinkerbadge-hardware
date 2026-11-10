# Independent display source review

Reviewer: schematic integration owner, independent of the display extractor. Date: 2026-11-09.
Reviewed contract SHA-256: `5637f5153512fbd0b6c09f2443de585b489ec08fbeca15db035c08ad3192e751`. Source hashes are in [display_inventory.json](../datasheets/display_inventory.json).

## Evidence and result

Reopened the original panel pin table (PDF page 6), DC characteristics (page 8), Waveshare HAT schematic (page 1), SSD1677 application circuit (page 45), Vishay Si1308EDL top-view diagram (page 1), the Vishay termination notice replacement table (page 3), onsemi SOD-123 top-view numbering (page 4), and TI SN74LVC541A PW top-view/pin table and Ioff table (pages 4 and 7). Inspected the diagrams rather than relying on extracted text.

- All 24 panel contacts agree with the contract. Pins 1 and 4 are NC. Pin 5 is reserved VSH2, not VGH. Pins 21 and 23 are the external +20 V / -20 V boost nodes. VDD at pin 18 is the local 1.8 V node, not 3.3 V. The HAT's generic labels do not override these physical pin facts.
- Q301 mapping is gate 1, source 2, drain 3, top view. The manufacturer lists -GE3 as the replacement for -BE3 and the same Si1308EDL datasheet covers -GE3.
- D301–303 use cathode pad 1 and anode pad 2. Their polarities match the positive boost and negative pump in the HAT and controller reference. The source-sense resistor is 0.47 ohm and the panel HAT inductor is 68 uH. The controller's generic 47 uH / 2.2 ohm example is intentionally not substituted.
- U301 has OE pins 1/19 low, VCC20, GND10, inputs2–9 and outputs18–11. PW has no thermal pad. The five active channels and three grounded unused inputs agree. Ioff at VCC=0 limits leakage rather than claiming mathematical zero. Off-state backfeed measurement remains required.
- The buffer's lightly loaded high/low output guarantees meet the panel's 0.8/0.2 VDD thresholds on the same switched supply. BUSY's 0.8 VDD output meets the MCU's 0.75 VDD input only while switch/distribution droop stays below 6.25% of the parent rail; measure transients. A 100k pulldown does not overload the 400uA test condition.
- Support-capacitor endpoint sets match the panel HAT, with pin4's capacitor omitted because this exact panel declares NC. VSH2's capacitor is corroborated by the SSD1677 application drawing. Capacitor voltage ratings are conservative but effective capacitance and selected MPNs still require qualification.

Electrical contract accepted for a prototype schematic. J301 is explicitly the electrical panel-flex interface; no AYF532435 mating-view/footprint approval is implied. Exact delivered panel revision, connector mating orientation, inductor saturation, PCB thermal/current limits, and physical prototypes remain release gates.

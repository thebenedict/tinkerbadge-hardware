# SKSCLBE010 component facts

## Sources and selection

Alps Alpine SKSCLBE010, JLC/LCSC C115361, selected for both function buttons SW401/SW402 (UI-03) on 9 November 2026. This replaces XUNPU TS-1088-AR02016. It is the side-actuated, guide-boss, 2.2 N SKSC variant, not the SKSCP ground-terminal variant.

- [Exact product specification](https://tech.alpsalpine.com/cms.media/product_spec_sksclbe010_en_f052c78d76.pdf): KSC-701, Date 201707, six pages, marked For reference. [Manufacturer PDF](https://tech.alpsalpine.com/cms.media/product_spec_sksclbe010_en_f052c78d76.pdf). SHA256 `06eed78e94af6bb6c3885a1baa87f00e6f522a61240e1aa8243afbaadf611521`.
- [Current SKSC catalog](https://tech.alpsalpine.com/cms.media/product_catalog_ta_02_sksc_en_f9e52a07d5.pdf): Update 2510. The exact-part row on p1 selects Drawing No.2 on p2. [Manufacturer PDF](https://tech.alpsalpine.com/cms.media/product_catalog_ta_02_sksc_en_f9e52a07d5.pdf). SHA256 `cc8baff4e324df2cf6a71b9319ab9dbfd9e56d2e589dce392456b8afc99ca5bb`.
- [Current manufacturer page](https://tech.alpsalpine.com/e/products/detail/SKSCLBE010/) confirms exact SKU, 2.2 N, guide bosses and limits. [JLC C115361](https://jlcpcb.com/partdetail/ALPSALPINE-SKSCLBE010/C115361) establishes supplier identity only; its 2.24 N rounded listing does not override the manufacturer's 2.2 N.

## Physical terminal contract

Four physical electrical terminals form two permanently common pairs. **1–2 are one side of the switch; 3–4 are the other.** The momentary normally-open mechanism joins the pairs on press. No separate ground terminal or exposed pad exists on this L variant. The two locating bosses and PCB holes are mechanical, not extra symbol pins.

Positions below follow Drawing No.2's component illustration with actuator at the lower edge. The adjacent PCB land drawing explicitly says viewed from switch mounting face. The package illustration's view is not separately titled; do not silently mirror it into a PCB footprint. The four-pin schematic can use either contact pair for signal because it is unpolarized, but the physical numbered pairs must remain correct.

| Physical terminal | Name | Position in component illustration | Function |
|---|---|---|---|
| 1 | CONTACT_A | lower left | Permanently common with terminal 2; momentary press joins pairs A and B |
| 2 | CONTACT_A | lower right | Permanently common with terminal 1; momentary press joins pairs A and B |
| 3 | CONTACT_B | upper left | Permanently common with terminal 4; momentary press joins pairs A and B |
| 4 | CONTACT_B | upper right | Permanently common with terminal 3; momentary press joins pairs A and B |

Exact custom symbol `Tinkerbadge_Peripherals:SKSCLBE010` has four passive pins and draws permanently common pairs1–2 and3–4 with one normally-open contact between the pairs. The generic `Switch:SW_Push_Dual` was rejected in disposable review because its glyph depicts two ganged switches. Saved pin readback and the corrected disposable render passed independent review before placement. Footprint deliberately blank: no exact installed SKSC footprint was found, and no land pattern or physical case fit is accepted yet.

## Mechanical facts and release gate

Catalog p2 Drawing No.2: body 3.5±0.1 by 3.55±0.15 mm; height 1.25 +0.05/−0.15 mm. **4.85±0.1 mm is the overall electrical terminal span**, not body width, pad pitch or the PCB land span. The recommended copper pattern spans5.0 mm with2.2 mm inner gap; each pad width is derived1.4 mm. Combined land depth2.2 mm with0.4 mm gap gives derived0.9 mm pad height.

There are two Ø0.6±0.1 mm guide bosses, protruding0.5±0.1 mm below the mounting plane. Recommended PCB holes are **2×Ø0.8±0.05 mm, spaced1.8±0.05 mm**. Their datum must follow the drawing, not be assumed centered on land rows. Footprint acceptance must check all four pads, numbering/view, locating-hole coordinates and drill tolerance, half-mount board edge/cutout, actuator access, courtyard and paste. Case fit, side-load path and human tactile review remain open.

KSC-701 p2: force2.2±0.65 N, travel0.2 +0.1/−0.05 mm, returnforce≥0.1 N, ON/OFFbounce≤10 ms. P5 recommends flat Ø1.2 mm key tip, tilt≤3°, center actuation and no continuous pressing; avoid overtravel and side stress outside the intended actuation axis.

## Electrical use and qualification

KSC-701 p1: max12 V DC/50 mA, min1 V DC/10 µA, initial contact resistance≤100 mΩ. P3:100,000 operations at5 V/5 mA. Operatingtemperature−30…85°C. There is no powered IC rail, startup sequence or backfeed source inside this passive switch.

Project: each switch pins1/2→BTN_A_SW_N or BTN_B_SW_N; pins3/4→GND. Keep330 Ω series to MCU input,100 kΩ pull-up to shared+3V3 and100 nF toGND at the MCU. Approximate held current33 µA is above10 µA minimum; capacitor discharge initially≈10 mA is below50 mA maximum, with0.55 µJ stored at3.3 V. ReleaseRC≈10 ms; firmware starts with20 ms debounce. BTN_A is retained storage-wake; GPIO and firmware roles do not change. Unpowered open or closed switch cannot inject an external supply.

These calculations do **not** qualify lifetime or every usage condition. KSC-701 p5 A2 specifies DC resistive use and asks consultation for capacitive loads. The limited100 nF discharge remains a prototype qualification item. P5 D11 cautions against use kept powered; the intended continuously pulled-up open switch needs manufacturer/application clarification before production acceptance. P6 G1 says the reference specification requires formal supply acceptance; obtain current formal specification before manufacture. Verify debounce, wake/held-button behavior, low-current contact reliability, case actuation and actual reflow conditions. No cleaning solvent after soldering (p5 C1).

## Review state

Source facts, four-terminal assignments and the corrected symbol passed [independent review](../design/review_alps_buttons.md) before native capture. The source-map submission status is historical; the separate review records the accepted hash. The machine-readable source map is [SKSCLBE010.pins.json](SKSCLBE010.pins.json); project assignments are [peripherals_contract.json](../design/peripherals_contract.json). This record does not claim a qualified footprint or enclosure.

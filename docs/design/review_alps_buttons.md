# Independent Alps button review

9 November 2026. **PASS for physical-source mapping and corrected symbol, as a selected prototype candidate.** Permanent-bias application qualification and the physical footprint remain open. Actual native capture is reviewed separately below when available.

## Exact part and drawing

Official KSC-701 (201707), `SKSCLBE010.pdf`, identifies the exact MPN. Current SKSC catalog Update 2510, page 1, selects Drawing No. 2 on page 2: side push, 2.2 N, guide bosses, nominal 3.5 × 3.55 × 1.25 mm. This is not the SKSCP variant with a ground terminal. The current product page's mechanical, land and circuit GIFs were independently downloaded and inspected and agree with the saved catalog.

The switch has **four electrical terminals**: 1–2 permanently common, 3–4 permanently common, and one normally-open contact joining the two pairs on press. With actuator downward in the component illustration, 1/2 are lower left/right and 3/4 upper left/right. The land view is explicitly from the switch mounting face. SW401 pins 1/2 go to BTN_A_SW_N, SW402 pins 1/2 to BTN_B_SW_N; both switches' pins 3/4 go to GND. Both retain the existing series resistor, pull-up, capacitor and MCU assignments. A complete contract comparison found only SW401/SW402 changed.

**4.85 ±0.1 mm is terminal outer span, not pad pitch.** The copper drawing implies 1.4 × 0.9 mm lands from a 5 mm outer span / 2.2 mm inner gap and a 2.2 mm outer depth / 0.4 mm row gap. Two Ø0.8 ±0.05 mm PCB holes, spaced 1.8 ±0.05 mm, receive the mechanical bosses. They are not electrical pins. Footprints remain deliberately blank: no physical land pattern, datum/orientation, half-mount board-edge fit, actuator access or manufacturing acceptance is claimed.

## Corrected symbol

The first disposable `Switch:SW_Push_Dual` was rejected before real capture. Its graphic shows two ganged switches rather than the manufacturer's permanently common terminal pairs. The replacement `Tinkerbadge_Peripherals:SKSCLBE010` was independently queried and the corrected disposable render inspected. It has four numbered passive pins, permanent pair connections and one normally-open closure. Its blank footprint and exact library ID are explicit in both contracts. This electrical symbol is accepted; it is not a footprint approval.

## Continuous-bias limitation

KSC-701 page 5 D11 says: “Do not use the product in a manner that it is kept being powered.” The Japanese is **常時電圧印加される様なご使用はお避け下さい。**, meaning avoid use with continuously applied voltage. D10 separately prohibits keeping the switch pressed. Thus D11 cannot safely be reinterpreted as only a warning about a continuously depressed/conducting switch.

The permanent 100 kΩ pull-up leaves DC voltage across the open contacts, including during storage wake. Approximately 33 µA held current is not a stated exemption. The integration owner directed capture as the selected prototype candidate with this uncertainty explicit, not as source-qualified permanent-bias service. Obtain manufacturer/current formal specification clarification and appropriate biased-life qualification before production. No external outreach has been performed.

The 330 Ω resistor limits the 100 nF discharge to roughly 10 mA at nominal 3.3 V, but page 5 A2 separately calls for capacitive-load qualification. Debounce, held-button wake/re-entry behavior, enclosure force/overtravel, reflow and no-solvent-cleaning requirements remain bench/assembly gates.

Source, contract, library and disposable-render hashes and direct saved-symbol readback are recorded in `review_alps_buttons.json`. Native replacement/export/render review remains pending.

## Contract wording amendment

Current contract SHA-256: `e6c3819998aac6863f164209df1b9a84b1fa9d0e6f3a30eacf522b9cf9e4f1ec`. The stale 4.10 V criterion was replaced with the shared nominal 3.3 V prototype exception and switch qualification gates. Rechecked the entire component set against the pre-switch contract: only SW401/SW402 differ, with no additional pin or value changes. The source facts and corrected symbol library hashes remain unchanged.

## Native capture accepted

The actual revised lighting sheet passed independent exported endpoint/property checks and complete-sheet visual inspection. See [final lighting/peripheral capture review](peripherals_independent_capture_review.md) for current native hashes and evidence. This closes electrical capture only; permanent-bias application and physical footprint gates above remain open.

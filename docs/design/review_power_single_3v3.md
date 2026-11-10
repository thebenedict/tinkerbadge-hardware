# Independent single-3.3 V amendment review

9 November 2026. Result: **PASS for the authorized first-prototype schematic amendment**, with the documented LED exception and existing release gates. This is a source/contract review, not acceptance of the native implementation.

Reviewed contract SHA-256: `20fb7654f96922426fbc6a5b73ef70995b394aab9696421ed483bcbc73615563`.

## Exact change

Compared with the frozen previous contract, exactly U106, C110 and C111 are removed. U103.6, R117.1, C108.1 and C109.1 change from VLED_3V9 to +3V3. R117 changes from 69.0 kΩ to 56.0 kΩ, still 0.1%. All other retained physical assignments remain unchanged, including charger hard-disable, ADC isolation, source selection and the switched display rail. New count: 60 parts, 195 endpoints, 14 intentional NCs.

## Source and calculation review

Original TPS63802 pages 4, 6 and 19 were inspected as images. Pin 6 is VOUT; FB4 and grounds 3/8 remain correct. The 56.0 kΩ / 10.0 kΩ divider selects 3.300 V. With reference/resistor extremes and a deliberately conservative signed 100 nA bias term using maximum upper resistance, PWM static bounds are **3.255855938–3.344267262 V**. These do not bound PFM ripple, wiring loss or transients. Page 19 permits retaining two 22 µF output capacitors. Exact biased capacitance and startup still require qualification.

A source-table reading was corrected before capture: TPS63802 page 6 puts 2.3 V in the **MAX** column for the minimum input needed for 2 A at 3.3 V, once started, TJ = 25°C. It is not a typical-column entry and not an unconditional full-temperature or system-current guarantee. The author corrected the facts and decision record.

The provisional 750 mA rail target is below headline converter capability but does not qualify the unspecified inductor, pack, connector or USB path. At assumed 85% efficiency and maximum static output, 750 mA implies 0.922 A at 3.2 V input and 1.073 A at 2.75 V before path losses. Full simultaneous loads remain restricted pending measurement. The MCU's supply-capability recommendation remains at least 500 mA; its example RF current is not a guaranteed peak-load maximum.

## Accepted prototype exception

Original exact WS2812C-2020-V6 pages 2–3 and ESP module page 27 were inspected. The LED source lower supply bound is 3.3 V, so the new rail may be 44.14 mV below it even in the conservative static calculation. No guaranteed LED operation is claimed there. The LED VIH table is characterized at 5 V / 25°C, and the MCU DC table at 3.3 V / 25°C. Their favorable ratios support the prototype choice but are not a guaranteed 3.3 V LED interface over temperature. The author added these conditions to the decision record.

Removing the LDO also removes its load isolation. Probe the regulator, MCU and farthest LED during startup, PFM/light-load operation, low battery, radio/display activity and full-white transitions. Confirm other consumers remain within their valid ranges. Check resets, data errors, brightness/color, ringing and source current. The 3.10–3.50 V target is a test target only and does not waive the LED's 3.3 V source bound. Revisit the architecture if tests fail.

R120 still hard-disables charging. Battery polarity/current and autonomous temperature-safety gates remain open. Native power capture, fresh exported connectivity/field checks, root ERC and visual review follow separately. Source/artifact hashes and the bounded change are in `review_power_single_3v3.json`.

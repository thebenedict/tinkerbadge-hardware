# Optical-space placement review

Native board SHA256 `8fa1ac386d237944d634cd7b5be0ca3ad3188f87965fbee94499eb1a51859399`, KiCad 10.0.8. Updated 10 November 2026.

Twelve optical/support footprints move into the exposed shoulder and area right of the MCU. Role LEDs, all other placements, outline and keepouts stay unchanged. U501 is at (145,108.25); U504 at (166,106.5),180°; D501 at (176,107.5). The three optical courtyards remain outside glass with 0.555/0.705/0.755 mm gaps. Support electronics sit under the raised panel. Optical angles, barriers and tolerances remain prototype gates.

The user selected a rear-copper NFC PCB coil with front/inner-layer clearance and front-side tag/tuning components. No coil is drawn or tuned, and the native clearance reserve is retained.

`functional-blocks.png` has 14 external callouts, with separate Ambient light and Infrared groups. Its editable SVG embeds unchanged native pixels; provenance and reproduction instructions are retained. The other four PNGs show native front/rear/raised-display views, with review-only mechanical allowances. Native assembly SVGs and check reports are included.

Independent native parity preserves all 186 complete footprint records after inverse poses, with no unexpected changes, geometric collisions or missing models. DRC retains the four USB hole errors, one silk-edge warning, 390 unconnected items and nine missing footprints. ERC has zero errors and one unchanged warning. No routing was added. Human placement approval and remaining RF/flex/optical/parts/manufacturing qualification are still required.

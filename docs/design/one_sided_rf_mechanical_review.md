# One-sided RF and mechanical review

9 November 2026. Dimensioned placement proposal for the 110 × 100 mm board. Read-only native inspection used KiCad 10.0.8 and board SHA256 `99158950ecce21da92f8c0e9343ecf60316f321255fd496f790517ac7717f49f`. This review did not save or modify CAD.

## Recommendation

Keep the present board size. Use a top-open routed notch for the ESP32 antenna, with the module slightly inside the outer bounding rectangle. The full-width affinity row fits an 18 × 17 mm NFC reservation between its final two LEDs, but that smaller coil remains a prototype RF risk. Neither reservation establishes communication performance.

## ESP32 cutout

The placed RF_Module:ESP32-S3-WROOM-1 footprint and manufacturer drawings agree: nominal body 18 × 25.5 mm, antenna strip 18 × 6 mm, first side-pad centers 7.49 mm below the antenna tip, and side copper lands 1.5 × 0.9 mm. The source specifies body length/width ±0.2 mm and height 3.1 ±0.15 mm. Pad 1 is at local (-8.75,-5.26), pad 40 at (+8.75,-5.26). Existing native keepout spans local x=-24..24, y=-27.75..-6.75 on all four copper layers, prohibiting tracks, vias, pads, pours and other footprints.

| Geometry, mm | Requested trial | Preferred tolerance allowance |
|---|---:|---:|
| U201 origin, F.Cu, 0° | (130,112.75) | (130,113.25) |
| Antenna nominal rectangle | x121..139, y100..106 | x121..139, y100.5..106.5 |
| Entire module nominal body | x121..139, y100..125.5 | x121..139, y100.5..126 |
| Native keepout | x106..154, y85..106 | x106..154, y85.5..106.5 |
| Notch opening | x105..155 | x105..155 |
| Recommended notch floor | y106.25 | y106.75 |
| First pad copper north edge | y107.04 | y107.54 |
| Pad copper to notch floor | 0.79 | 0.79 |

The initially suggested floor y106.50 with the first origin gives only 0.54 mm copper clearance against the configured 0.50 mm copper-to-edge rule. Its 0.04 mm surplus is poor manufacturing margin. The preferred option gives a nominal 0.50 mm inward antenna-tip allowance, 0.25 mm clearance beyond the antenna strip, and 0.79 mm pad-to-edge distance. Fabricator profile/registration and assembler placement tolerances must still be budgeted; the inward allowance is not a guarantee against every stack-up.

Make the notch part of the single closed Edge.Cuts outline, open to the top at y100, rather than a copper-only keepout or isolated enclosed hole. Retain the original outer x100..210, y100..200 rectangle and corner chamfers. Use inside floor radii no larger than 0.5 mm and verify the resulting arcs leave the entire keepout free of FR4. The notch removes approximately 337.5 mm² before fillet adjustment in the preferred option. At its middle, FR4 resumes at y106.75, north of every solder land. The antenna overhangs the cut edge by 6.25 mm while remaining within the overall PCB bounding rectangle.

Required surrounding changes:

- H5=(145,105) is inside the removed material and must move. Recheck its complete courtyard and actual strap/clip swept envelope, not only the drill. H6=(176,104.5) is outside the notch; its hardware remains unqualified.
- The preferred module body overlaps the present glass rectangle by 2.95 mm in Y. Its 3.25 mm maximum specified height, solder standoff, warp and support tolerances must fit beneath the raised display. A 1 mm gap fails here. Do not support the glass on the shield can.
- Preserve the native RF keepout beyond the PCB, including y85.5..100. The physical notch does not make the external RF clearance disappear. Keep enclosure metal, batteries, display metal, fasteners, clips, conductive coatings and cables out of the antenna clearance. Protect the unsupported antenna mechanically without loading it. Qualify plastic, adhesive and worn-body effects in the final assembly.
- Espressif recommends an edge-open cutout when overhang is unavailable, with clearance beside and underneath the antenna. Its housing guidance calls for at least 15 mm clearance in all directions. Maintain ground and stitching near the supported module region outside the antenna exclusion, and test final throughput/range.

## Full-width affinity row and NFC

D404..D408 centers must be x=108,131.5,155,178.5,202 at y190. Pitch is 23.5 mm and the endpoint margins are both 8 mm. The former reserve x176..206,y181..198 contains the last two LEDs and cannot remain.

The proposed replacement x182..200,y181..198 is 18 × 17 mm, 306 mm² versus 510 mm² previously: a 40% reduction. Native LED copper gives 2.235 mm from D407 to the reserve and 0.735 mm from the reserve to D408. Courtyard-line bounds leave about 1.955 mm and 0.455 mm respectively. A translated C407 at (181,190),90° would leave only 0.245 mm courtyard separation from the reserve; move this capacitor above/below or to the left of its LED. Route LED signals and supplies around the reserve, not through it or its interior on another layer.

Retain an all-layer exclusion for unrelated copper, vias and components. Coil copper and its feed must be introduced through a deliberately reviewed replacement rule when AE501 is designed. Keep U503 and DNP tuning capacitors near a north-edge feed, with short LA/LB connections. Their old positions do not constitute a completed antenna layout. VOUT remains unconnected.

The reserve stays 3.05 mm below nominal glass, 2 mm above the bottom board edge and 10.5 mm right of the nominal battery allowance. These are spacing facts, not accepted RF clearances. Verify final battery, panel/flex metal, dock hardware, ferrite if used, supports and enclosure. Adjacent LED copper is close enough that the finished assembly matters.

A useful feasibility calculation, not a coil design: allow 0.5 mm inside the reservation, leaving a 17 × 16 mm outer coil. At 0.20 mm trace/space, nine turns leave an approximately 10.2 × 9.2 mm inner opening. The AN11276 rectangular-coil approximation with 35 µm copper and etched turn exponent 1.75–1.85 estimates 1.90–2.36 µH. This is a plausible starting region for a tuned small tag, but excludes measured loss, self-capacitance, feed, vias, surrounding metal and reader coupling.

With 50 pF IC capacitance alone, ideal resonance requires 2.755 µH at 13.56 MHz, or 2.410 µH at 14.5 MHz. The specified 44–56 pF range alone changes the 13.56 MHz result to 2.46–3.13 µH. Added capacitance lowers the required inductance and can tune a smaller-inductance coil down in frequency, but cannot rescue excessive inductance with only parallel capacitors. NXP recommends 14.5 MHz as a nominal single-tag design starting point; final resonance and read/write tests decide the actual values.

The 25 × 20 mm Class 6 region described by NXP is a class boundary, not a claimed minimum antenna size. An 18 × 17 mm reserve is a custom design, not a copied qualified reference. Build several coil variants, measure isolated R/L/C and assembled resonance/Q, tune, then test target phones, tap positions, battery-off passive reads and enclosure/worn conditions. If reliability is inadequate, retain the LED row and consider a separate flex/ferrite antenna or revised mechanics; do not silently reduce spacing or claim a read range.

## Sources and checks

- Archived Espressif module datasheet v1.8, pp42 and45: dimension and land-pattern images visually inspected. [Source](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf), hashes in [MCU inventory](../datasheets/mcu_inventory.json).
- Archived Espressif hardware guidelines §1.4.7, printed pp30–31 / PDF pp33–34: placement text and cutout figure inspected. [Source](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/esp-hardware-design-guidelines-en-master-esp32s3.pdf).
- [NTAG component record](../components/NT3H2111W0FHKH.md), exact-part source record and native footprint geometry.
- [NXP AN11276 rev1.8](https://community.nxp.com/pwmxy87654/attachments/pwmxy87654/nfc/6155/1/AN11276.pdf), §§4.2–4.4 and5.1.4: calculation, tolerance and size guidance; [NXP tuning procedure](https://community.nxp.com/t5/NXP-Designs-Knowledge-Base/Guide-to-designing-antennas-for-the-NTAG-I2C-plus/ta-p/1104729).

Performed: native footprint/pad/keepout/outline extraction; project clearance inspection; manufacturer drawings; explicit coordinate arithmetic and preliminary coil estimate. Pending: final placed-board reread and DRC, complete all-component/height check, fabrication tolerances, support/strap validation, antenna layout, RF tuning and prototype performance. No detailed routing or manufacturing acceptance is implied.

## Follow-up: 80 mm height target

The user subsequently requested approximately 80 mm height. **Proceed with an explicitly provisional 110 × 80 mm placement trial.** The unchanged module/notch can fit, and the proposed NFC region is a credible custom-coil experiment. The principal tradeoff is reduced RF/mechanical margin, not a demonstrated inability to fit components. Keep a 90 mm fallback if phone testing or physical clearances fail.

| Height option | Proposed vertical arrangement | RF/mechanical implication |
|---|---|---|
| 80 mm, y100..180 | Glass y110..164.9; affinity LEDs y174; NFC x182..200,y166..179 (18 × 13) | Glass begins only 3.5 mm below the antenna strip; NFC has 1.1 mm glass gap and 1 mm board-edge gap. Most compact, most demanding validation. |
| 90 mm, y100..190 | Illustrative glass y116..170.9; affinity LEDs y184; NFC x182..200,y172..189 (18 × 17) | Restores 31% more NFC height and reserve area than the 80 mm trial; glass is 9.5 mm below the antenna. Still a compact RF layout requiring validation. |
| 100 mm, y100..200 | Existing glass y123.05..177.95; affinity LEDs y190; NFC x182..200,y181..198 (18 × 17) | Glass begins 16.55 mm below the antenna; most perimeter and support room. |

The 90 mm arrangement is a comparison, not a checked placement. The same all-layer keepouts, PCB bounding width and X anchors apply. Relative height reductions do not authorize moving the fixed X positions: affinity centers remain 108,131.5,155,178.5,202. The absolute LED Y positions necessarily change when shortening the board.

### Immediate 80 mm geometry checks

- Keep U201=(130,113.25),0°, notch x105..155 with floor y106.75 and ≤0.5 mm floor radii. Module remains nominally inside the unchanged top bounding edge. Retain the off-board RF exclusion to y85.5.
- **Role LED D401 cannot sit at (144,108) under the current copper-to-edge rule.** Its north pad copper is y107.10, only 0.35 mm from the notch floor, below the 0.50 mm rule. Minimum nominal center Y is 108.15; prefer 108.5 or later after checking the display/optical window. At 108.5 its copper-to-notch distance is 0.85 mm. Re-place C401: a 90° 0603 capacitor centered at y108 has its north copper at 106.775, leaving only 0.025 mm. Neither the cap nor an optical baffle can be checked from the LED center alone.
- Glass y110..164.9 does not intersect the native antenna XY keepout, which ends at 106.5. It overlays 16 mm of the module body length. A 4.5 mm glass-underside gap leaves 1.25 mm above the module maximum specified 3.25 mm body before solder, supports and warp. Qualify that stack and avoid shield-to-glass contact or load transfer.
- Moving the glass to 110 sharply reduces separation from antenna to display conductors. Passing the native two-dimensional keepout does not establish compliance with Espressif’s broader 15 mm housing-clearance recommendation. Model the actual panel/FPC metallization and mounting hardware, and compare assembled RF performance. A simple vertical stack preserving 15 mm antenna-to-glass separation,54.9 mm glass,1.1 mm gap,13 mm NFC reservation and 1 mm bottom margin would already need 91.5 mm overall height. That illustrates the tradeoff; 15 mm is not being invented as a manufacturer minimum glass offset.
- Recheck lanyard holes, top optics, power/USB and FPC mating, display supports, dock contacts, battery strain relief and component heights in the final compact placement. No complete 80 mm mechanical fit is certified by these two RF reservations.

### 18 × 13 mm NFC feasibility

The 80 mm reserve is 234 mm², 23.5% less than 18 × 17 and 54.1% less than the original 30 × 17. Keep the previous LED X clearances and C407 relocation requirement. Its 1.1 mm nominal glass separation and 1 mm bottom margin are provisional, and provide less room for manufacturing tolerance, enclosures and metal than the larger arrangement.

A 17 × 12 mm outer coil within 0.5 mm reservation margins can geometrically hold 9–10 turns at 0.20 mm trace/space. Using the same AN11276 approximation and 35 µm copper: 9 turns estimates 1.52–1.89 µH, with 10.2 × 5.2 mm inner opening; 10 turns estimates 1.74–2.19 µH, with 9.4 × 4.4 mm opening. At the midpoint exponent, the ideal total capacitance for 14.5 MHz is about 71 pF and 62 pF respectively, before choosing actual chip/coil/feed contributions. These calculations show plausible inductance and tuning headroom, not useful phone coupling or acceptable Q. More turns reduce open area and increase loss/parasitics; adding a capacitor does not restore lost coupling.

NXP’s dimensional guidance permits application-defined custom antennas but provides no demonstrated phone performance for this 18 × 13 target. Reserve it for prototype coil variants, short north-edge feeds, measured R/L/C and loaded resonance, followed by target-phone read/write tests with the actual display, battery, enclosure and wearer. Do not draw final copper or claim a tap distance from this estimate. If it fails, prefer a 90 mm board or a separately qualified flex/ferrite antenna before sacrificing the requested full-width LED spacing.

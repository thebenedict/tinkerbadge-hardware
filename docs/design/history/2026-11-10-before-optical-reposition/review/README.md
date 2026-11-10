# Organized placement and top role row

Native board SHA256 `08b5de1ac1b194544ebf15598fd0b40e66a4e0c05123c6da75603a769d91554e`, KiCad 10.0.8, 9 November 2026. The actual active board and placement plan match this checkpoint.

This revision has 110 × 80 mm outer dimensions, a left-open antenna shoulder, 48 relocated references in organized functional groups and three role LEDs at x 160/180.5/201, y 103 (20.5 mm pitch). The bottom five LEDs remain at 23.5 mm pitch across the board. No routing was added.

`functional-blocks.png` is the requested annotated native component render. `functional-blocks.svg` embeds the original PNG unchanged and adds only review callouts; `functional-blocks.json` gives source hashes, block membership and six-hole calibration. Dashed amber areas are unresolved reserves. Mechanical envelopes are hidden in this component view, not removed from the board.

The other four PNGs show the native front/rear/raised-display views. Rendering-only derivatives enable virtual envelopes without changing authoritative board attributes. The 93.3 × 54.9 mm glass has a proposed 4.5 mm underside lift; battery and socket are allowances. Native assembly SVGs retain actual pads/courtyards.

Fresh DRC: four existing USB NPTH-to-pad errors, one module silk-edge warning, 390 unconnected items and nine unresolved-footprint reports. Fresh ERC: zero errors and one unchanged warning. Contract/property checks pass. Full native inverse-placement comparison passes for all 186 footprints; no new geometric collision appears.

See `../../../docs/design/pcb_placement_review.md`, `organized_top_row_final_review.md` and `top_role_placement_review.md` for the review. Human placement approval and RF/flex/optical/parts/manufacturing qualification remain required before detailed routing/release.

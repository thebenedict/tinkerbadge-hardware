# Current PCB review checkpoint

**Experimental placement only. Human approval is required before detailed routing. Not for fabrication or assembly.**

The active board is `../../../tinkerbadge.kicad_pcb`, SHA256 `a49a19fdf1a2cea1b223f419887e369ab844f49adc9933a0688ba7f01e2ab7b4`.

It is now 110 × 80 mm, with front-side SMT, a proposed 4.5 mm raised display, full-width bottom LEDs, left-edge button pair, right-edge USB/Qwiic and a true antenna notch. The previous 100 mm placement is preserved under `../../../docs/design/history/2026-11-09-100mm-two-sided-fallback/`.

Review files in this directory:
- `front-with-display.png`: native front view with the raised display envelope.
- `rear-with-battery.png`: native rear view with battery allowance and provisional SAO body.
- `front-components.png`: all front electronics, with virtual mechanical models removed only for visibility.
- `raised-display-perspective.png`: native tilted view showing the proposed stack.
- `placement-zones.svg`: labeled functional diagram, not native geometry.
- `front-assembly.svg` and `rear-assembly.svg`: actual native pads, fabrication labels and courtyards.
- `drc.json`, `erc.json`, `endpoint-check.json` and `property-check.json`: check results.

See `../../../docs/design/pcb_placement_review.md` for the current proposal and `../../../docs/design/compact_one_sided_final_review.md` for independent final readback.

The board has 170 electrical footprints, ten review reservations, six holes and no routing. All 164 non-test electrical footprints are front; six bare test pads are rear. No courtyard, copper or keepout collision was found. DRC retains four existing USB source-footprint hole-clearance errors, one antenna-silkscreen edge warning, 390 unrouted-item reports and nine missing-footprint parity reports.

The glass is only 3.5 mm behind the antenna, below Espressif's recommended 15 mm surrounding clearance. The 18 × 13 mm NFC coil area and display-flex fold remain unqualified. Images show allowances, not guaranteed installed parts. Single-sided SMT does not eliminate battery/display fitting or possible secondary connector soldering.

All prior top-level placement images/maps/checks are historical. In particular, `led-spacing-*`, `placement-*-assembly.svg` and `placement-review-map.svg` represent the older 100 mm/two-sided proposal and must not be presented as the current board.

# Current PCB review checkpoint

The active 110 × 80 mm board is `../../tinkerbadge.kicad_pcb`, SHA256 `ddf824f2a59bc82568bbb03bcb3f89959f2ee12638b380790207739273c1844d`.

Start with `shared-optics/` for the current native front/component/rear/perspective views, annotated functional-block diagram and pinned checks. U501 now sits beside U504 below the display, with local bypass and a proposed clear corridor for a separate IR-transmitter optical compartment. The passive sensors may share a visible/940 nm-transmitting aperture. The board retains front-side SMT, the raised-display proposal, equal LED spacing, left buttons, right connectors, left-open radio shoulder and planned B.Cu NFC coil.

The independent four-part delta has zero new courtyard/edge/keepout collisions and preserves all 186 complete footprint records after inverse poses. Existing DRC findings remain four USB hole-clearance errors, one silk-edge warning, 390 unrouted items and nine missing footprints. Source contracts/properties pass; ERC has zero errors and one existing warning.

See `../../docs/design/pcb_placement_review.md` and `../../docs/design/shared_passive_optics_review.md`. Final enclosure optics, radio/display clearance, NFC tuning, flex/connector/part qualification and manufacturing exceptions remain open. No routing, enclosure or antenna copper has been added. Human placement approval is required before detailed routing.

Earlier `lower-ir/`, `optical-space/`, `organized-top-row/`, `compact-one-sided/`, `spread-one-sided/` and top-level views are historical. Native fallbacks are under `../../docs/design/history/`.

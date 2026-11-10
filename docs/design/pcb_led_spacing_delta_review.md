# LED spacing delta review

2026-11-09. **PASS for the bounded placement delta, with the optical caveat below.** This is not routing, manufacturing or overall mechanical approval.

## Pinned evidence

- Baseline: `docs/design/history/2026-11-09-left-button-placement/tinkerbadge.kicad_pcb`, SHA256 `322dc5d129db733813ff2d9dc0912e813fc9aa27043376b74c5deea2b9d668fa`.
- Reviewed board: `tinkerbadge.kicad_pcb`, SHA256 `99158950ecce21da92f8c0e9343ecf60316f321255fd496f790517ac7717f49f`.
- Change record: `exports/pcb-review/led-spacing-change.json`.
- Native KiCad10.0.8 read-only inspection of both boards. No SaveBoard, CAD changes or project changes by this reviewer.

## Independently verified

- Same186 footprint references. Only14 requested references moved: D402,D403,C402,C403 and D404-D408/C404-C408. All other positions, rotations and sides are unchanged.
- D401 remains F.Cu(144,114),0 degrees, exactly matching the archived baseline.
- Top LED centers: D401(144,114),D402(172.5,114),D403(201,114). Both adjacent pitches are exactly28.5 mm.
- Bottom LED centers: x=108,124,140,156,172 at y=190. All four pitches are exactly16 mm. This widens the evenly spaced row within the NFC-clear span; it intentionally does not extend across the full board width.
- C402 is(175.5,114); C403 is below D403 at(201,117.5). Bottom decouplers are x=110.5,126.5,142.5,158.5,174.5 at y=190. All remain F.Cu,90 degrees. Final short VDD/ground loops remain a routing requirement, especially for the relocated C403.
- For every footprint, native pad UUIDs, pad numbers, net names, relative positions, sizes, rotations, shapes, drill sizes, attributes and layer sets match the baseline. Footprint library IDs also match. This preserves the previously reviewed source pad maps; no new footprint substitution occurred.
- Zero tracks remain. The DRC result is unchanged: four existing USB hole-clearance errors, two radio-overhang silk warnings,390 unconnected items and the same nine missing electrical footprints. No new reported intercomponent clearance, overlap or keepout violation.

## NFC and mechanical clearance

The unchanged NFC reservation occupies x=176..206,y=181..198. Native courtyard bounds, including line stroke, give:

- D408 right edge173.545: **2.455 mm** gap to the NFC boundary.
- C408 right edge175.255: **0.745 mm** gap to the NFC boundary.

Neither moved footprint enters that reserve. These are geometric gaps, not proof of final NFC performance. The eventual coil, tuning parts, exclusion area and assembled RF behavior remain separate gates. Preserve the reserved span; any later expansion needs a placement recheck.

The updated front/rear envelope images were visually inspected. They show the requested regular rows, unchanged left top LED, both existing left-edge buttons and unchanged battery/SAO arrangement. No new obvious panel/body overlap appears. C403 remains north of the glass envelope; its courtyard lower edge119.005 leaves4.045 mm to the panel north edge123.05.

## Optical caveat requiring follow-through

D403 at(201,114) is now only **4.472 mm center-to-center** from ambient sensor U501 at(205,112), with **0.530 mm courtyard-to-courtyard separation**. The source-derived footprints do not physically overlap, but this is substantially stronger potential self-light coupling than the prior31.06 mm separation.

Do not infer accurate ambient-light measurements from the geometric pass. Use a verified LED-off measurement window and/or a physically qualified opaque optical barrier, then test through the final cover at all intended RGB brightness levels. Calibration alone must not be assumed to fix saturation or internal reflections. The tiny courtyard gap does not itself prove a baffle will fit. U501 and the optical group were not moved in this bounded change.

## Preview evidence and scope

- `exports/pcb-review/led-spacing-front-with-envelopes.png`, SHA256 `e6dab61ebc91bbc31670f559ecac5d10dc43cd54510a2018efcf4bd8d5d513c5`. Actual image inspected.
- `exports/pcb-review/led-spacing-rear-with-envelopes.png`, SHA256 `f4b7b662cd74c402f12def3caf4f47c11f72c08987fe399a19117eeaf85b9a9b`. Actual image inspected.

All previous unresolved connector, flex, battery, RF, optical and enclosure gates remain. This change does not implement single-sided assembly; all component sides are preserved.

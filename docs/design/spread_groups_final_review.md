# Organized front-side placement: final delta review

9 November 2026. **Pass for the saved native placement delta.** Exactly the proposed 32 references moved, the sensor capacitor allocation is corrected, and the left PCB sliver is removed. Existing routing, RF, mechanical and manufacturing gates remain.

## Pinned inputs and method

- Before: `tinkerbadge.kicad_pcb`, SHA256 `a49a19fdf1a2cea1b223f419887e369ab844f49adc9933a0688ba7f01e2ab7b4`.
- Candidate: `.build/spread-one-sided/tinkerbadge.kicad_pcb`, SHA256 `2ff74d95a154bce47ce87e97cf86c60af26514ff08235ffc70f8b9189b61ddda`.
- Proposal: `.build/spread_groups_proposal.json`.
- Tool: native KiCad 10.0.8, read-only LoadBoard and in-memory transforms.
- Machine-readable review: `.build/spread_groups_delta_check.json`.

The reviewer inspected the actual saved candidate independently of the change report. No SaveBoard, native CAD, project, library or model writes were made. Root and staged project settings matched at the inspection checkpoint; the 0.5 mm copper-edge rule remains unchanged.

## Exact placement and local geometry

All 32 proposed references match their exact native coordinates, side and angle. No other footprint moved.

The four rigid groups preserve their offsets in integer KiCad coordinates with no rounding allowance:

- ADC: U107, R127–R130, C115/C116, translated (−32,+2) mm.
- Main converter: U103, C107–C109, R117/R118, RES_L101, translated (−26,+17).
- Display load switch: U104, C112–C114, R119, translated (−7,+9).
- I/O expander: U506, C514/C515, R514–R517, translated (+3,+12).

For every one of the 186 footprints, the reviewer restored the candidate's position and rotation to the source values in memory, serialized the complete native footprint, and compared its parsed content with the source. **All 186 matched exactly**, ignoring only element serialization order. No numeric tolerance or field exclusion was necessary.

This comparison covers all 568 physical pad primitives, including 562 in electrical footprints and 539 numbered pads; pad numbers/nets, shape, size, drill, layer, local position/angle, mask/paste and custom geometry; all footprint properties/fields and schematic associations; graphics, attributes, model references/transforms and footprint-owned rule areas.

There remain 170 electrical footprints: 164 front electrical parts and six rear copper test pads. Four copper layers and zero tracks/vias are unchanged.

## Sensor correction and editor groups

The saved candidate places:

| Reference | X mm | Y mm | Rotation |
|---|---:|---:|---:|
| C501 | 201 | 103 | 180° |
| C502 | 208 | 104.5 | 270° |
| U502 | 162 | 133 | 0° |
| C503 | 165 | 133.5 | 0° |
| C504 | 165 | 131.5 | 0° |
| C505 | 162 | 136.5 | 270° |

U501 stays fixed at (205,103). The earlier allocation error is corrected: C501/C502 serve U501 VCC/DVI; C503/C504 serve U502 VDD/VDDIO; C505 is U502 local bulk. NFC C506 stays with U503. Values and nets are unchanged. U502's orientation is unchanged, preserving the established sensor axes.

The source-backed local arrangement and power-pin distances are documented in `spread_groups_placement_review.md`. Saved coordinates match that checked arrangement exactly. Both U502 100 nF positive pads face the east-side power pins, at 1.644 mm pad-center distances. Ambient bypass remains clear of the rounded edge and H6; the proposal measured approximately 1.468 mm minimum copper-edge clearance, 4.904 mm minimum added-capacitor copper-to-drill clearance, and 3.879 mm to the stroked cord reservation.

All six native editor groups match the proposal exactly and pass native group sanity checking. The accelerometer group contains U502/C503/C504/C505. The ambient-light bypass group contains C501/C502; U501 deliberately remains outside that movable group because its optical placement is fixed. The other four groups contain precisely the reference sets listed above. No duplicate or missing group member was found.

## Outline, reservations and collisions

Native outline extraction with inference disabled returns one valid closed outer contour, no enclosed outline holes, and bounds x100–210/y100–180 mm: 110 × 80 mm. Six line segments and five arcs form the new boundary.

The left-open shoulder uses the external R4 corner from (100,110.75) to (104,106.75), then the horizontal shoulder to (154.5,106.75), the existing R0.5 internal return to (155,106.25), and the wall to y100. Point/polygon tests confirm the former left sliver is absent, antenna-notch material is absent at y106.5, and material resumes below the shoulder at y106.8.

Native polygon intersection across all **177 front and 9 rear courtyard polygons finds zero positive-area collisions**, including all reservations and holes.

The radio rule area has 0 mm² intersection with FR4. The full NFC reservation remains on-board at 234 mm². Both footprint-owned keepouts retain all four copper layers and prohibitions on tracks, vias, pads, footprints and pours. Display, holes, fixed connectors, LEDs and other footprint-owned mechanical envelopes are unchanged by the full inverse-transform comparison.

## Dependencies and saved checks

All 167 model assignments resolve to 33 distinct model files. Staged model files, footprint libraries, schematic files and symbol libraries are byte-identical to root. Other board settings and non-drawing board content are unchanged.

The saved DRC report dated 2026-11-09 15:34:18 contains:
- Four existing USB NPTH-to-pad clearance errors, 0.1944 mm versus 0.2500 mm. Descriptions and affected pad UUID pairs match the prior report exactly.
- One existing radio silkscreen/edge warning at the revised shoulder.
- 390 unconnected-item reports for the unrouted board.
- Nine unresolved-footprint schematic-parity reports.

Ignored-check settings match the prior report. No new courtyard, copper, mask, keepout, outline or copper-edge violation appears. This reviewer inspected the saved DRC and independently checked geometry; it did not rerun the DRC engine. The board is not DRC-clean.

## Remaining requirements

The longer charger-to-converter VSYS feed needs wide, low-impedance copper, a deliberate corridor around the expander and continuous return. Keep converter bypass/feedback loops compact and ADC wiring away from switching currents. Actual ground vias, escapes and transient performance remain unverified.

Exact magnetic parts, unresolved connector/antenna footprints, effective capacitor ratings, display flex/support/height tolerances, final optics, antenna tuning, enclosure effects and USB manufacturing exceptions remain open. The 80 mm packaging does not satisfy the radio's previously documented 15 mm surrounding-housing recommendation.

Fresh candidate render inspection and human placement approval remain pending at this review checkpoint. No detailed routing has begun.

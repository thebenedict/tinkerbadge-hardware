# PCB placement review

9 November 2026. **Unrouted placement proposal, pending human approval. Not a fabrication or assembly release.**

Authoritative board: `tinkerbadge.kicad_pcb`, SHA256 `99158950ecce21da92f8c0e9343ecf60316f321255fd496f790517ac7717f49f`.

## LED spacing revision

The leftmost role LED D401 remains exactly at F(144,114). D402/D403 are now at F(172.5,114) and F(201,114), giving 28.5 mm center spacing across the three role lights. The five affinity LEDs now sit at x=108/124/140/156/172, y=190, at 16 mm pitch rather than the previous 12 mm pitch. The original bottom row was already equally spaced; this revision spreads it farther across the available NFC-clear span. It intentionally does not enter the lower-right NFC reservation.

Only these seven LEDs and their local decoupling capacitors moved. All other placements, sides, rotations, pad geometry and nets are unchanged. Latest evidence is `exports/pcb-review/led-spacing-change.json` and `drc-led-spacing.json`, plus the independent LED delta review. The rightmost role LED is 4.47 mm from the ambient sensor with 0.53 mm courtyard separation: optical isolation and/or LED-off measurement timing must be tested with the actual cover. Physical clearance does not certify optical performance.

The one-sided assembly question is assessed separately in `single_sided_assembly_assessment.md`. No one-sided rearrangement was made.

## Placement decision

Review the proposed 110 × 100 mm outline, component sides, display location, two adjacent left-edge buttons, connector access and mechanical reservations before detailed routing. The four-copper-layer board uses a nominal 1.6 mm thickness; the actual fabricator stackup, materials and impedance rules are not selected. The radio antenna projects beyond the top board edge and has its native all-copper keepout. A 30 × 17 mm all-four-layer no-metal rule area reserves space for the as-yet-undesigned NFC antenna.

The front carries the display, radio, three role lights, five affinity lights, ambient/IR sensing and the button pair. SW401 and SW402 are both front-side, 270°, at (102.1,161) and (102.1,171) mm. Their actuators face the left edge and their centers are 10 mm apart, matching the latest user request. The rear carries power, display support and expansion circuitry around a clear battery reservation. The Qwiic connector faces outward to the right, with its mating face 0.925 mm inside the PCB edge and at least 0.725 mm copper-to-edge clearance. Enclosure access still needs a cable/plug check.

## What is present

- 170 schematic-linked electrical footprints, ten padless mechanical/interface reservations and six provisional mounting/lanyard holes. No tracks, vias or copper pours have been routed.
- All 524 distinct logical endpoints and 539 numbered physical pad primitives on placed components match the saved schematic netlist. Source footprint geometry, model references, flags, sheet fields and UUID paths pass independent readback.
- 167 model references resolve to existing files. Standard-library models are used where available. Several local models are explicitly simplified dimensional/nominal envelopes, not manufacturer CAD or mating certification.
- Display glass envelope: 93.3 × 54.9 × 0.92 mm maximum, with a proposed 1 mm front support gap. The exact flex folding path/contact side remains unresolved.
- Rear battery reservation: 35 × 55 × 7 mm. This is a space allowance, not a selected or approved pack.
- The rear SAO reservation was moved above the glass to (151.5,116) mm so the candidate's 3.2 mm through-hole tails would not intersect the proposed display support gap. The simplified model does not contain those tails or certify the mating/key orientation.

## Check results

See `pcb_final_footprint_review.md`, `pcb_mechanical_placement_review.md` and `exports/pcb-review/` for evidence.

- Schematic contracts and property checks pass: 179 components, 576 contract endpoints and 30 intentional no-connect endpoints. Main export is `exports/tinkerbadge.net`, SHA256 `8409e65a237a60fd872eb89a0f4c5aa5caa0808df69a90cfe8a569411a77af59`.
- Fresh ERC: zero errors and the existing LIS2DW12 SDO/SA0 bidirectional-to-power warning. Netlist export also prints an annotation warning; explicit-reference contract validation and ERC do not show an annotation violation. This warning has not been represented as fixed.
- DRC: no courtyard overlaps, inter-component copper clearance/shorts, mask bridges or keepout violations.
- Four USB connector NPTH-to-pad clearance errors remain: the reviewed source land pattern gives 0.1944 mm against the provisional 0.25 mm rule. Do not suppress these or alter the source footprint without fabricator/connector acceptance.
- Two radio silkscreen edge warnings remain because the source outline extends across the board edge with the antenna overhang.
- 390 unconnected-item reports are expected because the PCB is unrouted. Nine schematic-footprint absences below are intentional and remain release blockers. DRC is not clean and this is not a manufacturing-ready design.

## Unresolved parts and release gates

| Reference | Required resolution |
|---|---|
| U105 | Accept exact TI DQA0010A/B package/land-pattern variant for the selected ordering code. |
| J102 | Select protected two-wire battery pack, connector, polarity and current capability. |
| J103 | Select dock contact, guide and mating mechanics. |
| J104 | Define optional, initially unpopulated thermistor interface if charging will be enabled. |
| L101 | Select exact 0.47 µH primary inductor with required current, saturation and DCR margins. |
| J301 | Validate exact display FPC connector, mating/contact side and fold geometry. |
| L301 | Select exact 68 µH display inductor. |
| AE501 | Design, lay out, simulate/measure and tune the NFC coil. |
| J502 | Verify exact keyed SAO socket mating view and pin/key orientation. |

Generic passive MPNs, MLCC bias/rating margins, fine-pitch stencil details, radio/antenna qualification, optical isolation, cable bending, fastener access, battery attachment, final silk and all routing/DFM checks remain open. Exact power-loop/decoupling placement will be refined with the selected inductors and routed paths. R120 holds charger CE high: onboard charging remains disabled. The shared 3.3 V LED supply retains the documented prototype/bench qualification gate.

C507/C508 record DNP in custom population text, but their native KiCad DNP flags are false, matching the existing schematic workflow. Do not use a native-flag-only BOM/position export as an assembly order.

## Preview provenance

`led-spacing-front-with-envelopes.png` and `led-spacing-rear-with-envelopes.png` are native KiCad renders of a rendering-only derivative. That derivative enables the three virtual mechanical models and resolves model paths; the authoritative board retains board-only/BOM/position exclusion flags. No electrical geometry or placements are changed in the render derivative. The white panel and gray battery are review envelopes, not guaranteed installed parts. The functional SVG is a simplified arrangement map; native assembly SVGs contain actual footprint geometry.

The original live import omitted model references, rule areas and footprint attributes. It was replaced safely with reviewed native KiCad footprint forms while the editor was closed, then independently checked. `tools/run_pcb_native.sh` preserves project rules around native API saves because an isolated API save can otherwise rewrite project defaults. Do not rerun the initial import or placement-generation scripts over this reviewed checkpoint without deliberate review.

The updated front/rear preview files were visually inspected after the final left-button change and saved to the user's file library. The simplified functional SVG is provided as vector artwork; the cropped Quick Look diagnostic was removed from the review deliverables.

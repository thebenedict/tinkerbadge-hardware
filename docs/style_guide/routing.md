# PCB layout and routing

Make the board's function easy to read, including through the enclosure. Electrical correctness, safety, RF performance, signal and power integrity, thermal behavior, manufacturer requirements, manufacturing limits, and mechanical/test access take precedence over appearance.

## Establish the layout constraints

- Start from a KiCad implementation checked against the reviewed component records and project pinouts in the [datasheet-first workflow](../design_workflow.md). Use its schematic connectivity and project rules to drive layout. Verify the selected MPN, pad numbers, pitch, drills, courtyard, polarity, and mechanical features against the datasheet before placement. Keep modified footprints in project-local libraries and update placed instances.
- Define the stackup, reference planes, net classes, and fabrication/assembly rules before routing. Size traces, vias, clearances, and thermal copper from voltage, current, temperature rise, impedance, and the chosen manufacturing process.
- For this badge, start with the [specification's](../spec.md#pcb) four-layer arrangement and largely continuous ground reference. Reserve the exact radio-module and NFC antenna keepouts across the applicable layers, components, battery, display, and enclosure.
- Establish the board outline, mounting holes, display/flex path, connector mating envelopes, component heights, optical openings, and probe/rework access. Check clearance-critical 3D models against datasheets.

## Place functional groups

- Place fixed mechanical, optical, and RF items first. Then arrange power, processor/radio, display support, sensors/inputs, LEDs, and connectors/test access into readable groups, with room for their interconnections.
- Keep each IC and its supporting components together. Put decoupling at the relevant power pins with a short supply/return loop; keep switching loops compact and feedback/sense paths away from noisy nodes. Place connector protection and filtering at the interface they protect.
- Align comparable components by body edge, pad row, or center. Use consistent orientation and spacing within a group, clear gaps between groups, and a small set of local alignment axes. Repeat placement patterns for equivalent channels.
- Let major components and user interfaces establish the composition. Reserve deliberate routing corridors and open space rather than spreading parts uniformly. Preserve electrically critical placement when aligning surrounding parts.
- Check the assembled badge: button reach, USB cable clearance, flex bend and insertion, dock seating, battery clearance, LED diffusion, and ambient-light sensor isolation from the LEDs.

## Review placement before routing

1. Define the functional zones and their interface connections. Check actual footprints/courtyards, usable area, keepouts, heights, connector access, and escape paths.
2. Estimate congestion using pad pitch, track widths/clearances, available layers, reference-plane continuity, and connections between zones. Identify crowded regions and assumptions that need a trial escape.
3. Present labeled top/bottom placement views, a 3D/enclosure view, and a short pre-check summary. Compare a few viable arrangements when composition is unresolved.
4. **Obtain human approval before detailed routing.** Return for review if routing requires a material change to the approved placement or zone plan.

## Route cleanly and preserve circuit behavior

- Route placement-sensitive and constrained nets first: RF/NFC connections, switching loops, clocks, USB pairs, sensitive analog paths, and major power paths as applicable. Follow the selected parts' reference layouts.
- Keep signal return paths short and continuous. Avoid crossing reference-plane gaps; provide appropriate return/stitching vias at layer changes. Preserve the circuit's intended ground/net-tie topology and keep high-current returns out of sensitive measurement paths.
- Where a shunt is used, take separate Kelvin sense connections from its specified terminals. Route sensitive differential inputs together and keep filtering close to the receiving pins. Apply impedance, coupling, and length/skew constraints only where the interface requires them.
- Prefer horizontal, vertical, and 45-degree diagonal segments. Turn ordinary elbows with two 45-degree bends. Allow clean perpendicular T/cross junctions into a straight through-route, including rotated diagonal junctions; avoid tiny decorative bevels at branch taps.
- Center a trace on the selected pad edge and enter perpendicular to it, with a short straight approach before the next bend. Evaluate the actual rotated pad geometry. Use radial/normal entry for curved boundaries and inspect exposed copper boundaries on compound pads.
- Keep fan-outs, parallel runs, widths, and transitions coherent. Remove needless jogs, short segments, detours, and layer changes while preserving branch points, required vias, and width transitions.
- Follow the electrical requirements for fine-pitch escapes, differential pairs, thermal connections, and antenna geometry when they need a different approach. Keep validated land patterns intact.
- Protect printed coils, tuning structures, and intentional net ties from same-net shortcuts as well as other-net clearance violations. Keep via holes clear of assembly paste lands unless a suitable via-in-pad process is specified.

## Inspect, refine, and release

- Refill zones after geometry changes. Check schematic/PCB connectivity parity, ERC, DRC, return paths, thermal paths, antenna keepouts, and mechanical fit.
- Render repeatable top/bottom and 3D views, plus close-ups of dense areas and pad entries. Inspect the actual images and silkscreen at physical size.
- Keep text size, orientation, and offsets consistent. Make references, polarity/pin-1 marks, connector functions, and revision identification legible and clear of pads; keep service labels visible after assembly.
- Report visual issues by component/net and location. Compare alignment, actual edge-to-edge spacing, pad-entry offset/angle, and unnecessary bends/vias within each functional group. Keep electrical failures separate from style suggestions.
- Make bounded edits, rerun affected checks, and inspect fresh views. Preserve the best valid revision and record important trade-offs. Obtain human visual review before release.
- Reuse alignment, repeated-block, fan-out, rendering, and checking tools. Validate their output against native KiCad geometry and connectivity; preserve accepted edits in reproducible inputs. Adapt tools to this board's stackup, component sides, and copper zones.

## Project references

- `Ultrasonic_Driver/KICAD.md` and `ARCHITECTURE_SPEC.md`: verified footprints/models, compact support circuits, explicit grounding, and sense-path review.
- `harvest/tools/README.md`, `docs/routing-review.md`, and `docs/junction-cleanup.md`: geometry-aware pad entry, 45-degree elbows, perpendicular branch junctions, protected copper, and checked cleanup.
- [Badge specification](../spec.md#pcb): functional zones, placement pre-checks, human approval, and visual review.

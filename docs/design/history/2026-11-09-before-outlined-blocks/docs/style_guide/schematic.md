# Schematic style guide

This is a partial historical snapshot. References to documents not preserved with this snapshot are retained as plain titles. Use the [current verification record](../../../../verification.md) for available project records; current documents may describe a later revision.

Make each sheet easy to follow as an explanation of the circuit.

Before creating or changing the schematic, follow the datasheet-first workflow. Use independently reviewed component records and project pinouts as the design inputs.

Use the [Seattle Transit Live main schematic](https://github.com/thebenedict/seattletransit-hardware/blob/main/transit.kicad_sch) as the style reference for clear labels and distinct, readable functional blocks.

## Functional organization

- Group circuitry by function: display, processor/radio, power, inputs/sensors, LEDs, and connectors/test access. Use clear block or sheet titles.
- Arrange blocks so signal and power flow are easy to follow. Each IC and its supporting components should fit within an imaginary rectangle.
- Keep decoupling capacitors, pull-ups, pull-downs, and other local support parts close to the pins they serve, with direct wire connections.
- Give components and blocks enough space for wiring and readable text. Choose a sheet size that fits the drawing, leaving at least 5 mm clearance from the border and full title block.

## Wiring and labels

- Snap symbols, wires, and labels to the KiCad grid.
- Use conventional, orthogonal wiring. Minimize crossings and make junctions unambiguous.
- Point ground symbols down and power symbols up. Align related power and ground symbols horizontally where practical.
- Use direct wires within small component groups. Use net labels to simplify long or complex connections, while keeping the circuit's relationships visible.
- Prefer sheet-local labels; use global labels when their scope is needed. Keep label formatting and justification consistent. Global labels need their own alignment; local-label bottom justification can misalign the global-label body.

## Symbols and text

- Use standard KiCad symbols where available, verifying pin numbers, functions, and polarity against the exact component's datasheet and reviewed record. Maintain the main-component PDFs in `docs/datasheets/` as specified by the workflow.
- For custom symbols, group pins for clear wiring and default to 150 mil pin lengths.
- Place reference designators and values close to their symbols, consistently and without overlapping bodies, pins, wires, or other text.
- For ICs, stack the reference designator and component label above or below the body. If pins occupy that space, place them beside a clear corner.

## Review

- Open the native KiCad project and confirm that its libraries resolve from the project or standard installation.
- Inspect fresh PDF or SVG exports for legibility, functional grouping, text collisions, ambiguous connections, and sheet/title-block clearance.
- Run ERC and compare the exported pin/net connectivity with the block contracts and BOM. Check connected pin endpoints, not just matching net names. Mark intentional NCs explicitly, explain warnings, and fix real connectivity errors rather than suppressing them.
- After meaningful edits, repeat the affected electrical checks and visual review. Record unresolved issues by component/net and location.

## Sources

- [Seattle Transit Live schematic](https://github.com/thebenedict/seattletransit-hardware/blob/main/transit.kicad_sch): public example of functional grouping and readable labels.
- [Wiring and labels](#wiring-and-labels), [symbols and text](#symbols-and-text), and [review](#review): the project guidance is recorded here so it can be followed without access to earlier local projects.

Earlier internal references informed these guidelines; no verified public copy was available for those documents at publication review.

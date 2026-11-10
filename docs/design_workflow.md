# Datasheet-first hardware workflow

Use this sequence for each hardware block: **datasheet PDFs → component facts → project pinouts → independent review → KiCad implementation → electrical and physical checks**.

## Component addition or replacement checklist

Work through one component or block at a time. Start with the smallest useful records for the first part, then extend them as actual design and checking needs emerge; do not design a comprehensive schema in advance.

- [ ] **Choose the exact part:** record its MPN, package/variant, role, and selection status in the [design BOM](AI_Tinkerers_Badge_Design_BOM_Draft_2026-11-09.md).
- [ ] **Save the sources:** collect the [datasheet PDFs](#1-collect-and-maintain-datasheets), revisions, source URLs, package drawings, and applicable errata.
- [ ] **Extract facts and assign pins:** capture cited [physical-pin facts](#2-extract-compact-component-facts), then define the separate [project pinouts](#3-define-the-projects-pinouts); mark unknowns and conflicts.
- [ ] **Adapt the reference circuit:** record support-component values and rationale, power/off-state behavior, and layout constraints in the [circuit decisions](#adapt-the-reference-circuit).
- [ ] **Review independently:** have another reviewer check critical facts and assignments against the [original sources](#4-independently-verify-critical-tables).
- [ ] **Implement in KiCad:** use [verified symbols and footprints](#5-generate-and-check-the-implementation) and include the required support circuitry.
- [ ] **Check the result:** compare nets and pin/pad mappings, run ERC, and inspect fresh schematic exports; perform board connectivity, DRC, and visual checks when a PCB exists.
- [ ] **Close the loop:** [synchronize the BOM and records](#6-keep-changes-synchronized), track remaining checks, and record bench-test plans and results as hardware becomes available.

## Sources and responsibilities

- Manufacturer datasheets, package drawings, reference circuits, and applicable errata establish what the exact component can do.
- [The specification](spec.md), design decisions, and reviewed project pinouts establish how this badge uses those components.
- Native KiCad schematic, board, project rules, and libraries implement that design and supply downstream exports. Create them after the inputs are reviewed.

If these disagree, trace the disputed fact to its source and correct the affected records and implementation. An existing symbol, footprint, or netlist does not settle a conflict with a manufacturer pin drawing. Record unresolved conflicts and block the affected design work until they are resolved.

## 1. Collect and maintain datasheets

For local design review, keep the PDF datasheet for each main component in the current design BOM in `docs/datasheets/`, relative to the project root. Public checkouts contain [source URLs and hash records](datasheets/README.md) rather than mirrored supplier documents; download the recorded revision before review. Match the exact MPN, package, and applicable revision; include required errata and separate package or connector drawings.

Keep this directory aligned with the BOM: add the corresponding PDFs when components are added, update them when parts or source revisions change, and remove PDFs when their components are removed and no remaining component needs them. Preserve evidence for past releases in versioned release history. Update source links and component records in the same change.

Record the manufacturer URL, local PDF filename, document revision/date, and file hash. If a required PDF is unavailable, record the gap and the work it blocks.

## 2. Extract compact component facts

Create a concise record in `docs/components/<mpn>.md` for each main component. Keep physical-pin facts in a minimal machine-readable source alongside it, and generate repeated pin tables from that source. Choose the initial format while documenting the first part. Read the PDF's pin table and package drawing, including the actual diagram; text extraction alone can lose numbering, polarity, or orientation.

Capture the facts needed to design and check the circuit:

- Exact MPN, package, variant, and source documents.
- Every physical package pin/pad number and its manufacturer name/function, including power, ground, exposed pads, NC/DNC pins, and reserved pins. Distinguish package pin numbers from MCU GPIO numbers and connector signal names.
- Relevant alternate functions, fixed peripheral pins, boot straps, reset defaults, wake capability, and restrictions imposed by module memory or package variants.
- Recommended operating supplies and I/O levels, absolute maximum limits, current requirements, power sequencing, and behavior when unpowered.
- Required support circuitry, decoupling, pull-ups/pull-downs, protection, reference-layout constraints, and applicable errata.

Cite the source page and table/figure for each critical fact. Label derived conclusions and unresolved items explicitly; use “unknown” rather than filling a gap from memory or a similar part. Keep the record focused, with links back to the PDF for detail.

## 3. Define the project's pinouts

Maintain `docs/pinouts.md` before generating the schematic. Separate manufacturer pin facts from design assignments. For each component or connector, record:

- Stable BOM/component ID and reference designator when assigned, exact MPN/package, and component-record link.
- Physical pin/pad number, manufacturer function, assigned project net, connected endpoints, and signal direction/voltage domain.
- Relevant pull, enable, boot/reset, sleep/wake, and powered-off behavior.
- Explicit unused-pin treatment and the source or design rationale for it.

Include MCU GPIO allocation, fixed/reserved pins, bus addresses, connector pin-1/contact-side/mating-view orientation, power domains, and block interfaces. Resolve pin conflicts and unsafe power-state combinations before implementing the affected block.

Keep one maintained machine-readable assignment source and generate its Markdown view. Component facts describe the part; project assignments describe this board's use of it. Link assignments to the component facts instead of maintaining another copy of the manufacturer's pin table.

### Adapt the reference circuit

Use the exact part's manufacturer reference circuit as the starting point. Record the selected topology and support-component values, ratings, tolerances, and calculations or rationale in the component's project-use notes or an existing design-decision record. Link that decision from the pinout rather than duplicating it.

Explain departures from the reference and check them against the badge's voltage/current budget, boot/reset, sleep/wake, and powered-off states, including leakage and back-power paths. Carry required decoupling, protection, grounding, thermal, antenna/keepout, and placement/routing constraints into the schematic and PCB work. Include unresolved assumptions in the independent review.

## 4. Independently verify critical tables

Have another agent or reviewer reopen the original PDFs and check the component facts and project assignments before schematic generation. The reviewer must establish the mapping from the source, rather than reuse the extractor's conclusions.

Check every critical pin-table row, especially power/ground/exposed pads, charger and regulator connections, connector polarity/orientation, MCU module pin-to-GPIO mapping, boot/wake/recovery pins, and voltage compatibility. Verify supporting circuit requirements and errata as well as pin names.

Record the reviewer, source revisions, reviewed record versions or hashes, findings, and unresolved items alongside the records. Resolve safety- or connectivity-critical unknowns before advancing the affected block; other reviewed blocks can proceed.

## 5. Generate and check the implementation

Build native KiCad block schematics from the reviewed records and assignments, including required support passives. Follow the [schematic guide](style_guide/schematic.md) and [routing guide](style_guide/routing.md).

Use checks independent of the generation logic:

- Export the schematic netlist and compare actual reference/pin/net endpoint sets with the reviewed contract. Check for missing or extra connections, swapped pins, accidental joins, and intentional NCs.
- Verify symbol pin numbers against the exact datasheet. Verify footprint pad numbering, pin-1 orientation, dimensions, exposed pads, and connector contact side against the manufacturer's drawing; then check schematic-to-board pin/pad/net parity.
- Run ERC after schematic changes. Once a board exists, refill zones and run DRC and connectivity checks after relevant board changes. Inspect fresh schematic exports and board views.
- Record tool versions, input revision/hashes, results, and justified exceptions. Fix mismatches at their source rather than changing expectations to match generated output.

A passing ERC/DRC result supplements the datasheet and contract checks. Keep the specification's human placement, visual review, and prototype gates.

## 6. Keep changes synchronized

For a component substitution, source revision, pin reassignment, or circuit change:

1. Update the BOM and `docs/datasheets/` inventory, affected component facts, design decisions, and project pinouts.
2. Re-review changed critical facts and all affected connections, power states, firmware mappings, and mechanical interfaces.
3. Regenerate or edit KiCad and dependent artifacts. Preserve accepted manual edits in reproducible inputs.
4. Rerun affected independent checks and inspect the connectivity diff. Run the complete release checks against one pinned revision before release.

Record what changed and which checks passed, failed, or remain pending. Keep unresolved work visible; do not leave documentation, firmware pin definitions, symbols, footprints, or generated exports silently out of step.

As each circuit is defined, record the bench tests needed to validate its assumptions and acceptance limits. When hardware is available, add the tested board/BOM and firmware revisions, setup and operating conditions, measurements, pass/fail results, and follow-up changes to the component's project-use notes or linked test record. Include relevant power/off-state and fault cases. Feed changes back through this checklist and retain the specification's prototype release gates.

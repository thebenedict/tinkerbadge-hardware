# Agent guide

Read the specification first, then follow the links for the task. Keep detailed requirements and procedures in their owning documents rather than duplicating them here.

## Start here

- [Specification](docs/spec.md): current requirements, working choices, operating journeys, power/privacy behavior, mechanical scope, and release pipeline.
- [Design BOM](docs/AI_Tinkerers_Badge_Design_BOM_Draft_2026-11-09.md): component candidates, interface/power budget, supplier evidence, and release-blocking decisions. Read its status definitions; the preliminary interface budget is not an approved pin map.

Manufacturer documents establish exact component facts; the specification, recorded decisions, and reviewed project pinouts establish design intent. Native KiCad implements that design. Resolve conflicts at their source and block affected work while critical facts remain unknown. Research and catalog listings do not approve substitutions or procurement.

## Read for the task

- **Hardware implementation or substitutions:** [Datasheet-first workflow](docs/design_workflow.md). Required sequence: source PDFs → component facts → project pinouts → independent review → KiCad → independent electrical/physical checks.
- **Schematics:** [Schematic guide](docs/style_guide/schematic.md), including the public style reference, library handling, connectivity checks, and visual review.
- **Placement/routing:** [PCB guide](docs/style_guide/routing.md). Obtain human placement approval before detailed routing and renewed approval for material placement changes. Electrical, safety, manufacturing, and mechanical requirements take precedence over appearance.
- **Documentation or copy:** [Writing guide](docs/style_guide/writing.md).
- **Alternatives, precedent, or reuse:** [Prior-art brief](docs/AI_Tinkerers_Badge_Prior_Art_2026-11-07.md), a historical research map with subsystem references and licensing checks. Use current project decisions rather than its older concept summary.
- **Public website/viewers:** [Tinker Badge Web requirements](https://github.com/thebenedict/tinkerbadge-web/blob/main/web_viewer.md). Website work belongs in that separate sibling project; hardware documentation and authoritative CAD remain here.

## Records and verification

- Follow the workflow's `docs/datasheets/` inventory, with exact-part PDFs, revisions, source URLs, and hashes. Keep it synchronized when BOM components are added, changed, or removed.
- Create `docs/components/<mpn>.md` and `docs/pinouts.md` as specified by the workflow before generating schematics. The current records and native KiCad files exist; read `docs/design/implementation_status.md` and the matching independent reviews before changing them.
- Preserve existing work. Keep BOM, component records, pinouts, firmware mappings, CAD, and derived outputs synchronized; retain accepted manual edits in reproducible inputs.
- Independently review critical source tables and pin assignments before implementation. After meaningful changes, rerun affected connectivity/ERC/DRC checks and inspect fresh exports as applicable. Release requires the specification's human visual review and prototype gates, with checks against one pinned revision.
- Report checks actually performed, tool/input versions, justified exceptions, and unresolved items. Distinguish passed, failed, and pending checks.

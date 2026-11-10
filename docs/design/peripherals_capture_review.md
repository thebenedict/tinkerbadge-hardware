# Lighting and peripheral capture evidence

Temporary review artifacts below are identified by filename only; these intermediate files are not distributed. Published source outputs and repeatable checks are linked from the [current verification record](verification.md).

9 November 2026. This is capture-author verification, separate from the [independent source review](review_peripherals.md) and the parent's final independent visual review. Native files were changed only through installed Konnect 0.12.1 MCP; KiCad exports report 10.0.8.

## Current result

- `lighting.kicad_sch`: 32 components and 86 physical endpoints.
- `peripherals.kicad_sch`: 43 components and 133 physical endpoints.
- Fresh root-netlist comparison: **75 components, 219 endpoints, five intentional NCs, PASS**. All assigned endpoints, actual net identity and pin cardinality match the revised contract. The complete project's independent checker also passes 179 components / 576 endpoints / 30 NCs.
- All 53 passive full specifications are retained in hidden `Rating` fields. Exact main-part `MPN` and `Population` values were verified from the exported native netlist. C507/C508 are `DNP`; their visible values also state DNP. Compact displayed values do not replace those full specifications.
- Fresh root ERC: **zero errors, one intentional warning**. U502 pin3 SDO/SA0 has a generic bidirectional type and is tied to +3V3 for I2C address 0x19. Archived LIS2DW12TR.pdf, DocID029682 Rev4 p9 Table2, specifies CS=1 enables I2C and pin3 SA0 is the I2C address LSB. CS2 and SA03 are tied high. The symbol type and warning are retained without a global suppression.
- The IR receiver supply after R507's 100-ohm filter has an explicit PWR_FLAG. It is a powered passive-filter output, not a separate supply source. This resolved the prior ERC power-input error.
- Official overlap checks found zero overlaps and zero unresolved symbol bounds. Fresh label-inclusive PNGs were also inspected manually and the observed collisions corrected. The original near-border sheet headers are retained with explicit draft-review acceptance.

## Alps button revision

Both function switches now use user-selected Alps SKSCLBE010 / C115361, not TS-1088-AR02016. Independent source review checked the exact SKSC Drawing No.2 and KSC-701 specification. Four physical terminals per part are explicit: pins1/2 are permanently common on the button-signal net; pins3/4 are permanently common on GND. Pressing connects the pairs. A misleading standard two-ganged-switch glyph was rejected in disposable review; the exact custom common-pair graphic passed before real placement.

The replacement changes only SW401/SW402 and adds four physical endpoints. Both native values, MPN, supplier IDs, blank footprints and application-qualification fields were queried and checked from the fresh root export. Four native lighting checks passed with no unconnected pins, floating wires, overlaps or hierarchical pin issues. Other native sheets remained byte-identical during this bounded edit. The actual saved operation/readback log is `alps_capture_results.json`.

The4.85 mm terminal span is not pad pitch. Two locating holes and half-mount board-edge/enclosure geometry remain physical gates. KSC-701 p5 D11's continuous-applied-voltage caution applies as an unresolved qualification question to the open-circuit always-pulled-up wake input, separately from its continuous-press prohibition. Low current is not an exemption or proof of biased lifetime. The series-limited100 nF capacitive load likewise needs application qualification under p5 A2. Proceeding as a prototype candidate does not establish production reliability. See [independent source review](review_alps_buttons.md) and [component facts](../components/SKSCLBE010.md).

## Shared supply revision

The user explicitly approved one nominal +3V3 supply and requested that the schematic reflect it before review. Exactly 17 endpoint assignments changed: eight RGB VDD pins and nine LED decoupler supply pins. The source pin maps and all other contract endpoints are unchanged. The previous contract and exports are preserved in `revisions/peripherals_contract_2026-11-09_before_shared_3v3.json` and `baseline_3v95`.

The exact V6 source still specifies 3.3–5.3 V. The new nominal supply can fall below 3.3 V through tolerance, distribution loss and transients. That is a user-approved **prototype exception**, not guaranteed operation or a changed device rating. The sheet, [peripheral decisions](peripherals.md) and [LED record](../components/WS2812C-2020-V6.md) call for measurement during startup, low battery, Wi-Fi and full-white load transitions, with sufficient shared peak-current capacity.

Current peripheral contract SHA256: `e6c3819998aac6863f164209df1b9a84b1fa9d0e6f3a30eacf522b9cf9e4f1ec`.

## Symbols and package maturity

Nine exact-part custom symbols live in `peripheral_symbols.kicad_sym`, registered as `Tinkerbadge_Peripherals`. Searches found no exact installed symbols for these parts. All physical pin names/numbers were read back from the saved library and checked against the approved maps. An isolated disposable schematic was rendered before real placement; four early text collisions were corrected there first.

AO3400A uses the installed symbol and SOT-23 footprint after comparing actual queried pad geometry with the manufacturer's top/bottom views. The source labels G/S/D and the gate index dot but does not print numerical pins. Rotating the standard top view so pad1 matches index/G makes pad2 adjacent S and pad3 opposite D without mirroring. **1G/2S/3D remains explicitly derived**, not a quoted numeric manufacturer table. TPS2553 DBV and TCA9534 PW16 symbol-pad ordering were likewise checked. Standard land patterns still need manufacturing/prototype review.

Nineteen physical footprints are deliberately blank: D401–D409, SW401/SW402, U501–U504, AE501, D501, J501/J502. Exact LED, switch, sensor and IR package land patterns are not yet qualified. JST and SAO mating orientation/cable continuity are release gates. AE501 is a PCB antenna feature requiring layout and loaded tuning. Do not generate an assembly package until these gates, final passive MPNs and `Population` handling are closed.

## Evidence

Machine-readable source hashes, actual custom pins, assigned footprint pad geometry, current native-file hashes, ERC interpretation, blank-footprint inventory and artifact paths are in [peripherals_capture_review.json](peripherals_capture_review.json). All 18 active archived peripheral source hashes pass; the replaced Xunpu source is retained separately in revision history. The exported-root endpoint checker and metadata checker read the netlist, not the native schematic source.

Current renders and PDFs: `lighting.png`, `lighting.pdf`, `peripherals.png`, `peripherals.pdf`. Root exported-netlist evidence: `root.net`, `endpoint_check.json`, `full_root_endpoint_check.json`, `metadata_check.json`, `root_erc.json`.

No board placement/routing, DRC, physical fit, manufacturing, procurement, antenna tuning, runtime or bench qualification is claimed.

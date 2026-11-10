# Independent final lighting and peripheral capture review

9 November 2026. **PASS for development schematic capture**, including the selected Alps prototype candidate. No native correction requested. Physical/manufacturing and application-reliability gates remain open.

Independently exported the actual current root through Konnect. The peripheral contract matches **75 components, 219 physical endpoints and five intentional NCs**. The complete review export also passes **179 components, 576 endpoints and 30 NCs**. All four connection validators were independently run on each of lighting and peripheral sheets, with zero findings. The explicit-property checker passes. Comparing the prior shared-3.3 V root export found every non-switch endpoint unchanged.

SW401 and SW402 use the corrected `Tinkerbadge_Peripherals:SKSCLBE010`, not the rejected ganged-switch symbol. Saved export confirms all four physical leads on each part: 1/2 to the respective button signal, 3/4 to GND. Exact MPN and visible value, C115361 supplier identifiers, fitted population, source URL, contract field, blank footprint and prototype application warning all match. The same-side pins are joined by actual wires, so connectivity does not rely on decorative internal symbol lines.

Inspected both complete fresh PNGs. The eight-pixel chain, separate status LED dies and both four-terminal button groups are clear. The sensor, NFC, expander, accessory power and IR groups remain readable with visible junctions, intentional NCs and DNP tuning capacitors. Shared-rail and switch application cautions are present. The existing top headings touch the inner border; this is the previously accepted cosmetic draft exception, with no circuitry obscured.

The author's fresh root ERC artifact contains zero errors and one previously justified LIS2DW12 SA0 address-strap warning. This review did not suppress it. Final pinned root ERC and delivery-export checks belong to the integration owner.

Current lighting native SHA-256: `c69b283fcddaf4dda80db415f7d009a5bf72508bbac4eab0f21db83e3aabc796`.
Current peripheral native SHA-256: `c3997e92e5deee52c05a2b8e3f9453e36f269b825047058acbd8ac74b381f77e`.
Current contract SHA-256: `e6c3819998aac6863f164209df1b9a84b1fa9d0e6f3a30eacf522b9cf9e4f1ec`.

The [Alps source review](review_alps_buttons.md) governs its four-terminal map and the unresolved continuous-voltage/capacitive-load cautions. The footprint is deliberately unassigned; locating holes, terminal geometry, board-edge fit and case actuation still need physical acceptance. LED undervoltage behavior, other footprints/interfaces, exact passive procurement, antenna tuning and storage/wake/system tests remain separate gates. No fresh live-GUI opening, PCB validation or manufacturing readiness is claimed here.

Artifact hashes, full switch readback, validator outputs and endpoint comparisons are in `peripherals_independent_capture_review.json`.

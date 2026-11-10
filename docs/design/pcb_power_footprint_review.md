# Power footprint review

Temporary review artifacts below are identified by filename only; these intermediate files are not distributed. Published source outputs and repeatable checks are linked from the [current verification record](verification.md).

9 November 2026. Independent power footprint reviewer. KiCad 10.0.8 and its installed footprint library were inspected against the archived manufacturer drawings. This review covers U101–U105, U107, Q101–Q103, D101–D102 and J101. No schematic, board or library was changed by this reviewer.

The source/footprint SHA256 manifest, exact U103 pad requirements and USB shell convention are in `review.json`. Source revisions and URLs remain in `docs/datasheets/power_inventory.json`. Actual package/land-pattern image pixels were inspected, including bottom-to-component-side conversion. Fresh PDF renders are under `pcb_power_review`; previously rendered originals are under `docs/datasheets/review_images/` and `peripheral_views/`.

## Placement decisions

| Reference | Exact part | Footprint decision |
|---|---|---|
| U101 | TPS2121RUXR | Accept `Package_DFN_QFN:Texas_VQFN-HR-12_2x2.5mm_P0.5mm`. |
| U102 | BQ24074RGTR | Accept `Package_DFN_QFN:VQFN-16-1EP_3x3mm_P0.5mm_EP1.68x1.68mm`; stencil/thermal implementation remains an assembly check. |
| U103 | TPS63802DLAR | Custom DLA0010A required. Ten asymmetric pads; no pin 11. Requirements below. |
| U104 | TPS22918DBVR | Accept `Package_TO_SOT_SMD:SOT-23-6`. |
| U105 | TPD4E05U06DQAR | Hold footprint association pending DQA0010A/B land-pattern qualification. Generic installed USON10 is not accepted unchanged. |
| U107 | TMUX1511PWR | Accept `Package_SO:TSSOP-14_4.4x5mm_P0.65mm`. |
| Q101–Q103 | AO3400A | Accept `Package_TO_SOT_SMD:SOT-23`, with 1=G, 2=S, 3=D. |
| D101–D102 | SMF6.0A | `Diode_SMD:D_SMF` has source-matching lands. Enlarge courtyard to accommodate maximum body plus desired clearance. Do not use `D_SOD-123F`. |
| J101 | USB4105-GF-A | Accept source geometry of `Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal`; retain four native `SH` pads. S1–S4 are documentation aliases only. Copper/drills match archived drawing A1. |

Acceptance is for placement using these land patterns. Check placed pad/net parity, DRC, paste/mask process, source current/thermal behavior and human placement approval separately before release/routing.

## Findings by part

### U101: TPS2121RUXR

TI SLVSEA3F, RUX0012A drawing 4224010/A (11/2017), PDF pp38–40, and bottom-view pinout p4. Body 2.0 × 2.5 mm, height ≤1.0 mm. Installed footprint has exactly pads 1–12, with pin1 at upper-left in component view. Power pads 1/2 at x=-0.675, y=-0.35/+0.35 and 8/7 at x=+0.675, y=-0.35/+0.35 are 1.05 × 0.4 mm. Pads3–6 run left-to-right at y=+1.15; pads12–9 run left-to-right at y=-1.15, 0.5 mm pitch, 0.2 × 0.6 mm lands. No extra ground/thermal pad is present. Copper and stencil extents match TI; power-pad corner radius is 0.1 rather than example R0.05, a small land-shape difference. Use the non-thermal-via version until via/paste manufacturing is defined.

The footprint references a STEP file that is absent from the installed 3D library. A model association string is not proof of a usable model.

### U102: BQ24074RGTR

TI SLUS810N; RGT0016C, 4222419/E (07/2025), PDF pp52–54. Package 3 × 3 mm, 0.5 mm pitch, exposed pad 1.68 ±0.07 mm square, height ≤1 mm. Source bottom-view numbering converts to pin1 upper-left, pins1–4 down left, 5–8 left-to-right along bottom, 9–12 up right, 13–16 right-to-left along top. Installed EP is pad17 and must join VSS/GND, including pin8.

Installed perimeter pads are 0.825 × 0.25 mm centered ±1.4625 mm normal to each edge, versus TI's example 0.6 × 0.24 at ±1.4. The IPC-style enlargement retains the correct lead overlap and clearance. EP copper is exactly 1.68 square. Its four rounded 0.68-square paste windows provide approximately 62% actual area coverage, versus TI's example 85%; qualify stencil solder coverage/voiding and thermal copper before fabrication. Do not silently substitute a generic different-EP QFN. The associated exact STEP file is absent locally.

### U103: TPS63802DLAR

TI SLVSEU9D, DLA0010A drawing 4223750/D (03/2019), PDF pp35–37. Body is 2 mm in X by 3 mm in Y in the source orientation, despite the common 3 × 2 naming. Maximum body is 2.1 × 3.1 mm; maximum height 1 mm. Pin1 is upper-left in component view.

No compatible installed DLA0010A footprint/model was found. `Texas_S-PVSON-N10` is a different 3 × 3 mm DRC package with EP and must not be used. Build these source lands, all dimensions in mm:

| Pads | Centers | Land size |
|---|---|---|
| 1,2,3,4,5 | x=-0.9; y=-1,-0.5,0,0.5,1 | 0.6 × 0.25 |
| 10,9,7,6 | x=0.75; y=-1,-0.5,0.5,1 | 0.9 × 0.25 |
| 8 | (0.55,0) | 1.3 × 0.25 |

Use R0.05 corners. Pad8 copper/mask is continuous, but its paste is split into two 0.55 × 0.25 windows centered (0.175,0) and (0.925,0). Omit default F.Paste on pad8. TI's p37 stencil example uses 0.1 mm thickness and states 83% paste coverage for pad8. Other pad apertures match their lands. No pin11 or separate EP.

Suggested project courtyard is x±1.45, y±1.8, derived from maximum body/land plus 0.25 mm. This is an engineering choice, not a TI dimension. Nominal Fab outline is x±1, y±1.5. Keep silk outside mask openings and retain upper-left pin1 identification. A clearance-envelope model should include the maximum 2.1 × 3.1 × 1.0 mm envelope; label nominal-only visualization accordingly.

### U104: TPS22918DBVR

TI SLVSD76C, DBV0006A 4214840/G (08/2024), pp27–29 plus pinout p3. Six pins, no EP, 0.95 mm pitch; body 1.45–1.75 × 2.75–3.05, lead span 2.6–3.0, height ≤1.45 mm. Standard SOT-23-6 has correct top-view numbering: 1–3 down left and 4–6 up right. Lands 1.325 × 0.6 at x±1.1375 retain the leads; TI example is 1.1 × 0.6 at x±1.3. This is a compatible IPC-style alternate. STEP association resolves locally.

### U105: TPD4E05U06DQAR

TI SLVSBO7O includes two DQA constructions: DQA0010A, 4220328/A (12/2015), pp28–30, and DQA0010B, 4230307/A (12/2023), pp31–33. Both share 1 × 2.5 mm body, 0.5 mm pitch, ≤0.55 mm height, and pins1–5 down left/6–10 up right in component view. DQA0010A has enlarged separate ground contacts3/8; DQA0010B has an exposed central grounded crossbar joining3/8. This is not a new numbered pin11, but it materially affects copper/paste beneath the package.

The installed `Package_SON:USON-10_2.5x1.0mm_P0.5mm` cites TPD4E02B04. Its identical 0.55 × 0.30 pads at x±0.385 do not reproduce this device's source pattern. Source A uses 0.565 mm pad length at x±0.4175, eight 0.2 mm-wide signal lands and two 0.4 mm-wide ground lands. Its ground paste apertures are 0.565 × 0.36. Source B instead specifies a connected, shaped ground land and different paste.

The generic DQAR ordering information does not constrain the drawing suffix. The archived PDF and focused primary-source searches did not provide an explicit common-footprint/interchangeability approval. Therefore a custom source-A footprint can only be accepted as variant-qualified until the supplied package is tied to that drawing or TI/assembly evidence validates a common land pattern. Do not infer union-pad compatibility. Leave the generic DQAR association open and reserve its placement area.

Primary follow-up sources: [TI exact-part page](https://www.ti.com/product/TPD4E05U06/part-details/TPD4E05U06DQAR), [TI datasheet](https://www.ti.com/lit/ds/symlink/tpd4e05u06.pdf). No external inquiry was sent.

### U107: TMUX1511PWR

TI SCDS390B, PW0014A 4220202/B (12/2023), pp42–44, pinout p3. Body 4.3–4.5 × 4.9–5.1, pitch0.65, span6.2–6.6, height≤1.2 mm, no EP. Standard TSSOP14 pin1 upper-left/pin7 lower-left/pin8 lower-right/pin14 upper-right agrees. Lands1.475 ×0.4 at x±2.8625 have adequate lead overlap; TI example is1.5 ×0.45 at x±2.9. STEP association exists.

### Q101–Q103: AO3400A

AOS Rev3.1 (July2023) p1 top/bottom diagrams and PO-00001 VersionN package drawing p1 were inspected. Dot-adjacent G is conventional pin1, S pin2, isolated D pin3. Neither source prints numeric pin identifiers; the mapping is established geometrically, not by pretending a numbered table exists. The standard footprint keeps pin1 upper-left, pin2 lower-left and pin3 right-center, correct after rotation of AOS's top view.

Package pitch0.95/1.90 mm, body nominal2.9 ×1.6, span2.6–3.0, height≤1.25. Standard lands1.475 ×0.6 at x±0.9375 accommodate the source's 0.30–0.50-wide leads and toe span. These differ from AOS's 0.8-square example at 2.4 mm row spacing but are a compatible alternate. STEP exists; this is not blanket acceptance of other MOSFET pinouts.

### D101–D102: SMF6.0A

Littelfuse SMF series Rev03/04/13, pp5–6. Source calls the package SOD-123; the component record's SOD-123FL name does not determine compatibility. Source body2.50–2.90 ×1.50–2.00, overall lead span3.40–3.90, lead width0.70–1.20, height0.95–1.10 mm. Color band identifies cathode. Project convention1=K,2=A matches D_SMF's left pad1 and cathode marking.

`D_SMF` lands exactly match the example:1.3 ×1.4, centers±1.45, inner gap1.6 mm. Existing courtyard is x±2.35,y±1.15; use y±1.25 for 0.25 clearance beyond maximum2.0mm body. Its Fab body is nominal2.8 ×1.8. `D_SOD-123F` is rejected unchanged:1.1-square pads miss the source's max1.2-wide terminal and have no toe extension at max3.9 span. D_SMF's STEP association exists but is generic and not certified as exact Littelfuse geometry.

### J101: USB4105-GF-A

Archived GCT drawing A1, released24 October2019, p1 actual component-side PCB layout and mating/bottom views were inspected. It gives12 physical solder lands for16 logical contacts: the four VBUS/GND pairs share lands. KiCad represents both logical numbers as overlapping identical pads; preserve them because the project contract includes all16. From left: A1/B12, A4/B9, B8,A5,B7,A6,A7,B6,A8,B5, B4/A9, B1/A12. Signal pitch0.5 mm; signal lands0.3 ×1.15, paired lands0.6 ×1.15.

With the installed origin, signal centers are y=-3.68, locating holesØ0.65 at (±2.89,-2.605), rear slots at (±4.32,-3.105) with drill0.6 ×1.7 and pad1.0 ×2.1; front slots at (±4.32,1.075) with drill0.6 ×1.4 and pad1.0 ×1.8. Board-edge/front reference is y=3.675. These match drawing A1 after a rigid origin shift.

The native J101 symbol has one electrical pin `SH` on GND, and the contract maps four physical-anchor aliases S1–S4 to that pin. Therefore all four native footprint anchors must retain pad number `SH`. The earlier review incorrectly treated documentation aliases as native pad identifiers; that recommendation is superseded. Physical positions remain rear-left=S1, front-left=S2, rear-right=S3 and front-right=S4 for documentation only. The manufacturer does not number these anchors. Preserve all four SH pad primitives, the logical contact duplicates and mechanical holes. The STEP exists; cable/enclosure mating clearance, actual assembled height and latest GCT drawing reconciliation remain separate mechanical checks. Archived source max overall width is9.58mm and height3.31mm; use these rather than approximate body artwork for clearance.

## Open checks

- Generated custom U103 and cloned USB/SMF native geometry is verified below. Schematic-to-board pad/net parity remains open.
- Resolve U105 package/land pattern. Do not hide it in a generic USON assignment.
- Qualify BQ24074 paste/thermal paths and all assembly mask/paste/via choices.
- Missing U101/U102 3D models and full 3D dimensional acceptance remain open. Existing STEP files were checked for resolution and identity association, not fully certified geometrically.
- Exact inductors, battery/connector/polarity, charge safety and other main-task blockers remain outside this footprint review.

## Generated custom footprint verification

Native KiCad 10.0.8 `FootprintLoad` successfully read all three generated files. Assertions checked actual pad identifiers, positions, sizes, layers, radii and drills. Re-inspected original TI land/stencil, Littelfuse package and GCT A1 drawing pixels. Exported native SVGs and inspected renders. Exact snapshot hashes, native pad data and checks are in `custom_verification.json`; no production CAD was edited.

- **TPS63802_DLA0010A_Reviewed:** Pass copper, stencil, pad numbering, courtyard and maximum clearance envelope. Exactly pads1–10 with R0.05; pad8 has no default paste, and its two unnumbered paste-only windows match source. Courtyard is ±1.45×±1.8. WRL units convert to2.1×3.1×1.0mm with z=0..1.0. The early unreviewed `TPS63802_DLA0010A` candidate must remain unused.
- **U103 cleanup resolved:** During review, the parent corrected the drawing identifier to `4223750/D` and removed the close-clearance silk rectangle and partly obscured pin-1 dot. Latest snapshot SHA256 begins `8cc7eabd`. Pin 1 is now indicated only by the F.Fab chamfer. Add a board-level visible pin-1 silk mark at placement with adequate mask/body clearance if practical.
- **USB4105-GF-A_ProjectShells:** Pass against archived A1. Native geometry and pad numbers match the accepted installed footprint. All four shell anchors repeat native pad `SH`, matching J101 symbol pin `SH`. Documentation aliases S1 rear-left, S2 front-left, S3 rear-right and S4 front-right describe positions only. All 16 logical contacts, 12 contact lands, 4 plated slots and 2 NPTH holes survive. Confirm actual placed net parity and source-current/mechanical gates separately.
- **SMF6.0A:** Pass. Lands retain accepted centers±1.45 and1.3×1.4mm size. Cathode/pad1 is left. Courtyard is enlarged to±2.35×±1.25mm. Header/value/description still use generic D_SMF/Vishay metadata, a cleanup item rather than a native load/pad failure. Its exact Littelfuse 3D fit remains unqualified.

### USB native pin normalization correction

The earlier S1–S4 native-pad recommendation was incorrect. Source facts name four unnumbered physical anchors for review, but `power_contract.json` explicitly maps each to the single native symbol pin `SH`. `tools/record_power_verification.py` applies this mapping when producing source-to-symbol records. KiCad PCB synchronization does not read that project alias map. All four footprint shell pad primitives must therefore use `SH`, not S1–S4. This distinction is now asserted in the independent native footprint checker.

After the parent restored `SH`, read-only KiCad 10.0.8 verification passed: four SH primitives, no S1–S4 native pad numbers, unchanged anchor positions/drills/layers, and an exact native-pad comparison with the source-reviewed installed footprint. A fresh root schematic netlist has 17 J101 logical nodes: 16 USB contacts plus one SH node on GND. Evidence and hashes are in `usb_shell_native_verification.json`. No electrical nets or production CAD were changed by this reviewer. Board synchronization and all four placed pad nets remain to be checked separately.

The netlist export also emitted an annotation warning. The shell-specific pass above is not a whole-project annotation/ERC pass.

# One-sided assembly assessment

9 November 2026. Feasibility assessment of the unrouted 110 × 100 mm badge. No CAD changes or one-sided placement trial were made.

## Recommendation

**One-sided SMT assembly is a realistic design target at the present board size, but the current placement is two-sided.** Prefer a front-side SMT layout, keeping the display and battery installation as later mechanical operations. First try arranging the power and display-support blocks in the exposed perimeter; only use the space beneath the glass after qualifying component height and display support.

The present area evidence does not justify declaring a larger board necessary. It also does not prove a complete one-sided layout fits: nine electrical footprints, routing, flex access, optics, supports and connector mating remain unresolved. Keep the present two-sided layout as the lower-redesign-risk prototype option and obtain assembly quotes before choosing.

## What “one-sided” means here

- **One-sided SMT/reflow:** all surface-mount parts are placed and reflowed on the front. Back copper, vias, exposed test/dock pads, a mechanically attached battery and a later-installed through-hole socket can remain.
- **All components physically on one face:** a stronger requirement that conflicts with the current rear battery and SAO plan and changes the wearable enclosure.
- **Single-sided copper PCB:** a different proposal. Retain the specified four copper layers and ground-reference strategy; one-sided component loading does not require reducing copper layers.

Single-side SMT still has later display/FPC, battery, enclosure and possibly through-hole soldering steps. It does not imply a one-operation finished badge.

## Actual geometry and area

Read-only KiCad 10.0.8 inspection of `tinkerbadge.kicad_pcb`, SHA256 `322dc5d129db733813ff2d9dc0912e813fc9aa27043376b74c5deea2b9d668fa`, confirms 170 electrical footprints: 46 front, 124 rear, including six rear test-point footprints. There are four copper layers, nominal 1.6 mm thickness and no tracks. These footprint counts are not an assembly BOM: C507/C508 are custom-field DNP parts and test points are not fitted components.

The board runs x=100–210, y=100–200 mm. Glass occupies x=109.35–202.65, y=123.05–177.95 mm.

| Exposed region | Gross dimensions | Gross area |
|---|---|---|
| Above glass | 110 × 23.05 mm | 2,535.5 mm² |
| Below glass | 110 × 22.05 mm | 2,425.5 mm² |
| Left, alongside glass | 9.35 × 54.9 mm | 513.3 mm² |
| Right, alongside glass | 7.35 × 54.9 mm | 403.5 mm² |

The glass covers 5,122.2 mm² of the 11,000 mm² PCB. Outside it are 5,877.8 mm² gross, or 5,367.8 mm² after subtracting the current 30 × 17 mm NFC reservation. These are not free-placement areas: subtract the radio, LEDs and their light-guide/baffle allowances, optical sensors, buttons, USB, holes, supports, cables and edge/assembly margins.

As a coarse density check, the existing rear electrical courtyard bounding boxes sum to about 936 mm². Front electrical courtyards excluding U201 sum to about 407 mm². U201 is excluded because its courtyard includes a large antenna exclusion rectangle extending off the PCB; it is not ordinary package area. These sums exclude unresolved footprints and do not account for routing or optimal packing. They nevertheless support trying a perimeter layout rather than assuming 170 references require two assembly faces.

The top strip already carries the radio, role lights and optical devices. The bottom strip includes affinity lights and the NFC reservation at x=176–206, y=181–198. The narrow side strips have USB/buttons on the left and flex/connector/mounting constraints on the right. The requested LED update retains the NFC reservation: affinity centers x=108/124/140/156/172 at y=190; role centers x=144/172.5/201 at y=114. The new rightmost role LED at (201,114) is only 4.47 mm center-to-center from the ambient sensor at (205,112). Reserve an optical barrier/window and verify LED-induced sensor bias; physical clearance alone does not establish optical isolation. These changes do not alter component sides or establish a one-sided layout.

## The 1 mm display gap is the main height constraint

The glass underside is currently proposed at only 1.0 mm above the front PCB surface; glass thickness is up to 0.92 mm. That gap is not a general electronics cavity.

- TCA9534PWR and TMUX1511PWR TSSOP packages are up to 1.2 mm high.
- AO3400A SOT-23 is up to 1.25 mm. SMF6.0A reaches 1.10 mm.
- TPS63802 and BQ24074 can reach 1.0 mm, leaving no clearance at the proposed gap before assembly/support tolerances.
- Generic passive MPNs are not finalized, so footprint size alone cannot establish their maximum installed height.
- L101 and L301 have only 6 × 6 and 5 × 5 mm XY reservations. Neither has an accepted part or height. Do not assume either fits under the glass.

Keep such parts in exposed regions, or define a larger support gap from maximum installed height plus solder, PCB/glass warp, support tolerances, insulation and shock allowance. Do not promise a specific larger gap before selecting the inductors. Low-profile passives beneath the panel are possible after checking their exact heights, non-contact clearance, support/adhesive zones, heat and service access.

Tall front parts already exist outside the glass: USB is up to 3.31 mm and the IR receiver up to 4.3 mm. Raising the display may fit within an existing front-cover envelope, but the enclosure has not been qualified. A nominal 3D body model cannot certify this.

## Battery, connectors and production sequence

- Keep the rear 35 × 55 × 7 mm battery allowance as a later mechanical installation. It does not force rear SMT. A front connector would need an approved cable path, polarity, insulation and strain relief; the pack and connector are unselected.
- A front-side Qwiic connector could still face an edge. Its 2.9 mm height and actual mating-plug access need checking. The FPC connector and fold/contact orientation remain unresolved; front-only SMT may simplify or worsen flex access depending on the approved fold.
- A rear through-hole SAO socket can be installed after front SMT. Its 8.5 mm body and 3.2 mm tails still need the proper soldering/mating process. With 1.6 mm PCB, nominal tails extend about 1.6 mm onto the front, so keep them outside the 1 mm glass gap. The current reservation above the glass avoids that particular conflict.
- USB includes plated shell slots. Qualify its soldering process too; do not count “one reflow” as proof that every through-hole joint is complete.
- Rear dock contact pads need not require rear components if spring contacts live in the dock. J103 mechanics are not yet selected, so this is an option, not the implemented interface.
- Assemble/reflow, inspect and electrically test before attaching glass and battery. Preserve test access and a practical repair sequence.

Putting all SMT on the rear would retain the front optical/user-interface problem. Reverse-mount LEDs, light pipes through PCB openings or a front daughterboard introduce substitutions, optical work or a second assembly. They are less direct than front-only SMT with the present parts.

## Cost and decision gate

Single-side SMT can remove the second print/place/reflow handling sequence. Actual savings depend on quantity, assembler setup, panelization, yield, through-hole labor and test. There is no quote or approved production quantity here. Larger PCB area, extra display spacers, special light pipes or a daughterboard could consume the saving. Keep the four-layer stack; do not trade away RF/return-path quality merely to call the assembly one-sided.

Before committing, resolve the nine existing references: U105, J102, J103, J104, L101, J301, L301, AE501 and J502. Then make a front-only placement trial with actual height envelopes, compact power loops and routing escapes, and compare like-for-like assembly quotes. Obtain placement approval before routing. R120 continues to hold charger CE high; onboard charging remains disabled.

## Evidence and verification

Sources: [placement review](pcb_placement_review.md), [mechanical review](pcb_mechanical_placement_review.md), [power-footprint review](pcb_power_footprint_review.md), [TCA9534](../components/TCA9534PWR.md), [AO3400A](../components/AO3400A.md), [SAO socket](../components/SFH11-NBPC-D03-ST-BK.md), [FPC connector](../components/AYF532435.md), and the native board/model definitions. Original TCA9534 package-outline and AOS SOT-23 drawing images were visually checked for the cited heights. The local panel envelope confirms the proposed 1 mm support gap, not manufacturer approval of that gap.

Performed: read-only native count/geometry/courtyard-area inspection, document/source-drawing review and dimensional feasibility reasoning. No board/project/schematic/model edits, SaveBoard, routing trial, new DRC or production quote. Existing USB clearance errors, overhang silk warnings and unrouted connectivity remain as recorded in the placement review.

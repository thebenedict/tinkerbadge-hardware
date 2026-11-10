# Independent display capture review

Temporary review artifacts below are identified by filename only; these intermediate files are not distributed. Published source outputs and repeatable checks are linked from the [current verification record](verification.md).

2026-11-09. Reviewer: display source extractor, independent of the display CAD author. **PASS electrical capture against the previously independently approved source contract.** No native CAD changes were made during this review. Minor presentation findings and unchanged release gates are below.

## Checks performed

Reopened the actual `display.png` sheet, original panel PDF p6 table, original Waveshare HAT schematic p1, SSD1677 application circuit p45, and TI SN74LVC541A electrical/Ioff table p7. Freshly exported standalone and complete-root netlists through Konnect MCP. Inspected actual net membership rather than assuming matching label text proves connection.

- Standalone display: **27 parts / 95 physical endpoints / 7 intentional NC, all pass**.
- Combined root display and MCU: **44 parts / 162 endpoints / 11 intentional NC, all pass**. Cross-sheet signals actually join the intended MCU pads. Actual +3V3_EPD includes U104 output pin6, U301 VCC20, J30115/16, L3011, bypasses and QOD resistor; EPD_EN includes U1043, U20133 and R2071.
- Four independent Konnect validators: **0 floating wire ends, 0 unconnected pins, 0 shorted named nets, 0 orphans**.
- All 27 observed values match the intended part/value after conventional unit/case normalization; all shown capacitor voltage ratings agree. J301 and L301 have no footprint, as required by their unresolved physical-selection gates. Exact transistor/buffer/diode suffixes are retained.

## Critical circuits

The boost network is correct: L3012, Q3013, C3021 and D3032 share SW; Q3011 and R3021 share panel GDR2; Q3012 and R3011 share panel RESE3. C302 is a flying capacitor, not a ground bypass. Its other end joins D301 anode2 and D302 cathode1. D301 cathode1 is ground, D302 anode2 joins VGL23/C309, and D303 cathode1 joins VGH21/C307. Thus the positive rectifier and negative pump polarities match the original HAT/controller topology. The panel-specific 68 uH / 0.47 ohm values are preserved rather than substituting the controller's generic 47 uH / 2.2 ohm example.

J301 implements all 24 **panel-flex** positions. NC1/4 and unused TSCL6/TSDA7 are flagged, BS1 pin8 is grounded, pin5 is VSH2 with separate bypass, pin18 is the bypass-only local 1.8 V node, and VGH21/VGL23 retain their correct physical assignments. The generic HAT labels have not displaced the exact panel table. No implied AYF mating-footprint approval is present.

U301's five A/Y channels correctly isolate MCU MOSI/SCK/CS/DC/RESET from the panel-side nets. It is powered from the switched rail, OE1/OE2 and unused inputs are grounded, and unused outputs11–13 have NC flags. The sole always-on CS pull-up is upstream of the Ioff-rated buffer; MOSI/SCK/DC/RESET defaults are also upstream. BUSY connects only J3019, MCU8 and its grounded 100 kohm pull-down, with no always-on pull-up. Ioff is finite and its guarantee at VCC=0 is not a guarantee for arbitrary ramp/brownout behavior. BUSY must remain an MCU input with pull-up disabled while the panel is off. This is not protection against arbitrary firmware reconfiguration of BUSY as an output.

## Minor findings and remaining gates

1. Three +3V3_EPD global labels sit over continuous wires, visibly striking through their text. Reported to the CAD author; short branch-end label stubs would improve readability. No electrical fault follows from this presentation issue.
2. `display.md` and the contract's status string still say source review is pending, although `review_display.md` accepts this unchanged contract hash. This is stale status prose, not an electrical discrepancy.
3. Generic passive footprints are candidates. Contract tolerances, X7R/DC-bias requirements, L301 saturation/current/DCR, R301 pulse capability and semiconductor voltage stress still need exact-part qualification. They must not be lost when producing a procurement BOM.

Completed-root ERC, final independent visual acceptance, received panel/flex identity and continuity, effective capacitance, switching stress/current, BUSY noise margin and startup/shutdown/off-state measurements remain release gates. No PCB placement/routing or manufacturing approval follows from this review.

All reviewed hashes, actual critical endpoint sets, fields and validator results are pinned in `display_capture_review.json`. Fresh exports: `display-independent.net` and `display-independent-root.net`.

## Corrected final capture accepted

Independently inspected `display-v2.png` after the CAD author moved all three +3V3_EPD labels onto 5.08 mm vertical branch-end stubs with junctions. The wire/text overlap is resolved; no new visual issue was observed. Rechecked `display-final.net`: **27 parts / 95 endpoints / 7 NC still pass**, and a complete named-net endpoint-set comparison with the prior independent export is identical. Reran all four local validators on the corrected native sheet: again zero floating, unconnected, shorted or orphan findings. **PASS independent electrical and final visual capture review**, subject to the unchanged prototype/manufacturing gates above.

Final native SHA-256: `96f687db90923b8398399747c0764a61544d29c7c5fff235ec29ffa5dc359953`.
Final inspected PNG SHA-256: `d320f40b327b9dcc8d150c4b94c69cc905b2d49a9e23a25fb9691cc391b8b8a9`.
Final netlist SHA-256: `37e4242dd1de511200f38c74b9bd60557768cec73057c1c01ec820eaf33061e8`.

The earlier prose finding about label overlap is retained as review history, now resolved. Source-status wording and exact procurement/physical qualifications remain documentation/release items, not reasons to reject this electrical capture.

## Metadata-only annotation verified

Independently parsed the later `display-final.net`: all27 references now contain the intended MPN and Contract properties, and every applicable Rating property matches the source contract. Exact selected parts and explicit TBD support parts are distinguished. Endpoint check remains27/95/7NC PASS. `display-v3.png` is byte-identical to the visually accepted v2 PNG, so no visible correction was lost.

Current native SHA-256: `8be61344e78d548e3f3712709e7a16c372141cc4027574d05ca7bf224ffaca6a`.
Current netlist SHA-256: `1e46a0832bd87d9c9865ef00b65cf9348018a0625c7258de1bc76529fce55a8d`.
Unchanged PNG SHA-256: `d320f40b327b9dcc8d150c4b94c69cc905b2d49a9e23a25fb9691cc391b8b8a9`.

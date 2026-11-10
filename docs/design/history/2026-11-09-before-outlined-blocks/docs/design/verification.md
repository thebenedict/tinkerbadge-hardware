# Schematic verification

This is a partial historical snapshot. References to documents not preserved with this snapshot are retained as plain titles. Use the [current verification record](../../../../verification.md) for available project records; current documents may describe a later revision.

Pinned development review snapshot, 2026-11-09. Open `tinkerbadge.kicad_pro`; the complete six-page review PDF is [tinkerbadge-schematic.pdf](../../exports/tinkerbadge-schematic.pdf).

## Results

| Check | Result |
|---|---|
| Complete root endpoint comparison | PASS: 179 components, 576 physical pins, 30 explicit NCs |
| Cross-sheet connectivity | PASS: each contract net is one actual exported KiCad net; no split same-name local nets |
| Declared component properties | PASS: exact declared MPNs, values, ratings, population, library IDs and footprints |
| Root ERC | 0 errors; 1 reviewed address-strap warning below |
| Checker regression tests | PASS: 12 endpoint tests, 7 property tests and 5 Alps-button tests, including deliberate failures |
| Archived source hashes | PASS: 43 inventory entries |
| Native input stability | PASS: source files and contracts unchanged throughout exports |
| Native project opening | Shared-3.3 V project opened in KiCad 10.0.8 with all six sheets; final button revision checked through fresh native exports because the Mac locked before GUI refresh |
| Review exports | Six PDF pages and six 3500-pixel sheet PNGs |
| Footprint completion | 81 unassigned footprints remain; listed in property-check.json |
| PCB checks | Not run: the badge PCB is an empty project placeholder |

Native capture used Konnect MCP 0.12.1; exports used KiCad 10.0.8. No native CAD file was directly text-edited. KiCad displays its older-format conversion notice for the MCP-produced files; the files load and export correctly. Opening for inspection did not save a conversion.

Exact file hashes and check summaries are in [manifest.json](../../exports/manifest.json). This pins the native sheets, project libraries, reviewed contracts, verification code, source inventories and delivered exports. The export-time native-inputs.json records stable inputs before and after generation. A subsequent edit requires fresh checks and exports.

## Reviewed ERC warning

U502 pin 3, SDO/SA0, has a generic bidirectional electrical type and is tied to +3V3 from U103 VOUT. The LIS2DW12 is configured for I²C: CS pin 2 is high and SA0 pin 3 selects address 0x19. ST DocID029682 Rev 4, page 9, Table 2 and footnote 1 establish this mode and address input. The warning is retained in [erc.json](../../exports/erc.json), with no global suppression or weakened symbol type.

## Independent evidence

- Power source revision and native capture.
- Processor source review and native capture.
- Display source review, native capture and package correspondence.
- Peripheral source review, Alps button amendment, capture evidence and independent final capture.
- Endpoint checker review and property checker review.

The endpoint checker reads the independently exported KiCad netlist, not native source. It compares every physical reference/pin/net assignment and the actual identity of nets across sheets. It detects missing/extra components, missing/extra/duplicated pins, wrong connections, merged or split nets, and absent NC markers. It does not validate values or analog behavior.

The separate property checker compares only explicitly declared fields. Full hidden support-component specifications remain in the native files alongside readable displayed values. Power's trace, visible values and specifications also received 235 independent field comparisons. Generic passives, unassigned footprints and missing procurement decisions are not converted to passes by either checker.

Fresh sheet renders were inspected for legibility, field/wire collisions, labels, NC markers and block flow. The overview shows the actual single-rail decision; power and lighting notes preserve its bench-test gate. Near-border headings on some child sheets are accepted as cosmetic for this draft. The final lighting revision identifies the selected Alps buttons. The PDF is derived from the same stable native snapshot.

## Decisions and remaining gates

The implementation status owns current decisions and release gates. In particular:

- All eight WS2812C-2020-V6 LEDs share nominal +3V3 with logic. Regulator tolerance and transients can fall below the LED's 3.3 V minimum. This is the user-approved first-prototype experiment; startup, low battery, radio/display activity, load steps and temperature/lot tests remain mandatory.
- The two-wire protected LiPo interface is retained; its exact pack, cable polarity and connector remain to be qualified. J104 optional cell-contact thermistor is unpopulated. Fitted R120 keeps onboard charging disabled until compatible hardware temperature limits and charging behavior are qualified.
- SW401/SW402 use the selected Alps SKSCLBE010 side-actuated switches as prototype candidates. KSC-701 page 5 D11 cautions against continuously applied voltage, while the badge has permanent pull-ups. Manufacturer clarification or biased-life qualification, exact footprint acceptance and enclosure actuation fit remain open; see the component record.
- Finish unassigned footprints, exact passive and inductor choices, display flex mating, antenna/layout, power/thermal/fault tests and human schematic/placement review.
- DNP options use explicit values and `Populate`/`Population` metadata because native DNP control is unavailable in the installed MCP. Reconcile those fields before generating any assembly BOM.

No main-board placement, routing, manufacturing output or production qualification is included.

#!/usr/bin/env python3
"""Pin completed native exports and checks. Does not edit CAD or run reviews."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
ep=read('exports/endpoint-check.json');pr=read('exports/property-check.json');erc=read('exports/erc.json');snap=read('exports/native-inputs.json')
assert ep['status']==pr['status']=='PASS'
graphics=read('exports/graphics-only-check.json')
assert graphics['status']=='PASS' and graphics['after_sha256']==sha('exports/tinkerbadge.net')
assert ep['netlist_sha256']==pr['netlist_sha256']==sha('exports/tinkerbadge.net')
assert snap['unchanged_during_export']
for p,h in snap['sha256'].items():assert sha(p)==h,('Snapshot changed',p)
for b,h in ep['contract_sha256'].items():assert sha('docs/design/'+b+'_contract.json')==h
assert not [r for r in erc if r['severity']=='error']
assert len(erc)==1 and erc[0]['rule']=='pin_to_pin' and 'U502 Pin 3 [SDO/SA0' in erc[0]['description']
for f,n in [('endpoint-checker-tests.txt',12),('property-checker-tests.txt',7),('alps-button-tests.txt',5)]:
 t=(ROOT/'exports'/f).read_text();assert 'Ran '+str(n)+' tests' in t and '\nOK' in t
pdf_text=(ROOT/'exports/pdf-extracted-text.txt').read_text()
assert pdf_text.count('=== PDF PAGE ')==6
assert 'VLED_3V9' not in (ROOT/'exports/tinkerbadge.net').read_text()
n=ep['expected_components'];pins=ep['expected_endpoints'];nc=ep['intentional_nc_endpoints'];blanks=len(pr['unassigned_footprints'])
source_checks=[]
for inv in ROOT.glob('docs/datasheets/*inventory.json'):
 raw=json.loads(inv.read_text());rows=raw if isinstance(raw,list) else raw.get('documents',raw.get('sources',[]))
 for row in rows:
  name=row.get('path') or row.get('filename') or row.get('file');path=name if name.startswith('docs/') else 'docs/datasheets/'+name
  assert sha(path)==row['sha256'],('Source hash mismatch',path)
  source_checks.append({'inventory':str(inv.relative_to(ROOT)),'path':path,'sha256':row['sha256'],'status':'PASS'})
(ROOT/'exports/source-check.json').write_text(json.dumps({'status':'PASS','documents':source_checks},indent=2)+'\n')
now=datetime.now(timezone.utc).isoformat()
content=f'''# Schematic verification

Pinned development review snapshot, {now[:10]}. Open `tinkerbadge.kicad_pro`; the complete six-page review PDF is [tinkerbadge-schematic.pdf](../../exports/tinkerbadge-schematic.pdf).

## Results

| Check | Result |
|---|---|
| Complete root endpoint comparison | PASS: {n} components, {pins} physical pins, {nc} explicit NCs |
| Cross-sheet connectivity | PASS: each contract net is one actual exported KiCad net; no split same-name local nets |
| Declared component properties | PASS: exact declared MPNs, values, ratings, population, library IDs and footprints |
| Root ERC | 0 errors; 1 reviewed address-strap warning below |
| Checker regression tests | PASS: 12 endpoint tests, 7 property tests and 5 Alps-button tests, including deliberate failures |
| Archived source hashes | PASS: {len(source_checks)} inventory entries |
| Native input stability | PASS: source files and contracts unchanged throughout exports |
| Native project opening | Shared-3.3 V hierarchy opened in KiCad 10.0.8; this graphics revision was reloaded by KiCad for fresh netlist, ERC, PDF and PNG exports |
| Graphics-only comparison | PASS: all 179 component records, 141 named nets and 32 library physical-pin definitions unchanged |
| Review exports | Six PDF pages and six 3500-pixel sheet PNGs |
| Footprint completion | {blanks} unassigned footprints remain; listed in property-check.json |
| PCB checks | Outside this schematic snapshot; PCB preparation proceeds separately |

Initial electrical capture used Konnect MCP 0.12.1. The user-approved outlined-block revision used a bounded, structure-aware native-file transformation, with untouched source sections preserved and complete exported electrical equivalence checked. Exports used KiCad 10.0.8 through Konnect. Older-format files load and export correctly; no GUI conversion was saved. See the [graphics revision review](outlined_blocks_review.md) for scope and independent visual evidence.

Exact file hashes and check summaries are in [manifest.json](../../exports/manifest.json). This pins the native sheets, project libraries, reviewed contracts, verification code, source inventories and delivered exports. The export-time [native-inputs.json](../../exports/native-inputs.json) records stable inputs before and after generation. A subsequent edit requires fresh checks and exports.

## Reviewed ERC warning

U502 pin 3, SDO/SA0, has a generic bidirectional electrical type and is tied to +3V3 from U103 VOUT. The LIS2DW12 is configured for I²C: CS pin 2 is high and SA0 pin 3 selects address 0x19. ST DocID029682 Rev 4, page 9, Table 2 and footnote 1 establish this mode and address input. The warning is retained in [erc.json](../../exports/erc.json), with no global suppression or weakened symbol type.

## Independent evidence

- [Power source revision](review_power_single_3v3.md) and [native capture](power_capture_review.md).
- [Processor source review](review_mcu.md) and [native capture](mcu_verification.md).
- [Display source review](review_display.md), [native capture](display_capture_review.md) and [package correspondence](../components/display_library_acceptance.md).
- [Peripheral source review](review_peripherals.md), [Alps button amendment](review_alps_buttons.md), [capture evidence](peripherals_capture_review.md) and [independent final capture](peripherals_independent_capture_review.md).
- [Endpoint checker review](contract_checker_review.md) and [property checker review](property_checker_review.md).
- [Outlined-block revision](outlined_blocks_review.md), including independent visual reviews of all five circuit sheets and full before/after electrical comparison.

The endpoint checker reads the independently exported KiCad netlist, not native source. It compares every physical reference/pin/net assignment and the actual identity of nets across sheets. It detects missing/extra components, missing/extra/duplicated pins, wrong connections, merged or split nets, and absent NC markers. It does not validate values or analog behavior.

The separate property checker compares only explicitly declared fields. Full hidden support-component specifications remain in the native files alongside readable displayed values. Power's trace, visible values and specifications also received 235 independent field comparisons. Generic passives, unassigned footprints and missing procurement decisions are not converted to passes by either checker.

Fresh sheet renders were inspected for legibility, field/wire collisions, labels, NC markers and block flow. The overview shows the actual single-rail decision; power and lighting notes preserve its bench-test gate. The five circuit sheets now contain 24 labeled Transit-style outlined functional groups. Titles, field positions and nearby branch geometry were adjusted for clearance and checked against the original electrical circuit. The final lighting revision identifies the selected Alps buttons. The PDF is derived from the same stable native snapshot.

## Decisions and remaining gates

The [implementation status](implementation_status.md) owns current decisions and release gates. In particular:

- All eight WS2812C-2020-V6 LEDs share nominal +3V3 with logic. Regulator tolerance and transients can fall below the LED's 3.3 V minimum. This is the user-approved first-prototype experiment; startup, low battery, radio/display activity, load steps and temperature/lot tests remain mandatory.
- The two-wire protected LiPo interface is retained; its exact pack, cable polarity and connector remain to be qualified. J104 optional cell-contact thermistor is unpopulated. Fitted R120 keeps onboard charging disabled until compatible hardware temperature limits and charging behavior are qualified.
- SW401/SW402 use the selected Alps SKSCLBE010 side-actuated switches as prototype candidates. KSC-701 page 5 D11 cautions against continuously applied voltage, while the badge has permanent pull-ups. Manufacturer clarification or biased-life qualification, exact footprint acceptance and enclosure actuation fit remain open; see the [component record](../components/SKSCLBE010.md).
- Finish unassigned footprints, exact passive and inductor choices, display flex mating, antenna/layout, power/thermal/fault tests and human schematic/placement review.
- DNP options use explicit values and `Populate`/`Population` metadata because native DNP control is unavailable in the installed MCP. Reconcile those fields before generating any assembly BOM.

No board-placement, routing, manufacturing or production-qualification conclusion is included in this schematic review.
'''
(ROOT/'docs/design/verification.md').write_text(content)
paths=set(snap['sha256'])
# PCB is a concurrently developed artifact, deliberately outside this schematic manifest.
paths.update(row['path'] for row in source_checks)
for pattern in ['exports/*','tools/*.py','tools/*.swift','docs/design/*','docs/components/*','docs/style_guide/schematic.md','docs/datasheets/*inventory.json','tests/fixtures/**/*']:
 paths.update(str(p.relative_to(ROOT)) for p in ROOT.glob(pattern) if p.is_file() and str(p.relative_to(ROOT))!='exports/manifest.json')
paths.update(['README.md','AGENTS.md','docs/pinouts.md','docs/spec.md','docs/AI_Tinkerers_Badge_Design_BOM_Draft_2026-11-09.md'])
manifest={'created_utc':now,'purpose':'Development schematic review, not fabrication release','tools':{'KiCad':'10.0.8','Konnect':'0.12.1'},'checks':{'endpoints':ep,'properties':pr,'erc_errors':0,'erc_reviewed_warnings':1,'regression_tests':24,'pdf_pages':6,'stable_export_inputs':True,'graphics_only':graphics,'archived_source_hashes':len(source_checks)},'files':{p:{'sha256':sha(p),'bytes':(ROOT/p).stat().st_size} for p in sorted(paths)}}
(ROOT/'exports/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'components':n,'pins':pins,'nc':nc,'files':len(paths),'netlist_sha256':ep['netlist_sha256'],'pdf_sha256':sha('exports/tinkerbadge-schematic.pdf'),'manifest_sha256':sha('exports/manifest.json')},indent=2))

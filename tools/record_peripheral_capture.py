#!/usr/bin/env python3
"""Record read-only verification evidence. Does not mutate native CAD."""
import json,pathlib,hashlib
r=pathlib.Path(__file__).resolve().parents[1];o=r/'.build/peripheral_cad';d=r/'docs/design'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
custom=[]
for x in map(json.loads,open(o/'shared_3v3_exports_results.jsonl')):
 if x['tool']=='get_symbol_info':
  assert not x['isError'];custom.append(x['result'][0])
alps=json.load(open(o/'alps_symbol_results.json'));custom.append([x['result'][0] for x in alps if x['tool']=='get_symbol_info'][-1])
specs=json.load(open(o/'create_symbols.json'));by={x['name']:x for x in custom}
for s in specs:
 a=s['arguments'];assert {p['number']:p['name'] for p in by[a['name']]['pins']}=={p['number']:p['name'] for p in a['pins']}
(o/'accepted_symbol_readback.json').write_text(json.dumps(custom,indent=2)+'\n')
source_checks=[]
for s in json.load(open(r/'docs/datasheets/peripheral_inventory.json'))['documents']:
 p=r/'docs/datasheets'/s['filename'];actual=sha(p);assert actual==s['sha256'],p
 source_checks.append(dict(mpn=s.get('mpn',s.get('role',s['filename'])),file=str(p.relative_to(r)),sha256=actual,status='PASS'))
contract=json.load(open(d/'peripherals_contract.json'));ep=json.load(open(o/'endpoint_check.json'));meta=json.load(open(o/'metadata_check.json'));erc=[x['result'][0] for x in json.load(open(o/'alps_capture_results.json')) if x['tool']=='run_erc'][-1]
assert ep['status']=='PASS' and meta['status']=='PASS' and erc['errors']==0
result={'date':'2026-11-09','role':'Capture-author verification; independent source and final visual review are separate records.','tools':{'Konnect':'0.12.1 official installed MCP','KiCad':'10.0.8','native_mutation_route':'Konnect MCP only'},'files_sha256':{name:sha(r/name) for name in ['lighting.kicad_sch','peripherals.kicad_sch','peripheral_symbols.kicad_sym','docs/design/peripherals_contract.json']},'endpoint_check':ep,'metadata_summary':{k:v for k,v in meta.items() if k!='components'},'source_hashes':source_checks,'custom_symbol_readback':custom,'standard_symbols_checked':['Transistor_FET:AO3400A','Interface_Expansion:TCA9534','Device:R','Device:C','Device:Antenna_Loop','Connector_Generic:Conn_01x04','Connector_Generic:Conn_02x03_Odd_Even'],'footprint_assignment_evidence':{'Q501':{'footprint':'Package_TO_SOT_SMD:SOT-23','pins':{'1':'G','2':'S','3':'D'},'pad_centers_mm':{'1':[-0.9375,-0.95],'2':[-0.9375,0.95],'3':[0.9375,0]},'qualification':'AOS Rev3.1 p1 labels G/S/D and gate index dot but does not print numeric pins. Rotating the installed top-view footprint to put pad1 at the index/G lead maps pad2 to adjacent S and pad3 to opposite D without reflection. Numbering remains explicitly derived. AOS PO-00001 VersionN supplies unnumbered package dimensions. Standard footprint is not a claim of manufacturing release.'},'U505':{'footprint':'Package_TO_SOT_SMD:SOT-23-6','pad_centers_mm':{'1':[-1.1375,-0.95],'2':[-1.1375,0],'3':[-1.1375,0.95],'4':[1.1375,0.95],'5':[1.1375,0],'6':[1.1375,-0.95]},'mapping':'TI DBV top-view pins1IN/2GND/3EN/4FAULT/5ILIM/6OUT; no EP.'},'U506':{'footprint':'Package_SO:TSSOP-16_4.4x5mm_P0.65mm','mapping':'TI PW16 top-view full pin map agrees with TCA9534 standard symbol; 16 numbered pads, no EP.'}},'erc':erc,'erc_interpretation':'The single pin_to_pin warning is the intentional LIS2DW12 SA0 high address strap in I2C mode. No global suppression or weakened library pin type was applied. CS=1 and SA0 address role are documented by archived DocID029682 Rev4 p9 Table2.','power_flag_interpretation':'IR_RX_3V3 is supplied through R507 100 ohm from the TPS2553 switched ACC_3V3 output. Its PWR_FLAG documents the passive supply path; it does not claim a separate source. At receiver idle maximum0.7mA, DC filter drop is0.07V; startup transients still need bench measurement.','visual_review':{'manual':'Fresh 4096px native renders inspected after geometry, field, label and rail-note corrections. No remaining component/label collision observed. Existing near-border sheet headers explicitly accepted for this draft by parent.','tool':'check_schematic_overlaps: lighting60 and peripherals76 bounds resolved, zero unresolved geometry, zero overlaps. Tool excludes free text, so manual render review remains necessary.'},'artifacts':{'lighting_png':'.build/peripheral_cad/lighting.png','lighting_pdf':'.build/peripheral_cad/lighting.pdf','peripherals_png':'.build/peripheral_cad/peripherals.png','peripherals_pdf':'.build/peripheral_cad/peripherals.pdf','root_netlist':'.build/peripheral_cad/root.net','root_erc':'.build/peripheral_cad/root_erc.json','full_root_check':'.build/peripheral_cad/full_root_endpoint_check.json','metadata_check':'.build/peripheral_cad/metadata_check.json','symbol_disposable_render':'.build/peripheral_cad/validation.png'},'release_gates':['User-approved nominal3.3V LED prototype exception: below the manufacturer3.3V minimum is unqualified. Measure startup, low battery, Wi-Fi and full-white load transitions.','Nineteen listed footprints remain explicitly blank; connector mating/orientation and all custom package land patterns need physical audit.','C507/C508 are DNP in visible values and Population metadata. Ensure assembly export respects Population; no assembly package has been generated.','Final exact passive MPNs, DC-bias capacitance, power ratings, antenna tuning, package fit and prototype electrical/thermal tests remain open.','No board placement, routing, DRC, manufacture, procurement or runtime qualification performed.']}
result['alps_button_revision']={'review':'docs/design/review_alps_buttons.md','operations_and_native_checks':'.build/peripheral_cad/alps_capture_results.json','symbol_disposable_render':'.build/peripheral_cad/alps_validation.png','regression_tests':'tools/test_alps_buttons.py:5 passed','application_gate':'Continuous voltage under KSC-701p5D11 and series-limited capacitive loading under A2 remain unqualified; prototype candidate only.'}
(d/'peripherals_capture_review.json').write_text(json.dumps(result,indent=2)+'\n')
md=f'''# Lighting and peripheral capture evidence

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

The replacement changes only SW401/SW402 and adds four physical endpoints. Both native values, MPN, supplier IDs, blank footprints and application-qualification fields were queried and checked from the fresh root export. Four native lighting checks passed with no unconnected pins, floating wires, overlaps or hierarchical pin issues. Other native sheets remained byte-identical during this bounded edit. The actual saved operation/readback log is `.build/peripheral_cad/alps_capture_results.json`.

The4.85 mm terminal span is not pad pitch. Two locating holes and half-mount board-edge/enclosure geometry remain physical gates. KSC-701 p5 D11's continuous-applied-voltage caution applies as an unresolved qualification question to the open-circuit always-pulled-up wake input, separately from its continuous-press prohibition. Low current is not an exemption or proof of biased lifetime. The series-limited100 nF capacitive load likewise needs application qualification under p5 A2. Proceeding as a prototype candidate does not establish production reliability. See [independent source review](review_alps_buttons.md) and [component facts](../components/SKSCLBE010.md).

## Shared supply revision

The user explicitly approved one nominal +3V3 supply and requested that the schematic reflect it before review. Exactly 17 endpoint assignments changed: eight RGB VDD pins and nine LED decoupler supply pins. The source pin maps and all other contract endpoints are unchanged. The previous contract and exports are preserved in `revisions/peripherals_contract_2026-11-09_before_shared_3v3.json` and `.build/peripheral_cad/baseline_3v95/`.

The exact V6 source still specifies 3.3–5.3 V. The new nominal supply can fall below 3.3 V through tolerance, distribution loss and transients. That is a user-approved **prototype exception**, not guaranteed operation or a changed device rating. The sheet, [peripheral decisions](peripherals.md) and [LED record](../components/WS2812C-2020-V6.md) call for measurement during startup, low battery, Wi-Fi and full-white load transitions, with sufficient shared peak-current capacity.

Current peripheral contract SHA256: `{sha(d/'peripherals_contract.json')}`.

## Symbols and package maturity

Nine exact-part custom symbols live in `peripheral_symbols.kicad_sym`, registered as `Tinkerbadge_Peripherals`. Searches found no exact installed symbols for these parts. All physical pin names/numbers were read back from the saved library and checked against the approved maps. An isolated disposable schematic was rendered before real placement; four early text collisions were corrected there first.

AO3400A uses the installed symbol and SOT-23 footprint after comparing actual queried pad geometry with the manufacturer's top/bottom views. The source labels G/S/D and the gate index dot but does not print numerical pins. Rotating the standard top view so pad1 matches index/G makes pad2 adjacent S and pad3 opposite D without mirroring. **1G/2S/3D remains explicitly derived**, not a quoted numeric manufacturer table. TPS2553 DBV and TCA9534 PW16 symbol-pad ordering were likewise checked. Standard land patterns still need manufacturing/prototype review.

Nineteen physical footprints are deliberately blank: D401–D409, SW401/SW402, U501–U504, AE501, D501, J501/J502. Exact LED, switch, sensor and IR package land patterns are not yet qualified. JST and SAO mating orientation/cable continuity are release gates. AE501 is a PCB antenna feature requiring layout and loaded tuning. Do not generate an assembly package until these gates, final passive MPNs and `Population` handling are closed.

## Evidence

Machine-readable source hashes, actual custom pins, assigned footprint pad geometry, current native-file hashes, ERC interpretation, blank-footprint inventory and artifact paths are in [peripherals_capture_review.json](peripherals_capture_review.json). All 18 active archived peripheral source hashes pass; the replaced Xunpu source is retained separately in revision history. The exported-root endpoint checker and metadata checker read the netlist, not the native schematic source.

Current renders and PDFs: `.build/peripheral_cad/lighting.png`, `lighting.pdf`, `peripherals.png`, `peripherals.pdf`. Root exported-netlist evidence: `.build/peripheral_cad/root.net`, `endpoint_check.json`, `full_root_endpoint_check.json`, `metadata_check.json`, `root_erc.json`.

No board placement/routing, DRC, physical fit, manufacturing, procurement, antenna tuning, runtime or bench qualification is claimed.
'''
(d/'peripherals_capture_review.md').write_text(md)
p=d/'peripherals.md';s=p.read_text().replace('The shared-3.3-V revision must pass fresh exported endpoint and ERC checks before review.','The shared-3.3-V revision passed a fresh exported 215-endpoint check. Root ERC has zero errors and the documented intentional LIS2DW12 SA0 address-strap warning. See [capture evidence](peripherals_capture_review.md).');p.write_text(s)
print('Recorded',len(source_checks),'source hashes;',len(custom),'custom symbols; contract',sha(d/'peripherals_contract.json'))

#!/usr/bin/env python3
"""Apply the user-approved shared-3.3-V prototype revision; native writes via MCP."""
import json,pathlib,hashlib,shutil,time
from konnect_call import Client,unbox
r=pathlib.Path(__file__).resolve().parents[1];out=r/'.build/peripheral_cad';history=r/'docs/design/revisions';history.mkdir(exist_ok=True);baseline=out/'baseline_3v95';baseline.mkdir(exist_ok=True)
contract=r/'docs/design/peripherals_contract.json';old=contract.read_bytes();expected='7c2255b353729eb2224e37685db379b598e1021d2ca95386573d9cc492554699';assert hashlib.sha256(old).hexdigest()==expected
(history/'peripherals_contract_2026-11-09_before_shared_3v3.json').write_bytes(old)
for name in ['root.net','root_erc.json','endpoint_check.json','lighting.png','peripherals.png','lighting.pdf','peripherals.pdf']:shutil.copy2(out/name,baseline/name)
d=json.loads(old);changes=[]
for c in d['components']:
 for p,n in c['pins'].items():
  if n=='VLED_3V9':c['pins'][p]='+3V3';changes.append([c['ref'],p])
assert len(changes)==17
rails=d['interfaces']['rails'];rails['rgb']='+3V3';rails['rgb_nominal_V']=3.3;rails.pop('rgb_upper_acceptance_V')
rails['rgb_datasheet_operating_minimum_V']=3.3
rails['rgb_prototype_exception']='User-approved nominal 3.3 V shared prototype supply. Tolerance, wiring losses and transients may put LEDs below the documented 3.3 V minimum; operation and timing there are not guaranteed.'
rails['rgb_actual_rail_bounds_source']='docs/design/power_contract.json'
d['status']='accepted_for_schematic_capture_with_user_approved_shared_3v3_prototype_exception'
d['scope']='Lighting and peripheral physical-pin endpoint assignments; native schematic captured through Konnect MCP.'
d['revision']={'date':'2026-11-09','decision':'User approved single nominal 3.3 V prototype supply and requested native schematic synchronization. Independent parent reviewer accepted the mapping-only change.','previous_contract_sha256':expected,'previous_contract':'docs/design/revisions/peripherals_contract_2026-11-09_before_shared_3v3.json','changed_endpoints':changes,'pin_maps_changed':False,'validation_required':['Measure voltage at the LEDs during startup and low-battery operation.','Exercise Wi-Fi activity and simultaneous full-white LED transitions.','Verify shared regulator peak-current capacity, rail dips, data timing and recovery.','Revisit the architecture if repeatable LED failures occur.']}
contract.write_text(json.dumps(d,indent=2)+'\n');print('New contract SHA256',hashlib.sha256(contract.read_bytes()).hexdigest())
p=r/'docs/design/peripherals.md';s=p.read_text();s=s.replace('Independent source/assignment review is pending before native CAD.','Source facts and original assignments passed independent review. The later user-approved shared-3.3-V mapping delta was independently accepted before native capture. The earlier contract is preserved under `docs/design/revisions/`.')
a=s.index('Eight exact WS2812C-2020-V6 pixels');b=s.index('\n\nLive onboard',a)
s=s[:a]+'''Eight exact WS2812C-2020-V6 pixels now share nominal **3.3 V** with the MCU, sensors, NFC, status LED and IR transmitter. This supersedes the 3.95 V primary rail plus 3.3 V LDO proposal. The power contract owns the final calculated DC tolerance and load/transient limits; nominal 3.3 V is not a guarantee that every LED sees at least 3.3 V.

The manufacturer specifies **3.3–5.3 V** for this exact V6. The user explicitly accepted a prototype experiment whose tolerance, wiring loss or transients can place the LEDs below that minimum. Function, color/current, timing and input thresholds below the rated range are **not guaranteed**. Within the rated range, a shared supply makes the LED VIH requirement (0.55 times supply) track the MCU high-level output (at least 0.8 times supply); retain the LED VIL maximum of 0.7 V. No level shifter or separate LED rail is fitted.

Measure the supply at the most distant LED and the MCU during startup, low battery, Wi-Fi activity and simultaneous full-white LED transitions. Verify enough shared peak-current capacity and effective local capacitance; test data timing, startup state, recovery from rail dips and storage darkness. Eight 100 nF local capacitors plus 22 uF LED bulk remain fitted. Brightness and simultaneous-load limits remain firmware requirements. Revisit the rail architecture if these tests show unreliable behavior.''' +s[b:]
s=s.replace('Contract parser checked unique references and every assigned electrical pin against source maps. No ERC, native CAD, physical fit, runtime, antenna or lab tests claimed.','Contract parser checked unique references and every assigned electrical pin against source maps. The original native capture passed all 215 endpoints across 75 components against an exported root netlist. The shared-3.3-V revision must pass fresh exported endpoint and ERC checks before review. Physical fit, runtime, antenna and lab tests remain unperformed; see the native-capture report for the final export evidence.')
p.write_text(s)
p=r/'docs/components/WS2812C-2020-V6.md';s=p.read_text();s=s.replace('Use only the specified operating range, not the promotional overvoltage-survival claim.','These are manufacturer limits. The project prototype exception below does not extend this range; do not rely on promotional overvoltage-survival claims.')
s=s.replace('VDD on VLED_3V9','VDD on the same nominal +3V3 supply as the MCU')
a=s.index('- Direct3.3V logic passes');b=s.index('\n\n## Firmware',a)
s=s[:a]+'''- Within the rated supply range, the shared rail makes the LED VIH requirement (0.55 times VDD) track the MCU guaranteed high level (at least 0.8 times VDD). Retain the LED VIL maximum of 0.7 V. No level shifter is fitted.
- **User-approved prototype exception:** nominal 3.3 V with regulator tolerance, distribution loss and transient droop does not guarantee the documented 3.3 V LED minimum. Operation and electrical thresholds below that minimum are not guaranteed. This is an explicit prototype experiment, not a revised manufacturer rating. Measure startup, low battery, Wi-Fi activity and full-white LED load transitions at the actual LED supply pins; verify shared peak-current capacity and recovery. Revisit the power architecture if the tests show unreliable behavior.''' +s[b:]
s=s.replace('Higher upstream LED rail is present before LDO-fed MCU, but LEDs must not be externally powered with MCU absent; quantify transient/backfeed and black leakage on the assembled board.','LEDs and MCU now share the same supply ramp. Keep the first DIN pulldown and hold the MCU output low until the shared rail has settled. Do not independently power the LED chain. Test reset/data behavior, shared-rail transients, recovery and black leakage on the assembled board.')
p.write_text(s)
for name in ['BH1730FVC','LIS2DW12TR','NT3H2111W0FHKH']:
 p=r/'docs/components'/f'{name}.md';s=p.read_text();s=s.replace('Rail decision update: core/MCU/sensor/NFC domain is always-on 3.3 V from TLV75733; the upstream nominal 3.95 V LED domain must never directly feed these supplies or pull-ups.','Rail decision update: the first prototype uses one nominal 3.3 V supply shared by MCU, sensors, NFC and LEDs. Keep this part within its specified supply and logic limits; the separately documented below-minimum LED experiment does not relax sensor limits.')
 if name=='LIS2DW12TR':s=s.replace('| 9 | SDA/SDI/SDO |','| 4 | SDA/SDI/SDO |')
 p.write_text(s)
# Keep the reproducible initial capture plan aligned with the new design choice.
p=r/'tools/wire_peripherals.py';s=p.read_text().replace("s.label('VLED_3V9',25.4,55.88,True)","s.power('+3V3',25.4,55.88)").replace('RGB chain: exact WS2812C-2020-V6. VLED maximum acceptance 4.10 V; MCU data is 3.3 V.','RGB chain: exact WS2812C-2020-V6 on shared nominal +3V3. Below 3.3 V operation is not guaranteed.')
p.write_text(s)
# Exactly replace the obsolete electrical rail label and note. Existing direct wires serve the new rail.
lighting=str(r/'lighting.kicad_sch');periph=str(r/'peripherals.kicad_sch')
calls=[dict(name='delete_schematic_net_label',arguments=dict(schematic=lighting,net='VLED_3V9',x=25.4,y=48.26)),dict(name='delete_schematic_wire',arguments=dict(schematic=lighting,x1=25.4,y1=48.26,x2=25.4,y2=55.88)),dict(name='add_power_symbol',arguments=dict(schematic=lighting,power_net='+3V3',x=25.4,y=55.88)),dict(name='batch_delete',arguments=dict(schematic=lighting,uuids=['8c4585af-7172-4a3b-83c4-796211b1f383'])),dict(name='add_schematic_text',arguments=dict(schematic=lighting,text='RGB chain: exact WS2812C-2020-V6 on shared nominal +3V3. Below 3.3 V operation is not guaranteed.',x=15.24,y=33.02,size=1.27)),dict(name='add_schematic_text',arguments=dict(schematic=lighting,text='Prototype gate: scope startup, low battery, Wi-Fi and full-white transitions at the LEDs; verify shared peak capacity.',x=15.24,y=43.18,size=1.27)),dict(name='add_power_symbol',arguments=dict(schematic=periph,power_net='PWR_FLAG',x=203.2,y=228.6))]
(out/'shared_3v3_native_plan.json').write_text(json.dumps(calls,indent=2));cli=Client()
try:
 for i,c in enumerate(calls):
  raw=cli.call(c['name'],c['arguments']);(out/f'shared-3v3-{i:02d}-{c["name"]}.json').write_text(json.dumps(raw,indent=2));u=unbox(raw);v=u['result'][0]
  if u['isError'] or isinstance(v,dict) and (v.get('errors') or v.get('failures') or v.get('success') is False):raise RuntimeError(str(u))
  print(c['name'],str(v)[:180],flush=True)
finally:cli.close()

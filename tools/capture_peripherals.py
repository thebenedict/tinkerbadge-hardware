#!/usr/bin/env python3
"""Capture accepted peripheral contracts using official Konnect MCP only."""
import json,pathlib,time,sys
from konnect_call import Client,unbox
root=pathlib.Path(__file__).resolve().parents[1]; out=root/'.build/peripheral_cad'; cli=Client()
contract=json.load(open(root/'docs/design/peripherals_contract.json')); cd={c['ref']:c for c in contract['components']}
custom={'SKSCLBE010':'SKSCLBE010','WS2812C-2020-V6':'WS2812C-2020-V6','HSMF-C165':'HSMF-C165','BH1730FVC':'BH1730FVC','LIS2DW12TR':'LIS2DW12TR','NT3H2111W0FHKH':'NT3H2111W0FHKH','IR67-21C/TR8':'IR67-21C_TR8','IRM-H638T/TR2':'IRM-H638T_TR2','TPS2553DBVR':'TPS2553DBVR'}
standard={'AO3400A':'Transistor_FET:AO3400A','TCA9534PWR':'Interface_Expansion:TCA9534','SM04B-SRSS-TB(LF)(SN)':'Connector_Generic:Conn_01x04','SFH11-NBPC-D03-ST-BK':'Connector_Generic:Conn_02x03_Odd_Even'}
fp={'Q501':'Package_TO_SOT_SMD:SOT-23','U505':'Package_TO_SOT_SMD:SOT-23-6','U506':'Package_SO:TSSOP-16_4.4x5mm_P0.65mm'}
loc={}
def at(ref,x,y,rot=0): loc[ref]=(x,y,rot)
for i in range(8):at(f'D{401+i}',63.5+43.18*i,88.9);at(f'C{401+i}',78.74+43.18*i,67.31)
for v in [('C409',25.4,66.04),('R401',40.64,88.9,90),('R402',48.26,104.14),('D409',104.14,181.61),('R403',76.2,179.07,90),('R404',76.2,184.15,90),('R405',50.8,198.12),('R406',63.5,210.82),('SW401',195.58,177.8,0),('R411',220.98,177.8,90),('R412',243.84,157.48),('C411',243.84,191.77),('SW402',297.18,177.8,0),('R413',322.58,177.8,90),('R414',345.44,157.48),('C412',345.44,191.77)]:at(*v)
for v in [('U501',63.5,76.2),('C501',88.9,49.53),('C502',109.22,49.53),('R501',22.86,53.34),('R502',38.1,53.34),('U502',175.26,78.74),('C503',190.5,43.18),('C504',210.82,43.18),('C505',231.14,43.18),('U503',287.02,81.28),('C506',307.34,48.26),('C507',340.36,88.9),('C508',365.76,88.9),('AE501',383.54,69.85),('R503',259.08,71.12),('U506',76.2,172.72),('C514',101.6,144.78),('C515',124.46,144.78),('R514',162.56,198.12),('R515',142.24,198.12),('R516',121.92,198.12),('R517',101.6,198.12),('U505',279.4,172.72),('C511',231.14,154.94),('C512',251.46,154.94),('C513',322.58,184.15),('R508',254,198.12),('R509',236.22,191.77),('R510',368.3,184.15),('R511',345.44,184.15),('Q501',55.88,255.27),('D501',58.42,238.76,270),('R504',58.42,222.25),('R505',35.56,255.27,90),('R506',45.72,269.24),('U504',162.56,251.46),('R507',121.92,228.6,90),('C509',187.96,240.03),('C510',210.82,240.03),('J501',279.4,240.03),('J502',365.76,240.03),('R512',307.34,224.79),('R513',330.2,224.79)]:at(*v)
assert set(loc)==set(cd),(set(loc)^set(cd))
def call(name,**args):
 r=cli.call(name,args);(out/f'{time.time_ns()}-{name}.json').write_text(json.dumps(r,indent=2));u=unbox(r)
 if u['isError']:raise RuntimeError(json.dumps(u))
 v=u['result'][0]
 if isinstance(v,dict) and (v.get('errors') or v.get('failures') or v.get('success') is False or v.get('outcome',{}).get('failed',0)):
  raise RuntimeError(json.dumps(v))
 print(name,str(v)[:180],flush=True);return v
def comp(c):
 ref=c['ref'];mpn=c.get('mpn');value=mpn or c.get('value','')
 if mpn in custom:lib='Tinkerbadge_Peripherals:'+custom[mpn]
 elif mpn in standard:lib=standard[mpn]
 elif ref=='AE501':lib='Device:Antenna_Loop';value='PCB LOOP / TUNE'
 else:lib='Device:'+c['kind']
 if c.get('kind')=='R':value=c['value'].split()[0].replace('R','')
 if c.get('kind')=='C':value=c['value'].split()[0].replace('F','')+' / 10V' if 'DNP' not in c['value'] else 'TUNE / DNP'
 footprint=fp.get(ref,'')
 if c.get('kind') in ('R','C'):
  pkg=c['package'];footprint=('Resistor_SMD:R_' if c['kind']=='R' else 'Capacitor_SMD:C_')+('0805_2012Metric' if '0805' in pkg else '0603_1608Metric')
 x,y,rot=loc[ref];return dict(reference=ref,lib_id=lib,x=round(x,5),y=round(y,5),rotation=rot,value=value,footprint=footprint)
try:
 for name,cond in [('lighting',lambda r:int(''.join(filter(str.isdigit,r)))<500),('peripherals',lambda r:int(''.join(filter(str.isdigit,r)))>=500)]:
  sch=str(root/(name+'.kicad_sch'));comps=[comp(c) for c in contract['components'] if cond(c['ref'])]
  (out/(name+'_placement_plan.json')).write_text(json.dumps(comps,indent=2))
  call('set_schematic_page',schematic=sch,size='A3')
  response=call('batch_place_components',schematic=sch,components=comps);(out/(name+'_placement_result.json')).write_text(json.dumps(response,indent=2))
  pins=call('batch_get_schematic_pin_locations',schematic=sch,references=[c['reference'] for c in comps]);(out/(name+'_pins.json')).write_text(json.dumps(pins,indent=2))
finally:cli.close()

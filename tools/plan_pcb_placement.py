#!/usr/bin/env python3
"""Historical initial placement seed only. Writes .build, never the accepted current placement JSON."""
import pathlib,json,sys
from check_schematic_contracts import sexp,children,val
ROOT=pathlib.Path(__file__).resolve().parents[1];p={}
def put(ref,x,y,rot=0,side='B.Cu',group=''):
 assert ref not in p,ref;p[ref]={'reference':ref,'x':x,'y':y,'rotation':rot,'side':side,'group':group}
# Mechanical/RF/display fixed anchors.
put('U201',118,106.75,0,'F.Cu','processor/radio')
put('J101',103.675,130,270,'F.Cu','USB')
put('SW401',102.1,171,270,'F.Cu','buttons')
put('SW402',207.9,171,90,'F.Cu','buttons')
for r,x,y,rot in [('C201',105,105.5,90),('C202',106.5,102.8,0),('C203',106.5,106.8,0),('R201',106.5,110,0),('R202',130,119,0),('R205',106,117,0),('R206',106,119.5,0)]:put(r,x,y,rot,'F.Cu','processor/radio')
for r,x,y in [('R203',114,122),('R204',117,122),('R207',126,122)]:put(r,x,y,0,'B.Cu','processor/radio')
for n in range(6):put('TP'+str(201+n),135+3*n,133,0,'B.Cu','recovery/test')
# LED emitters remain front-facing. Individual decoupling follows each emitter.
for n,x,y in [(401,144,114),(402,159,114),(403,174,114),(404,114,190),(405,126,190),(406,138,190),(407,150,190),(408,162,190)]:
 put('D'+str(n),x,y,0,'F.Cu','role/affinity light');put('C'+str(n),x+3,y,90,'F.Cu','LED decoupling')
put('C409',141,118,0,'F.Cu','LED bulk')
put('D409',104,143,90,'F.Cu','power indicator')
for r,x,y,side in [('R401',114,121,'F.Cu'),('R402',140.5,114,'F.Cu'),('R403',108,143,'B.Cu'),('R404',108,146,'B.Cu'),('R405',132,115.5,'F.Cu'),('R406',135,115.5,'F.Cu'),('R411',130,109,'F.Cu'),('C411',132.5,109,'F.Cu'),('R412',135,109,'F.Cu'),('R413',130,112,'F.Cu'),('C412',132.5,112,'F.Cu'),('R414',135,112,'F.Cu')]:put(r,x,y,0,side,'buttons/status')
# Source selection and disabled charger.
for r,x,y,rot in [('U101',115,146,0),('U102',123,152,0),('U103',118,169,0),('Q103',114,155,0),('Q101',109,132,0),('Q102',109,183,0),('D101',104.5,137,90),('D102',114.5,194,0),('C101',109,139,0),('C102',109,142,0),('C103',119.5,146.5,0),('C104',115,150,0),('C105',127,152,90),('C106',120,154.5,90),('C107',117,164.5,270),('C108',116.5,174,270),('C109',112,174,270),('R101',110,135,0),('R102',113,135,0),('R103',111,145,90),('R104',111,148,90),('R105',118,141,90),('R106',118,144,90),('R107',111,141,90),('R108',114,141,90),('R109',118,150,0),('R110',110.5,154.5,0),('R111',110.5,157.5,0),('R112',127,149,0),('R113',121,148.5,0),('R114',124,148.5,0),('R115',128,156,0),('R116',128,159,0),('R117',113,168.5,90),('R118',113,171,90),('R120',120,151.5,0),('R121',109,127,0),('R122',112,127,0),('R123',112,130,0),('R124',109,178,0),('R125',112,178,0),('R126',112,181,0)]:put(r,x,y,rot,'B.Cu','power')
for r,x,y,rot in [('U107',134,123,90),('R127',131,129,0),('R128',134,129,0),('R129',137,118,0),('R130',134,118,0),('C115',130,123,0),('C116',137,129,0)]:put(r,x,y,rot,'B.Cu','battery ADC')
# Display power and support stay to the right of the battery, near the proposed flex corridor.
for r,x,y,rot in [('U104',181,128,0),('C112',177.5,126,0),('C113',179,131.5,0),('C114',184.5,126,0),('R119',183,131.5,0),('U301',183,137,90),('R302',189,134,0),('R303',189,137,0),('R304',189,140,0),('R305',185,142.5,0),('R306',181,142.5,0),('R307',177,142.5,0),('R308',177,145.5,0),('Q301',185,155,0),('R301',185,158.5,0),('D301',191,149,0),('D302',191,154,0),('D303',191,159,0),('C301',179,149,90),('C302',179,155,90),('C303',178,136,0),('C304',174.5,139,0),('C305',176,160,0),('C306',180,162,0),('C307',184,162,0),('C308',188,163,0),('C309',176,165,0),('C310',180,167,0),('C311',184,167,0),('C312',176,133,0)]:put(r,x,y,rot,'B.Cu','display support')
# Optical items on top edge, isolated by a future opaque light barrier.
for r,x,y,rot,side in [('U501',205,112,0,'F.Cu'),('C501',205,115.5,0,'F.Cu'),('U504',185,110,0,'F.Cu'),('D501',195,110,0,'F.Cu'),('R507',182,115,0,'F.Cu'),('C509',185,115,0,'F.Cu'),('C510',188,115,0,'F.Cu'),('Q501',195,115,0,'B.Cu'),('R504',195,119,0,'B.Cu'),('R505',192,115,0,'B.Cu'),('R506',192,118,0,'B.Cu')]:put(r,x,y,rot,side,'sensing/IR')
for r,x,y in [('U502',162,121),('C502',159,121),('C503',159,124),('R501',140,117),('R502',143,117)]:put(r,x,y,0,'B.Cu','sensors/I2C')
for r,x,y in [('U503',174.5,178),('R503',174.5,174.5),('C504',177.5,176.5),('C505',181,176.5),('C506',174.5,170),('C507',173.5,182),('C508',173.5,185)]:put(r,x,y,0,'B.Cu','NFC')
for r,x,y,rot in [('U505',195,169,0),('J501',206.5,165,90),('C511',192,165,0),('C512',192,162,0),('C513',198.5,169,0),('R508',195,173,0),('R509',195,176,0),('R510',198.5,176,0),('R511',202,176,0),('R512',201,170,0),('R513',201,173,0)]:put(r,x,y,rot,'B.Cu','accessories')
put('U506',146,124,0,'B.Cu','I/O expander')
for r,x,y in [('C514',151.5,122),('C515',151.5,125.5),('R514',143,130),('R515',146,130),('R516',149,130),('R517',152,130)]:put(r,x,y,0,'B.Cu','I/O expander')
blocked={'U105':'DQA0010A/B package acceptance','J102':'pack connector/polarity/current','J103':'dock contact and guide mechanics','J104':'optional DNP thermistor interface','L101':'exact .47uH inductor','J301':'FPC mating/contact side/fold','L301':'exact68uH inductor','AE501':'antenna/tuning design','J502':'housing key-to-contact verification'}
r=sexp((ROOT/'exports/tinkerbadge.net').read_text());refs={val(c,'ref') for c in children(children(r,'components')[0],'comp')}
assert refs==set(p)|set(blocked),(refs-set(p)-set(blocked),set(p)-refs)
mechanical=[
 {'reference':'MECH_PANEL','footprint':'Tinkerbadge:Review_Panel_93.3x54.9','x':155,'y':150.5,'rotation':0,'side':'F.Cu'},
 {'reference':'MECH_BATTERY','footprint':'Tinkerbadge:Review_Battery_Allowance','x':154,'y':163.5,'rotation':0,'side':'B.Cu'},
 {'reference':'MECH_NFC','footprint':'Tinkerbadge:Review_NFC_Area','x':191,'y':189.5,'rotation':0,'side':'F.Cu'},
 {'reference':'RES_J301','footprint':'Tinkerbadge:Review_Flex_Mating','x':202,'y':149,'rotation':0,'side':'B.Cu'},
 {'reference':'RES_U105','footprint':'Tinkerbadge:Review_ESD_Package','x':109.5,'y':130,'rotation':0,'side':'F.Cu'},
 {'reference':'RES_L101','footprint':'Tinkerbadge:Review_Inductor_6x6','x':124,'y':169,'rotation':90,'side':'B.Cu'},
 {'reference':'RES_L301','footprint':'Tinkerbadge:Review_Inductor_5x5','x':185,'y':149,'rotation':0,'side':'B.Cu'},
 {'reference':'RES_J502','footprint':'Tinkerbadge:Review_SAO_12.7x7','x':170,'y':128,'rotation':0,'side':'B.Cu'},
 {'reference':'RES_J102','footprint':'Tinkerbadge:Review_Battery_Connector','x':130,'y':138,'rotation':0,'side':'B.Cu'},
 {'reference':'RES_J103','footprint':'Tinkerbadge:Review_Dock_Contacts','x':124,'y':193,'rotation':0,'side':'B.Cu'}]
data={'status':'preliminary_not_approved_for_routing','board_mm':[110,100],'origin_mm':[100,100],'copper_layers':4,'placements':list(p.values()),'blocked_electrical_references':blocked,'non_electrical_envelopes':mechanical,'mounting_holes_mm':[[104,121,2.2],[206,121,2.2],[104,195,2.2],[206,175,2.2]],'lanyard_holes_mm':[[145,105,3.2],[183,105,3.2]],'notes':['Mechanical envelopes are clearance proposals, not approved mating definitions.','No detailed routing before human placement approval.','Panel glass93.3x54.9 rotated180 to reserve flex on right; exact fold/mating remains blocked.','No coil copper, RF tune or battery/connector assumptions are released.']}
(ROOT/'.build/pcb_initial_seed_placement.json').write_text(json.dumps(data,indent=2)+'\n')
print(len(p),'electrical placements;',len(blocked),'blocked references')

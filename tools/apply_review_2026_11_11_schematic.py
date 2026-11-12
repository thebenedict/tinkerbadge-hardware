#!/usr/bin/env python3
"""Schematic and contract changes answering docs/review/design_review_2026-11-11.md.

One-shot edit of the native sheets and block contracts as committed at
3120d6e. Run from the repository root, then
`kicad-cli sch upgrade --force tinkerbadge.kicad_sch`.

Changes
- J301: Hirose FH34SRJ-24S-0.5SH(50), top-and-bottom contact (DISP-1).
- Button B moves to GPIO0 so it doubles as BOOT; R414 removed; GPIO4 unused (UI-1).
- SW403 + R415: reset button on MCU_EN (UI-1).
- RT102: 100 k NTC in parallel with RT101 to centre the charge window (PWR-1).
- IR receiver supply from expander P1 instead of the accessory rail.
- TP101 VSYS, TP301 +3V3_EPD, TP501/TP502 internal I2C probe pads (SERVICE-1).
- Contract notes for expander initialisation (DOC-1).
"""
import copy
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from schlib import Sheet, kid, kids, pt, prop, pval, parse, new_uuid  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
NOTE = 'design review 2026-11-11'
pwr_n = [950]


def gnd(sheet, at):
    template = next(pval(s, 'Reference') for s in sheet.symbols()
                    if pval(s, 'Reference').startswith('#') and pval(s, 'Value') == 'GND'
                    and float(kid(s, 'at')[3]) == 0 and kid(s, 'mirror') is None)
    pwr_n[0] += 1
    sheet.clone_symbol(template, f'#PWR{pwr_n[0]}', at)


def drop_stub(sheet, pin_pt):
    ws, pts = sheet.trace(pin_pt)
    sheet.remove(ws + sheet.items_at(pts))


def ensure_lib(dst, src, lib_id):
    if lib_id not in dst.libs:
        node = copy.deepcopy(src.libs[lib_id])
        kid(dst.root, 'lib_symbols').append(node)
        dst.libs[lib_id] = node


def import_symbol(dst, src, src_ref, new_ref, at, rot=0, props=None):
    """Copy a symbol instance from another sheet, re-homed to dst's hierarchy path."""
    s = copy.deepcopy(src.by_ref(src_ref))
    ensure_lib(dst, src, kid(s, 'lib_id')[1])
    old = kid(s, 'at')
    dx, dy = at[0] - float(old[1]), at[1] - float(old[2])
    old[1], old[2] = at[0], at[1]
    old[3] = rot
    for m in kids(s, 'mirror'):
        s.remove(m)
    kid(s, 'uuid')[1] = new_uuid()
    for p in kids(s, 'property'):
        a = kid(p, 'at')
        a[1], a[2] = round(float(a[1]) + dx, 2), round(float(a[2]) + dy, 2)
    for p in kids(s, 'pin'):
        kid(p, 'uuid')[1] = new_uuid()
    prop(s, 'Reference')[2] = new_ref
    anchor = next(x for x in dst.symbols() if not pval(x, 'Reference').startswith('#'))
    path = kid(kid(kid(anchor, 'instances'), 'project'), 'path')[1]
    for inst in kids(s, 'instances'):
        for proj in kids(inst, 'project'):
            for p in kids(proj, 'path'):
                p[1] = path
                kid(p, 'reference')[1] = new_ref
    dst.add(s)
    for k, v in (props or {}).items():
        dst.set_prop(new_ref, k, v)
    return s


def text(sheet, s, at, size=1.27):
    sheet.add(parse(f'(text "{s}" (exclude_from_sim no) (at {at[0]} {at[1]} 0) (effects (font (size {size} {size})) (justify left bottom)) (uuid "{new_uuid()}"))'))


def testpoint(dst, mcu, ref, at, net, kind, contract):
    import_symbol(dst, mcu, 'TP203', ref, at, 0, {'Value': net.lstrip('+') if False else net, 'Contract': contract,
                                                  'Footprint': 'TestPoint:TestPoint_Pad_D1.0mm'})
    end = (at[0] + 5.08, at[1])
    dst.add_wire(at, end)
    dst.add_label(net, end, 0, kind=kind, shape='passive')


mcu = Sheet('mcu.kicad_sch')
light = Sheet('lighting.kicad_sch')
power = Sheet('power.kicad_sch')
disp = Sheet('display.kicad_sch')
per = Sheet('peripherals.kicad_sch')

# ---------------------------------------------------------------- lighting: R414 out
r414 = light.pins(light.by_ref('R414'))
junction = (345.44, 177.8)
doomed = [light.by_ref('R414')]
ws, pts = light.trace(r414['1'])                 # +3V3 stub and its power symbol
doomed += ws
doomed += [s for s in light.symbols() if pval(s, 'Reference').startswith('#') and any(q in pts for q in light.pins(s).values())]
doomed += [w for w in light.wires() if r414['2'] in light.wire_pts(w)]
light.remove(doomed)
# the node that remains is R413.2 - C412.1 - label; rebuild the vertical leg that passed through R414.2
if not any(light.on_seg((345.44, 180.0), *light.wire_pts(w)) for w in light.wires()):
    light.add_wire(junction, light.pins(light.by_ref('C412'))['1'])
for t in kids(light.root, 'text'):
    if 'BTN_B' in t[1] or 'Button B' in t[1]:
        pass
text(light, 'BTN_B_N is GPIO0: holding B through a reset enters ROM download. Pull-up R202 is on the processor sheet.', (292.1, 200.66))

# ---------------------------------------------------------------- mcu: GPIO0 / GPIO4 / reset
u201 = mcu.pins(mcu.by_ref('U201'))
drop_stub(mcu, u201['4'])
mcu.add_nc(u201['4'])
for n in list(kids(mcu.root, 'label')):
    if n[1] == 'BOOT_N':
        at = kid(n, 'at')
        rot = int(float(at[3])) if len(at) > 3 else 0
        mcu.remove([n])
        mcu.add_label('BTN_B_N', (float(at[1]), float(at[2])), rot, kind='global', shape='input')
mcu.set_prop('TP202', 'Value', 'BOOT / BTN_B')
for t in kids(mcu.root, 'text'):
    if t[1].startswith('Hold BOOT low'):
        t[1] = 'Button B is BOOT: hold B, tap RESET.'
    elif t[1].startswith('EN: 10 k'):
        t[1] = 'EN: 10 k / 1 uF. SW403 resets.'
sw = import_symbol(mcu, light, 'SW402', 'SW403', (101.6, 172.72), 0,
                   {'Contract': 'docs/design/mcu_contract.json'})
r = import_symbol(mcu, light, 'R413', 'R415', (116.84, 172.72), 90,
                  {'Contract': 'docs/design/mcu_contract.json'})
swp, rp = mcu.pins(sw), mcu.pins(r)
mcu.add_wire(swp['1'], rp['1'])
mcu.add_wire(swp['2'], swp['1'])
mcu.add_wire(swp['3'], swp['4'])
mcu.add_wire(swp['4'], (swp['4'][0], 180.34))
gnd(mcu, (swp['4'][0], 180.34))
mcu.add_wire(rp['2'], (rp['2'][0] + 2.54, rp['2'][1]))
mcu.add_label('MCU_EN', (rp['2'][0] + 2.54, rp['2'][1]), 0)
mcu.add_label('MCU_EN_SW', (swp['1'][0] + 1.27, swp['1'][1]), 0)
text(mcu, 'RESET (recessed): SW403 pulls EN low through 330R.', (93.98, 165.1))

# ---------------------------------------------------------------- power: second NTC, VSYS probe pad
rt1 = power.by_ref('RT101')
x1 = float(kid(rt1, 'at')[1])
rt2 = power.clone_symbol('RT101', 'RT102', (x1 + 12.7, float(kid(rt1, 'at')[2])), 0, '100k NTC B3950 1%')
p2 = power.pins(rt2)
power.add_wire(p2['1'], (p2['1'][0], 99.06))
power.add_label('BATT_NTC', (p2['1'][0], 99.06), 90)
gnd(power, p2['2'])
for k, v in {'MPN': 'KNTC0603/100KF3950', 'LCSC': 'C2892545',
             'Description': 'Second NTC in parallel with RT101; shifts the BQ24074 TS window about 2.4 degC colder'}.items():
    power.set_prop('RT102', k, v)
testpoint(power, mcu, 'TP101', (345.44, 33.02), 'VSYS', 'label', 'docs/design/power_contract.json')
for t in kids(power.root, 'text'):
    if t[1].startswith('CHARGING'):
        t[1] = ('CHARGING\nCE tied low: charger enabled, 270 mA (R113), USB500 input limit.\n'
                'RT101 10k || RT102 100k NTC under the cell: charge window 1.7-44.8 degC nominal,\n'
                '0.1-48.4 degC over the charger\'s threshold and bias tolerance.\n'
                'J102 is JST-PH, pin 1 = battery +. CHECK PACK POLARITY before connecting.\n'
                'Use a protected 1S 4.2 V pack rated for >= 300 mA charge.')

# ---------------------------------------------------------------- display: connector, probe pad
disp.set_prop('J301', 'Footprint', 'Tinkerbadge:Hirose_FH34SRJ-24S-0.5SH_PanelOrder')
disp.set_prop('J301', 'MPN', 'FH34SRJ-24S-0.5SH(50)')
disp.set_prop('J301', 'LCSC', 'C324726')
testpoint(disp, mcu, 'TP301', (223.52, 33.02), '+3V3_EPD', 'global', 'docs/design/display_contract.json')
for t in kids(disp.root, 'text'):
    if t[1].startswith('J301: FH12'):
        t[1] = 'J301: FH34SRJ top-and-bottom contact. Pads are numbered in panel order for the folded flex; dry-fit a real panel.'

# ---------------------------------------------------------------- peripherals: IR supply, probe pads
for n in kids(per.root, 'label'):
    if n[1] == 'ACC_3V3' and pt(kid(n, 'at')) == (113.03, 228.6):
        n[1] = 'IR_RX_EN'
u506 = per.pins(per.by_ref('U506'))
per.remove([n for n in kids(per.root, 'no_connect') if pt(kid(n, 'at')) == u506['5']])
per.add_wire(u506['5'], (u506['5'][0] + 5.08, u506['5'][1]))
per.add_label('IR_RX_EN', (u506['5'][0] + 5.08, u506['5'][1]), 0)
testpoint(per, mcu, 'TP501', (330.2, 33.02), 'I2C_SDA', 'global', 'docs/design/peripherals_contract.json')
testpoint(per, mcu, 'TP502', (330.2, 43.18), 'I2C_SCL', 'global', 'docs/design/peripherals_contract.json')
for t in kids(per.root, 'text'):
    s = t[1]
    if s.startswith('IR RX shares ACC_EN'):
        t[1] = 'IR RX is powered from expander P1 (IR_RX_EN), independent of the accessory rail.'
    elif 'direction register 0xFB' in s:
        t[1] = s.replace('direction register 0xFB', 'direction register 0x09')
    elif s.startswith('Optional IR Receiver'):
        t[1] = 'IR Receiver (supply from expander P1)'

for s in (mcu, light, power, disp, per):
    s.save()

# ---------------------------------------------------------------- contracts
D = ROOT / 'docs/design'


def load(b):
    return json.loads((D / f'{b}_contract.json').read_text())


def save(b, d):
    (D / f'{b}_contract.json').write_text(json.dumps(d, indent=2, ensure_ascii=False) + '\n')


def get(d, ref):
    for k in ('components', 'two_terminal_support'):
        for c in d.get(k, []):
            if c['ref'] == ref:
                return c
    raise KeyError(ref)


TP = lambda ref, net: {'ref': ref, 'lib_id': 'Connector:TestPoint', 'value': net, 'pins': {'1': net},
                       'footprint': 'TestPoint:TestPoint_Pad_D1.0mm'}

m = load('mcu')
get(m, 'U201')['pins'].update({'4': None, '27': 'BTN_B_N'})
get(m, 'R202')['pins']['2'] = 'BTN_B_N'
tp = get(m, 'TP202'); tp['pins']['1'] = 'BTN_B_N'; tp['value'] = 'BOOT / BTN_B'
m['components'].append({'ref': 'SW403', 'mpn': 'SKSCLBE010', 'lib_id': 'Tinkerbadge_Peripherals:SKSCLBE010',
                        'pins': {'1': 'MCU_EN_SW', '2': 'MCU_EN_SW', '3': 'GND', '4': 'GND'},
                        'footprint': 'Tinkerbadge:SKSCLBE010', 'note': 'Recessed reset button. ' + NOTE})
m['components'].append({'ref': 'R415', 'lib_id': 'Device:R', 'pins': {'1': 'MCU_EN_SW', '2': 'MCU_EN'},
                        'footprint': 'Resistor_SMD:R_0603_1608Metric',
                        'note': '330R limits the C203 discharge current through the switch contact; EN low level about 0.1 V.'})
m['gpio']['0'] = 'BTN_B_N'
m['gpio']['4'] = 'NC'
m['unused_pins']['U201'] = sorted(set(m['unused_pins']['U201']) | {'4'}, key=int)
m['notes'] = [n.replace('GPIO0 BOOT10k pullup', 'GPIO0 is BOOT and button B with a 10k pullup (R202) and 100 nF (C412)') for n in m['notes']]
m['notes'].append('Button B is GPIO0: hold B through reset (SW403) for ROM download. GPIO4 is unused. EN RC is 10 ms, GPIO0 RC 1 ms, so the strap is high at release unless B is held. ' + NOTE)
save('mcu', m)

p = load('peripherals')
p['components'] = [c for c in p['components'] if c['ref'] != 'R414']
u = get(p, 'U506')
u['pins']['5'] = 'IR_RX_EN'
u['notes'] = 'Non-A address0x20; polled. Write output latch0x00 BEFORE direction0x09. P1 powers the IR receiver; P4-P7 unused, driven low.'
get(p, 'R507')['pins']['1'] = 'IR_RX_EN'
get(p, 'U504')['notes'] = 'Receiver supply comes from expander P1 through R507; independent of the accessory rail. MCU input no pulls while off.'
p['components'] += [TP('TP501', 'I2C_SDA'), TP('TP502', 'I2C_SCL')]
ex = p['interfaces']['expander']
ex['port_bits'] = {'0': 'CHARGER_CHG_N input', '1': 'IR_RX_EN output (high = receiver powered)', '2': 'ACC_EN output',
                   '3': 'ACC_FAULT_N input', '4': 'unused, output low', '5': 'unused, output low',
                   '6': 'unused, output low', '7': 'unused, output low'}
ex['direction_register'] = '0x09'
ex['note'] = 'Write the output latch 0x00 first, then direction 0x09 (inputs P0 and P3 only). An MCU reset does not reset the expander.'
p['interfaces']['power_status_inputs'] = ['CHARGER_CHG_N']
save('peripherals', p)

w = load('power')
w['two_terminal_support'].append({
    'ref': 'RT102', 'kind': 'R', 'value': '100k NTC B3950 1%', 'pins': {'1': 'BATT_NTC', '2': 'GND'}, 'fitted': True,
    'note': 'In parallel with RT101. Charge window 1.7-44.8 degC nominal, 0.1-48.4 degC over BQ24074 threshold/bias tolerance. ' + NOTE,
    'footprint': 'Resistor_SMD:R_0603_1608Metric',
    'footprint_status': 'standard KiCad library footprint; verify against the exact part drawing before fabrication'})
w['components'].append({'ref': 'TP101', 'mpn': None, 'facts': None, 'status': 'rear probe pad', 'pins': {'1': 'VSYS'},
                        'footprint': 'TestPoint:TestPoint_Pad_D1.0mm'})
save('power', w)

d = load('display')
j = get(d, 'J301')
j['exact_mpn'] = 'FH34SRJ-24S-0.5SH(50)'
j['footprint'] = 'Tinkerbadge:Hirose_FH34SRJ-24S-0.5SH_PanelOrder'
d['components'].append({'ref': 'TP301', 'exact_mpn': None, 'pins': [{'number': '1', 'name': 'pad', 'net': '+3V3_EPD', 'treatment': 'connected'}],
                        'kind': 'test point', 'populated': True, 'footprint': 'TestPoint:TestPoint_Pad_D1.0mm'})
save('display', d)
print('schematic and contracts updated')

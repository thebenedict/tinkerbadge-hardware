#!/usr/bin/env python3
"""Replace the SAO socket with the unpopulated expansion header. Schematic and contracts.

One-shot edit of the native sheets and block contracts as committed at c008fbd
(board revision 0.3). Run from the repository root after
tools/create_expansion_header_footprint.py, then
`kicad-cli sch upgrade --force tinkerbadge.kicad_sch`. Do not rerun on the
edited files. Design input: docs/design/expansion_header.md and its
independent review.

Changes
- J502 (SAO socket, EXP-02) removed.
- J503: unpopulated 2 x 5, 2.54 mm header (EXP-05). Odd row GND, ACC_3V3,
  EXT_SDA, EXT_SCL, IO4; even row TX, RX, IO42, IO47, GND. Standard header
  numbering for a part fitted on the front: pin 1 is top right from the front.
- R518-R522: 330R in series with TX, RX, IO42, IO47 and IO4 at the header.
- SAO_GPIO1 -> EXP_IO42, SAO_GPIO2 -> EXP_IO47; GPIO4 (was NC) -> EXP_IO4.
- UART_TX / UART_RX become global labels so the header branch can reach them;
  TP205 / TP206 stay directly on the MCU pins.
"""
import copy
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from schlib import Sheet, Sym, kid, kids, pt, prop, pval, parse, new_uuid  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
KICAD_SYM = pathlib.Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Connector_Generic.kicad_sym')
NOTE = 'expansion header 2026-11-12'
CONTRACT = 'docs/design/peripherals_contract.json'
HDR_LIB = 'Connector_Generic:Conn_02x05_Odd_Even'
HDR_FP = 'Tinkerbadge:Expansion_Header_2x05_P2.54mm'

# header pin -> (net at the pin, label kind)
HEADER = {
    '1': ('GND', 'global'), '3': ('ACC_3V3', 'label'), '5': ('EXT_SDA', 'global'), '7': ('EXT_SCL', 'global'),
    '9': ('HDR_IO4', 'label'),
    '2': ('HDR_TX', 'label'), '4': ('HDR_RX', 'label'), '6': ('HDR_IO42', 'label'), '8': ('HDR_IO47', 'label'),
    '10': ('GND', 'global'),
}
# series resistor: (MCU-side global net, header-side local net), in header pin order
SERIES = [('R518', 'UART_TX', 'HDR_TX'), ('R519', 'UART_RX', 'HDR_RX'), ('R520', 'EXP_IO42', 'HDR_IO42'),
          ('R521', 'EXP_IO47', 'HDR_IO47'), ('R522', 'EXP_IO4', 'HDR_IO4')]


def text(sheet, s, at, size=1.27):
    sheet.add(parse(f'(text "{s}" (exclude_from_sim no) (at {at[0]} {at[1]} 0) '
                    f'(effects (font (size {size} {size})) (justify left bottom)) (uuid "{new_uuid()}"))'))


def to_global(sheet, name):
    """Turn every local label of this name into a global label at the same place."""
    for n in list(kids(sheet.root, 'label')):
        if n[1] == name:
            at = kid(n, 'at')
            rot = int(float(at[3])) if len(at) > 3 else 0
            sheet.remove([n])
            sheet.add_label(name, (float(at[1]), float(at[2])), rot, kind='global', shape='input')


mcu = Sheet('mcu.kicad_sch')
per = Sheet('peripherals.kicad_sch')

# ---------------------------------------------------------------- processor sheet
u201 = mcu.pins(mcu.by_ref('U201'))
mcu.remove([n for n in kids(mcu.root, 'no_connect') if pt(kid(n, 'at')) == u201['4']])
end = (u201['4'][0] - 5.08, u201['4'][1])
mcu.add_wire(u201['4'], end)
mcu.add_label('EXP_IO4', end, 180, kind='global', shape='input')
for n in kids(mcu.root, 'global_label'):
    if n[1] == 'SAO_GPIO1':
        n[1] = 'EXP_IO42'
    elif n[1] == 'SAO_GPIO2':
        n[1] = 'EXP_IO47'
to_global(mcu, 'UART_TX')
to_global(mcu, 'UART_RX')
text(mcu, 'TX / RX also reach expansion header J503 through 330R.\\nGPIO4, 42, 47 are header GPIOs.', (198.12, 55.88), 1.0)

# ---------------------------------------------------------------- expansion sheet
j502 = per.by_ref('J502')
template = copy.deepcopy(j502)
per.remove_symbol('J502')

# library symbol for the 2 x 5 header, from the installed KiCad library
lib = parse(KICAD_SYM.read_text())
sym = copy.deepcopy(next(s for s in kids(lib, 'symbol') if s[1] == 'Conn_02x05_Odd_Even'))
sym[1] = HDR_LIB
kid(per.root, 'lib_symbols').append(sym)
per.libs[HDR_LIB] = sym

X0, Y0 = 189.23, 193.04
j = template
kid(j, 'lib_id')[1] = HDR_LIB
at = kid(j, 'at')
at[1], at[2] = X0, Y0
kid(j, 'uuid')[1] = new_uuid()
for k, v in (('in_bom', 'no'), ('dnp', 'yes'), ('in_pos_files', 'no')):
    if kid(j, k) is not None:
        kid(j, k)[1] = Sym(v)
for p in kids(j, 'pin'):
    j.remove(p)
inst = kid(j, 'instances')
j.remove(inst)
for n in range(1, 11):
    j.append(parse(f'(pin "{n}" (uuid "{new_uuid()}"))'))
j.append(inst)
kid(kid(kid(inst, 'project'), 'path'), 'reference')[1] = 'J503'
for p in kids(j, 'property'):
    a = kid(p, 'at')
    a[1], a[2] = X0, Y0
FIELDS = {
    'Reference': 'J503', 'Value': '2x05 2.54 mm, not fitted', 'Footprint': HDR_FP,
    'Description': 'Unpopulated expansion header: ten plated holes on a 2.54 mm grid, odd/even numbering',
    'Contract': CONTRACT, 'FootprintStatus': 'Project footprint on the KiCad PinHeader_2x05_P2.54mm hole pattern; placement review pending',
    'MPN': 'PCB holes only: no fitted component', 'Population': 'DNP', 'Rating': '2x05 P2.54mm THT holes, 1.0 mm drill',
}
for k, v in FIELDS.items():
    prop(j, k)[2] = v
for k in ('LCSC', 'Assembly'):
    if prop(j, k) is not None:
        j.remove(prop(j, k))
ref, val = kid(prop(j, 'Reference'), 'at'), kid(prop(j, 'Value'), 'at')
ref[1], ref[2] = X0 + 1.27, Y0 - 12.7
val[1], val[2] = X0 + 1.27, Y0 - 10.16
per.add(j)
per.set_prop('J503', 'Note', 'Pin numbers are those of a standard header fitted on the front. 3.3 V signals only.')

pins = per.pins(j)
for num, (net, kind) in HEADER.items():
    x, y = pins[num]
    left = int(num) % 2 == 1
    # on the left, global labels sit further out than local ones so that neighbouring rows do not collide
    reach = (12.7 if kind == 'global' else 2.54) if left else 2.54
    end = (round(x - reach, 2), y) if left else (round(x + reach, 2), y)
    per.add_wire((x, y), end)
    per.add_label(net, end, 180 if left else 0, kind=kind, shape='input')

# series resistors, cloned from the horizontal R507
RX, RY0, RPITCH = 190.5, 139.7, 7.62
for i, (ref_, mcu_net, hdr_net) in enumerate(SERIES):
    y = round(RY0 + i * RPITCH, 2)
    r = per.clone_symbol('R507', ref_, (RX, y), 90, '330')
    for k, v in {'MPN': '0603WAF3300T5E', 'LCSC': 'C23138', 'Rating': '330R 1%', 'Population': 'fitted',
                 'Contract': CONTRACT, 'Assembly': 'JLCPCB SMT'}.items():
        per.set_prop(ref_, k, v)
    a = kid(prop(r, 'Reference'), 'at')
    a[1], a[2] = RX, round(y - 2.54, 2)
    a = kid(prop(r, 'Value'), 'at')
    a[1], a[2] = RX, round(y + 2.54, 2)
    rp = per.pins(r)
    lft, rgt = (rp['1'], rp['2']) if rp['1'][0] < rp['2'][0] else (rp['2'], rp['1'])
    assert lft == rp['1'], 'pin 1 must be the MCU side'
    a, b = (round(lft[0] - 2.54, 2), y), (round(rgt[0] + 2.54, 2), y)
    per.add_wire(lft, a)
    per.add_wire(rgt, b)
    per.add_label(mcu_net, a, 180, kind='global', shape='input')
    per.add_label(hdr_net, b, 0)

# outlines: narrow the expander block (its right half is empty) and add the header block
for r in kids(per.root, 'rectangle'):
    if pt(kid(r, 'start')) == (17.78, 124.46) and pt(kid(r, 'end')) == (182.88, 212.09):
        kid(r, 'end')[1] = 152.4
        box = copy.deepcopy(r)
        kid(box, 'start')[1], kid(box, 'end')[1] = 156.21, 214.63
        kid(box, 'uuid')[1] = new_uuid()
        per.add(box)
        break
else:
    raise SystemExit('expander outline not found')
title = next(t for t in kids(per.root, 'text') if t[1] == 'Status / Enable Expander')
t2 = copy.deepcopy(title)
t2[1] = 'Expansion Header (not fitted)'
kid(t2, 'at')[1] = 156.21
kid(t2, 'uuid')[1] = new_uuid()
per.add(t2)
text(per, 'Series 330R on each GPIO and on the UART branch.\\nTP205 / TP206 stay direct on TX / RX.', (158.75, 132.08), 1.0)
text(per, 'J503: bare 2.54 mm holes, pin 1 square, top-right from the front.\\n'
          '3.3 V signals only. ACC_3V3 is shared with Qwiic: 50 mA total.\\n'
          'TX carries the ROM boot log. IO4 pulses low at power-up.', (158.75, 209.55), 1.0)
for t in kids(per.root, 'text'):
    if t[1] == 'Protected Accessory Rail + Qwiic / SAO':
        t[1] = 'Protected Accessory Rail + Qwiic'
    elif t[1].startswith('Qwiic + SAO: 3.3 V only'):
        t[1] = 'Qwiic + expansion header: 3.3 V only. 50 mA shared budget.'

mcu.save()
per.save()

# ---------------------------------------------------------------- contracts
D = ROOT / 'docs/design'


def load(b):
    return json.loads((D / f'{b}_contract.json').read_text())


def save(b, d):
    (D / f'{b}_contract.json').write_text(json.dumps(d, indent=2, ensure_ascii=False) + '\n')


def get(d, ref):
    for c in d['components']:
        if c['ref'] == ref:
            return c
    raise KeyError(ref)


m = load('mcu')
upins = get(m, 'U201')['pins']
if isinstance(upins, list):
    for q in upins:
        q['net'] = {'4': 'EXP_IO4', '24': 'EXP_IO47', '35': 'EXP_IO42'}.get(str(q['number']), q['net'])
else:
    upins.update({'4': 'EXP_IO4', '24': 'EXP_IO47', '35': 'EXP_IO42'})
m['gpio'].update({'4': 'EXP_IO4', '42': 'EXP_IO42', '47': 'EXP_IO47'})
m['unused_pins']['U201'] = [p for p in m['unused_pins']['U201'] if p != '4']
m['notes'] = [n.replace('External I2C and SAO are separate from onboard bus', 'External I2C (Qwiic and expansion header) is separate from the onboard bus')
              .replace('GPIO4 is unused. ', '') for n in m['notes']]
m['notes'].append('GPIO4, GPIO42 and GPIO47 go to expansion header J503 through 330R (R522, R520, R521). UART0 TX/RX keep their direct '
                  'probe pads TP205/TP206 and also reach J503 through R518/R519. GPIO4 pulses low for about 60 us at power-up; '
                  'TX carries the ROM boot log. ' + NOTE)
save('mcu', m)

p = load('peripherals')
p['components'] = [c for c in p['components'] if c['ref'] != 'J502']
p['components'].append({
    'ref': 'J503', 'value': '2x05 2.54 mm, not fitted', 'bom_id': 'EXP-05', 'package': '2x05 P2.54mm THT holes, 1.0 mm drill',
    'population': 'DNP', 'lib_id': HDR_LIB,
    'pins': {'1': 'GND', '2': 'HDR_TX', '3': 'ACC_3V3', '4': 'HDR_RX', '5': 'EXT_SDA', '6': 'HDR_IO42', '7': 'EXT_SCL',
             '8': 'HDR_IO47', '9': 'HDR_IO4', '10': 'GND'},
    'pin_fact_file': 'docs/components/Expansion_Header_2x05.pins.json',
    'notes': 'Unpopulated expansion header on the front top edge between role LEDs D402/D403. Standard header numbering for a part fitted '
             'on the front; pin 1 is top right. Front view, left to right, top row: IO4, SCL, SDA, 3V3, GND; bottom row: GND, IO47, IO42, RX, TX. '
             '3.3 V signals only; supply shared with Qwiic. See design/expansion_header.md.',
    'footprint': HDR_FP,
    'footprint_status': 'project footprint on the KiCad 2x05 2.54 mm hole pattern; placement review pending'})
for ref_, mcu_net, hdr_net in SERIES:
    p['components'].append({'ref': ref_, 'value': '330R 1%', 'kind': 'R', 'package': '0603', 'population': 'fitted',
                            'pins': {'1': mcu_net, '2': hdr_net},
                            'notes': 'Series protection at expansion header J503. Same part as R415 (0603WAF3300T5E, C23138).',
                            'footprint': 'Resistor_SMD:R_0603_1608Metric'})
req = p['interfaces']['mcu_required']
for old in ('SAO_GPIO1', 'SAO_GPIO2'):
    req.pop(old, None)
req.update({'EXP_IO4': '3.3V GPIO/ADC1_CH3/RTC wake; highZ/low while accessory rail off',
            'EXP_IO42': '3.3V GPIO highZ/low while accessory rail off',
            'EXP_IO47': '3.3V GPIO highZ/low while accessory rail off',
            'UART_TX': 'UART0 TX; also on header through R518; stop driving before accessory rail off if a header accessory uses it',
            'UART_RX': 'UART0 RX; also on header through R519'})
p['interfaces']['external_i2c']['notes'] = ('Separate MCU bus shared by Qwiic J501 and expansion header J503. Inputs highZ/no pulls whileoff. '
                                            'Pull-ups are on ACC_3V3, so the bus is unusable while the accessory rail is off. '
                                            'Duplicate accessory addresses not resolved.')
p['interfaces']['expansion_header'] = {
    'ref': 'J503', 'series_resistors': {'R518': 'TX', 'R519': 'RX', 'R520': 'IO42', 'R521': 'IO47', 'R522': 'IO4'},
    'series_value_ohm': 330, 'signal_level_V': 3.3, 'supply': 'ACC_3V3, shared 50 mA normal budget with Qwiic',
    'pin_order_front_view_left_to_right': {'top_row_pins_9_7_5_3_1': ['IO4', 'SCL', 'SDA', '3V3', 'GND'],
                                           'bottom_row_pins_10_8_6_4_2': ['GND', 'IO47', 'IO42', 'RX', 'TX']},
    'numbering': 'KiCad PinHeader_2x05 odd/even pattern rotated, not mirrored: standard for a header fitted on the front',
    'record': 'docs/design/expansion_header.md'}
p['unresolved'].append('Accessory fault figures in interfaces.rails and the U505 note were calculated for RILIM 210k. The fitted R508 is 200k 1%: '
                       '114.7 mA minimum, 135.3 mA nominal, 159.4 mA maximum (TPS2553 equations 1-3), above the 155 mA upstream reserve. '
                       'Found by docs/design/review_expansion_header.md; power budget to be re-stated.')
p['unresolved'] = [u.replace('Qwiic cable and SAO keyed physical mating/footprint review before layout.',
                             'Qwiic cable physical mating review before layout. Expansion header J503 placement and enclosure access review.')
                   for u in p['unresolved']]
p['revision'] = {'date': '2026-11-12',
                 'change': 'Remove SAO socket J502. Add unpopulated 2x5 expansion header J503 with 330R series resistors R518-R522; '
                           'SAO_GPIO1/2 renamed EXP_IO42/EXP_IO47, GPIO4 added as EXP_IO4, UART0 branched to the header.',
                 'previous_commit': 'c008fbd', 'review': 'docs/design/review_expansion_header.md'}
save('peripherals', p)

(ROOT / 'docs/components/Expansion_Header_2x05.pins.json').write_text(json.dumps({
    'mpn': None, 'package': 'Ten plated holes, 2 x 5 on a 2.54 mm grid, 1.0 mm drill; KiCad odd/even numbering',
    'source': {'footprint': 'Tinkerbadge.pretty/Expansion_Header_2x05_P2.54mm.kicad_mod',
               'pattern': 'KiCad Connector_PinHeader_2.54mm:PinHeader_2x05_P2.54mm_Vertical'},
    'pins': [{'number': str(n), 'name': f"{'top' if n % 2 else 'bottom'} row, hole {(n + 1) // 2} from the right (front view)"}
             for n in range(1, 11)]}, indent=2) + '\n')
print('schematic and contracts updated')

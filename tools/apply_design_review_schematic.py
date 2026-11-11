#!/usr/bin/env python3
"""Apply the 2026-11-10 design-review schematic changes (docs/design/design_review_2026-11-10.md).

One-shot, non-idempotent edit of the native sheets. Run from the repository
root on a clean checkout of the pre-review schematic, then normalise with
`kicad-cli sch upgrade --force tinkerbadge.kicad_sch`.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from schlib import Sheet, kid, kids, pt, prop, pval, parse  # noqa: E402

pwr_n = [900]


def gnd(sheet, at, template=None):
    """Clone a GND power symbol so that its pin lands on `at`."""
    if template is None:
        template = next(pval(s, 'Reference') for s in sheet.symbols()
                        if pval(s, 'Reference').startswith('#') and pval(s, 'Value') == 'GND'
                        and float(kid(s, 'at')[3]) == 0 and kid(s, 'mirror') is None)
    pwr_n[0] += 1
    sheet.clone_symbol(template, f'#PWR{pwr_n[0]}', at)


def drop_stub(sheet, pin_pt):
    ws, pts = sheet.trace(pin_pt)
    sheet.remove(ws + sheet.items_at(pts))


def set_fp(sheet, ref, fp, mpn=None, value=None):
    sheet.set_prop(ref, 'Footprint', fp)
    if mpn:
        sheet.set_prop(ref, 'MPN', mpn)
    if value:
        sheet.set_prop(ref, 'Value', value)


def set_dnp(sheet, ref, state=True):
    s = sheet.by_ref(ref)
    kid(s, 'dnp')[1] = type(kid(s, 'dnp')[1])('yes' if state else 'no')
    kid(s, 'in_bom')[1] = type(kid(s, 'in_bom')[1])('no' if state else 'yes')


# ---------------------------------------------------------------- power
p = Sheet('power.kicad_sch')

# 1. Battery ADC: plain 1M/1M divider with 100 nF, no analog switch.
for ref in ('U107', 'C115', 'R129', 'R130'):
    p.remove_symbol(ref)
for n in list(kids(p.root, 'label')):
    if n[1] == 'BAT_DIV_PRE':
        at = kid(n, 'at')
        p.remove([n])
        p.add_label('BAT_ADC', (float(at[1]), float(at[2])), 0, kind='global', shape='output')
p.set_prop('R127', 'Value', '1M 1%')
p.set_prop('R128', 'Value', '1M 1%')
p.set_prop('C116', 'Value', '100nF 6.3V X7R')

# 2. Charger input mode fixed at USB500: EN1 pulled high, EN2 low.
for ref in ('Q103', 'R110'):
    p.remove_symbol(ref)
u101 = p.pins(p.by_ref('U101'))
drop_stub(p, u101['9'])
p.add_nc(u101['9'])

# 3. Mux over-voltage supervisors unused (charger tolerates 28 V, OVP 10.5 V).
for ref in ('R103', 'R104', 'R105', 'R106'):
    p.remove_symbol(ref)
for pin in ('5', '4'):
    drop_stub(p, u101[pin])
x = 176.53
p.add_wire(u101['5'], (x, u101['5'][1]))
p.add_wire(u101['4'], (x, u101['4'][1]))
p.add_wire((x, u101['5'][1]), (x, u101['4'][1]))
p.add_wire((x, u101['4'][1]), (x, 66.04))
p.add_junction((x, u101['4'][1]))
gnd(p, (x, 66.04))

# 4. Charging enabled in hardware: CE tied low.
u102 = p.pins(p.by_ref('U102'))
p.remove_symbol('R120')
ce = u102['4']
p.add_wire(ce, (297.18, ce[1]))
p.add_wire((297.18, ce[1]), (297.18, 63.5))
gnd(p, (297.18, 63.5))

# 5. On-board cell-area NTC replaces the DNP thermistor connector.
j104 = p.pins(p.by_ref('J104'))
p.remove_symbol('J104')
for n in kids(p.root, 'label'):
    if n[1] == 'BATT_NTC_OPTIONAL':
        n[1] = 'BATT_NTC'
rt = p.clone_symbol('R113', 'RT101', (386.08, 107.95), 0, '10k NTC B3950 1%')
rtp = p.pins(rt)
p.add_wire(rtp['1'], (rtp['1'][0], 99.06))
p.add_label('BATT_NTC', (rtp['1'][0], 99.06), 90)
gnd(p, rtp['2'])
set_fp(p, 'RT101', 'Resistor_SMD:R_0603_1608Metric', 'NTC 10k B25/50=3950 1% 0603 (select at quote)')
p.set_prop('RT101', 'Description', 'NTC thermistor under the cell; BQ24074 TS charge-temperature window')

# 5b. Charger PGOOD is redundant with USB/dock presence sensing: leave it unconnected.
p.remove_symbol('R115')
drop_stub(p, u102['7'])
p.add_nc(u102['7'])

# 5c. USB ESD array: map channels in connector order (CC2, D+, D-, CC1) and tie
# each NC twin pad to its line so the traces run straight through the package.
u105 = p.pins(p.by_ref('U105'))
for pin in ('1', '2', '4', '5'):
    drop_stub(p, u105[pin])
p.remove([n for n in kids(p.root, 'no_connect') if pt(kid(n, 'at')) in {u105[k] for k in ('6', '7', '9', '10')}])
for pins, net, kind in ((('1', '10'), 'USB_CC2', 'label'), (('2', '9'), 'USB_DP', 'global'),
                        (('4', '7'), 'USB_DM', 'global'), (('5', '6'), 'USB_CC1', 'label')):
    for pin in pins:
        x, y = u105[pin]
        left = x < 100.33
        end = (x - 2.54, y) if left else (x + 2.54, y)
        p.add_wire((x, y), end)
        p.add_label(net, end, 180 if left else 0, kind=kind, shape='bidirectional')

# 6. E24 / 1 % value consolidation.
for ref, val in {'R107': '30k 1%', 'R108': '10k 1%', 'R109': '82k 1%', 'R112': '4.3k 1%',
                 'R113': '3.3k 1%', 'R114': '47k 1%', 'R117': '56k 1%', 'R118': '10k 1%'}.items():
    p.set_prop(ref, 'Value', val)

# 7. Footprints for previously blank parts.
set_fp(p, 'U105', 'Package_SON:USON-10_2.5x1.0mm_P0.5mm')
set_fp(p, 'J102', 'Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal', 'S2B-PH-K-S(LF)(SN)', 'LiPo JST-PH')
set_fp(p, 'J103', 'Tinkerbadge:Dock_Pads_2x_4x6mm', 'PCB pads only: no fitted component', 'Dock 5V pads')
kid(p.by_ref('J103'), 'in_bom')[1] = type(kid(p.by_ref('J103'), 'in_bom')[1])('no')
set_fp(p, 'L101', 'Inductor_SMD:L_Coilcraft_XxL4020', 'XFL4015-471MEB')

# Sheet notes that described the removed circuits.
for t in kids(p.root, 'text'):
    s = t[1]
    if 'R120 fitted' in s:
        t[1] = ('CHARGING\\nCE tied low: charger enabled, 270 mA (R113), USB500 input limit.\\n'
                'RT101 10k NTC sits under the cell: nominal 3-47 degC charge window.\\n'
                'J102 is JST-PH, pin 1 = battery +. CHECK PACK POLARITY before connecting.\\n'
                'Use a protected 1S 4.2 V pack rated for >= 300 mA charge.').replace('\\n', '\n')
    elif 'charging disabled' in s:
        t[1] = s.replace('charging disabled', 'charger enabled')
    elif 'Battery ADC' in s:
        t[1] = 'Battery ADC (VBAT/2) / source presence'
p.save()

# -------------------------------------------------------------- display
d = Sheet('display.kicad_sch')
j301 = d.pins(d.by_ref('J301'))
for ref in ('U301', 'C312', 'R303', 'R304', 'R305', 'R306', 'R307'):
    d.remove_symbol(ref)
for pin, net in {'14': 'EPD_MOSI', '13': 'EPD_SCK', '12': 'EPD_CS_N', '11': 'EPD_DC', '10': 'EPD_RST_N'}.items():
    x, y = j301[pin]
    d.add_wire((x, y), (x - 5.08, y))
    d.add_label(net, (x - 5.08, y), 180, kind='global', shape='input')
set_fp(d, 'J301', 'Connector_FFC-FPC:Hirose_FH12-24S-0.5SH_1x24-1MP_P0.50mm_Horizontal', 'FH12-24S-0.5SH(55)')
set_fp(d, 'L301', 'Inductor_SMD:L_Bourns-SRN4018', 'SRN4018-680M')
for t in kids(d.root, 'text'):
    s = t[1]
    if s.startswith('U301 isolates'):
        t[1] = 'MCU drives the panel directly. Firmware must drive SPI/DC/RST low before EPD_EN goes low.'
    elif 'J301 intentionally has no PCB footprint' in s:
        t[1] = 'J301: FH12 bottom-contact footprint. VERIFY flex pin-1 side on a real panel before fab.'
    elif s.startswith('Boot / off-state bias'):
        t[1] = 'BUSY bias'
d.save()

# ---------------------------------------------------------- peripherals
q = Sheet('peripherals.kicad_sch')
u506 = q.pins(q.by_ref('U506'))
for ref in ('R514', 'R515', 'R516', 'R517'):
    q.remove_symbol(ref)          # unused expander pins: firmware drives them low
for pin in ('5', '9', '10', '11', '12'):
    drop_stub(q, u506[pin])
    q.add_nc(u506[pin])
q.set_prop('R508', 'Value', '200k')
for t in kids(q.root, 'text'):
    if t[1].startswith('50 mA normal total'):
        t[1] = '50 mA normal total. 200k / 1% sets roughly 115-160 mA current limit.'
set_fp(q, 'J502', 'Tinkerbadge:SAO_Socket_2x03_Front', 'SFH11-NBPC-D03-ST-BK')
set_fp(q, 'AE501', 'Tinkerbadge:NFC_Coil_Rear_18x13', 'PCB feature: no fitted component', 'NFC PCB coil')
set_dnp(q, 'C508')
q.set_prop('C507', 'Value', '27p C0G (tune)')
q.set_prop('C507', 'Rating', '27p C0G 50V')
q.set_prop('C507', 'Population', 'fitted')
q.set_prop('R508', 'Rating', '200k 1%')
kid(q.by_ref('AE501'), 'in_bom')[1] = type(kid(q.by_ref('AE501'), 'in_bom')[1])('no')
q.save()
print('schematic changes applied')

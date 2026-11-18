#!/usr/bin/env python3
"""Board placement for the unpopulated expansion header. KiCad Python.

Usage: tools/run_pcb_native.sh tools/apply_expansion_header_board.py NETLIST BOARD

Starts from the board committed at c008fbd (revision 0.3) and the netlist
exported after tools/apply_expansion_header_schematic.py. It stops at
placement: nothing is routed.

- removes J502 (SAO socket);
- places J503 (Tinkerbadge:Expansion_Header_2x05_P2.54mm) on the front top
  edge and R518-R522 in a row directly below it;
- renames the nets that changed name and assigns every pad net from the netlist;
- clears the header area of the copper that ran to the socket: the five nets
  that reached J502 are cut back to the edge of the header window, and any
  other copper that touches a new pad is reported and removed;
- marks the board revision 0.4 and refills zones.
Do not rerun on the edited board. Design input: docs/design/expansion_header.md.
"""
import pathlib
import sys

import pcbnew

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from sync_board_design_review import read_netlist, KICAD_FP  # noqa: E402
from schlib import parse, kids, kid  # noqa: E402

MM = pcbnew.FromMM
mm = pcbnew.ToMM
PROJ = str(ROOT / 'Tinkerbadge.pretty')

HDR = ('J503', 190.0, 106.4)
PITCH = 2.54
ROW_Y = 110.75
# resistor: column (0 = left) under the header pin it serves. Bottom row from the left is
# GND(10), IO47(8), IO42(6), RX(4), TX(2); the IO4 resistor takes the free column under pins 9/10.
SERIES = {'R518': 4, 'R519': 3, 'R520': 2, 'R521': 1, 'R522': 0}
REMOVED = ['J502']
RENAME_NETS = {
    'SAO_GPIO1': 'EXP_IO42', 'SAO_GPIO2': 'EXP_IO47',
    '/02  PROCESSOR + RECOVERY/UART_TX': 'UART_TX', '/02  PROCESSOR + RECOVERY/UART_RX': 'UART_RX',
}
# nets that ran to the socket; their copper inside WINDOW is removed and cut back to its edge
CUT_NETS = ['/05  SENSORS + EXPANSION/ACC_3V3', 'EXT_SDA', 'EXT_SCL', 'EXP_IO42', 'EXP_IO47']
WINDOW = (183.0, 100.0, 197.6, 112.4)
REV_TEXT = {'rev 0.3  2026-11-11': 'rev 0.4  2026-11-12',
            'TINKER BADGE 110 x 80 - REV 0.3 2026-11-11 - PROTOTYPE, VISUAL REVIEW REQUIRED':
            'TINKER BADGE 110 x 80 - REV 0.4 2026-11-12 - PLACEMENT REVIEW, NOT ROUTED'}


def load(lib, nick, name):
    f = pcbnew.FootprintLoad(lib, name)
    assert f is not None, (lib, name)
    f.SetFPID(pcbnew.LIB_ID(nick, name))
    return f


def inside(p):
    x, y = mm(p.x), mm(p.y)
    return WINDOW[0] <= x <= WINDOW[2] and WINDOW[1] <= y <= WINDOW[3]


def crossing(a, b):
    """Point where segment a(inside) -> b(outside) leaves WINDOW."""
    ax, ay, bx, by = mm(a.x), mm(a.y), mm(b.x), mm(b.y)
    best = 1.0
    for lo, hi, p0, d in ((WINDOW[0], WINDOW[2], ax, bx - ax), (WINDOW[1], WINDOW[3], ay, by - ay)):
        if d > 0:
            best = min(best, (hi - p0) / d)
        elif d < 0:
            best = min(best, (lo - p0) / d)
    return pcbnew.VECTOR2I(MM(ax + (bx - ax) * best), MM(ay + (by - ay) * best))


def main(netlist, board_path):
    comps, padnets = read_netlist(netlist)
    tree = parse(open(netlist).read())
    descr = {kid(c, 'ref')[1]: kid(c, 'description')[1] for c in kids(kid(tree, 'components'), 'comp') if kid(c, 'description')}
    b = pcbnew.LoadBoard(board_path)

    # ---- footprints
    for ref in REMOVED:
        b.RemoveNative(b.FindFootprintByReference(ref))
    ref, x, y = HDR
    f = load(PROJ, 'Tinkerbadge', 'Expansion_Header_2x05_P2.54mm')
    f.SetReference(ref)
    f.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
    b.Add(f)
    f.SetOrientationDegrees(0)
    for ref, col in SERIES.items():
        r = load(f'{KICAD_FP}/Resistor_SMD.pretty', 'Resistor_SMD', 'R_0603_1608Metric')
        r.SetReference(ref)
        r.SetPosition(pcbnew.VECTOR2I(MM(HDR[1] + (col - 2) * PITCH), MM(ROW_Y)))
        b.Add(r)
        r.SetOrientationDegrees(90)
        pad = {p.GetNumber(): p.GetPosition().y for p in r.Pads()}
        if pad['2'] > pad['1']:                   # pad 2 is the header side: it must face the header
            r.SetOrientationDegrees(270)
        r.Reference().SetLayer(pcbnew.F_Fab)
        r.Reference().SetVisible(True)

    # ---- nets
    nets = b.GetNetsByName()

    def net(name):
        if not nets.has_key(name):
            ni = pcbnew.NETINFO_ITEM(b, name)
            b.Add(ni)
            return ni
        return nets[name]

    for t in b.GetTracks():
        if t.GetNetname() in RENAME_NETS:
            t.SetNet(net(RENAME_NETS[t.GetNetname()]))
    for fp in b.GetFootprints():
        ref = fp.GetReference()
        if ref not in comps:
            continue
        fp.SetValue(comps[ref][0])
        for name, value in comps[ref][2].items():
            if name in ('Reference', 'Value', 'Footprint', 'Sheetname', 'Sheetfile', 'ki_fp_filters', 'ki_keywords', 'ki_description'):
                continue
            if not fp.HasField(name):
                fld = pcbnew.PCB_FIELD(fp, pcbnew.FIELD_T_USER, name)
                fld.SetVisible(False)
                fld.SetLayer(pcbnew.B_Fab if fp.IsFlipped() else pcbnew.F_Fab)
                fld.SetPosition(fp.GetPosition())
                fp.Add(fld)
            fp.GetField(name).SetText(value)
        if ref in ('J503', *SERIES) and ref in descr:
            fp.GetField('Description').SetText(descr[ref])
        fp.SetDNP('dnp' in comps[ref][3])
        fp.SetExcludedFromBOM('exclude_from_bom' in comps[ref][3])
        for p in fp.Pads():
            want = padnets.get((ref, p.GetNumber()))
            if want is not None and p.GetNetname() != want:
                p.SetNet(net(want))
    j = b.FindFootprintByReference('J503')
    j.SetExcludedFromPosFiles(True)

    # ---- copper that ran to the socket: remove inside the window, cut back at its edge
    removed = trimmed = 0
    for t in list(b.GetTracks()):
        if t.GetNetname() not in CUT_NETS:
            continue
        if t.Type() == pcbnew.PCB_VIA_T:
            if inside(t.GetPosition()):
                b.RemoveNative(t)
                removed += 1
            continue
        a_in, b_in = inside(t.GetStart()), inside(t.GetEnd())
        if a_in and b_in:
            b.RemoveNative(t)
            removed += 1
        elif a_in:
            t.SetStart(crossing(t.GetStart(), t.GetEnd()))
            trimmed += 1
        elif b_in:
            t.SetEnd(crossing(t.GetEnd(), t.GetStart()))
            trimmed += 1

    # ---- any other copper touching a new pad
    hits = []
    for ref in ['J503', *SERIES]:
        fp = b.FindFootprintByReference(ref)
        for p in fp.Pads():
            box = p.GetBoundingBox()
            box.Inflate(MM(0.2))
            for t in list(b.GetTracks()):
                if t.GetNetname() == p.GetNetname():
                    continue
                on = t.Type() == pcbnew.PCB_VIA_T or p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH or p.IsOnLayer(t.GetLayer())
                if on and t.HitTest(box, False):
                    s = t.GetStart()
                    hits.append((ref, p.GetNumber(), t.GetNetname(), b.GetLayerName(t.GetLayer()), round(mm(s.x), 2), round(mm(s.y), 2)))
                    b.RemoveNative(t)

    # ---- revision marking
    for d in b.GetDrawings():
        if d.Type() == pcbnew.PCB_TEXT_T and d.GetText() in REV_TEXT:
            d.SetText(REV_TEXT[d.GetText()])

    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(board_path, b)
    print('removed', REMOVED, '| window copper removed', removed, 'cut back', trimmed)
    print('other copper removed at new pads:', len(hits))
    for h in hits:
        print('  ', *h)
    for ref in ['J503', *SERIES]:
        fp = b.FindFootprintByReference(ref)
        p = fp.GetPosition()
        print(ref, round(mm(p.x), 3), round(mm(p.y), 3), fp.GetOrientationDegrees(),
              [(q.GetNumber(), q.GetNetname().split('/')[-1], round(mm(q.GetPosition().x), 2), round(mm(q.GetPosition().y), 2)) for q in fp.Pads()])


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

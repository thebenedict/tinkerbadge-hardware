#!/usr/bin/env python3
"""Bring tinkerbadge.kicad_pcb in line with the post-review schematic.

Run with KiCad's bundled Python (pcbnew). Reads an exported KiCad netlist,
removes footprints that left the schematic, adds and places the newly
resolved footprints, reassigns every pad net, and rips copper that belonged
to changed nets or collides with a new pad. Routing is completed afterwards by
tools/route_remaining.py.
"""
import pathlib
import sys

import pcbnew

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from schlib import parse, kids, kid  # noqa: E402

KICAD_FP = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints'
MM = pcbnew.FromMM

# reference: (library dir, footprint, x, y, rotation, flipped)
NEW = {
    'RT101': (f'{KICAD_FP}/Resistor_SMD.pretty', 'R_0603_1608Metric', 168.8, 123.0, 90, False),
    'U105': (f'{KICAD_FP}/Package_SON.pretty', 'USON-10_2.5x1.0mm_P0.5mm', 197.0, 126.0, 0, False),
    'J102': (f'{KICAD_FP}/Connector_JST.pretty', 'JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal', 175.5, 140.5, 0, True),
    'J103': (str(ROOT / 'Tinkerbadge.pretty'), 'Dock_Pads_2x_4x6mm', 124.0, 175.5, 0, False),
    'L101': (f'{KICAD_FP}/Inductor_SMD.pretty', 'L_Coilcraft_XxL4020', 144.5, 147.0, 270, False),
    'L301': (f'{KICAD_FP}/Inductor_SMD.pretty', 'L_Bourns-SRN4018', 167.0, 152.0, 270, False),
    'J301': (f'{KICAD_FP}/Connector_FFC-FPC.pretty', 'Hirose_FH12-24S-0.5SH_1x24-1MP_P0.50mm_Horizontal', 198.5, 145.0, 90, False),
    'J502': (str(ROOT / 'Tinkerbadge.pretty'), 'SAO_Socket_2x03_Front', 190.75, 105.0, 0, False),
    'AE501': (str(ROOT / 'Tinkerbadge.pretty'), 'NFC_Coil_Rear_18x13', 191.0, 172.5, 0, False),
}
LIB_NICK = {'Tinkerbadge.pretty': 'Tinkerbadge'}
# existing footprints repositioned by the review: reference: (x, y, rotation)
MOVED = {
    'R102': (199.3, 123.4, 180),   # CC2 pull-down beside its connector row
    'C512': (191.3, 151.3, 90),    # clear of the display-connector via lattice
}
DROP_REVIEW = ['RES_J102', 'RES_J103', 'RES_J301', 'RES_J502', 'RES_L101', 'RES_L301', 'RES_U105', 'MECH_NFC']
BIG = {'GND', '+3V3', '+3V3_EPD', '/01  POWER + CHARGING/VSYS', 'USB_VBUS', 'DOCK_5V'}


def read_netlist(path):
    t = parse(open(path).read())
    comps = {}
    for c in kids(kid(t, 'components'), 'comp'):
        fields = {p[1][1]: p[2][1] for p in kids(c, 'property') if len(p) > 2 and isinstance(p[2], list) and len(p[2]) > 1}
        flags = {p[1][1] for p in kids(c, 'property') if len(p) == 2}
        comps[kid(c, 'ref')[1]] = (kid(c, 'value')[1], kid(c, 'footprint')[1] if kid(c, 'footprint') else '', fields, flags)
    pads = {}
    for n in kids(kid(t, 'nets'), 'net'):
        for node in kids(n, 'node'):
            pads[(kid(node, 'ref')[1], kid(node, 'pin')[1])] = kid(n, 'name')[1]
    return comps, pads


def main(netlist, board_path):
    comps, padnets = read_netlist(netlist)
    b = pcbnew.LoadBoard(board_path)
    old = {}
    for f in b.GetFootprints():
        for p in f.Pads():
            old[(f.GetReference(), p.GetNumber())] = p.GetNetname()

    # 1. remove footprints that left the schematic, and resolved placeholders
    removed = []
    doomed = []
    for f in list(b.GetFootprints()):
        ref = f.GetReference()
        electrical = any(p.GetNumber() for p in f.Pads()) and not ref.startswith(('H', 'MECH', 'RES'))
        if (electrical and ref not in comps) or ref in DROP_REVIEW:
            removed.append(ref)
            doomed.append(f)
    for f in doomed:
        b.RemoveNative(f)

    # 2. add newly resolved footprints
    have = {f.GetReference() for f in b.GetFootprints()}
    for ref, (lib, name, x, y, rot, flip) in NEW.items():
        if ref in have:
            continue
        f = pcbnew.FootprintLoad(lib, name)
        assert f is not None, (lib, name)
        nick = LIB_NICK.get(pathlib.Path(lib).name, pathlib.Path(lib).stem)
        f.SetFPID(pcbnew.LIB_ID(nick, name))
        f.SetReference(ref)
        f.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        b.Add(f)
        if flip:
            f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        f.SetOrientationDegrees(rot)

    for ref, (x, y, rot) in MOVED.items():
        f = b.FindFootprintByReference(ref)
        f.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        f.SetOrientationDegrees(rot)
        for p in f.Pads():
            for t in list(b.GetTracks()):
                if t.GetNetname() == p.GetNetname() and t.Type() != pcbnew.PCB_VIA_T and (p.HitTest(t.GetStart()) or p.HitTest(t.GetEnd())):
                    pass

    # 3. values and pad nets from the netlist
    nets = b.GetNetsByName()

    def net(name):
        if not nets.has_key(name):
            ni = pcbnew.NETINFO_ITEM(b, name)
            b.Add(ni)
            return ni
        return nets[name]

    changed = set()
    for f in b.GetFootprints():
        ref = f.GetReference()
        if ref not in comps:
            continue
        f.SetValue(comps[ref][0])
        for name, value in comps[ref][2].items():
            if name in ('Reference', 'Value', 'Footprint', 'Sheetname', 'Sheetfile', 'ki_fp_filters', 'ki_keywords', 'ki_description'):
                continue
            if not f.HasField(name):
                fld = pcbnew.PCB_FIELD(f, pcbnew.FIELD_T_USER, name)
                fld.SetVisible(False)
                fld.SetLayer(pcbnew.F_Fab if not f.IsFlipped() else pcbnew.B_Fab)
                fld.SetPosition(f.GetPosition())
                f.Add(fld)
            f.GetField(name).SetText(value)
        f.SetDNP('dnp' in comps[ref][3])
        f.SetExcludedFromBOM('exclude_from_bom' in comps[ref][3])
        for p in f.Pads():
            num = p.GetNumber()
            if not num:
                continue
            want = padnets.get((ref, num))
            if want is None:
                # extra mechanical pads (shield/mount) keep their net; FPC/JST mounting pads go to GND
                continue
            if p.GetNetname() != want:
                if (ref, num) in old:
                    changed.add(old[(ref, num)])
                    changed.add(want)
                p.SetNet(net(want))

    # nets that lost pads through removal
    live = set(padnets.values())
    for (ref, num), name in old.items():
        if ref in removed:
            changed.add(name)
    changed -= BIG
    changed.discard('')

    # 4. rip copper of changed or vanished nets
    ripped = 0
    for t in list(b.GetTracks()):
        n = t.GetNetname()
        if n in changed or (n and n not in live and not n.startswith('unconnected')):
            b.RemoveNative(t)
            ripped += 1

    # 5. rip copper that collides with pads of the new footprints
    hit = 0
    for f in b.GetFootprints():
        if f.GetReference() not in NEW:
            continue
        for p in f.Pads():
            box = p.GetBoundingBox()
            box.Inflate(MM(0.3))
            for t in list(b.GetTracks()):
                if t.GetNetname() == p.GetNetname():
                    continue
                if t.Type() == pcbnew.PCB_VIA_T:
                    on = True
                else:
                    on = p.IsOnLayer(t.GetLayer())
                if on and t.GetBoundingBox().Intersects(box) and t.HitTest(box, False):
                    b.RemoveNative(t)
                    hit += 1
        # coil turns are footprint graphics: clear the whole courtyard on its copper layer
        if f.GetReference() == 'AE501':
            box = f.GetBoundingBox(False)
            for t in list(b.GetTracks()):
                if t.GetBoundingBox().Intersects(box) and t.HitTest(box, False) and (t.Type() == pcbnew.PCB_VIA_T or t.GetLayer() == pcbnew.B_Cu) and t.GetNetname() != 'GND':
                    b.RemoveNative(t)
                    hit += 1

    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(board_path, b)
    print('removed', sorted(removed))
    print('changed nets', sorted(changed))
    print('ripped', ripped, 'collisions', hit)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

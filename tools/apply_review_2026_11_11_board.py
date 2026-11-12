#!/usr/bin/env python3
"""Board changes answering docs/review/design_review_2026-11-11.md. KiCad Python.

Usage: apply_review_2026_11_11_board.py NETLIST BOARD

Starts from the board committed at 3120d6e and the netlist exported after
tools/apply_review_2026_11_11_schematic.py. It
- replaces J301 with the FH34SRJ footprint, centred on the panel flex (y 137.45);
- refreshes J502 from the corrected SAO footprint (true body, key, model);
- adds SW403/R415 (reset), RT102, and rear probe pads TP101/TP301/TP501/TP502;
- moves RT101 to mid-cell, and D101/C303 out of the new connector area;
- restores the NFC antenna window as a named rule area on all copper layers and
  removes every track and via inside it;
- rips copper belonging to changed nets or lying in the display fan-out area,
  and lays the new display-connector via lattice.
Routing is completed afterwards with tools/route_remaining.py using
docs/design/routing/router_config_2026-11-11.json.
"""
import json
import pathlib
import sys

import pcbnew

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from sync_board_design_review import read_netlist, KICAD_FP  # noqa: E402

MM = pcbnew.FromMM
PROJ = str(ROOT / 'Tinkerbadge.pretty')

# NFC antenna window: winding 182..200 x 166..179 plus terminal lead, open to the bottom board edge
NFC_WINDOW = (180.55, 165.2, 200.45, 180.0)
NFC_NETS = ('/05  SENSORS + EXPANSION/NFC_LA', '/05  SENSORS + EXPANSION/NFC_LB')

J301_AT = (199.4, 137.45, 90)
REPLACE = {   # reference: (library dir, lib nickname, footprint, x, y, rotation or None to keep the present pose)
    'J301': (PROJ, 'Tinkerbadge', 'Hirose_FH34SRJ-24S-0.5SH_PanelOrder', *J301_AT),
    'J502': (PROJ, 'Tinkerbadge', 'SAO_Socket_2x03_Front', None, None, None),
}
NEW = {       # reference: (library dir, nickname, footprint, x, y, rotation, rear)
    'SW403': (PROJ, 'Tinkerbadge', 'SKSCLBE010', 102.1, 135.0, 270, False),
    'R415': (f'{KICAD_FP}/Resistor_SMD.pretty', 'Resistor_SMD', 'R_0603_1608Metric', 106.0, 139.0, 0, False),
    'RT102': (f'{KICAD_FP}/Resistor_SMD.pretty', 'Resistor_SMD', 'R_0603_1608Metric', 153.5, 142.0, 90, False),
    'TP101': (f'{KICAD_FP}/TestPoint.pretty', 'TestPoint', 'TestPoint_Pad_D1.0mm', 192.0, 116.0, 0, True),
    'TP301': (f'{KICAD_FP}/TestPoint.pretty', 'TestPoint', 'TestPoint_Pad_D1.0mm', 195.0, 116.0, 0, True),
    'TP501': (f'{KICAD_FP}/TestPoint.pretty', 'TestPoint', 'TestPoint_Pad_D1.0mm', 198.0, 116.0, 0, True),
    'TP502': (f'{KICAD_FP}/TestPoint.pretty', 'TestPoint', 'TestPoint_Pad_D1.0mm', 201.0, 116.0, 0, True),
}
MOVED = {     # reference: (x, y, rotation)
    'RT101': (150.5, 142.0, 90),      # under the middle of the cell, 30 mm from the charger
    'D101': (200.6, 116.2, 0),        # USB TVS, clear of the display connector and flex
    'C303': (193.2, 136.0, 90),       # display supply bypass beside connector pins 15/16
}
REMOVED = ['R414']
RENAME_NETS = {'BOOT_N': 'BTN_B_N'}
# whole nets to rip and re-route
RIP_NETS = ['/01  POWER + CHARGING/BATT_NTC', *NFC_NETS, '/04  LIGHTING + BUTTONS/RGB_LINK_7']
# everything in these boxes is ripped (old and new display-connector fan-out)
RIP_BOXES = [(193.0, 129.9, 202.0, 152.9)]


def load(lib, nick, name):
    f = pcbnew.FootprintLoad(lib, name)
    assert f is not None, (lib, name)
    f.SetFPID(pcbnew.LIB_ID(nick, name))
    return f


def box(x0, y0, x1, y1):
    return pcbnew.BOX2I(pcbnew.VECTOR2I(MM(x0), MM(y0)), pcbnew.VECTOR2I(MM(x1 - x0), MM(y1 - y0)))


def main(netlist, board_path):
    comps, padnets = read_netlist(netlist)
    b = pcbnew.LoadBoard(board_path)
    ripped = 0

    old_pad_net = {(f.GetReference(), p.GetNumber()): p.GetNetname() for f in b.GetFootprints() for p in f.Pads()}

    # ---- footprints out / replaced / added / moved
    for ref in REMOVED:
        b.RemoveNative(b.FindFootprintByReference(ref))
    for ref, (lib, nick, name, x, y, rot) in REPLACE.items():
        old = b.FindFootprintByReference(ref)
        f = load(lib, nick, name)
        f.SetReference(ref)
        f.SetPosition(old.GetPosition() if x is None else pcbnew.VECTOR2I(MM(x), MM(y)))
        b.Add(f)
        f.SetOrientationDegrees(old.GetOrientationDegrees() if rot is None else rot)
        f.Reference().SetLayer(pcbnew.F_Fab)
        b.RemoveNative(old)
    for ref, (lib, nick, name, x, y, rot, rear) in NEW.items():
        f = load(lib, nick, name)
        f.SetReference(ref)
        f.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        b.Add(f)
        if rear:
            f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        f.SetOrientationDegrees(rot)
        f.Reference().SetLayer(pcbnew.B_Fab if rear else pcbnew.F_Fab)
    for ref, (x, y, rot) in MOVED.items():
        f = b.FindFootprintByReference(ref)
        f.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        f.SetOrientationDegrees(rot)

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
    changed_pads = []
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
                fld.SetLayer(pcbnew.B_Fab if f.IsFlipped() else pcbnew.F_Fab)
                fld.SetPosition(f.GetPosition())
                f.Add(fld)
            f.GetField(name).SetText(value)
        for p in f.Pads():
            want = padnets.get((ref, p.GetNumber()))
            if want is None:
                continue
            before = old_pad_net.get((ref, p.GetNumber()))
            before = RENAME_NETS.get(before, before)
            if before is not None and before != want and ref not in REPLACE and ref not in MOVED:
                changed_pads.append((p, before))
            p.SetNet(net(want))

    # ---- rip: stubs of the old net at pads whose net changed (follow the chain to the first junction)
    def touching(pt_, name, skip):
        out = []
        for t in b.GetTracks():
            if t.GetNetname() == name and t.m_Uuid.AsString() not in skip and t.HitTest(pt_, MM(0.05)):
                out.append(t)
        return out

    for pad, old in changed_pads:
        gone = set()
        frontier = [t for t in b.GetTracks() if t.GetNetname() == old and t.Type() == pcbnew.PCB_TRACE_T
                    and pad.IsOnLayer(t.GetLayer()) and (pad.HitTest(t.GetStart()) or pad.HitTest(t.GetEnd()))]
        while frontier:
            t = frontier.pop()
            if t.m_Uuid.AsString() in gone:
                continue
            gone.add(t.m_Uuid.AsString())
            far = t.GetEnd() if pad.HitTest(t.GetStart()) or any(True for _ in ()) else t.GetStart()
            for end in (t.GetStart(), t.GetEnd()):
                nxt = touching(end, old, gone)
                on_pad = any(q.GetNetname() == old and q.HitTest(end) for f in b.GetFootprints() for q in f.Pads())
                if len(nxt) == 1 and not on_pad and nxt[0].Type() == pcbnew.PCB_TRACE_T:
                    frontier.append(nxt[0])
        for t in list(b.GetTracks()):
            if t.m_Uuid.AsString() in gone:
                b.RemoveNative(t)
                ripped += 1

    # ---- rip: whole nets, boxes, the antenna window, and collisions with new or moved pads
    live = set(padnets.values())
    for t in list(b.GetTracks()):
        n = t.GetNetname()
        if n in RIP_NETS or (n and n not in live and not n.startswith('unconnected')):
            b.RemoveNative(t)
            ripped += 1
    for bx in RIP_BOXES + [NFC_WINDOW]:
        r = box(*bx)
        for t in list(b.GetTracks()):
            if t.HitTest(r, False):
                b.RemoveNative(t)
                ripped += 1
    for ref in list(REPLACE) + list(NEW) + list(MOVED):
        f = b.FindFootprintByReference(ref)
        for p in f.Pads():
            r = p.GetBoundingBox()
            r.Inflate(MM(0.3))
            for t in list(b.GetTracks()):
                if t.GetNetname() == p.GetNetname():
                    continue
                on = t.Type() == pcbnew.PCB_VIA_T or p.IsOnLayer(t.GetLayer()) or p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH
                if on and t.HitTest(r, False):
                    b.RemoveNative(t)
                    ripped += 1

    # ---- NFC antenna window: a named rule area that keeps zone fills out on every copper layer
    for z in list(b.Zones()):
        if z.GetZoneName() == 'NFC_WINDOW':
            b.RemoveNative(z)
    z = pcbnew.ZONE(b)
    z.SetIsRuleArea(True)
    z.SetZoneName('NFC_WINDOW')
    ls = pcbnew.LSET()
    for layer in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu):
        ls.AddLayer(layer)
    z.SetLayerSet(ls)
    z.SetDoNotAllowZoneFills(True)
    z.SetDoNotAllowTracks(False)       # NFC feed tracks are legal; unrelated nets are rejected by tinkerbadge.kicad_dru
    z.SetDoNotAllowVias(False)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(False)
    x0, y0, x1, y1 = NFC_WINDOW
    o = z.Outline()
    o.NewOutline()
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        o.Append(MM(x), MM(y))
    b.Add(z)

    # ---- display-connector via lattice (0.48/0.25 mm vias in three staggered columns)
    j301 = b.FindFootprintByReference('J301')
    cols = (196.85, 195.95, 195.05)
    made = {'tracks': [], 'vias': []}
    for p in j301.Pads():
        num = p.GetNumber()
        name = p.GetNetname()
        if not num.isdigit() or not name or name.startswith('unconnected'):
            continue
        y = pcbnew.ToMM(p.GetPosition().y)
        x = pcbnew.ToMM(p.GetPosition().x)
        cx = cols[int(num) % 3]
        t = pcbnew.PCB_TRACK(b)
        t.SetStart(pcbnew.VECTOR2I(MM(x), MM(y)))
        t.SetEnd(pcbnew.VECTOR2I(MM(cx), MM(y)))
        t.SetWidth(MM(0.2))
        t.SetLayer(pcbnew.F_Cu)
        t.SetNet(p.GetNet())
        b.Add(t)
        v = pcbnew.PCB_VIA(b)
        v.SetPosition(pcbnew.VECTOR2I(MM(cx), MM(y)))
        v.SetWidth(pcbnew.F_Cu, MM(0.48))
        v.SetDrill(MM(0.25))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        v.SetNet(p.GetNet())
        b.Add(v)
        made['tracks'].append([num, name.split('/')[-1], round(x, 3), round(y, 3), cx])
    # NFC coil terminals reach the front through one via each
    ae = b.FindFootprintByReference('AE501')
    for p in ae.Pads():
        v = pcbnew.PCB_VIA(b)
        v.SetPosition(p.GetPosition())
        v.SetWidth(pcbnew.F_Cu, MM(0.6))
        v.SetDrill(MM(0.3))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        v.SetNet(p.GetNet())
        b.Add(v)

    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(board_path, b)
    (ROOT / 'tinkerbadge.kicad_dru').write_text(
        '(version 1)\n\n'
        '# NFC antenna window (docs/review/design_review_2026-11-11.md, NFC-1).\n'
        '# The rule area NFC_WINDOW keeps zone fills out. This rule rejects any track or via\n'
        '# inside it that does not belong to the coil feed.\n'
        '(rule "NFC window: only the coil feed"\n'
        f'  (condition "A.intersectsArea(\'NFC_WINDOW\') && A.NetName != \'{NFC_NETS[0]}\' && A.NetName != \'{NFC_NETS[1]}\'")\n'
        '  (constraint disallow track via))\n')
    print('ripped', ripped, 'lattice entries', len(made['tracks']))
    for row in made['tracks']:
        print('  J301', *row)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

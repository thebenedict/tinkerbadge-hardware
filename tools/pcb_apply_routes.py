#!/usr/bin/env python3
"""Add router output (tracks/vias JSON) to the board; optional dangling-copper prune. KiCad Python."""
import json
import sys

import pcbnew

MM = pcbnew.FromMM


def main(board_path, routes, prune=False):
    b = pcbnew.LoadBoard(board_path)
    nets = b.GetNetsByName()
    if routes != '-':
        r = json.load(open(routes))
        # optional placement changes recorded with the hand routing
        for ref, x, y, rot in r.get('moves', []):
            fp = b.FindFootprintByReference(ref)
            fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
            fp.SetOrientationDegrees(rot)
        for ref, lib, name in r.get('refresh_footprints', []):
            old = b.FindFootprintByReference(ref)
            lib_dir = lib if lib.startswith('/') else str(__import__('pathlib').Path(board_path).resolve().parent / lib)
            fp = pcbnew.FootprintLoad(lib_dir, name)
            fp.SetFPID(old.GetFPID())
            fp.SetReference(ref)
            fp.SetValue(old.GetValue())
            fp.SetPosition(old.GetPosition())
            b.Add(fp)
            fp.SetOrientationDegrees(old.GetOrientationDegrees())
            by_num = {p.GetNumber(): p.GetNet() for p in old.Pads()}
            for p in fp.Pads():
                if p.GetNumber() in by_num:
                    p.SetNet(by_num[p.GetNumber()])
            for fld in old.GetFields():
                if not fp.HasField(fld.GetName()):
                    nf = pcbnew.PCB_FIELD(fp, pcbnew.FIELD_T_USER, fld.GetName())
                    nf.SetVisible(False)
                    nf.SetLayer(fld.GetLayer())
                    nf.SetPosition(fp.GetPosition())
                    fp.Add(nf)
                fp.GetField(fld.GetName()).SetText(fld.GetText())
            fp.Reference().SetLayer(old.Reference().GetLayer())
            fp.SetExcludedFromBOM(old.IsExcludedFromBOM())
            fp.SetExcludedFromPosFiles(old.IsExcludedFromPosFiles())
            b.RemoveNative(old)
        # optional rip-up: whole nets, or items of one net touching given circles (x, y, radius in mm)
        rip_nets = set(r.get('rip_nets', []))
        spots = [(MM(x), MM(y), MM(rad)) for x, y, rad in r.get('rip_at', [])]
        ripped = 0
        for t in list(b.GetTracks()):
            name = t.GetNetname()
            kill = name in rip_nets
            if not kill and name == r.get('rip_at_net'):
                for x, y, rad in spots:
                    if t.HitTest(pcbnew.VECTOR2I(x, y), rad):
                        kill = True
            if kill:
                b.RemoveNative(t)
                ripped += 1
        for name, x, y, rad in r.get('rip_spots', []):
            for t in list(b.GetTracks()):
                if t.GetNetname() == name and t.HitTest(pcbnew.VECTOR2I(MM(x), MM(y)), MM(rad)):
                    b.RemoveNative(t)
                    ripped += 1
        for x0, y0, x1, y1 in r.get('rip_boxes', []):
            box = pcbnew.BOX2I(pcbnew.VECTOR2I(MM(x0), MM(y0)), pcbnew.VECTOR2I(MM(x1 - x0), MM(y1 - y0)))
            for t in list(b.GetTracks()):
                if t.HitTest(box, False):
                    b.RemoveNative(t)
                    ripped += 1
        # exact-geometry rip list written by the router
        key = lambda x, y: (round(x / 1e6, 3), round(y / 1e6, 3))
        rt = {(tuple(map(lambda v: round(v, 3), t['a'])), tuple(map(lambda v: round(v, 3), t['b'])), t['layer'], t['net']) for t in r.get('rip_tracks', [])}
        rv = {(round(v['x'], 3), round(v['y'], 3), v['net']) for v in r.get('rip_vias', [])}
        for t in list(b.GetTracks()):
            if t.Type() == pcbnew.PCB_VIA_T:
                if (*key(t.GetPosition().x, t.GetPosition().y), t.GetNetname()) in rv:
                    b.RemoveNative(t)
                    ripped += 1
            elif (key(t.GetStart().x, t.GetStart().y), key(t.GetEnd().x, t.GetEnd().y), 'F' if t.GetLayer() == pcbnew.F_Cu else 'B', t.GetNetname()) in rt:
                b.RemoveNative(t)
                ripped += 1
        if ripped:
            print('ripped', ripped)
        for t in r['tracks']:
            s = pcbnew.PCB_TRACK(b)
            s.SetStart(pcbnew.VECTOR2I(MM(t['a'][0]), MM(t['a'][1])))
            s.SetEnd(pcbnew.VECTOR2I(MM(t['b'][0]), MM(t['b'][1])))
            s.SetWidth(MM(t['w']))
            s.SetLayer({'F': pcbnew.F_Cu, 'B': pcbnew.B_Cu, 'I': pcbnew.In2_Cu}[t['layer']])
            s.SetNet(nets[t['net']])
            b.Add(s)
        for v in r['vias']:
            s = pcbnew.PCB_VIA(b)
            s.SetPosition(pcbnew.VECTOR2I(MM(v['x']), MM(v['y'])))
            s.SetWidth(pcbnew.F_Cu, MM(v['d']))
            s.SetDrill(MM(v['drill']))
            s.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
            s.SetNet(nets[v['net']])
            b.Add(s)
        print('added', len(r['tracks']), 'tracks', len(r['vias']), 'vias')
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(board_path, b)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

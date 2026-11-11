#!/usr/bin/env python3
"""Dump board copper geometry to JSON for the pure-Python router (run with KiCad's Python)."""
import json
import sys

import pcbnew

mm = lambda v: round(v / 1e6, 4)


def main(board_path, out):
    b = pcbnew.LoadBoard(board_path)
    data = {'pads': [], 'tracks': [], 'vias': [], 'graphics': [], 'outline': [], 'classes': {}}
    for name, ni in b.GetNetsByName().items():
        data['classes'][str(name)] = ni.GetNetClassName()
    for f in b.GetFootprints():
        ref = f.GetReference()
        for p in f.Pads():
            bb = p.GetBoundingBox()
            d = p.GetDrillSize()
            data['pads'].append({
                'ref': ref, 'num': p.GetNumber(), 'net': p.GetNetname(),
                'x': mm(p.GetPosition().x), 'y': mm(p.GetPosition().y),
                'box': [mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())],
                'F': p.IsOnLayer(pcbnew.F_Cu), 'B': p.IsOnLayer(pcbnew.B_Cu),
                'drill': mm(max(d.x, d.y)), 'tht': p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH),
                'circle': p.GetShape(pcbnew.F_Cu if p.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu) == pcbnew.PAD_SHAPE_CIRCLE})
        for g in f.GraphicalItems():
            if g.Type() == pcbnew.PCB_SHAPE_T and g.GetLayer() in (pcbnew.F_Cu, pcbnew.B_Cu) and g.GetShape() == pcbnew.SHAPE_T_SEGMENT:
                data['graphics'].append({'ref': ref, 'layer': 'F' if g.GetLayer() == pcbnew.F_Cu else 'B',
                                         'a': [mm(g.GetStart().x), mm(g.GetStart().y)], 'b': [mm(g.GetEnd().x), mm(g.GetEnd().y)], 'w': mm(g.GetWidth())})
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            data['vias'].append({'x': mm(t.GetPosition().x), 'y': mm(t.GetPosition().y), 'd': mm(t.GetWidth(pcbnew.F_Cu)), 'drill': mm(t.GetDrillValue()), 'net': t.GetNetname()})
        elif t.Type() == pcbnew.PCB_TRACE_T:
            if t.GetLayer() not in (pcbnew.F_Cu, pcbnew.B_Cu, pcbnew.In2_Cu):
                continue
            data['tracks'].append({'a': [mm(t.GetStart().x), mm(t.GetStart().y)], 'b': [mm(t.GetEnd().x), mm(t.GetEnd().y)], 'w': mm(t.GetWidth()),
                                   'layer': {pcbnew.F_Cu: 'F', pcbnew.B_Cu: 'B', pcbnew.In2_Cu: 'I'}[t.GetLayer()], 'net': t.GetNetname()})
        else:
            raise SystemExit('unsupported track item (arc?)')
    polys = pcbnew.SHAPE_POLY_SET()
    b.GetBoardPolygonOutlines(polys, True)
    o = polys.Outline(0)
    data['outline'] = [[mm(o.CPoint(i).x), mm(o.CPoint(i).y)] for i in range(o.PointCount())]
    data['holes'] = [[[mm(h.CPoint(i).x), mm(h.CPoint(i).y)] for i in range(h.PointCount())] for h in (polys.Hole(0, k) for k in range(polys.HoleCount(0)))]
    json.dump(data, open(out, 'w'))
    print(len(data['pads']), 'pads', len(data['tracks']), 'tracks', len(data['vias']), 'vias', len(data['graphics']), 'graphics', len(data['outline']), 'outline pts', len(data['holes']), 'holes')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

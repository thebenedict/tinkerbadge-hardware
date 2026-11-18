#!/usr/bin/env python3
"""Regenerate docs/design/pcb_placement.json from the native board. KiCad Python.

The JSON is a derived record of what the board file contains; the board is
authoritative. Functional group labels are carried over from the previous file.

Usage: write_pcb_placement.py BOARD
"""
import json
import pathlib
import sys

import pcbnew

ROOT = pathlib.Path(__file__).resolve().parents[1]
PATH = ROOT / 'docs/design/pcb_placement.json'
GROUPS = {'SW403': 'buttons', 'R415': 'buttons', 'RT101': 'charger / cell temperature', 'RT102': 'charger / cell temperature',
          'J301': 'display interface', 'J503': 'expansion header', 'R518': 'expansion header', 'R519': 'expansion header',
          'R520': 'expansion header', 'R521': 'expansion header', 'R522': 'expansion header', 'J102': 'battery', 'J103': 'dock', 'AE501': 'NFC',
          'TP101': 'recovery/test', 'TP301': 'recovery/test', 'TP501': 'recovery/test', 'TP502': 'recovery/test',
          'U105': 'USB connector and protection', 'L101': 'regulator', 'L301': 'display boost'}


def main(board):
    b = pcbnew.LoadBoard(board)
    old = json.loads(PATH.read_text())
    groups = {p['reference']: p.get('group', '') for p in old.get('placements', [])}
    groups.update(GROUPS)
    rev = next((d.GetText() for d in b.GetDrawings() if d.Type() == pcbnew.PCB_TEXT_T and d.GetText().startswith('rev ')), 'rev ?')
    out = {'status': f'derived from tinkerbadge.kicad_pcb, {" ".join(rev.split())}; the board file is authoritative',
           'board_mm': old['board_mm'], 'origin_mm': old['origin_mm'], 'copper_layers': b.GetCopperLayerCount(), 'placements': []}
    for f in sorted(b.GetFootprints(), key=lambda f: f.GetReference()):
        ref = f.GetReference()
        if ref.startswith(('MECH', 'RES')):
            continue
        p = f.GetPosition()
        out['placements'].append({'reference': ref, 'x': round(pcbnew.ToMM(p.x), 3), 'y': round(pcbnew.ToMM(p.y), 3),
                                  'rotation': round(f.GetOrientationDegrees(), 1), 'side': 'B.Cu' if f.IsFlipped() else 'F.Cu',
                                  'group': groups.get(ref, '')})
    PATH.write_text(json.dumps(out, indent=2) + '\n')
    print('placements', len(out['placements']))


if __name__ == '__main__':
    main(sys.argv[1])

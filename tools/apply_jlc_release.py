#!/usr/bin/env python3
"""Board and contract side of the JLCPCB release changes. Idempotent.

  apply_jlc_release.py contracts            (plain Python)
  apply_jlc_release.py board NETLIST PCB    (KiCad Python)

contracts: R112 value and L101 part/footprint in the power contract.
board: copies schematic fields to footprints, swaps L101 to the NR4020-style
land pattern, enlarges silkscreen to JLCPCB's legend minimum (1.0 mm text,
0.15 mm line), adds three fiducials, and sets hand-fit parts as excluded from
the placement file.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIDUCIALS = [(103.6, 176.4), (206.5, 107.2), (206.4, 176.4)]
HAND_FIT = {'J102', 'J502'}


def contracts():
    path = ROOT / 'docs/design/power_contract.json'
    d = json.loads(path.read_text())
    for c in d['components'] + d['two_terminal_support']:
        if c['ref'] == 'R112':
            c['value'] = '4.7k 1%'
        if c['ref'] == 'L101':
            c.update({'mpn': 'SWPA4020SR47NT', 'footprint': 'Inductor_SMD:L_Changjiang_FNR4020S',
                      'note': 'Sunlord SWPA4020SR47NT (LCSC C98415): 0.47 uH, 7 A saturation, 3.3 A rms, 29 mOhm, 4 x 4 x 2 mm. Stocked at JLCPCB; replaces the Coilcraft part, which is not.'})
    path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + '\n')
    print('power contract updated')


def board(netlist, pcb):
    import pcbnew
    sys.path.insert(0, str(ROOT / 'tools'))
    from sync_board_design_review import read_netlist, KICAD_FP
    MM = pcbnew.FromMM
    comps, padnets = read_netlist(netlist)
    b = pcbnew.LoadBoard(pcb)

    # L101 land pattern
    old = b.FindFootprintByReference('L101')
    if str(old.GetFPID().GetLibItemName()) != 'L_Changjiang_FNR4020S':
        new = pcbnew.FootprintLoad(f'{KICAD_FP}/Inductor_SMD.pretty', 'L_Changjiang_FNR4020S')
        new.SetFPID(pcbnew.LIB_ID('Inductor_SMD', 'L_Changjiang_FNR4020S'))
        new.SetReference('L101')
        new.SetPosition(old.GetPosition())
        new.SetOrientationDegrees(old.GetOrientationDegrees())
        nets = {p.GetNumber(): p.GetNet() for p in old.Pads()}
        for p in new.Pads():
            p.SetNet(nets[p.GetNumber()])
        new.Reference().SetLayer(pcbnew.F_Fab)
        b.RemoveNative(old)
        b.Add(new)

    # fields from the schematic
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
        f.SetExcludedFromPosFiles(ref in HAND_FIT or f.IsExcludedFromPosFiles())

    # legend minimums
    silk = (pcbnew.F_SilkS, pcbnew.B_SilkS)
    def fix_text(t):
        if t.GetLayer() in silk and t.IsVisible():
            if t.GetTextHeight() < MM(1.0):
                t.SetTextSize(pcbnew.VECTOR2I(MM(1.0), MM(1.0)))
            if t.GetTextThickness() < MM(0.15):
                t.SetTextThickness(MM(0.15))
    for d in b.GetDrawings():
        if d.Type() == pcbnew.PCB_TEXT_T:
            fix_text(d)
        elif d.Type() == pcbnew.PCB_SHAPE_T and d.GetLayer() in silk and 0 < d.GetWidth() < MM(0.15):
            d.SetWidth(MM(0.15))
    for f in b.GetFootprints():
        for fld in f.GetFields():
            fix_text(fld)
        for g in f.GraphicalItems():
            if g.Type() == pcbnew.PCB_TEXT_T:
                fix_text(g)
            elif g.Type() == pcbnew.PCB_SHAPE_T and g.GetLayer() in silk and 0 < g.GetWidth() < MM(0.15):
                g.SetWidth(MM(0.15))

    # fiducials
    have = {f.GetReference() for f in b.GetFootprints()}
    for k, (x, y) in enumerate(FIDUCIALS, 1):
        ref = f'FID{k}'
        if ref in have:
            continue
        f = pcbnew.FootprintLoad(f'{KICAD_FP}/Fiducial.pretty', 'Fiducial_1mm_Mask2mm')
        f.SetFPID(pcbnew.LIB_ID('Fiducial', 'Fiducial_1mm_Mask2mm'))
        f.SetReference(ref)
        f.SetValue('Fiducial')
        f.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        f.Reference().SetVisible(False)
        f.SetBoardOnly(True)
        f.SetExcludedFromBOM(True)
        f.SetExcludedFromPosFiles(True)
        b.Add(f)

    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(pcb, b)
    print('board updated')


if __name__ == '__main__':
    if sys.argv[1] == 'contracts':
        contracts()
    else:
        board(sys.argv[2], sys.argv[3])

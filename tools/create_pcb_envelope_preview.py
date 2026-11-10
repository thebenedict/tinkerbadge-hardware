#!/usr/bin/env python3
"""Create a NON-AUTHORITATIVE rendering derivative with virtual models enabled.
The main board's board-only / BOM exclusion flags are unchanged.
"""
import pcbnew as p,pathlib
root=pathlib.Path(__file__).resolve().parents[1];b=p.LoadBoard(str(root/'tinkerbadge.kicad_pcb'))
for f in b.GetFootprints():
 for i in range(len(f.Models())):
  m=f.Models()[i];m.m_Filename=m.m_Filename.replace('${KIPRJMOD}',str(root));f.Models()[i]=m
 if f.GetReference() in ['MECH_PANEL','MECH_BATTERY','RES_J502']:
  f.SetAttributes(p.FP_SMD);f.SetExcludedFromPosFiles(False)
out=root/'.build/visual-preview.kicad_pcb';p.SaveBoard(str(out),b);print(out)

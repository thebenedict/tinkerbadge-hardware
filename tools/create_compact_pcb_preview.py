#!/usr/bin/env python3
"""Rendering-only copies. Retains authoritative board/attributes unchanged."""
import pcbnew as p,pathlib,hashlib,sys
root=pathlib.Path(__file__).resolve().parents[1];stage=root/(sys.argv[1] if len(sys.argv)>1 else '.build/compact-one-sided')
src=stage/'tinkerbadge.kicad_pcb';h=hashlib.sha256(src.read_bytes()).hexdigest()
b=p.LoadBoard(str(src))
for f in b.GetFootprints():
 for i in range(len(f.Models())):
  m=f.Models()[i];m.m_Filename=m.m_Filename.replace('$'+'{KIPRJMOD}',str(stage));f.Models()[i]=m
 if f.GetReference() in ['MECH_PANEL','MECH_BATTERY','RES_J502']:
  f.SetAttributes(p.FP_SMD);f.SetExcludedFromPosFiles(False)
p.SaveBoard(str(stage/'visual-preview.kicad_pcb'),b)
for f in b.GetFootprints():
 if f.GetReference() in ['MECH_PANEL','MECH_BATTERY','RES_J502']:f.Models().clear()
p.SaveBoard(str(stage/'bare-preview.kicad_pcb'),b)
assert hashlib.sha256(src.read_bytes()).hexdigest()==h
print(h)


#!/usr/bin/env python3
"""Convert simple envelope boxes to IndexedFaceSet for KiCad's VRML renderer.
Dimensions, units, colors and transforms are preserved; these are not vendor CAD.
"""
import pathlib,re,shutil
root=pathlib.Path(__file__).resolve().parents[1];backup=root/'.build/vrml-box-sources';backup.mkdir(exist_ok=True)
def mesh(m):
 x,y,z=[float(v)/2 for v in m.groups()];pts=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
 return 'geometry IndexedFaceSet { coord Coordinate { point [ '+', '.join(' '.join(str(v) for v in p) for p in pts)+' ] } coordIndex [ 0,3,2,1,-1, 4,5,6,7,-1, 0,1,5,4,-1, 1,2,6,5,-1, 2,3,7,6,-1, 3,0,4,7,-1 ] solid TRUE }'
for f in (root/'models').glob('*.wrl'):
 s=f.read_text();out,n=re.subn(r'geometry Box \{ size ([\d.eE+-]+) ([\d.eE+-]+) ([\d.eE+-]+) \}',mesh,s)
 if n:
  if not (backup/f.name).exists():shutil.copy2(f,backup/f.name)
  f.write_text(out);print(f.name,n)

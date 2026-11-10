#!/usr/bin/env python3
"""Apply reviewed project netclasses and explicit provisional layer stackup."""
from pathlib import Path
import json,copy,sys,re,hashlib
R=Path(__file__).resolve().parents[1]
board=Path(sys.argv[1]).resolve();assert str(board).startswith(str(R/".build/"))
spec=json.loads((R/"docs/design/routing_constraints.json").read_text())
project=json.loads((R/"tinkerbadge.kicad_pro").read_text())
default=project["net_settings"]["classes"][0]
classes=[]
for priority,(name,parameters) in enumerate(spec["class_parameters_mm"].items()):
 entry=copy.deepcopy(default);entry.update(parameters);entry["name"]=name
 entry["priority"]=2147483647 if name=="Default" else priority
 classes.append(entry)
project["net_settings"]["classes"]=classes
project["net_settings"]["netclass_patterns"]=spec["suggested_kicad_netclass_patterns"]
project["net_settings"]["netclass_assignments"]={}
project["board"]["design_settings"]["track_widths"]=[0.0,.15,.2,.25,.3,.4,.5,.6,.8,1.0]
project["board"]["design_settings"]["via_dimensions"]=[{"diameter":.6,"drill":.3},{"diameter":.8,"drill":.4}]
board.with_suffix(".kicad_pro").write_text(json.dumps(project,indent=2)+"\n")
text=board.read_text();assert "(stackup" not in text
lines=["\t\t(stackup"]
for layer in spec["stackup"]["layers"]:
 name=layer["name"];lines += [f'\t\t\t(layer "{name}"']
 if "dielectric" in name:
  typ="core" if name=="dielectric 2" else "prepreg"
  lines += [f'\t\t\t\t(type "{typ}")',f'\t\t\t\t(thickness {layer["thickness_mm"]})',f'\t\t\t\t(material "{layer["material"]}")',f'\t\t\t\t(epsilon_r {layer["epsilon_r"]})']
 else:lines += ['\t\t\t\t(type "copper")',f'\t\t\t\t(thickness {layer["thickness_mm"]})']
 lines += ["\t\t\t)"]
lines += ["\t\t\t(dielectric_constraints no)","\t\t)"]
text,n=re.subn(r"\(setup\s*\n","(setup\n"+"\n".join(lines)+"\n",text,count=1)
assert n==1;board.write_text(text)
print(json.dumps({"board":str(board.relative_to(R)),"sha256":hashlib.sha256(board.read_bytes()).hexdigest(),"project_sha256":hashlib.sha256(board.with_suffix(".kicad_pro").read_bytes()).hexdigest(),"netclasses":len(classes),"special_patterns":len(spec["suggested_kicad_netclass_patterns"]),"stackup":"JLC04161H-7628 provisional; sum 1.5862 mm, nominal finished board 1.6 mm"}))


#!/usr/bin/env python3
"""Add the provisional two inner GND references to a staged board."""
from pathlib import Path
import json,hashlib,pcbnew as p
from pcb_local_routes import V
R=Path(__file__).resolve().parents[1];O=R/".build/routing-pass"
b=p.LoadBoard(str(O/"local-prewired.kicad_pcb"))
assert all(z.GetIsRuleArea() for z in b.Zones())
gnd=b.FindNet("GND").GetNetCode()
for layer in [p.In1_Cu,p.In2_Cu]:
 z=p.ZONE(b);z.SetLayer(layer);z.SetNetCode(gnd);z.SetLocalClearance(p.FromMM(.20));z.SetMinThickness(p.FromMM(.20));z.SetPadConnection(p.ZONE_CONNECTION_FULL)
 z.SetThermalReliefGap(p.FromMM(.25));z.SetThermalReliefSpokeWidth(p.FromMM(.3))
 z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
 poly=z.Outline();poly.NewOutline()
 for x,y in [(100,100),(210,100),(210,180),(100,180)]:poly.Append(p.FromMM(x),p.FromMM(y))
 z.SetZoneName("GND reference; preserve radio and NFC clearance")
 b.Add(z)
b.BuildConnectivity();fill=p.ZONE_FILLER(b);fill.Fill(b.Zones())
out=O/"local-grounded.kicad_pcb";p.SaveBoard(str(out),b)
print(json.dumps({"board_sha256":hashlib.sha256(out.read_bytes()).hexdigest(),"tracks_vias":len(list(b.GetTracks())),"planes":[b.GetLayerName(z.GetLayer()) for z in b.Zones() if not z.GetIsRuleArea()],"active_source_unchanged":hashlib.sha256((R/"tinkerbadge.kicad_pcb").read_bytes()).hexdigest()=="ddf824f2a59bc82568bbb03bcb3f89959f2ee12638b380790207739273c1844d"},indent=2))


#!/usr/bin/env python3
"""Normalize review-envelope metadata and add native all-copper NFC rule area."""
import pcbnew as p,pathlib
root=pathlib.Path(__file__).resolve().parents[1];lib=root/'Tinkerbadge.pretty'
for path in sorted(lib.glob('Review_*.kicad_mod')):
 f=p.FootprintLoad(str(lib),path.stem);f.SetFPIDAsString('Tinkerbadge:'+path.stem)
 f.SetReference('REF**');f.Reference().SetLayer(p.Dwgs_User);f.Reference().SetVisible(False)
 f.SetValue(path.stem);f.Value().SetVisible(False)
 if path.stem=='Review_NFC_Area' and not list(f.Zones()):
  z=p.ZONE(f);z.SetIsRuleArea(True);z.SetZoneName('NFC reserved - coil and tuning pending');layers=p.LSET()
  for layer in [p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu]:layers.AddLayer(layer)
  z.SetLayerSet(layers);z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowPads(True);z.SetDoNotAllowZoneFills(True);z.SetDoNotAllowFootprints(True)
  poly=z.Outline();poly.NewOutline()
  for x,y in [(-15,-8.5),(15,-8.5),(15,8.5),(-15,8.5)]:poly.Append(p.FromMM(x),p.FromMM(y))
  f.Add(z)
 p.FootprintSave(str(lib),f)
 print(path.name)

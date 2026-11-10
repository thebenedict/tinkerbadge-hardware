#!/usr/bin/env python3
"""Create explicitly non-electrical review envelopes. Not approved mechanical parts."""
from create_pcb_local_assets import *
def make(c,name,w,h,layer,description,boxes=None,cy=.25):
 p=LIB/(name+'.kicad_mod');assert not p.exists()
 a={'output':str(p),'name':name,'pads':[],'body_width':w,'body_height':h,'description':description}
 if boxes:
  envelope(name,boxes);a['model']={'path':'${KIPRJMOD}/models/'+name+'.wrl'}
 call(c,'create_footprint',a)
 call(c,'set_footprint_metadata',{'footprint_path':str(p),'attributes':['board_only','exclude_from_pos_files','exclude_from_bom']})
 call(c,'set_footprint_graphics',{'footprint_path':str(p),'selector':{'layer':'F.CrtYd'},'mode':'replace','graphics':[rect(-w/2-cy,-h/2-cy,w/2+cy,h/2+cy)]})
 call(c,'set_footprint_graphics',{'footprint_path':str(p),'selector':{'layer':'Dwgs.User'},'mode':'append','graphics':[rect(-w/2,-h/2,w/2,h/2,.12)]})
 call(c,'set_footprint_graphics',{'footprint_path':str(p),'selector':{'layer':'F.SilkS'},'mode':'delete'})
 return p
if __name__=='__main__':
 c=k.Client()
 try:
  make(c,'Review_Panel_93.3x54.9',93.3,54.9,'F','Waveshare ED037TC1 Rev1 p5 glass. Source max thickness .92mm. Z1mm support gap is a proposal. Mating/flex not qualified.',[((93.3,54.9,.92),(0,0,1.46),(.13,.15,.17),0),((81.12,47.32,.03),(-2.3,0,1.935),(.88,.90,.85),0)],.3)
  make(c,'Review_Battery_Allowance',35,55,'B','Reserved pack allowance only: 35x55x7mm. Exact two-wire protected pack, cable and polarity pending. Not a selected battery.',[((35,55,7),(0,0,3.5),(.62,.65,.68),0)],1.0)
  make(c,'Review_NFC_Area',30,17,'F','Reserved NFC antenna area only, not a coil/land pattern. No metal, copper pours or battery within this allowance pending RF design.',None,0)
  make(c,'Review_Flex_Mating',14,18,'B','Unverified FPC mating/fold corridor. Connector/contact side and allowable bend must be proven before routing.',None,0)
  make(c,'Review_ESD_Package',3.5,2,'F','U105 DQA0010A/B source variant conflict unresolved. No electrical footprint or fake pads.',None,.25)
  make(c,'Review_Inductor_6x6',6,6,'B','L101 reserve only. Exact .47uH 7A saturation target part not selected.',None,.25)
  make(c,'Review_Inductor_5x5',5,5,'B','L301 reserve only. Exact68uH DCR/saturation/package not selected.',None,.25)
  make(c,'Review_SAO_12.7x7',12.7,7,'B','Exact SFH11 connector body clearance reserve. Key-to-pin mapping not proven, no electrical footprint.',[((12.7,6,8.5),(0,0,4.25),(.1,.1,.12),0),((3.7,1,8.5),(0,3.5,4.25),(.1,.1,.12),0)],.3)
  make(c,'Review_Battery_Connector',8,6,'B','Battery connector area only. Pack/connector/polarity/current rating unknown.',None,.5)
  make(c,'Review_Dock_Contacts',12,7,'B','Dock contact/mating allowance only; contact geometry and polarity-safe guide pending.',None,.5)
 finally:c.close()

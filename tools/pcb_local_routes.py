#!/usr/bin/env python3
"""Conservative native geometry checks for bounded, pad-normal PCB prewires.

This is a placement-preserving helper, not a substitute for KiCad DRC or
electrical/return-path review. Only explicit connections are added.
"""
import math
import pcbnew as p

def V(x,y): return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def xy(v): return (p.ToMM(v.x),p.ToMM(v.y))
def shape(item,layer,clearance=0):
    q=p.SHAPE_POLY_SET()
    item.TransformShapeToPolygon(q,layer,p.FromMM(clearance),p.FromMM(.001),p.ERROR_OUTSIDE)
    return q
def intersects(a,b):
    if not a.OutlineCount() or not b.OutlineCount() or not a.BBox().Intersects(b.BBox()): return False
    c=p.SHAPE_POLY_SET();c.BooleanIntersection(a,b);return c.Area()>0
def outside(a,b):
    c=p.SHAPE_POLY_SET();c.BooleanSubtract(a,b);return c.Area()>0
def length(points):return sum(math.dist(a,b) for a,b in zip(points,points[1:]))
def simplify(points):
    out=[]
    for q in points:
        q=tuple(round(z,6) for z in q)
        if out and math.dist(q,out[-1])<.000001:continue
        out.append(q)
        while len(out)>=3:
            a,b,c=out[-3:]
            if abs((b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0]))<1e-8 and (b[0]-a[0])*(c[0]-b[0])+(b[1]-a[1])*(c[1]-b[1])>=0:out.pop(-2)
            else:break
    return out
def octile(a,b):
    dx=b[0]-a[0];dy=b[1]-a[1];d=min(abs(dx),abs(dy))
    yield simplify([a,(a[0]+math.copysign(d,dx),a[1]+math.copysign(d,dy)),b])
    yield simplify([a,(b[0]-math.copysign(d,dx),b[1]-math.copysign(d,dy)),b])
    yield simplify([a,(a[0],b[1]),b])
    yield simplify([a,(b[0],a[1]),b])

class Router:
    def __init__(self,board,net_clearances=None):
        self.b=board;self.fs={f.GetReference():f for f in board.GetFootprints()}
        self.clearances=net_clearances or {}
        self.code_clearances={n.GetNetCode():self.clearances.get(n.GetNetname(),.15) for n in board.GetNetsByNetcode().values()}
        self.pads=[];self.holes=[];self.keeps=[];self.tracks=[];self.added=[];self.failures=[]
        self.outline=p.SHAPE_POLY_SET()
        assert board.GetBoardPolygonOutlines(self.outline,False,None,False,False)
        for f in board.GetFootprints():
            for pad in f.Pads():
                for layer in [p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu]:
                    if pad.IsOnLayer(layer) and pad.GetAttribute()!=p.PAD_ATTRIB_NPTH:
                        q=shape(pad,layer)
                        if q.OutlineCount():self.pads.append((layer,pad.GetNetCode(),q,pad))
                if pad.GetDrillSize().x:
                    q=p.SHAPE_POLY_SET();pad.TransformHoleToPolygon(q,0,p.FromMM(.001),p.ERROR_OUTSIDE)
                    self.holes.append((q,pad))
            for z in f.Zones():
                if z.GetIsRuleArea():self.keeps.append(z)
        self.keeps += [z for z in board.Zones() if z.GetIsRuleArea()]
        for t in board.GetTracks():self.register(t)
    def pad(self,r,n):
        return next(a for a in self.fs[r].Pads() if a.GetNumber()==str(n))
    def track(self,a,b,net,width,layer=p.F_Cu):
        t=p.PCB_TRACK(self.b);t.SetStart(V(*a));t.SetEnd(V(*b));t.SetWidth(p.FromMM(width));t.SetLayer(layer);t.SetNetCode(net);return t
    def register(self,t):
        layers=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu] if isinstance(t,p.PCB_VIA) else [t.GetLayer()]
        for layer in layers:self.tracks.append((layer,t.GetNetCode(),shape(t,layer),t))
    def valid(self,t,clearance=.15,via_paste_guard=True):
        layers=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu] if isinstance(t,p.PCB_VIA) else [t.GetLayer()]
        for layer in layers:
            clearance=max(clearance,self.code_clearances.get(t.GetNetCode(),.15))
            q=shape(t,layer,clearance+.002)
            cache={clearance:q}
            edge=shape(t,layer,.502)
            if outside(edge,self.outline):return False
            raw=shape(t,layer)
            for z in self.keeps:
                if z.IsOnLayer(layer) and intersects(raw,z.Outline()):return False
            for l,n,poly,pad in self.pads:
                if l!=layer:continue
                actual=max(clearance,self.code_clearances.get(n,.15))
                if actual not in cache:cache[actual]=shape(t,layer,actual+.002)
                if n!=t.GetNetCode() and intersects(cache[actual],poly):return False
                if isinstance(t,p.PCB_VIA) and via_paste_guard and pad.GetAttribute()==p.PAD_ATTRIB_SMD and pad.IsOnLayer(p.F_Paste) and intersects(raw,poly):return False
            for l,n,poly,item in self.tracks:
                actual=max(clearance,self.code_clearances.get(n,.15))
                if actual not in cache:cache[actual]=shape(t,layer,actual+.002)
                if l==layer and n!=t.GetNetCode() and intersects(cache[actual],poly):return False
            # Copper clearance to every pre-existing drill, regardless of net.
            hq=shape(t,layer,.252)
            for hole,pad in self.holes:
                # Same-net PTH annuli are intended contact targets, not external holes.
                if pad.GetAttribute()==p.PAD_ATTRIB_PTH and pad.GetNetCode()==t.GetNetCode():continue
                if intersects(hq,hole):return False
        if isinstance(t,p.PCB_VIA):
            x,y=xy(t.GetPosition())
            for _,_,_,other in self.tracks:
                if isinstance(other,p.PCB_VIA):
                    d=math.dist((x,y),xy(other.GetPosition()))
                    if d<(p.ToMM(t.GetDrillValue()+other.GetDrillValue())/2+.252):return False
        return True
    def add_path(self,points,net,width,layer=p.F_Cu):
        ts=[self.track(a,b,net,width,layer) for a,b in zip(simplify(points),simplify(points)[1:]) if math.dist(a,b)>.000001]
        if not all(self.valid(t) for t in ts):return False
        for t in ts:self.b.Add(t);self.register(t);self.added.append(t)
        return True
    def exits(self,pad,extension=.35):
        x,y=xy(pad.GetPosition());box=pad.GetBoundingBox()
        w=p.ToMM(box.GetWidth())/2;h=p.ToMM(box.GetHeight())/2
        f=pad.GetParentFootprint();fx,fy=xy(f.GetPosition())
        dirs=[(1,0,w),(-1,0,w),(0,1,h),(0,-1,h)]
        # Prefer an exit away from the package, preserving a centered normal.
        dirs.sort(key=lambda d:-(d[0]*(x-fx)+d[1]*(y-fy)))
        return [((x+dx*(a+extension),y+dy*(a+extension)),rank) for rank,(dx,dy,a) in enumerate(dirs)]
    def connect(self,r,n,s,m,width=.20,max_detour=6):
        a=self.pad(r,n);b=self.pad(s,m)
        assert a.GetNetCode()==b.GetNetCode() and a.GetNetCode()!=0,(r,n,s,m)
        net=a.GetNetCode();pa=xy(a.GetPosition());pb=xy(b.GetPosition())
        # Aligned adjacent pads on one package can connect through their facing
        # edge midpoints directly; a decorative outward loop only adds length.
        if r==s and (abs(pa[0]-pb[0])<1e-6 or abs(pa[1]-pb[1])<1e-6):
            if self.add_path([pa,pb],net,width):
                return {"from":f"{r}.{n}","to":f"{s}.{m}","net":a.GetNetname(),"width_mm":width,"length_mm":length([pa,pb]),"points_mm":[pa,pb]}
        options=[]
        for ea,ra in self.exits(a):
            for eb,rb in self.exits(b):
                for mid in octile(ea,eb):
                    path=[pa]+mid+[pb]
                    options.append((length(path)+.08*(ra+rb),path))
                for shift in [.6,-.6,1.2,-1.2,2,-2]:
                    cx=(ea[0]+eb[0])/2+shift;cy=(ea[1]+eb[1])/2+shift
                    for way in [[ea,(cx,ea[1]),(cx,eb[1]),eb],[ea,(ea[0],cy),(eb[0],cy),eb]]:
                        path=[pa]+way+[pb];options.append((length(path)+.08*(ra+rb),path))
        for cost,path in sorted(options,key=lambda q:q[0]):
            if length(path)>math.dist(pa,pb)+max_detour:continue
            if self.add_path(path,net,width):
                return {"from":f"{r}.{n}","to":f"{s}.{m}","net":a.GetNetname(),"width_mm":width,"length_mm":length(path),"points_mm":simplify(path)}
        self.failures.append([r,str(n),s,str(m)]);return None
    def ground_via(self,pad,width=.25):
        net=pad.GetNetCode();assert pad.GetNetname()=="GND"
        pa=xy(pad.GetPosition())
        if pad.GetAttribute()==p.PAD_ATTRIB_PTH:return {"reference":pad.GetParentFootprint().GetReference(),"pad":pad.GetNumber(),"existing_PTH":True}
        for extension in [.45,.75,1.05,1.5,2.0]:
            for end,rank in self.exits(pad,extension):
                via=p.PCB_VIA(self.b);via.SetPosition(V(*end));via.SetWidth(p.FromMM(.6));via.SetDrill(p.FromMM(.3));via.SetViaType(p.VIATYPE_THROUGH);via.SetLayerPair(p.F_Cu,p.B_Cu);via.SetNetCode(net)
                if not self.valid(via):continue
                t=self.track(pa,end,net,width,p.F_Cu)
                if not self.valid(t):continue
                self.b.Add(t);self.register(t);self.added.append(t)
                self.b.Add(via);self.register(via);self.added.append(via)
                return {"reference":pad.GetParentFootprint().GetReference(),"pad":pad.GetNumber(),"via_mm":end,"stub_mm":math.dist(pa,end),"width_mm":width}
        return None

    def back_connect(self,r,n,s,m,width=.2,neck=.2,power=False):
        """Explicit front-to-back-to-front bridge with paste-clear through vias."""
        a=self.pad(r,n);b=self.pad(s,m)
        assert a.GetNetCode()==b.GetNetCode() and a.GetNetCode()!=0
        net=a.GetNetCode();pa=xy(a.GetPosition());pb=xy(b.GetPosition())
        diameter,drill=(.8,.4) if power else (.6,.3)
        choices=[]
        self.b.BuildConnectivity()
        for pad,which in [(a,0),(b,1)]:
            vias=[v for v in self.b.GetConnectivity().GetConnectedItems(pad) if isinstance(v,p.PCB_VIA) and p.ToMM(v.GetWidth())>=diameter-.001]
            for via in sorted(vias,key=lambda v:math.dist(xy(v.GetPosition()),xy(pad.GetPosition())))[:8]:
                choices.append((which,xy(via.GetPosition()),via,None,0))
        for extension in [.6,1.0,1.5]:
            for pad,which in [(a,0),(b,1)]:
                for point,rank in self.exits(pad,extension):
                    v=p.PCB_VIA(self.b);v.SetPosition(V(*point));v.SetWidth(p.FromMM(diameter));v.SetDrill(p.FromMM(drill));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNetCode(net)
                    t=self.track(xy(pad.GetPosition()),point,net,neck)
                    if self.valid(v) and self.valid(t):choices.append((which,point,v,t,rank))
        options=[]
        for _,va,via_a,stub_a,ra in [q for q in choices if q[0]==0]:
            for _,vb,via_b,stub_b,rb in [q for q in choices if q[0]==1]:
                mids=list(octile(va,vb))
                for offset in [1,-1,3,-3,6,-6,12,-12,18,-18]:
                    x=(va[0]+vb[0])/2+offset;y=(va[1]+vb[1])/2+offset
                    mids += [[va,(x,va[1]),(x,vb[1]),vb],[va,(va[0],y),(vb[0],y),vb]]
                for path in mids:options.append((length(path)+.1*(ra+rb),path,via_a,via_b,stub_a,stub_b))
        for _,path,via_a,via_b,stub_a,stub_b in sorted(options,key=lambda x:x[0]):
            ts=[self.track(x,y,net,width,p.B_Cu) for x,y in zip(simplify(path),simplify(path)[1:])]
            if not all(self.valid(t) for t in ts):continue
            items=ts+([stub_a,via_a] if stub_a else [])+([stub_b,via_b] if stub_b else [])
            for item in items:self.b.Add(item);self.register(item);self.added.append(item)
            stubs=[[xy(t.GetStart()),xy(t.GetEnd())] for t in [stub_a,stub_b] if t]
            return {"from":f"{r}.{n}","to":f"{s}.{m}","net":a.GetNetname(),"layer":"B.Cu","width_mm":width,"neck_mm":neck,"via_diameter_drill_mm":[diameter,drill],"back_path_mm":simplify(path),"front_stubs_mm":stubs,"reused_start_via":stub_a is None,"reused_end_via":stub_b is None,"length_mm":length(path)+sum(math.dist(*ends) for ends in stubs)}
        return None


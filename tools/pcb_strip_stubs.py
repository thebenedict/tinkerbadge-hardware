#!/usr/bin/env python3
"""Remove dead-end track chains and exact duplicate segments. KiCad Python.

pcb_prune_dangling.py removes one dangling segment per pass, which is slow when a dead
end is a chain of short segments. For every track KiCad reports as dangling, this walks
the chain from its free end through segments that share exact end points, stopping at a
pad, a via or a junction. Each chain is removed on a scratch copy and kept only if DRC
shows no new unconnected item, so a T-junction join that KiCad calls dangling survives.

Usage: pcb_strip_stubs.py board.kicad_pcb
"""
import collections
import json
import math
import shutil
import subprocess
import sys

import pcbnew


def drc(path):
    out = path + '.drc.json'
    subprocess.run(['kicad-cli', 'pcb', 'drc', path, '--severity-all', '--format', 'json', '-o', out], capture_output=True)
    return json.load(open(out))


def key(t, p):
    return (t.GetNetCode(), t.GetLayer(), round(p.x / 1000), round(p.y / 1000))


def chain(b, uuid):
    """UUIDs of the dead-end chain that starts at the dangling track, or []."""
    segs = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T]
    vias = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]
    pads = [p for f in b.GetFootprints() for p in f.Pads()]
    at = collections.defaultdict(list)
    for t in segs:
        at[key(t, t.GetStart())].append(t)
        at[key(t, t.GetEnd())].append(t)

    def anchored(t, p):
        for v in vias:
            if v.GetNetCode() == t.GetNetCode() and v.IsOnLayer(t.GetLayer()) and \
                    math.hypot(v.GetPosition().x - p.x, v.GetPosition().y - p.y) <= v.GetWidth(t.GetLayer()) / 2:
                return True
        return any(pad.GetNetCode() == t.GetNetCode() and pad.IsOnLayer(t.GetLayer()) and pad.HitTest(p) for pad in pads)

    def shared(t, p):
        return [o for o in at[key(t, p)] if o is not t]

    cur = next((t for t in segs if t.m_Uuid.AsString() == uuid), None)
    if cur is None:
        return []
    free = [p for p in (cur.GetStart(), cur.GetEnd()) if not shared(cur, p) and not anchored(cur, p)]
    if len(free) != 1:
        return []
    out = []
    near = free[0]
    while True:
        far = cur.GetEnd() if (cur.GetStart().x, cur.GetStart().y) == (near.x, near.y) else cur.GetStart()
        out.append(cur.m_Uuid.AsString())
        nxt = shared(cur, far)
        if anchored(cur, far) or len(nxt) != 1 or nxt[0].m_Uuid.AsString() in out:
            return out
        cur, near = nxt[0], far


def remove(path, ids):
    b = pcbnew.LoadBoard(path)
    for t in list(b.GetTracks()):
        if t.m_Uuid.AsString() in ids:
            b.RemoveNative(t)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(path, b)


def duplicates(b):
    seen, out = set(), []
    for t in b.GetTracks():
        if t.Type() != pcbnew.PCB_TRACE_T:
            continue
        a, c = (t.GetStart().x, t.GetStart().y), (t.GetEnd().x, t.GetEnd().y)
        k = (min(a, c), max(a, c), t.GetLayer(), t.GetNetCode())
        if k in seen:
            out.append(t.m_Uuid.AsString())
        seen.add(k)
    return out


def main(path):
    scratch = path.replace('.kicad_pcb', '.strip_tmp.kicad_pcb')
    report = drc(path)
    base = len(report['unconnected_items'])
    starts = sorted({i['uuid'] for v in report['violations'] if v['type'] == 'track_dangling' for i in v['items']})
    b = pcbnew.LoadBoard(path)
    jobs = [('duplicates', duplicates(b))] + [(u[:8], chain(b, u)) for u in starts]
    total = 0
    for label, ids in jobs:
        if not ids:
            continue
        shutil.copy(path, scratch)
        remove(scratch, set(ids))
        if len(drc(scratch)['unconnected_items']) <= base:
            shutil.copy(scratch, path)
            total += len(ids)
            print(label, 'removed', len(ids), 'segments')
        else:
            print(label, 'kept: it carries a connection')
    print('total removed', total)


if __name__ == '__main__':
    main(sys.argv[1])

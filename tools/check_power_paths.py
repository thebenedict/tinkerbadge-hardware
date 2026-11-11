#!/usr/bin/env python3
"""Report the narrowest track on the widest copper path between two pads.

Pure Python on the tools/pcb_dump.py JSON. For each (net, from pad, to pad)
it finds the path whose narrowest segment is as wide as possible, so a thin
link hiding in a power path shows up even when most of the net is wide.

Usage: check_power_paths.py board.json
"""
import heapq
import json
import math
import sys

sys.path.insert(0, __import__('pathlib').Path(__file__).parent.as_posix())
from route_remaining import seg_dist, LID  # noqa: E402

PATHS = [
    ('USB_VBUS', 'J101.A4', 'U101.7'), ('DOCK_5V', 'J103.1', 'U101.2'),
    ('/01  POWER + CHARGING/VEXT_5V', 'U101.1', 'U102.13'),
    ('/01  POWER + CHARGING/VBAT_PROTECTED', 'J102.1', 'U102.2'),
    ('/01  POWER + CHARGING/VSYS', 'U102.10', 'U103.10'),
    ('+3V3', 'U103.6', 'U201.2'), ('+3V3', 'U103.6', 'D408.4'), ('+3V3', 'U103.6', 'U104.1'),
    ('+3V3_EPD', 'U104.6', 'J301.15'), ('+3V3', 'U103.6', 'U505.1'),
]


def main(path):
    d = json.load(open(path))
    for net, a, b in PATHS:
        items = [('pad', p) for p in d['pads'] if p['net'] == net] + [('trk', t) for t in d['tracks'] if t['net'] == net] + [('via', v) for v in d['vias'] if v['net'] == net]

        def layers(it):
            k, o = it
            if k == 'pad':
                return {0, 1, 2} if o['tht'] else ({0} if o['F'] else {1})
            return {LID[o['layer']]} if k == 'trk' else {0, 1, 2}

        def touch(x, y):
            (kx, ox), (ky, oy) = x, y
            if not layers(x) & layers(y):
                return False
            if kx == 'trk' and ky == 'trk':
                tol = (ox['w'] + oy['w']) / 2 - 0.01
                return any(seg_dist(q[0], q[1], *oy['a'], *oy['b']) <= tol for q in (ox['a'], ox['b'])) or any(seg_dist(q[0], q[1], *ox['a'], *ox['b']) <= tol for q in (oy['a'], oy['b']))
            if kx == 'trk':
                return touch(y, x)
            if kx == 'pad' and ky == 'trk':
                m = oy['w'] / 2
                x0, y0, x1, y1 = ox['box']
                return any(x0 - m <= q[0] <= x1 + m and y0 - m <= q[1] <= y1 + m for q in (oy['a'], oy['b']))
            if kx == 'via' and ky == 'trk':
                return seg_dist(ox['x'], ox['y'], *oy['a'], *oy['b']) <= oy['w'] / 2 + ox['d'] / 2 - 0.01
            if kx == 'pad' and ky == 'via':
                x0, y0, x1, y1 = ox['box']
                r = oy['d'] / 2
                return x0 - r <= oy['x'] <= x1 + r and y0 - r <= oy['y'] <= y1 + r
            if kx == 'via' and ky == 'pad':
                return touch(y, x)
            if kx == 'via' and ky == 'via':
                return math.hypot(ox['x'] - oy['x'], ox['y'] - oy['y']) < 0.3
            return False

        def find(name):
            ref, num = name.split('.')
            return next(i for i, (k, o) in enumerate(items) if k == 'pad' and o['ref'] == ref and o['num'] == num)

        cap = [o['w'] if k == 'trk' else 9.0 for k, o in items]
        s, t = find(a), find(b)
        best = {s: 9.0}
        prev = {}
        heap = [(-9.0, s)]
        while heap:
            c, u = heapq.heappop(heap)
            c = -c
            if u == t:
                break
            if c < best.get(u, 0):
                continue
            for v in range(len(items)):
                if v != u and touch(items[u], items[v]):
                    w = min(c, cap[v])
                    if w > best.get(v, 0):
                        best[v] = w
                        prev[v] = u
                        heapq.heappush(heap, (-w, v))
        thin = total = 0.0
        u = t
        while u in prev:
            k, o = items[u]
            if k == 'trk':
                ln = math.hypot(o['b'][0] - o['a'][0], o['b'][1] - o['a'][1])
                total += ln
                if o['w'] < 0.4:
                    thin += ln
            u = prev[u]
        print(f'{net.split("/")[-1]:16s} {a:9s} -> {b:9s} narrowest {best.get(t, 0):.2f} mm; path {total:5.1f} mm, of which {thin:5.1f} mm is under 0.4 mm wide')


if __name__ == '__main__':
    main(sys.argv[1])

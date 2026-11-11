#!/usr/bin/env python3
"""Grid maze router for the connections left open on the badge board.

Pure Python. Reads the JSON written by tools/pcb_dump.py, finds the
unconnected copper islands of every net, and joins them on F.Cu/B.Cu with
45-degree routing and through vias. Clearance is enforced through a distance
field to foreign copper, so results are intended to be DRC-clean, but KiCad's
own DRC remains the authority. Writes a JSON list of new tracks and vias for
tools/pcb_apply_routes.py.

Usage: route_remaining.py board.json routes.json [--only NET ...] [--skip NET ...]
"""
import argparse
import heapq
import json
import math
import sys
import time
from array import array

G = 0.05                      # grid pitch, mm
X0, Y0 = 99.0, 99.0           # grid origin
W, H = int(112 / G) + 1, int(82 / G) + 1
MAXR = 0.80                   # distance-field reach, mm
MARGIN = 0.03                 # rasterisation safety margin, mm
INF = 9.0
VIA_D, VIA_DRILL = 0.6, 0.3
CLASS_CLR = {'Default': 0.15, 'EPD_HV': 0.15, 'NFC_HOLD': 0.15, 'Power_Trunk': 0.15,
             'PowerBranch': 0.2, 'AnalogSense': 0.15, 'USB_HOLD': 0.15, 'Switching_HOLD': 0.2}
CLASS_W = {'Default': 0.2, 'EPD_HV': 0.2, 'NFC_HOLD': 0.2, 'Power_Trunk': 0.5, 'PowerBranch': 0.3,
           'AnalogSense': 0.2, 'USB_HOLD': 0.2, 'Switching_HOLD': 0.4}
# no new copper here: module antenna shoulder (both layers)
KEEPOUTS = [(104.0, 99.0, 154.6, 108.0)]
COIL = (181.75, 165.75, 200.25, 179.25)
NL = 3                        # routing layers: 0 F.Cu, 1 B.Cu, 2 In2.Cu (In1.Cu stays a solid ground plane)
LID = {'F': 0, 'B': 1, 'I': 2}
LNAME = 'FBI'
HWEIGHT = 1.4                 # A* heuristic weight; raise for a faster, greedier search
INNER_COST = 13               # per-step cost on In2 (outer layers cost 10)


def gx(x):
    return int(round((x - X0) / G))


def gy(y):
    return int(round((y - Y0) / G))


def seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    l2 = dx * dx + dy * dy
    if l2 == 0:
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / l2
    t = 0 if t < 0 else 1 if t > 1 else t
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


class Field:
    """Per layer: distance to the nearest copper (d1, of net n1) and to the
    nearest copper of any other net (d2). Foreign-class clearance above
    0.15 mm is folded into the stored distance."""

    def __init__(self):
        n = W * H
        self.d1 = [array('f', [INF]) * n for _ in range(NL)]
        self.n1 = [array('i', [0]) * n for _ in range(NL)]
        self.d2 = [array('f', [INF]) * n for _ in range(NL)]
        self.hole = bytearray(n)      # no via: too close to another hole
        self.smd = bytearray(n)       # no via: on or beside an SMD pad
        self.inside = bytearray(n)

    def _put(self, layer, i, d, net):
        d1, n1, d2 = self.d1[layer], self.n1[layer], self.d2[layer]
        if n1[i] == net:
            if d < d1[i]:
                d1[i] = d
        elif d < d1[i]:
            if n1[i] != 0 and d1[i] < d2[i]:
                d2[i] = d1[i]
            d1[i] = d
            n1[i] = net
        elif d < d2[i]:
            d2[i] = d

    def seg(self, layer, net, ax, ay, bx, by, radius, extra=0.0):
        r = MAXR + radius
        for j in range(max(0, gy(min(ay, by) - r)), min(H - 1, gy(max(ay, by) + r)) + 1):
            py = Y0 + j * G
            row = j * W
            for i in range(max(0, gx(min(ax, bx) - r)), min(W - 1, gx(max(ax, bx) + r)) + 1):
                d = seg_dist(X0 + i * G, py, ax, ay, bx, by) - radius - extra
                if d < MAXR:
                    self._put(layer, row + i, d, net)

    def rect(self, layer, net, x0, y0, x1, y1, extra=0.0):
        r = MAXR
        for j in range(max(0, gy(y0 - r)), min(H - 1, gy(y1 + r)) + 1):
            py = Y0 + j * G
            dy = y0 - py if py < y0 else py - y1 if py > y1 else 0.0
            row = j * W
            for i in range(max(0, gx(x0 - r)), min(W - 1, gx(x1 + r)) + 1):
                px = X0 + i * G
                dx = x0 - px if px < x0 else px - x1 if px > x1 else 0.0
                d = math.hypot(dx, dy) - extra
                if d < MAXR:
                    self._put(layer, row + i, d, net)

    def mark(self, arr, x, y, radius):
        for j in range(max(0, gy(y - radius)), min(H - 1, gy(y + radius)) + 1):
            for i in range(max(0, gx(x - radius)), min(W - 1, gx(x + radius)) + 1):
                if math.hypot(X0 + i * G - x, Y0 + j * G - y) <= radius:
                    arr[j * W + i] = 1

    def mark_rect(self, arr, x0, y0, x1, y1):
        for j in range(max(0, gy(y0)), min(H - 1, gy(y1)) + 1):
            for i in range(max(0, gx(x0)), min(W - 1, gx(x1)) + 1):
                arr[j * W + i] = 1

    def free(self, layer, i, net, r):
        if not self.inside[i]:
            return False
        d = self.d2[layer][i] if self.n1[layer][i] == net else self.d1[layer][i]
        return d >= r


class Board:
    def __init__(self, data):
        self.data = data
        self.ids = {}
        self.cls = data['classes']
        self.f = Field()
        self.new_tracks = []
        self.new_vias = []
        t0 = time.time()
        self._inside()
        for p in data['pads']:
            self._add_pad(p)
        for t in data['tracks']:
            self.add_track(t, record=False)
        for v in data['vias']:
            self.add_via(v, record=False)
        for g in data['graphics']:
            layer = LID[g['layer']]
            self.f.seg(layer, self.nid('#graphic-' + g['ref']), g['a'][0], g['a'][1], g['b'][0], g['b'][1], g['w'] / 2)
        o = data['outline']
        for a, b in zip(o, o[1:] + o[:1]):
            for layer in range(NL):
                self.f.seg(layer, -2, a[0], a[1], b[0], b[1], 0.37)
        for x0, y0, x1, y1 in KEEPOUTS:
            for layer in range(NL):
                self.f.rect(layer, -2, x0, y0, x1, y1)
        self.f.rect(2, -2, *COIL)      # no inner copper under the NFC coil
        # coil interior on the rear belongs to the coil's inner terminal only
        self.f.rect(1, self.nid('/05  SENSORS + EXPANSION/NFC_LB'), COIL[0] + 4.3, COIL[1] + 4.3, COIL[2] - 4.3, COIL[3] - 4.3)
        print(f'field built in {time.time() - t0:.1f}s', file=sys.stderr)

    def nid(self, name):
        if name == '':
            return -2
        if name not in self.ids:
            self.ids[name] = len(self.ids) + 1
        return self.ids[name]

    def extra(self, name):
        return max(0.0, CLASS_CLR.get(self.cls.get(name, 'Default'), 0.15) - 0.15)

    def _inside(self):
        o = self.data['outline']
        n = len(o)
        for j in range(H):
            py = Y0 + j * G + 1e-6
            xs = []
            for k in range(n):
                (ax, ay), (bx, by) = o[k], o[(k + 1) % n]
                if (ay > py) != (by > py):
                    xs.append(ax + (py - ay) * (bx - ax) / (by - ay))
            xs.sort()
            for a, b in zip(xs[0::2], xs[1::2]):
                for i in range(max(0, gx(a) + 1), min(W - 1, gx(b) - 1) + 1):
                    self.f.inside[j * W + i] = 1

    def _add_pad(self, p):
        net = self.nid(p['net']) if p['net'] else -2
        if not p['num'] and not p['net']:
            net = -2
        x0, y0, x1, y1 = p['box']
        ex = self.extra(p['net'])
        layers = [l for l, k in ((0, 'F'), (1, 'B')) if p[k]]
        if p['tht']:
            layers = [0, 1, 2]
        for layer in layers:
            if p['circle'] or (p['tht'] and not (p['F'] or p['B'])):
                rad = max((x1 - x0) / 2, p['drill'] / 2 + 0.1)
                self.f.seg(layer, net, p['x'], p['y'], p['x'], p['y'], rad, ex)
            else:
                self.f.rect(layer, net, x0, y0, x1, y1, ex)
        if p['drill'] > 0:
            self.f.mark(self.f.hole, p['x'], p['y'], p['drill'] / 2 + VIA_DRILL / 2 + 0.25 + MARGIN)
        if not p['tht']:
            self.f.mark_rect(self.f.smd, x0 - 0.4, y0 - 0.4, x1 + 0.4, y1 + 0.4)

    def add_track(self, t, record=True):
        layer = LID[t['layer']]
        self.f.seg(layer, self.nid(t['net']), t['a'][0], t['a'][1], t['b'][0], t['b'][1], t['w'] / 2, self.extra(t['net']))
        if record:
            self.data['tracks'].append(t)
            self.new_tracks.append(t)

    def add_via(self, v, record=True):
        for layer in range(NL):
            self.f.seg(layer, self.nid(v['net']), v['x'], v['y'], v['x'], v['y'], v['d'] / 2, self.extra(v['net']))
        self.f.mark(self.f.hole, v['x'], v['y'], v['drill'] / 2 + VIA_DRILL / 2 + 0.25 + MARGIN)
        if record:
            self.data['vias'].append(v)
            self.new_vias.append(v)

    # ---- islands --------------------------------------------------------
    def islands(self, name):
        """Group the copper of one net into connected islands."""
        items = []
        for p in self.data['pads']:
            if p['net'] == name:
                items.append(('pad', p))
        for t in self.data['tracks']:
            if t['net'] == name:
                items.append(('trk', t))
        for v in self.data['vias']:
            if v['net'] == name:
                items.append(('via', v))
        parent = list(range(len(items) + 1))
        plane = len(items)

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        def union(a, b):
            parent[find(a)] = find(b)

        def layers(it):
            k, o = it
            if k == 'pad':
                return {0, 1, 2} if o['tht'] else {l for l, key in ((0, 'F'), (1, 'B')) if o[key]}
            if k == 'trk':
                return {LID[o['layer']]}
            return {0, 1, 2}

        def touch(a, b):
            (ka, oa), (kb, ob) = a, b
            if not (layers(a) & layers(b)):
                return False
            if ka == 'trk' and kb == 'trk':
                tol = (oa['w'] + ob['w']) / 2 - 0.01
                return any(seg_dist(q[0], q[1], *ob['a'], *ob['b']) <= tol for q in (oa['a'], oa['b'])) or \
                    any(seg_dist(q[0], q[1], *oa['a'], *oa['b']) <= tol for q in (ob['a'], ob['b']))
            if ka == 'trk':
                return touch(b, a)
            if ka == 'pad':
                x0, y0, x1, y1 = oa['box']
                if kb == 'trk':
                    for q in (ob['a'], ob['b']):
                        if x0 - 0.01 <= q[0] <= x1 + 0.01 and y0 - 0.01 <= q[1] <= y1 + 0.01:
                            return True
                    # segment crossing a pad counts too
                    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
                    return seg_dist(cx, cy, *ob['a'], *ob['b']) <= min(x1 - x0, y1 - y0) / 2
                if kb == 'via':
                    return x0 - 0.05 <= ob['x'] <= x1 + 0.05 and y0 - 0.05 <= ob['y'] <= y1 + 0.05
                if kb == 'pad':
                    return oa is not ob and not (x1 < ob['box'][0] or ob['box'][2] < x0 or y1 < ob['box'][1] or ob['box'][3] < y0)
            if ka == 'via':
                if kb == 'trk':
                    return any(math.hypot(q[0] - oa['x'], q[1] - oa['y']) <= oa['d'] / 2 for q in (ob['a'], ob['b'])) or \
                        seg_dist(oa['x'], oa['y'], *ob['a'], *ob['b']) <= ob['w'] / 2
                if kb == 'via':
                    return math.hypot(oa['x'] - ob['x'], oa['y'] - ob['y']) <= 0.3
                return touch(b, a)
            return False

        for a in range(len(items)):
            if name == 'GND' and (items[a][0] == 'via' or (items[a][0] == 'pad' and items[a][1]['tht'])):
                union(a, plane)
            for b in range(a + 1, len(items)):
                if find(a) != find(b) and touch(items[a], items[b]):
                    union(a, b)
        groups = {}
        for a in range(len(items)):
            groups.setdefault(find(a), []).append(items[a])
        out = list(groups.values())
        if name == 'GND':
            out.sort(key=lambda g: 0 if any(k == 'via' for k, _ in g) else 1)
        return out

    def cells(self, island):
        """Grid cells (layer, i, j) -> exact (x, y) anchor for an island."""
        out = {}
        for k, o in island:
            if k == 'pad':
                ls = [0, 1, 2] if o['tht'] else [l for l, key in ((0, 'F'), (1, 'B')) if o[key]]
                for l in ls:
                    out[(l, gx(o['x']), gy(o['y']))] = (o['x'], o['y'])
            elif k == 'via':
                for l in range(NL):
                    out[(l, gx(o['x']), gy(o['y']))] = (o['x'], o['y'])
            else:
                l = LID[o['layer']]
                (ax, ay), (bx, by) = o['a'], o['b']
                n = max(1, int(math.hypot(bx - ax, by - ay) / G))
                for s in range(n + 1):
                    x, y = ax + (bx - ax) * s / n, ay + (by - ay) * s / n
                    out.setdefault((l, gx(x), gy(y)), (x, y))
        return out

    # ---- fine-pitch escapes ----------------------------------------------
    def escapes(self, names, width=0.2):
        """Straight, staggered stubs out of unconnected fine-pitch pads so that
        neighbouring pads cannot block each other during the maze search."""
        by_ref = {}
        for p in self.data['pads']:
            by_ref.setdefault(p['ref'], []).append(p)
        made = 0
        for ref, pads in by_ref.items():
            cx = sum(p['x'] for p in pads) / len(pads)
            cy = sum(p['y'] for p in pads) / len(pads)
            todo = []
            for p in pads:
                if p['net'] not in names or p['tht']:
                    continue
                if not any(q is not p and math.hypot(q['x'] - p['x'], q['y'] - p['y']) < 0.7 for q in pads):
                    continue
                x0, y0, x1, y1 = p['box']
                lx, ly = x1 - x0, y1 - y0
                if lx > ly + 0.05:
                    horiz = True
                elif ly > lx + 0.05:
                    horiz = False
                else:
                    horiz = abs(p['x'] - cx) >= abs(p['y'] - cy)
                if horiz:
                    d = (1 if p['x'] >= cx else -1, 0)
                    end = x1 if d[0] > 0 else x0
                    reach = abs(end - p['x'])
                else:
                    d = (0, 1 if p['y'] >= cy else -1)
                    end = y1 if d[1] > 0 else y0
                    reach = abs(end - p['y'])
                todo.append((p, d, reach))
            for p, d, reach in todo:
                # is this pad still alone?
                touching = any(t['net'] == p['net'] and LID[t['layer']] == (0 if p['F'] else 1) and
                               any(p['box'][0] - 0.01 <= q[0] <= p['box'][2] + 0.01 and p['box'][1] - 0.01 <= q[1] <= p['box'][3] + 0.01 for q in (t['a'], t['b']))
                               for t in self.data['tracks'])
                if touching:
                    continue
                rank = sorted(q['y'] if d[0] else q['x'] for q, dd, _ in todo if dd == d).index(p['y'] if d[0] else p['x'])
                want = reach + 0.5 + 0.7 * (rank % 3)
                layer = 0 if p['F'] else 1
                net = self.nid(p['net'])
                clr = CLASS_CLR.get(self.cls.get(p['net'], 'Default'), 0.15)
                good = 0.0
                s = reach
                while s <= want + 1e-9:
                    i, j = gx(p['x'] + d[0] * s), gy(p['y'] + d[1] * s)
                    if not self.f.free(layer, j * W + i, net, clr + width / 2 + 0.005):
                        break
                    good = s
                    s += G
                if good < reach + 0.3:
                    continue
                self.add_track({'a': [p['x'], p['y']], 'b': [round(p['x'] + d[0] * good, 4), round(p['y'] + d[1] * good, 4)],
                                'w': width, 'layer': 'F' if layer == 0 else 'B', 'net': p['net']})
                made += 1
        return made

    def escapable(self, cells, net, r, limit=600):
        """Cheap flood: can this island leave its own copper at all?"""
        seen = set(cells)
        todo = list(cells)
        n = 0
        while todo and n < limit:
            l, i, j = todo.pop()
            n += 1
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                c = (l, i + dx, j + dy)
                if c not in seen and 0 <= c[1] < W and 0 <= c[2] < H and self.f.free(l, c[2] * W + c[1], net, r):
                    seen.add(c)
                    todo.append(c)
        return n >= limit

    # ---- search ---------------------------------------------------------
    def route(self, name, src, dst, width, budget=600000, to_plane=False):
        net = self.nid(name)
        clr = CLASS_CLR.get(self.cls.get(name, 'Default'), 0.15)
        r_trk = clr + width / 2 + MARGIN
        r_via = clr + VIA_D / 2 + MARGIN
        f = self.f
        own = set(src) | set(dst)
        cache = {}
        if not self.escapable(src, net, r_trk) and not to_plane:
            # an island walled in on its own layer can still leave through a via
            if not any(self.f.free(m, j * W + i, net, r_trk) for (l, i, j) in src for m in range(NL) if m != l):
                return None

        def ok(l, i, j):
            key = (l, i, j)
            v = cache.get(key)
            if v is None:
                if not (0 <= i < W and 0 <= j < H):
                    v = False
                else:
                    v = key in own or f.free(l, j * W + i, net, r_trk)
                cache[key] = v
            return v

        def via_ok(i, j):
            idx = j * W + i
            return not f.hole[idx] and not f.smd[idx] and f.free(0, idx, net, r_via) and f.free(1, idx, net, r_via) and f.free(2, idx, net, r_via)

        if dst:
            xs = [c[1] for c in dst]
            ys = [c[2] for c in dst]
            bx0, bx1, by0, by1 = min(xs), max(xs), min(ys), max(ys)
        moves = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]

        def h(i, j):
            if to_plane:
                return 0
            dx = bx0 - i if i < bx0 else i - bx1 if i > bx1 else 0
            dy = by0 - j if j < by0 else j - by1 if j > by1 else 0
            return int(HWEIGHT * (10 * max(dx, dy) + 4 * min(dx, dy)))

        heap = []
        best = {}
        prev = {}
        for (l, i, j) in src:
            s = (l, i, j, 8)
            best[s] = 0
            heapq.heappush(heap, (h(i, j), 0, s))
        n = 0
        goal = None
        while heap:
            _, g, s = heapq.heappop(heap)
            if best.get(s, 1 << 60) < g:
                continue
            l, i, j, d = s
            if to_plane:
                if g >= 120 and via_ok(i, j):
                    goal = s
                    break
            elif (l, i, j) in dst:
                goal = s
                break
            n += 1
            if n > budget:
                break
            for k, (dx, dy) in enumerate(moves):
                if d != 8:
                    turn = (k - d) % 8
                    turn = min(turn, 8 - turn)
                    if turn > 2:
                        continue
                    pen = (0, 4, 12)[turn]
                else:
                    pen = 0
                ni, nj = i + dx, j + dy
                if not ok(l, ni, nj):
                    continue
                if dx and dy and not (ok(l, ni, j) and ok(l, i, nj)):
                    continue
                ng = g + ((14 if dx and dy else 10) if l != 2 else (18 if dx and dy else INNER_COST)) + pen
                ns = (l, ni, nj, k)
                if ng < best.get(ns, 1 << 60):
                    best[ns] = ng
                    prev[ns] = s
                    heapq.heappush(heap, (ng + h(ni, nj), ng, ns))
            if not to_plane and via_ok(i, j):
                for m in range(NL):
                    if m == l or not ok(m, i, j):
                        continue
                    ng = g + 250
                    ns = (m, i, j, 8)
                    if ng < best.get(ns, 1 << 60):
                        best[ns] = ng
                        prev[ns] = s
                        heapq.heappush(heap, (ng + h(i, j), ng, ns))
        if goal is None:
            return None
        path = [goal]
        while path[-1] in prev:
            path.append(prev[path[-1]])
        path.reverse()
        # emit geometry
        pts = [(s[0], X0 + s[1] * G, Y0 + s[2] * G) for s in path]
        a0 = src.get(path[0][:3])
        if a0:
            pts[0] = (pts[0][0], a0[0], a0[1])
        a1 = dst.get(path[-1][:3]) if dst else None
        if a1:
            pts[-1] = (pts[-1][0], a1[0], a1[1])
        tracks, vias = [], []
        run = [pts[0]]
        for p, q in zip(pts, pts[1:]):
            if p[0] != q[0]:
                self._flush(run, name, width, tracks)
                vias.append({'x': round(p[1], 4), 'y': round(p[2], 4), 'd': VIA_D, 'drill': VIA_DRILL, 'net': name})
                run = [q]
            else:
                run.append(q)
        self._flush(run, name, width, tracks)
        if to_plane:
            vias.append({'x': round(pts[-1][1], 4), 'y': round(pts[-1][2], 4), 'd': VIA_D, 'drill': VIA_DRILL, 'net': name})
        for t in tracks:
            self.add_track(t)
        for v in vias:
            self.add_via(v)
        return n

    @staticmethod
    def _flush(run, name, width, tracks):
        if len(run) < 2:
            return
        layer = LNAME[run[0][0]]
        start = run[0]
        for k in range(1, len(run)):
            last = k == len(run) - 1
            if not last:
                ax, ay = run[k][1] - run[k - 1][1], run[k][2] - run[k - 1][2]
                bx, by = run[k + 1][1] - run[k][1], run[k + 1][2] - run[k][2]
                if abs(ax * by - ay * bx) < 1e-9 and ax * bx + ay * by > 0 and k > 1 and k < len(run) - 2:
                    continue
            if (start[1], start[2]) != (run[k][1], run[k][2]):
                tracks.append({'a': [round(start[1], 4), round(start[2], 4)], 'b': [round(run[k][1], 4), round(run[k][2], 4)],
                               'w': width, 'layer': layer, 'net': name})
            start = run[k]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('board')
    ap.add_argument('out')
    ap.add_argument('--only', nargs='*')
    ap.add_argument('--skip', nargs='*', default=[])
    ap.add_argument('--width', nargs='*', default=[], help='NET=mm overrides (suffix match)')
    ap.add_argument('--budget', type=int, default=1500000)
    ap.add_argument('--config')
    ap.add_argument('--retries', type=int, default=4)
    ap.add_argument('--hweight', type=float, default=1.4)
    ap.add_argument('--via', nargs=2, type=float, metavar=('DIA', 'DRILL'), help='via size for this run (default 0.6 0.3)')
    a = ap.parse_args()
    data = json.load(open(a.board))
    global VIA_D, VIA_DRILL, HWEIGHT
    if a.via:
        VIA_D, VIA_DRILL = a.via
    HWEIGHT = a.hweight
    cfg = json.load(open(a.config)) if a.config else {}
    ripped = {'tracks': [], 'vias': []}

    def inbox(x, y, box):
        return box[0] <= x <= box[2] and box[1] <= y <= box[3]

    for rip in cfg.get('rips', []):
        box, keep = rip['box'], {tuple(k) for k in rip.get('keep', [])}
        kept = []
        for t in data['tracks']:
            (ax, ay), (bx, by) = t['a'], t['b']
            n = max(2, int(max(abs(bx - ax), abs(by - ay)) / 0.1))
            hit = any(inbox(ax + (bx - ax) * i / n, ay + (by - ay) * i / n, box) for i in range(n + 1))
            if hit and (t['net'], t['layer']) not in keep:
                ripped['tracks'].append(t)
            else:
                kept.append(t)
        data['tracks'] = kept
        kept = []
        for v in data['vias']:
            if inbox(v['x'], v['y'], box) and not any(k[0] == v['net'] for k in keep):
                ripped['vias'].append(v)
            else:
                kept.append(v)
        data['vias'] = kept
    b = Board(data)
    for v in cfg.get('pre_vias', []):
        b.add_via(dict(v))
    widths = dict(w.split('=') for w in a.width)
    widths.update(cfg.get('widths', {}))
    names = sorted({p['net'] for p in data['pads'] if p['net'] and not p['net'].startswith('unconnected')})

    def match(name, pats):
        return any(name == p or name.endswith('/' + p) for p in pats)

    def span(name):
        ps = [p for p in data['pads'] if p['net'] == name]
        return max(p['x'] for p in ps) - min(p['x'] for p in ps) + max(p['y'] for p in ps) - min(p['y'] for p in ps)
    prio = cfg.get('priority', [])

    def rank(name):
        for k, pat in enumerate(prio):
            if match(name, [pat]):
                return k
        return len(prio)

    def join(name, budget):
        """Join all islands of one net. Returns True when the net is whole."""
        width = CLASS_W.get(b.cls.get(name, 'Default'), 0.2)
        for pat, w in widths.items():
            if match(name, [pat]):
                width = float(w)
        while True:
            isl = b.islands(name)
            if len(isl) < 2:
                return True
            cells = [b.cells(g) for g in isl]
            if name == 'GND':
                ok = True
                for g, c in zip(isl, cells):
                    if any(k == 'via' or (k == 'pad' and o['tht']) for k, o in g):
                        continue
                    if b.route(name, c, {}, 0.3, budget, to_plane=True) is None:
                        ok = False
                return ok
            order = sorted(range(len(isl)), key=lambda k: len(cells[k]))
            done = False
            for k in order:
                dst = {}
                for m, c in enumerate(cells):
                    if m != k:
                        dst.update(c)
                t0 = time.time()
                n = b.route(name, cells[k], dst, width, budget)
                if n is None and width > 0.2:
                    n = b.route(name, cells[k], dst, 0.2 if width <= 0.3 else 0.3, budget)
                if n is not None:
                    print(f'  {name.split("/")[-1]}: joined ({n} expansions, {time.time() - t0:.1f}s)', file=sys.stderr, flush=True)
                    done = True
                    break
            if not done:
                print(f'  {name.split("/")[-1]}: FAILED with {len(isl)} islands', file=sys.stderr, flush=True)
                return False

    def open_nets():
        out = []
        for name in names:
            if a.only and not match(name, a.only):
                continue
            if match(name, a.skip):
                continue
            if len(b.islands(name)) > 1:
                out.append(name)
        return out

    jobs = open_nets()
    jobs.sort(key=lambda n: (n in ('GND', '+3V3'), rank(n), span(n)))
    made = b.escapes(set(jobs))
    print('open nets:', len(jobs), 'escape stubs:', made, file=sys.stderr)
    failed = [n for n in jobs if not join(n, a.budget)]
    rips = {}
    for attempt in range(a.retries):
        if not failed:
            break
        # rip-up: router-added copper of other nets that crowds a walled-in island
        victims = set()
        for name in failed:
            net = b.nid(name)
            clr = CLASS_CLR.get(b.cls.get(name, 'Default'), 0.15)
            for g in b.islands(name):
                c = b.cells(g)
                if b.escapable(c, net, clr + 0.1 + MARGIN, limit=4000):
                    continue
                pts = list(c.values())
                for t in b.new_tracks:
                    if t['net'] != name and t['net'] != 'GND' and rips.get(t['net'], 0) < 2 and \
                            any(seg_dist(x, y, *t['a'], *t['b']) < 1.3 for x, y in pts):
                        victims.add(t['net'])
                for v in b.new_vias:
                    if v['net'] != name and v['net'] != 'GND' and rips.get(v['net'], 0) < 2 and \
                            any(math.hypot(x - v['x'], y - v['y']) < 1.5 for x, y in pts):
                        victims.add(v['net'])
        print(f'retry {attempt + 1}: failed {len(failed)}, ripping {sorted(n.split("/")[-1] for n in victims)}', file=sys.stderr, flush=True)
        for n in victims:
            rips[n] = rips.get(n, 0) + 1
        keep_t = [t for t in b.new_tracks if t['net'] not in victims]
        keep_v = [v for v in b.new_vias if v['net'] not in victims]
        gone_t = {id(t) for t in b.new_tracks if t['net'] in victims}
        gone_v = {id(v) for v in b.new_vias if v['net'] in victims}
        data['tracks'] = [t for t in data['tracks'] if id(t) not in gone_t]
        data['vias'] = [v for v in data['vias'] if id(v) not in gone_v]
        b = Board(data)
        b.new_tracks, b.new_vias = keep_t, keep_v
        order = failed + sorted(victims, key=span)
        b.escapes(set(order))
        failed = [n for n in order if not join(n, a.budget * (2 if not victims else 1))]
        failed += [n for n in open_nets() if n not in failed and not join(n, a.budget)]
    failed = open_nets()
    json.dump({'tracks': b.new_tracks, 'vias': b.new_vias, 'failed': failed, 'rip_tracks': ripped['tracks'], 'rip_vias': ripped['vias']}, open(a.out, 'w'))
    print('new tracks', len(b.new_tracks), 'new vias', len(b.new_vias), 'failed', failed, file=sys.stderr)


if __name__ == '__main__':
    main()

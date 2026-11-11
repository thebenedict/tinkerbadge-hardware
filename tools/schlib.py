#!/usr/bin/env python3
"""Small S-expression helpers for scripted edits of native KiCad schematics.

Used by the 2026-11-10 design-review change scripts. Parses a .kicad_sch file
into nested lists, resolves symbol pin positions, traces wire connectivity and
writes the file back. Run `kicad-cli sch upgrade --force` afterwards to restore
KiCad's own formatting.
"""
import math
import re
import uuid as _uuid


class Sym(str):
    """Bare (unquoted) token."""


def parse(text):
    tokens = re.findall(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+', text)
    stack = [[]]
    for t in tokens:
        if t == '(':
            new = []
            stack[-1].append(new)
            stack.append(new)
        elif t == ')':
            stack.pop()
        elif t.startswith('"'):
            stack[-1].append(bytes(t[1:-1], 'utf-8').decode('unicode_escape').encode('latin-1').decode('utf-8') if '\\' in t else t[1:-1])
        else:
            stack[-1].append(Sym(t))
    return stack[0][0]


def dump(node, depth=0):
    if isinstance(node, Sym):
        return str(node)
    if isinstance(node, (int, float)):
        return ('%.4f' % node).rstrip('0').rstrip('.')
    if isinstance(node, str):
        return '"' + node.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'
    simple = all(not isinstance(c, list) for c in node)
    if simple:
        return '(' + ' '.join(dump(c) for c in node) + ')'
    out = '(' + dump(node[0])
    pad = '\t' * (depth + 1)
    for c in node[1:]:
        if isinstance(c, list):
            out += '\n' + pad + dump(c, depth + 1)
        else:
            out += ' ' + dump(c)
    return out + '\n' + '\t' * depth + ')'


def kids(node, key):
    return [c for c in node[1:] if isinstance(c, list) and c and c[0] == key]


def kid(node, key):
    k = kids(node, key)
    return k[0] if k else None


def prop(sym, name):
    for p in kids(sym, 'property'):
        if p[1] == name:
            return p
    return None


def pval(sym, name, default=None):
    p = prop(sym, name)
    return p[2] if p else default


def r2(v):
    return round(float(v), 2)


def pt(node):
    return (r2(node[1]), r2(node[2]))


def new_uuid():
    return str(_uuid.uuid4())


class Sheet:
    def __init__(self, path):
        self.path = path
        self.root = parse(open(path, encoding='utf-8').read())
        self.libs = {s[1]: s for s in kids(kid(self.root, 'lib_symbols'), 'symbol')}

    def save(self):
        text = dump(self.root) + '\n'
        open(self.path, 'w', encoding='utf-8').write(text)

    # ---- symbols -------------------------------------------------------
    def symbols(self):
        return kids(self.root, 'symbol')

    def by_ref(self, ref):
        for s in self.symbols():
            if pval(s, 'Reference') == ref:
                return s
        raise KeyError(ref)

    def lib_pins(self, lib_id):
        lib = self.libs[lib_id]
        if kid(lib, 'extends'):
            lib = self.libs[lib_id.split(':')[0] + ':' + kid(lib, 'extends')[1]] if (lib_id.split(':')[0] + ':' + kid(lib, 'extends')[1]) in self.libs else self.libs[kid(lib, 'extends')[1]]
        pins = []
        for unit in kids(lib, 'symbol'):
            for p in kids(unit, 'pin'):
                at = kid(p, 'at')
                pins.append((kid(p, 'number')[1], kid(p, 'name')[1], float(at[1]), float(at[2])))
        return pins

    def pins(self, sym):
        """Return {number: (x, y)} absolute pin positions."""
        at = kid(sym, 'at')
        x0, y0, rot = float(at[1]), float(at[2]), float(at[3]) if len(at) > 3 else 0.0
        mirror = kid(sym, 'mirror')
        out = {}
        for num, name, px, py in self.lib_pins(kid(sym, 'lib_id')[1]):
            if mirror is not None:
                if mirror[1] == 'x':
                    py = -py
                else:
                    px = -px
            a = math.radians(rot)
            rx = px * math.cos(a) - py * math.sin(a)
            ry = px * math.sin(a) + py * math.cos(a)
            out[num] = (r2(x0 + rx), r2(y0 - ry))
        return out

    def pin_names(self, sym):
        return {num: name for num, name, _, _ in self.lib_pins(kid(sym, 'lib_id')[1])}

    # ---- connectivity --------------------------------------------------
    def wires(self):
        return kids(self.root, 'wire')

    @staticmethod
    def wire_pts(w):
        p = kid(w, 'pts')
        return pt(p[1]), pt(p[2])

    @staticmethod
    def on_seg(p, a, b):
        if abs((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])) > 1e-6:
            return False
        return min(a[0], b[0]) - 1e-6 <= p[0] <= max(a[0], b[0]) + 1e-6 and min(a[1], b[1]) - 1e-6 <= p[1] <= max(a[1], b[1]) + 1e-6

    def trace(self, start):
        """Flood along wires from a point. Returns (wires, points)."""
        junctions = {pt(kid(j, 'at')) for j in kids(self.root, 'junction')}
        todo = [start]
        seen_pts = set()
        found = []
        while todo:
            p = todo.pop()
            if p in seen_pts:
                continue
            seen_pts.add(p)
            for w in self.wires():
                if any(w is f for f in found):
                    continue
                a, b = self.wire_pts(w)
                if p == a or p == b or (p in junctions and self.on_seg(p, a, b)):
                    found.append(w)
                    todo += [a, b]
                    todo += [j for j in junctions if self.on_seg(j, a, b)]
        return found, seen_pts

    def items_at(self, points, kinds=('label', 'global_label', 'hierarchical_label', 'no_connect', 'junction')):
        out = []
        for k in kinds:
            for n in kids(self.root, k):
                if pt(kid(n, 'at')) in points:
                    out.append(n)
        return out

    def remove(self, nodes):
        ids = {id(n) for n in nodes}
        self.root[:] = [c for c in self.root if id(c) not in ids]

    def remove_symbol(self, ref, keep_points=()):
        """Delete a symbol and every wire/label/junction/NC reachable from its
        pins. Power symbols that become dangling are removed too. Returns the
        set of points touched, for the caller to re-label surviving pins."""
        sym = self.by_ref(ref)
        touched = set()
        doomed = [sym]
        for p in self.pins(sym).values():
            ws, pts = self.trace(p)
            doomed += ws
            touched |= pts
        touched -= set(keep_points)
        doomed += self.items_at(touched)
        segs = [self.wire_pts(w) for w in doomed if isinstance(w, list) and w[0] == 'wire']
        for k in ('label', 'global_label', 'hierarchical_label'):
            for n in kids(self.root, k):
                q = pt(kid(n, 'at'))
                if q not in touched and any(self.on_seg(q, a, b) for a, b in segs):
                    doomed.append(n)
        for s in self.symbols():
            if pval(s, 'Reference', '').startswith('#') and s is not sym:
                if any(q in touched for q in self.pins(s).values()):
                    doomed.append(s)
        self.remove(doomed)
        return touched

    # ---- creation ------------------------------------------------------
    def add(self, node):
        # keep sheet_instances / embedded_fonts at the end
        idx = len(self.root)
        for i, c in enumerate(self.root):
            if isinstance(c, list) and c and c[0] in ('sheet_instances', 'embedded_fonts'):
                idx = i
                break
        self.root.insert(idx, node)

    def add_wire(self, a, b):
        self.add(parse(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)) (uuid "{new_uuid()}"))'))

    def add_label(self, name, at, rot=0, kind='label', shape='input'):
        just = 'left bottom' if rot in (0, 90) else 'right bottom'
        if kind == 'label':
            self.add(parse(f'(label "{name}" (at {at[0]} {at[1]} {rot}) (effects (font (size 1.27 1.27)) (justify {just})) (uuid "{new_uuid()}"))'))
        else:
            j = 'left' if rot in (0, 90) else 'right'
            self.add(parse(f'(global_label "{name}" (shape {shape}) (at {at[0]} {at[1]} {rot}) (effects (font (size 1.27 1.27)) (justify {j})) (uuid "{new_uuid()}"))'))

    def add_nc(self, at):
        self.add(parse(f'(no_connect (at {at[0]} {at[1]}) (uuid "{new_uuid()}"))'))

    def add_junction(self, at):
        self.add(parse(f'(junction (at {at[0]} {at[1]}) (diameter 0) (color 0 0 0 0) (uuid "{new_uuid()}"))'))

    def set_prop(self, ref, name, value):
        s = self.by_ref(ref)
        p = prop(s, name)
        if p is None:
            at = kid(s, 'at')
            s.append(parse(f'(property "{name}" "" (at {at[1]} {at[2]} 0) (hide yes) (effects (font (size 1.27 1.27))))'))
            p = prop(s, name)
        p[2] = value

    def clone_symbol(self, src_ref, new_ref, at, rot=0, value=None):
        """Duplicate an existing symbol (same lib symbol) at a new place."""
        import copy
        src = self.by_ref(src_ref)
        s = copy.deepcopy(src)
        old = kid(s, 'at')
        dx, dy = at[0] - float(old[1]), at[1] - float(old[2])
        old[1], old[2] = at[0], at[1]
        if len(old) > 3:
            old[3] = rot
        for m in kids(s, 'mirror'):
            s.remove(m)
        kid(s, 'uuid')[1] = new_uuid()
        for p in kids(s, 'property'):
            a = kid(p, 'at')
            a[1], a[2] = r2(float(a[1]) + dx), r2(float(a[2]) + dy)
        for p in kids(s, 'pin'):
            kid(p, 'uuid')[1] = new_uuid()
        prop(s, 'Reference')[2] = new_ref
        if value is not None:
            prop(s, 'Value')[2] = value
        for inst in kids(s, 'instances'):
            for proj in kids(inst, 'project'):
                for path in kids(proj, 'path'):
                    kid(path, 'reference')[1] = new_ref
        self.add(s)
        return s

#!/usr/bin/env python3
"""Annotated front and rear placement views for human review. KiCad Python (pcbnew + wx).

Usage: render_placement_review.py BOARD OUTDIR [--reuse]

--reuse keeps existing renders in OUTDIR and only redraws the annotation.

Renders the board with `kicad-cli pcb render`, then draws one outline per
functional group over the unchanged render. Group outlines are computed from
the native footprint bounding boxes in BOARD; the board file is not written.
The image-to-board fit is measured from the four M2 mounting holes in a
transparent-background render taken with the same camera.
"""
import pathlib
import subprocess
import sys

import pcbnew
import wx

mm = pcbnew.ToMM
W, H = 3300, 2400
PAD = 0.45

# colour per domain
C = {'power': (255, 140, 60), 'mcu': (90, 170, 255), 'display': (200, 140, 255), 'light': (255, 225, 80),
     'sense': (110, 230, 150), 'port': (90, 225, 235), 'new': (255, 70, 200), 'mech': (235, 235, 235)}

# name, domain, shape, label side, label nudge (dx, dy) in mm.
# shape: a list of references (one outline around them), {'parts': [[refs], ...]} (one outline per
# sub-list, labelled once), {'rect': (x0, y0, x1, y1)} or {'poly': [(x, y), ...]} in board millimetres.
FRONT = [
    ('Expansion header J503 + 330R series (new)', 'new', {'rect': (183.0, 100.25, 197.75, 112.45)}, 'above', (-9.5, 0)),
    ('Role lights', 'light', {'parts': [['D401', 'C401'], ['D402', 'C402'], ['D403', 'C403']]}, 'below', (0, 0)),
    ('Processor + radio', 'mcu', {'rect': (109.6, 100.3, 140.3, 133.6)}, 'inside-bottom', (0, 0)),
    ('LED data + bulk', 'light', ['R401', 'R402', 'C409'], 'right', (0, 0)),
    ('Status LED', 'light', ['D409', 'R403', 'R404'], 'right', (0, 0)),
    ('Battery sense', 'power', ['R127', 'R128', 'C116'], 'right', (0, 0)),
    ('Buttons: reset, A, B/boot', 'light', {'poly': [(99.4, 131.8), (107.7, 131.8), (107.7, 142.6), (115.4, 142.6), (115.4, 160.4), (99.4, 160.4)]},
     'below', (0, 0)),
    ('USB-C input + protection', 'power', ['D101', 'J101', 'Q101', 'R101', 'R102', 'R121', 'R122', 'R123', 'U105'], 'below', (9.5, 0)),
    ('Power mux + charger', 'power', ['C101', 'C102', 'C103', 'C104', 'C105', 'C106', 'R107', 'R108', 'R109', 'R111', 'R112', 'R113',
                                      'R114', 'R116', 'U101', 'U102'], 'above', (-6, 0)),
    ('I2C pull-ups', 'sense', ['R501', 'R502'], 'above', (0, 0)),
    ('Motion sensor', 'sense', ['U502', 'C503', 'C504', 'C505'], 'below', (0, 0)),
    ('I/O expander', 'mcu', ['U506', 'C514', 'C515'], 'above', (-6, 0)),
    ('Cell NTCs', 'power', ['RT101', 'RT102'], 'right', (0, 0)),
    ('3.3 V converter', 'power', ['U103', 'L101', 'C107', 'C108', 'C109', 'R117', 'R118'], 'left', (0, 0)),
    ('Display load switch', 'display', ['U104', 'C112', 'C113', 'C114', 'R119'], 'below', (0, 0)),
    ('Display boost + panel rails', 'display', ['C301', 'C302', 'C304', 'C305', 'C306', 'C307', 'C308', 'C309', 'C310', 'C311', 'D301',
                                               'D302', 'D303', 'Q301', 'R301', 'R302', 'L301'], 'above', (0, 0)),
    ('Display connector', 'display', {'parts': [['J301', 'C303'], ['R308']]}, 'left', (0, 3.0)),
    ('Accessory switch + Qwiic', 'port', {'parts': [['U505', 'C511', 'C512', 'C513', 'R508', 'R509', 'R510', 'R511'], ['J501', 'R512'], ['R513']]},
     'above', (0, 0)),
    ('NFC tag', 'sense', ['U503', 'C506', 'C507', 'C508', 'R503'], 'below', (0, 0)),
    ('Dock sensing', 'power', {'parts': [['Q102', 'R124', 'R125', 'R126'], ['D102']]}, 'above', (0, 0)),
    ('IR receiver', 'sense', ['U504', 'C509', 'C510', 'R507'], 'above', (0, 0)),
    ('Light sensor', 'sense', ['U501', 'C501', 'C502'], 'below', (-5, 0)),
    ('IR emitter', 'sense', ['D501', 'Q501', 'R504', 'R505', 'R506'], 'above', (0, 0)),
    ('Affinity lights (5)', 'light', {'parts': [['D407', 'C407'], ['D404', 'C404'], ['D405', 'C405'], ['D406', 'C406'], ['D408', 'C408']]},
     'above', (0, 0)),
]
REAR = [
    ('Expansion header J503: full legend (new)', 'new', {'rect': (169.2, 100.25, 197.75, 112.75)}, 'right', (0, 0)),
    ('Probe pads', 'mcu', ['TP101', 'TP201', 'TP202', 'TP203', 'TP204', 'TP205', 'TP206', 'TP301', 'TP501', 'TP502'], 'below', (0, 3.2)),
    ('Battery connector', 'power', ['J102'], 'right', (0, 0)),
    ('Dock pads', 'power', ['J103'], 'above', (0, -2.6)),
    ('NFC coil', 'sense', ['AE501'], 'above', (0, -2.6)),
]
# dashed mechanical outlines: label, footprint, label position as a fraction of the outline
OUTLINES = {'F': [('Display glass above, raised 4.5 mm', 'MECH_PANEL', (0.13, 0.53))], 'B': [('Battery allowance', 'MECH_BATTERY', (0.5, 0.75))]}
CROP = (93.0, 91.5, 217.0, 185.5)      # board millimetres kept in the annotated image
CLOSEUP = (166.0, 98.5, 205.0, 119.5)   # unannotated close-up of the expansion header, both sides


def run(*a):
    subprocess.run(a, check=True, capture_output=True)


def hole_fit(path, holes, mirrored):
    """Least-squares image fit from transparent hole centres. Returns (ax, ay, s, sign)."""
    img = wx.Image(str(path))
    alpha, w = img.GetAlpha(), img.GetWidth()
    # first guess from the board edge: scan for the opaque extent of the row through the lower holes
    rows = [y for y in range(0, img.GetHeight(), 4) if any(alpha[y * w + x] > 200 for x in range(0, w, 16))]
    top, bottom = rows[0], rows[-1]
    s = (bottom - top) / 80.0
    cx = w / 2
    pts = []
    for hx, hy in holes:
        gx = cx + (-(hx - 155.0) if mirrored else (hx - 155.0)) * s
        gy = top + (hy - 100.0) * s
        sx = sy = n = 0
        r = int(2.2 * s)
        for y in range(int(gy) - r, int(gy) + r):
            for x in range(int(gx) - r, int(gx) + r):
                if alpha[y * w + x] < 40:
                    sx += x
                    sy += y
                    n += 1
        assert n > 50, ('hole not found', hx, hy, gx, gy)
        pts.append((sx / n, sy / n))
    (x0, y0), (x1, y1) = pts[0], pts[3]
    (hx0, hy0), (hx1, hy1) = holes[0], holes[3]
    sgn = -1 if mirrored else 1
    s = ((x1 - x0) * sgn / (hx1 - hx0) + (y1 - y0) / (hy1 - hy0)) / 2
    ax = sum(px - sgn * s * hx for (px, _), (hx, _) in zip(pts, holes)) / len(pts)
    ay = sum(py - s * hy for (_, py), (_, hy) in zip(pts, holes)) / len(pts)
    err = max(abs(ax + sgn * s * hx - px) + abs(ay + s * hy - py) for (px, py), (hx, hy) in zip(pts, holes))
    return ax, ay, s, sgn, err


def bbox(b, refs):
    x0 = y0 = 1e9
    x1 = y1 = -1e9
    for r in refs:
        f = b.FindFootprintByReference(r)
        assert f is not None, r
        bb = f.GetBoundingBox(False)
        x0, y0 = min(x0, mm(bb.GetLeft())), min(y0, mm(bb.GetTop()))
        x1, y1 = max(x1, mm(bb.GetRight())), max(y1, mm(bb.GetBottom()))
    return x0 - PAD, y0 - PAD, x1 + PAD, y1 + PAD


def annotate(b, base, fit, groups, outlines, title, out):
    ax, ay, s, sgn, _ = fit
    px = lambda x, y: (ax + sgn * s * x, ay + s * y)
    bmp = wx.Bitmap(wx.Image(str(base)))
    dc = wx.MemoryDC(bmp)
    gc = wx.GraphicsContext.Create(dc)
    font = wx.Font(wx.FontInfo(27).Bold().FaceName('Helvetica Neue'))
    small = wx.Font(wx.FontInfo(23).FaceName('Helvetica Neue'))

    def label(text, x, y, col, f=font, anchor='lt'):
        gc.SetFont(f, wx.Colour(255, 255, 255))
        tw, th = gc.GetTextExtent(text)[:2]
        if 'r' in anchor:
            x -= tw + 16
        if 'c' in anchor:
            x -= tw / 2 + 8
        if 'b' in anchor:
            y -= th + 8
        x = max(8, min(W - tw - 30, x))
        gc.SetPen(wx.Pen(wx.Colour(*col, 255), 3))
        gc.SetBrush(wx.Brush(wx.Colour(18, 22, 28, 225)))
        gc.DrawRoundedRectangle(x, y, tw + 16, th + 8, 8)
        gc.DrawText(text, x + 8, y + 4)

    for text, ref, (fx, fy) in outlines:
        bb = b.FindFootprintByReference(ref).GetBoundingBox(False)
        x0, y0 = px(mm(bb.GetLeft()), mm(bb.GetTop()))
        x1, y1 = px(mm(bb.GetRight()), mm(bb.GetBottom()))
        x0, x1 = min(x0, x1), max(x0, x1)
        pen = wx.Pen(wx.Colour(*C['mech'], 230), 4, wx.PENSTYLE_LONG_DASH)
        gc.SetPen(pen)
        gc.SetBrush(wx.TRANSPARENT_BRUSH)
        gc.DrawRectangle(x0, y0, x1 - x0, y1 - y0)
        label(text, x0 + (x1 - x0) * (fx if sgn > 0 else 1 - fx), y0 + (y1 - y0) * fy, C['mech'], small, 'c')

    for name, dom, spec, side, (dx, dy) in groups:
        col = C[dom]
        width = 7 if dom == 'new' else 4
        gc.SetPen(wx.Pen(wx.Colour(*col, 255), width))
        gc.SetBrush(wx.Brush(wx.Colour(*col, 46 if dom == 'new' else 24)))
        if isinstance(spec, dict) and 'poly' in spec:
            pts = [px(*p) for p in spec['poly']]
            path = gc.CreatePath()
            path.MoveToPoint(*pts[0])
            for p in pts[1:]:
                path.AddLineToPoint(*p)
            path.CloseSubpath()
            gc.DrawPath(path)
            xs, ys = [p[0] for p in spec['poly']], [p[1] for p in spec['poly']]
            r = (min(xs), min(ys), max(xs), max(ys))
        else:
            if isinstance(spec, dict) and 'parts' in spec:
                rects = [bbox(b, part) for part in spec['parts']]
            else:
                rects = [spec['rect'] if isinstance(spec, dict) else bbox(b, spec)]
            for q in rects:
                a, c = px(q[0], q[1]), px(q[2], q[3])
                gc.DrawRoundedRectangle(min(a[0], c[0]), a[1], abs(c[0] - a[0]), c[1] - a[1], 10)
            r = rects[0]
        a, c = px(r[0], r[1]), px(r[2], r[3])
        lx0, lx1 = min(a[0], c[0]), max(a[0], c[0])
        ox, oy = sgn * dx * s, dy * s
        if side == 'above':
            label(name, lx0 + ox, a[1] - 6 + oy, col, anchor='lb')
        elif side == 'below':
            label(name, lx0 + ox, c[1] + 6 + oy, col)
        elif side == 'right':
            label(name, lx1 + 8 + ox, (a[1] + c[1]) / 2 - 22 + oy, col)
        elif side == 'left':
            label(name, lx0 - 8 + ox, (a[1] + c[1]) / 2 - 22 + oy, col, anchor='r')
        else:                                   # inside-bottom
            label(name, lx0 + 10 + ox, c[1] - 6 + oy, col, anchor='lb')

    a, c = px(CROP[0], CROP[1]), px(CROP[2], CROP[3])
    cx0, cx1 = int(max(0, min(a[0], c[0]))), int(min(W, max(a[0], c[0])))
    cy0, cy1 = int(max(0, a[1])), int(min(H, c[1]))
    gc.SetFont(wx.Font(wx.FontInfo(38).Bold().FaceName('Helvetica Neue')), wx.Colour(20, 24, 30))
    gc.DrawText(title, cx0 + 40, cy0 + 28)
    del gc
    dc.SelectObject(wx.NullBitmap)
    bmp.GetSubBitmap(wx.Rect(cx0, cy0, cx1 - cx0, cy1 - cy0)).ConvertToImage().SaveFile(str(out), wx.BITMAP_TYPE_PNG)


def main(board, outdir):
    out = pathlib.Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    app = wx.App(False)  # noqa: F841
    b = pcbnew.LoadBoard(board)
    holes = []
    for ref in ('H1', 'H2', 'H3', 'H4'):
        p = b.FindFootprintByReference(ref).GetPosition()
        holes.append((mm(p.x), mm(p.y)))
    rev = next((d.GetText() for d in b.GetDrawings() if d.Type() == pcbnew.PCB_TEXT_T and d.GetText().startswith('rev ')), '')
    for side, name, groups, mirrored in (('top', 'front', FRONT, False), ('bottom', 'rear', REAR, True)):
        raw, cal = out / f'{name}.png', out / f'.{name}-alpha.png'
        common = ['kicad-cli', 'pcb', 'render', board, '--side', side, '-w', str(W), '--height', str(H)]
        if not ('--reuse' in sys.argv and raw.exists() and cal.exists()):
            run(*common, '-o', str(raw), '--quality', 'high', '--background', 'opaque')
            run(*common, '-o', str(cal), '--quality', 'basic', '--background', 'transparent')
        fit = hole_fit(cal, holes, mirrored)
        print(name, 'fit px/mm %.3f, worst hole error %.2f px' % (fit[2], fit[4]))
        ax, ay, sc, sgn, _ = fit
        xs = sorted((ax + sgn * sc * CLOSEUP[0], ax + sgn * sc * CLOSEUP[2]))
        box = wx.Rect(int(xs[0]), int(ay + sc * CLOSEUP[1]), int(xs[1] - xs[0]), int(sc * (CLOSEUP[3] - CLOSEUP[1])))
        wx.Bitmap(wx.Image(str(raw))).GetSubBitmap(box).ConvertToImage().SaveFile(str(out / f'{name}-header-closeup.png'), wx.BITMAP_TYPE_PNG)
        title = f'Tinker Badge {rev}: {name} placement, functional groups (not routed)'
        annotate(b, raw, fit, groups, OUTLINES['B' if mirrored else 'F'], title, out / f'{name}-functional-groups.png')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

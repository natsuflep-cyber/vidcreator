import numpy as np, cv2, math, random
from PIL import Image, ImageDraw, ImageFont

W, H = 720, 1280
OUT = (38, 28, 40)
import os
_CANDS = [
    os.environ.get("FONT_PATH", ""),
    "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSansCondensed-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]
FONT = next((p for p in _CANDS if p and os.path.exists(p)), None)
if FONT is None:
    raise SystemExit("Fonte não encontrada. Defina a variável FONT_PATH com o caminho de um .ttf em negrito.")
_fonts = {}


def font(sz):
    sz = int(sz)
    if sz not in _fonts:
        _fonts[sz] = ImageFont.truetype(FONT, sz)
    return _fonts[sz]


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def eo(x):  # ease out
    x = clamp(x)
    return 1 - (1 - x) ** 3


def eb(x):  # ease out back (overshoot)
    x = clamp(x)
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def I(v):
    return int(round(v))


def C(img, c):
    return tuple(c) if img.shape[2] == 3 else (c[0], c[1], c[2], 255)


# ---------- primitives ----------
def circ(img, x, y, r, col, ow=0):
    if r <= 0:
        return
    if ow:
        cv2.circle(img, (I(x), I(y)), I(r + ow), C(img, OUT), -1, cv2.LINE_AA)
    cv2.circle(img, (I(x), I(y)), I(r), C(img, col), -1, cv2.LINE_AA)


def ell(img, x, y, ax, ay, col, ow=0, a0=0, a1=360, ang=0):
    if ax <= 0 or ay <= 0:
        return
    if ow:
        cv2.ellipse(img, (I(x), I(y)), (I(ax + ow), I(ay + ow)), ang, a0, a1, C(img, OUT), -1, cv2.LINE_AA)
    cv2.ellipse(img, (I(x), I(y)), (I(ax), I(ay)), ang, a0, a1, C(img, col), -1, cv2.LINE_AA)


def rect(img, x0, y0, x1, y1, col):
    cv2.rectangle(img, (I(x0), I(y0)), (I(x1), I(y1)), C(img, col), -1)


def _rr(img, x0, y0, x1, y1, r, col):
    r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
    c = C(img, col)
    cv2.rectangle(img, (I(x0 + r), I(y0)), (I(x1 - r), I(y1)), c, -1)
    cv2.rectangle(img, (I(x0), I(y0 + r)), (I(x1), I(y1 - r)), c, -1)
    for cx, cy in ((x0 + r, y0 + r), (x1 - r, y0 + r), (x0 + r, y1 - r), (x1 - r, y1 - r)):
        cv2.circle(img, (I(cx), I(cy)), I(r), c, -1, cv2.LINE_AA)


def rr(img, x0, y0, x1, y1, r, col, ow=3):
    if ow:
        _rr(img, x0 - ow, y0 - ow, x1 + ow, y1 + ow, r + ow, OUT)
    _rr(img, x0, y0, x1, y1, r, col)


def poly(img, pts, col, ow=0):
    p = np.array([[I(a), I(b)] for a, b in pts], np.int32)
    if ow:
        cv2.fillPoly(img, [p], C(img, OUT), cv2.LINE_AA)
        cv2.polylines(img, [p], True, C(img, OUT), ow * 2, cv2.LINE_AA)
    cv2.fillPoly(img, [p], C(img, col), cv2.LINE_AA)


def line(img, p, q, col, th, ow=0):
    if ow:
        cv2.line(img, (I(p[0]), I(p[1])), (I(q[0]), I(q[1])), C(img, OUT), I(th + 2 * ow), cv2.LINE_AA)
    cv2.line(img, (I(p[0]), I(p[1])), (I(q[0]), I(q[1])), C(img, col), I(th), cv2.LINE_AA)


def heart(img, x, y, s, col=(255, 80, 130)):
    circ(img, x - s * 0.5, y - s * 0.25, s * 0.55, col)
    circ(img, x + s * 0.5, y - s * 0.25, s * 0.55, col)
    poly(img, [(x - s * 1.02, y - s * 0.05), (x + s * 1.02, y - s * 0.05), (x, y + s * 1.1)], col)


def star(img, x, y, r, col):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((x + math.cos(a) * rad, y + math.sin(a) * rad))
    poly(img, pts, col, 2)


def forbidden(img, x, y, r, p=1.0, col=(235, 50, 70)):
    th = max(6, I(r * 0.16))
    cv2.ellipse(img, (I(x), I(y)), (I(r), I(r)), 0, -90, -90 + 360 * clamp(p * 1.4), C(img, col), th, cv2.LINE_AA)
    q = clamp((p - 0.5) * 2)
    if q > 0:
        a = (x - r * 0.7, y + r * 0.7)
        b = (x + r * 0.7, y - r * 0.7)
        line(img, a, (a[0] + (b[0] - a[0]) * q, a[1] + (b[1] - a[1]) * q), col, th)


def xmark(img, x, y, r, col=(235, 50, 70), p=1.0):
    th = max(6, I(r * 0.28))
    q1 = clamp(p * 2)
    q2 = clamp(p * 2 - 1)
    a, b = (x - r, y - r), (x + r, y + r)
    line(img, a, (a[0] + (b[0] - a[0]) * q1, a[1] + (b[1] - a[1]) * q1), col, th)
    if q2 > 0:
        a, b = (x + r, y - r), (x - r, y + r)
        line(img, a, (a[0] + (b[0] - a[0]) * q2, a[1] + (b[1] - a[1]) * q2), col, th)


def clock(img, x, y, r, hour_ang, min_ang, face=(252, 248, 238)):
    circ(img, x, y, r, face, 4)
    for k in range(12):
        a = k * math.pi / 6
        line(img, (x + math.sin(a) * r * 0.82, y - math.cos(a) * r * 0.82),
             (x + math.sin(a) * r * 0.94, y - math.cos(a) * r * 0.94), OUT, 3)
    a = math.radians(min_ang)
    line(img, (x, y), (x + math.sin(a) * r * 0.78, y - math.cos(a) * r * 0.78), OUT, 4)
    a = math.radians(hour_ang)
    line(img, (x, y), (x + math.sin(a) * r * 0.52, y - math.cos(a) * r * 0.52), OUT, 6)
    circ(img, x, y, 5, OUT)


def note(img, x, y, s, col=(250, 250, 250)):
    ell(img, x, y, 13 * s, 9 * s, col, 2, ang=-20)
    line(img, (x + 11 * s, y - 3 * s), (x + 11 * s, y - 46 * s), col, 5 * s, 2)
    poly(img, [(x + 11 * s, y - 46 * s), (x + 34 * s, y - 34 * s), (x + 11 * s, y - 28 * s)], col, 2)


# ---------- backgrounds ----------
_g = {}


def grad(top, bot):
    k = (top, bot)
    if k not in _g:
        t = np.linspace(0, 1, H)[:, None, None]
        a = np.array(top, np.float32)[None, None, :]
        b = np.array(bot, np.float32)[None, None, :]
        arr = (a * (1 - t) + b * t).astype(np.uint8)
        _g[k] = np.repeat(arr, W, axis=1)
    return _g[k].copy()


_bok = None


def bokeh(t=0.0, base=((22, 20, 52), (48, 26, 72))):
    global _bok
    if _bok is None:
        rnd = random.Random(7)
        lay = np.zeros((H, W, 3), np.float32)
        for _ in range(26):
            x, y, r = rnd.randint(0, W), rnd.randint(0, H), rnd.randint(26, 100)
            col = rnd.choice([(120, 90, 190), (90, 100, 200), (170, 100, 180)])
            for dy in (-H, 0, H):
                tmp = np.zeros((H, W, 3), np.uint8)
                cv2.circle(tmp, (x, y + dy), r, col, -1, cv2.LINE_AA)
                lay += tmp.astype(np.float32) * 0.16
        lay = cv2.GaussianBlur(lay, (0, 0), 5)
        _bok = lay
    off = I(t * 10) % H
    lay = np.roll(_bok, off, axis=0)
    img = grad(*base).astype(np.float32) + lay
    return np.clip(img, 0, 255).astype(np.uint8)


def sky(top=(130, 200, 245), bot=(220, 240, 250)):
    return grad(top, bot)


def sunset():
    return grad((120, 60, 120), (250, 170, 120))


def night():
    return grad((14, 16, 46), (40, 36, 90))


def hills(img, y, col=(110, 190, 90)):
    ell(img, W * 0.3, y + 200, 620, 230, col)
    ell(img, W * 0.85, y + 220, 520, 200, tuple(int(c * 0.93) for c in col))
    rect(img, 0, y + 140, W, H, col)


def house(img, cx, base, w, h, wall=(246, 232, 196), roof=(200, 70, 60), door_open=0.0, lit=False):
    x0, x1 = cx - w / 2, cx + w / 2
    rr(img, x0, base - h, x1, base, 4, wall, 4)
    poly(img, [(x0 - 26, base - h + 4), (x1 + 26, base - h + 4), (cx, base - h - w * 0.42)], roof, 4)
    dw, dh = w * 0.2, h * 0.62
    wc = (255, 226, 120) if lit else (170, 220, 250)
    for wx in (cx - w * 0.3, cx + w * 0.3):
        rr(img, wx - 38, base - h * 0.78, wx + 38, base - h * 0.78 + 74, 4, wc, 3)
        line(img, (wx, base - h * 0.78), (wx, base - h * 0.78 + 74), OUT, 3)
        line(img, (wx - 38, base - h * 0.78 + 37), (wx + 38, base - h * 0.78 + 37), OUT, 3)
    rr(img, cx - dw / 2, base - dh, cx + dw / 2, base, 4, (255, 230, 130) if door_open > 0 else (150, 90, 60), 3)
    if door_open > 0:
        wdt = dw * (1 - 0.7 * door_open)
        rr(img, cx - dw / 2, base - dh, cx - dw / 2 + wdt, base, 2, (150, 90, 60), 3)


def fence(img, x0, x1, y, col=(188, 134, 84)):
    line(img, (x0, y - 46), (x1, y - 46), col, 12, 3)
    line(img, (x0, y - 14), (x1, y - 14), col, 12, 3)
    x = x0
    while x <= x1:
        rr(img, x - 9, y - 72, x + 9, y + 6, 4, col, 3)
        x += 52


def room(img, wall=(240, 222, 178), floor=(176, 122, 88), fy=900, win=True, picture=True, night_=False):
    rect(img, 0, 0, W, fy, wall)
    rect(img, 0, fy, W, H, floor)
    rect(img, 0, fy - 10, W, fy + 6, tuple(int(c * 0.8) for c in floor))
    if win:
        sk = (40, 44, 100) if night_ else (170, 222, 250)
        rr(img, 470, 230, 650, 470, 6, sk, 4)
        line(img, (560, 230), (560, 470), OUT, 4)
        line(img, (470, 350), (650, 350), OUT, 4)
        if night_:
            circ(img, 520, 290, 22, (250, 240, 190))
        else:
            ell(img, 560, 460, 90, 28, (130, 200, 110))
    if picture:
        rr(img, 70, 260, 200, 360, 6, (240, 240, 235), 4)
        poly(img, [(80, 350), (130, 290), (190, 350)], (120, 190, 120))
        circ(img, 165, 290, 12, (250, 210, 90))


def phone(img, x, y, s=1.0, screen=(250, 250, 255), ang=0):
    rr(img, x - 36 * s, y - 70 * s, x + 36 * s, y + 70 * s, 12 * s, (60, 64, 90), 3)
    _rr(img, x - 29 * s, y - 60 * s, x + 29 * s, y + 60 * s, 6 * s, screen)


def calendar_page(img, x, y, w, h, head=(220, 60, 70)):
    rr(img, x - w / 2, y - h / 2, x + w / 2, y + h / 2, 14, (252, 250, 244), 4)
    rr(img, x - w / 2, y - h / 2, x + w / 2, y - h / 2 + h * 0.24, 14, head, 4)
    rect(img, x - w / 2 + 2, y - h / 2 + h * 0.14, x + w / 2 - 2, y - h / 2 + h * 0.24, head)


# ---------- character ----------
SKIN = (196, 138, 100)
HAIR_K = (30, 24, 30)
HAIR_BR = (92, 56, 40)
HAIR_GR = (204, 204, 212)


def person(img, x, y, s=1.0, skin=SKIN, hair=HAIR_K, style='short', shirt=(64, 124, 196),
           pants=(60, 64, 90), mouth='smile', eyes='open', aL=8, aR=8, hs=1.0,
           glasses=False, walk=0.0, bob=0.0, look=0.0, brow=0, shoe=(70, 60, 80), tilt=0.0):
    ow = max(2, I(3.5 * s))
    leg_h, torso_h, tw = 92 * s, 100 * s, 82 * s
    hr = 46 * s * hs
    hip_y = y - leg_h + bob
    sh_y = hip_y - torso_h
    hx = x + tilt * 14 * s
    hy = sh_y - hr * 0.82
    # cabelo comprido fica ATRÁS do corpo (só aparece nas laterais, sem parecer barba)
    if style == 'long':
        rr(img, hx - hr - 6 * s, hy - hr * 0.2, hx + hr + 6 * s, sh_y + 40 * s, hr * 0.55, hair, ow)
    # legs
    for sg in (-1, 1):
        ph = walk + (0 if sg < 0 else math.pi)
        sw = math.sin(ph) * 24 * s if walk else 0
        lift = max(0, math.sin(ph)) * 12 * s if walk else 0
        lx, fy = x + sg * 17 * s + sw, y - lift
        line(img, (x + sg * 17 * s, hip_y), (lx, fy - 6 * s), pants, 30 * s, ow)
        ell(img, lx + 4 * s, fy - 2 * s, 19 * s, 10 * s, shoe, ow)
    rr(img, x - tw / 2, sh_y, x + tw / 2, hip_y + 10 * s, 24 * s, shirt, ow)
    # arms
    for sg, ang in ((-1, aL), (1, aR)):
        sx, sy = x + sg * (tw / 2 - 8 * s), sh_y + 18 * s
        a = math.radians(ang)
        L = 86 * s
        ex, ey = sx + sg * math.sin(a) * L, sy + math.cos(a) * L
        line(img, (sx, sy), (ex, ey), shirt, 25 * s, ow)
        mx, my = sx + (ex - sx) * 0.55, sy + (ey - sy) * 0.55
        line(img, (mx, my), (ex, ey), skin, 20 * s, 0)
        circ(img, ex, ey, 13 * s, skin, ow)
    # hair back
    if style == 'bun':
        circ(img, hx, hy - hr * 1.12, hr * 0.42, hair, ow)
    circ(img, hx, hy, hr, skin, ow)
    # hair front
    if style in ('short', 'long', 'bun'):
        ell(img, hx, hy - hr * 0.36, hr + ow * 0.6, hr * 0.84, hair, ow, 180, 360)
    # face
    ey_ = hy + hr * 0.08
    for sg in (-1, 1):
        ex_ = hx + sg * hr * 0.37
        if eyes == 'open':
            circ(img, ex_, ey_, hr * 0.24, (255, 255, 255), 2)
            circ(img, ex_ + look * hr * 0.07, ey_ + hr * 0.02, hr * 0.12, OUT)
            circ(img, ex_ + look * hr * 0.07 + hr * 0.04, ey_ - hr * 0.03, hr * 0.04, (255, 255, 255))
        elif eyes == 'closed':
            cv2.ellipse(img, (I(ex_), I(ey_)), (I(hr * 0.2), I(hr * 0.12)), 0, 20, 160, C(img, OUT), max(2, I(3 * s)), cv2.LINE_AA)
        elif eyes == 'happy':
            cv2.ellipse(img, (I(ex_), I(ey_ + hr * 0.08)), (I(hr * 0.2), I(hr * 0.16)), 0, 200, 340, C(img, OUT), max(2, I(3.5 * s)), cv2.LINE_AA)
        by = ey_ - hr * 0.42
        if brow != 0:
            line(img, (ex_ - hr * 0.2, by + sg * brow * hr * 0.1), (ex_ + hr * 0.2, by - sg * brow * hr * 0.1), OUT, max(2, 3 * s))
        else:
            line(img, (ex_ - hr * 0.2, by), (ex_ + hr * 0.2, by), OUT, max(2, 3 * s))
        if glasses:
            cv2.circle(img, (I(ex_), I(ey_)), I(hr * 0.33), C(img, OUT), max(2, I(3 * s)), cv2.LINE_AA)
    if glasses:
        line(img, (hx - hr * 0.06, ey_), (hx + hr * 0.06, ey_), OUT, max(2, 3 * s))
    my = hy + hr * 0.52
    th = max(2, I(3.5 * s))
    if mouth == 'smile':
        cv2.ellipse(img, (I(hx), I(my - hr * 0.1)), (I(hr * 0.28), I(hr * 0.24)), 0, 15, 165, C(img, OUT), th, cv2.LINE_AA)
    elif mouth == 'open':
        ell(img, hx, my, hr * 0.24, hr * 0.2, (150, 40, 60), 2)
        ell(img, hx, my + hr * 0.1, hr * 0.14, hr * 0.07, (240, 110, 120))
    elif mouth == 'o':
        circ(img, hx, my + hr * 0.04, hr * 0.12, (150, 40, 60), 2)
    elif mouth == 'sad':
        cv2.ellipse(img, (I(hx), I(my + hr * 0.18)), (I(hr * 0.22), I(hr * 0.16)), 0, 200, 340, C(img, OUT), th, cv2.LINE_AA)
    else:
        line(img, (hx - hr * 0.15, my + hr * 0.04), (hx + hr * 0.15, my + hr * 0.04), OUT, th)
    for sg in (-1, 1):
        ell(img, hx + sg * hr * 0.62, my - hr * 0.1, hr * 0.14, hr * 0.09, (226, 130, 110))


def davi(img, x, y, s=1.55, **k):
    d = dict(skin=SKIN, hair=HAIR_K, style='short', shirt=(64, 124, 196), pants=(58, 62, 88))
    d.update(k)
    person(img, x, y, s, **d)


def rita(img, x, y, s=1.4, **k):
    d = dict(skin=SKIN, hair=HAIR_GR, style='bun', shirt=(150, 84, 160), pants=(96, 70, 110), glasses=True)
    d.update(k)
    person(img, x, y, s, **d)


def mom(img, x, y, s=1.55, **k):
    d = dict(skin=SKIN, hair=HAIR_BR, style='long', shirt=(70, 164, 112), pants=(60, 62, 92))
    d.update(k)
    person(img, x, y, s, **d)


def kid(img, x, y, s=0.9, **k):
    d = dict(skin=SKIN, hair=HAIR_K, style='short', shirt=(232, 100, 76), pants=(70, 100, 170), hs=1.45)
    d.update(k)
    person(img, x, y, s, **d)


# ---------- sprites (RGBA canvas, rotated + composited) ----------
def blit(img, spr, cx, cy, ang=0.0, sc=1.0, alpha=1.0, gray=0.0):
    h, w = spr.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), ang, sc)
    M[0, 2] += cx - w / 2
    M[1, 2] += cy - h / 2
    warped = cv2.warpAffine(spr, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    a = warped[:, :, 3:4].astype(np.float32) / 255.0 * alpha
    rgb = warped[:, :, :3].astype(np.float32)
    if gray > 0:
        g = rgb.mean(axis=2, keepdims=True)
        rgb = rgb * (1 - gray) + g * gray * 0.9
    m = a[:, :, 0] > 0
    if not m.any():
        return
    ys, xs = np.where(m)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    reg = img[y0:y1, x0:x1].astype(np.float32)
    aa = a[y0:y1, x0:x1]
    img[y0:y1, x0:x1] = (reg * (1 - aa) + rgb[y0:y1, x0:x1] * aa).astype(np.uint8)


def new_sprite(w, h):
    return np.zeros((h, w, 4), np.uint8)


def polaroid(kind, w=400, h=480):
    s = new_sprite(w + 40, h + 40)
    ox, oy = 20, 20
    rr(s, ox, oy, ox + w, oy + h, 8, (252, 250, 244), 4)
    px0, py0, px1, py1 = ox + 24, oy + 24, ox + w - 24, oy + h - 100
    ph = py1 - py0
    pw = px1 - px0
    ph_img = new_sprite(pw, ph)
    if kind == 'mom_baby':
        rect(ph_img, 0, 0, pw, ph, (240, 222, 178))
        rect(ph_img, 0, int(ph * 0.78), pw, ph, (176, 122, 88))
        mom(ph_img, pw // 2, ph + 40, 0.95, mouth='smile', aL=-35, aR=-35)
        kid(ph_img, pw // 2, int(ph * 0.99), 0.42, hs=1.5, mouth='smile', aL=60, aR=60)
    elif kind == 'hug':
        rect(ph_img, 0, 0, pw, ph, (250, 190, 140))
        rect(ph_img, 0, int(ph * 0.8), pw, ph, (110, 180, 100))
        davi(ph_img, int(pw * 0.38), ph + 20, 0.9, mouth='smile', eyes='happy', aL=-50, aR=-70)
        rita(ph_img, int(pw * 0.64), ph + 20, 0.78, mouth='smile', eyes='happy', aL=-70, aR=-50)
    elif kind == 'lanche':
        rect(ph_img, 0, 0, pw, ph, (250, 236, 170))
        rect(ph_img, 0, int(ph * 0.75), pw, ph, (190, 140, 96))
        circ(ph_img, pw // 2, ph // 2, 50, (240, 190, 90), 3)
        circ(ph_img, pw // 2, ph // 2, 22, (250, 230, 150), 2)
    elif kind == 'escola':
        rect(ph_img, 0, 0, pw, ph, (170, 222, 250))
        rect(ph_img, 0, int(ph * 0.7), pw, ph, (120, 190, 100))
        kid(ph_img, int(pw * 0.62), ph - 10, 0.8, mouth='smile')
    else:
        rect(ph_img, 0, 0, pw, ph, (240, 222, 178))
        star(ph_img, pw // 2, ph // 2, 60, (250, 205, 60))
    s[py0:py1, px0:px1] = ph_img
    cv2.rectangle(s, (px0, py0), (px1, py1), (*OUT, 255), 3, cv2.LINE_AA)
    return s


# ---------- text ----------
class Ctx:
    def __init__(self):
        self.texts = []
        self.over = []

    def text(self, s, x, y, size, col=(255, 255, 255), stroke=6, anchor='mm', rot=0, alpha=1.0, sc=1.0, outc=(10, 8, 14), over=False):
        (self.over if over else self.texts).append((s, x, y, size, col, stroke, anchor, rot, alpha, sc, outc))


def draw_texts(img, items):
    if not items:
        return img
    pil = Image.fromarray(img)
    d = ImageDraw.Draw(pil)
    for (s, x, y, size, col, stroke, anchor, rot, alpha, sc, outc) in items:
        if alpha <= 0.01 or sc <= 0.01:
            continue
        f = font(size * sc)
        st = max(0, I(stroke * sc))
        if rot == 0 and alpha >= 0.99:
            d.text((x, y), s, font=f, fill=col, anchor=anchor, stroke_width=st, stroke_fill=outc)
        else:
            bb = d.textbbox((0, 0), s, font=f, stroke_width=st, anchor='lt')
            tw, th = bb[2] - bb[0] + 40, bb[3] - bb[1] + 40
            lay = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
            ld = ImageDraw.Draw(lay)
            ld.text((tw / 2, th / 2), s, font=f, fill=col + (255,), anchor='mm', stroke_width=st, stroke_fill=outc + (255,))
            lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
            if alpha < 0.99:
                a = lay.getchannel('A').point(lambda v: int(v * alpha))
                lay.putalpha(a)
            lw, lh = lay.size
            pil.paste(lay.convert('RGB'), (I(x - lw / 2), I(y - lh / 2)), lay.getchannel('A'))
    return np.array(pil)

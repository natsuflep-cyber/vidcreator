import sys, os, subprocess, math
from lib import *

BASE = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(BASE, '..', 'assets', 'narracao.mp3')

FPS = 30
DUR = 92.0
YEL = (255, 226, 70)
RED = (255, 84, 96)
GRN = (96, 240, 140)
WHT = (255, 255, 255)
DK = (30, 24, 30)

PHR = [
    (" avisa quando é a última vez.", 0.0, 2.33),
    ("A última vez que sua mãe te pegou no colo.", 3.02, 5.26),
    ("Você não sabia.", 5.8, 6.56),
    ("Ela também não.", 7.03, 7.75),
    ("A última vez que ela cortou o seu lanche.", 8.39, 10.54),
    ("A última vez que ela te esperou na porta da escola.", 11.03, 13.68),
    ("A última vez que você correu pra contar uma novidade pra ela antes de contar pra qualquer pessoa.", 14.14, 19.54),
    ("Nenhuma veio com aviso.", 19.99, 21.46),
    ("Nenhuma teve carimbo.", 21.85, 23.09),
    ("Só passaram.", 23.62, 24.25),
    ("O Davi tem trinta e quatro anos e uma mãe,", 25.02, 27.66),
    ("a dona Rita,", 27.92, 28.61),
    ("que mora a três horas dele.", 28.92, 30.28),
    ("Ele ama a mãe.", 30.74, 31.66),
    ("Mas a semana é corrida,", 32.12, 33.41),
    ("e a resposta é sempre a mesma:", 33.68, 35.49),
    ("Mãe,", 35.93, 36.18),
    ("domingo que vem eu passo aí.", 36.47, 37.66),
    ("O domingo que vem vira o outro,", 38.34, 39.96),
    ("que vira o outro.", 40.31, 41.05),
    ("Numa noite sem sono,", 41.52, 42.73),
    ("ele fez a conta.", 42.97, 43.83),
    ("A mãe tinha sessenta e oito anos.", 44.22, 46.43),
    ("Se ela chegasse aos oitenta e cinco,", 46.84, 48.64),
    ("e ele continuasse visitando duas vezes por ano,", 48.89, 51.48),
    ("restariam", 51.79, 52.33),
    ("trinta e quatro visitas.", 52.5, 53.87),
    ("De umas três horas cada.", 54.27, 55.59),
    ("Ele somou tudo.", 56.05, 56.99),
    ("Deu pouco mais de quatro dias.", 57.49, 59.63),
    ("Quatro dias.", 60.17, 61.22),
    ("Pelo resto da vida inteira.", 61.64, 63.46),
    ("O Davi pegou a chave e foi.", 64.14, 66.07),
    ("Três horas de estrada, sem música.", 66.63, 68.91),
    ("A dona Rita abriu a porta:", 69.43, 70.94),
    ("Aconteceu alguma coisa?", 71.41, 72.8),
    ("Nada, mãe.", 73.08, 73.73),
    ("Só vim.", 74.02, 74.43),
    ("Ela demorou pra soltar o abraço.", 75.0, 76.83),
    ("Não era a trigésima quarta visita.", 77.29, 79.37),
    ("Era a primeira que ele realmente contou.", 79.84, 82.19),
    ("Você também tem alguém assim.", 82.75, 84.25),
    ("E ninguém vai te avisar quando for a última vez.", 84.68, 87.57),
    ("Então", 88.03, 88.42),
    ("não deixa pro domingo que vem.", 88.7, 90.19),
    ("Vai hoje.", 90.61, 91.16),
]
YW = set("última vez trinta quatro anos três horas oitenta cinco sessenta oito dias duas trigésima visitas davi dona rita hoje domingo mãe".split())
RW = set("nenhuma aviso carimbo passaram sono não sem nada ninguém".split())
GW = set("primeira abraço ama contou vai vim só".split())

WORDS = []  # (start, end, text, color)
for txt, a, b in PHR:
    ws = txt.split()
    wt = [len(w) + 1.5 for w in ws]
    tot = sum(wt)
    cum = 0
    for i, w in enumerate(ws):
        s0 = a + (b - a) * cum / tot
        cum += wt[i]
        s1 = a + (b - a) * cum / tot
        clean = "".join(ch for ch in w if ch.isalnum() or ch == '-' or ch == '?').strip()
        key = clean.lower().strip('?')
        col = YEL if key in YW else RED if key in RW else GRN if key in GW else WHT
        WORDS.append([s0, s1, clean.upper(), col])
for i in range(len(WORDS) - 1):
    # hold word until the next starts if the gap is tiny
    if WORDS[i + 1][0] - WORDS[i][1] < 0.25:
        WORDS[i][1] = WORDS[i + 1][0]
    else:
        WORDS[i][1] += 0.12
WORDS[-1][1] += 0.6


def caption(ctx, t):
    for s0, s1, tx, col in WORDS:
        if s0 <= t < s1:
            age = t - s0
            pop = 1 + 0.2 * max(0, 1 - age / 0.13)
            sz = 84
            while font(sz).getlength(tx) > 640 and sz > 40:
                sz -= 4
            ctx.text(tx, W / 2, 1090, sz, col, 8, sc=pop, over=True)
            return


def stamp(ctx, tl, t0, s, x=360, y=170, size=92, col=RED, rot=-4):
    p = tl - t0
    if p < 0:
        return
    sc = 1 + 1.4 * max(0, 1 - p / 0.2)
    ctx.text(s, x, y, size, col, 7, rot=rot, sc=sc, alpha=clamp(p / 0.08), over=True)


def title(ctx, tl, t0, s, x=360, y=160, size=76, col=YEL):
    p = tl - t0
    if p < 0:
        return
    ctx.text(s, x, y, size, col, 7, sc=eb(p / 0.25), over=True)


def blink(tl):
    return 'closed' if (tl % 3.1) > 2.95 else 'open'


def hand_pos(x, y, s, sg, ang):
    tw = 82 * s
    sh_y = y - 92 * s - 100 * s
    sx, sy = x + sg * (tw / 2 - 8 * s), sh_y + 18 * s
    a = math.radians(ang)
    return sx + sg * math.sin(a) * 86 * s, sy + math.cos(a) * 86 * s


def bubble(img, ctx, x, y, lines, p, size=34, w=None, tail=0):
    if p <= 0:
        return
    n = len(lines)
    bw = w or (max(font(size).getlength(l) for l in lines) + 56)
    bh = n * (size + 8) + 36
    bw, bh = bw * clamp(p), bh * clamp(p)
    rr(img, x - bw / 2, y - bh / 2, x + bw / 2, y + bh / 2, 22, (255, 255, 255), 4)
    poly(img, [(x - 14 + tail, y + bh / 2 - 3), (x + 14 + tail, y + bh / 2 - 3), (x + tail * 1.6, y + bh / 2 + 34)], (255, 255, 255), 3)
    rect(img, x - 12 + tail, y + bh / 2 - 6, x + 12 + tail, y + bh / 2 - 1, (255, 255, 255))
    if p > 0.95:
        for i, l in enumerate(lines):
            ctx.text(l, x, y - bh / 2 + 18 + size / 2 + 4 + i * (size + 8), size, DK, 0)


def floating_hearts(img, tl, t0, x, y, n=5, spread=140, rise=220, s=16):
    for i in range(n):
        p = ((tl - t0) * 0.55 + i / n) % 1.0
        if tl < t0:
            return
        hx = x + math.sin(i * 2.1 + p * 5) * spread * 0.5 + (i - n / 2) * spread / n
        hy = y - p * rise
        heart(img, hx, hy, s * (0.7 + 0.5 * math.sin(i)), (255, 90, 140))


_pol = {}


def pol(kind, w=400, h=480):
    k = (kind, w, h)
    if k not in _pol:
        _pol[k] = polaroid(kind, w, h)
    return _pol[k]


# ------------------------------------------------ scenes
def R(top, bot, **kw):
    im = grad(top, bot)
    room(im, **kw)
    return im


def sc1(ctx, tl, T):
    img = bokeh(tl)
    sc = 0.55 + 0.45 * eb(tl / 0.6) + 0.012 * math.sin(tl * 3)
    blit(img, pol('mom_baby'), 360, 540, -12 + 8 * eo(tl / 0.6), sc * 1.15)
    if tl < 0.25:
        ctx.flash = 1 - tl / 0.25
    return img


def sc2(ctx, tl, T):
    img = R((240, 222, 178), (240, 222, 178))
    mom(img, 360, 1000, 1.55, mouth='smile', eyes=blink(tl), aL=-38, aR=-38, bob=math.sin(tl * 2.2) * 2, tilt=0.2)
    kid(img, 360, 948, 0.75, mouth='smile', eyes='open' if tl < 3.4 else 'closed', aL=70, aR=70, look=1)
    for sg in (-1, 1):
        circ(img, 360 + sg * 58, 880, 14, SKIN, 3)
    stamp(ctx, tl, 0.1, "ÚLTIMA VEZ")
    if 2.78 < tl < 3.7:
        ctx.text("?", 450, 700, 80, YEL, 6, sc=eb((tl - 2.78) / 0.2))
    if 4.0 < tl < 5.0:
        ctx.text("?", 470, 560, 80, YEL, 6, sc=eb((tl - 4.0) / 0.2))
    ctx.gray = clamp((tl - 4.3) / 1.0)
    return img


def sc3(ctx, tl, T):
    img = R((250, 236, 176), (250, 236, 176), wall=(252, 238, 180), floor=(190, 140, 96), fy=860, win=True, picture=False)
    ang = 105 + 22 * math.sin(tl * 9)
    mom(img, 190, 1010, 1.4, mouth='smile', eyes='open', aL=20, aR=ang)
    kx, ky = hand_pos(190, 1010, 1.4, 1, ang)
    line(img, (kx, ky), (kx + 40, ky + 26), (225, 228, 235), 9, 3)
    kid(img, 530, 1010, 0.95, mouth='open', eyes='happy', aL=40 + 10 * math.sin(tl * 6), aR=40)
    # table
    rr(img, 40, 800, 680, 850, 12, (176, 120, 78), 4)
    rect(img, 80, 850, 110, 1040, (150, 100, 64))
    rect(img, 610, 850, 640, 1040, (150, 100, 64))
    ell(img, 360, 790, 120, 26, (255, 255, 255), 3)
    g = 26 * eo((tl - 0.9) / 0.5)
    poly(img, [(300 - g, 790), (420 - g, 790), (300 - g, 740)], (240, 200, 120), 3)
    poly(img, [(300 + g, 790 + g * 0.0), (420 + g, 790), (420 + g, 740)], (240, 200, 120), 3)
    stamp(ctx, tl, 0.1, "ÚLTIMA VEZ", rot=3)
    return img


def sc4(ctx, tl, T):
    img = sky()
    hills(img, 880)
    rr(img, 60, 520, 660, 880, 6, (250, 214, 120), 4)
    rect(img, 40, 500, 680, 540, (200, 90, 70))
    rr(img, 280, 700, 440, 880, 6, (150, 96, 66), 4)
    rr(img, 220, 560, 500, 640, 8, (255, 255, 255), 3)
    ctx.text("ESCOLA", 360, 600, 52, (60, 80, 160), 0)
    fence(img, 30, 700, 960)
    xk = 120 + 300 * eo(tl / 2.4)
    walk = tl * 11 if tl < 2.4 else 0
    rr(img, xk - 34, 1000 - 144 - 20, xk + 34, 1000 - 70, 10, (90, 120, 220), 3)
    kid(img, xk, 1000, 0.9, mouth='smile', eyes='open', walk=walk, aL=20, aR=20)
    mom(img, 580, 1000, 1.45, mouth='smile', eyes='open', aL=10, aR=135 + 25 * math.sin(tl * 7))
    stamp(ctx, tl, 0.1, "ÚLTIMA VEZ", rot=-3)
    return img


def sc5(ctx, tl, T):
    img = sky()
    hills(img, 860)
    house(img, 540, 880, 320, 240)
    fence(img, 20, 360, 940)
    xk = 70 + 380 * eo(tl / 4.2)
    run = tl < 4.2
    jump = abs(math.sin((tl - 4.2) * 7)) * 30 if tl > 4.2 and tl < 5.5 else 0
    kid(img, xk, 1010 - jump, 0.9, mouth='open', eyes='happy', walk=tl * 16 if run else 0, aL=150, aR=150, bob=-abs(math.sin(tl * 16)) * 6 if run else 0)
    px, py = xk, 668 - jump
    rr(img, px - 36, py - 40, px + 36, py + 40, 6, (255, 255, 255), 3)
    star(img, px, py - 4, 24, (250, 205, 60))
    mom(img, 610, 1010, 1.45, mouth='smile' if tl < 3.8 else 'open', eyes='open' if tl < 4.2 else 'happy',
        aL=20 if tl < 3.8 else 55, aR=20 if tl < 3.8 else 55)
    bubble(img, ctx, min(xk + 70, 380), 560, ["Mãe!!"], eb((tl - 0.9) / 0.25) if 0.9 < tl < 3.2 else 0, size=44, tail=-30)
    if tl > 4.3:
        floating_hearts(img, tl, 4.3, 560, 760, n=5, spread=220, rise=260, s=16)
    stamp(ctx, tl, 0.1, "ÚLTIMA VEZ", rot=4)
    return img


def sc6(ctx, tl, T):
    img = bokeh(tl)
    fade = clamp((tl - 3.63) / 1.2)
    rise = fade * 150
    blit(img, pol('lanche', 340, 400), 190, 800 - rise, -9 + math.sin(tl * 1.6) * 2, 0.86, alpha=1 - fade, gray=fade)
    blit(img, pol('escola', 340, 400), 530, 840 - rise, 8 + math.sin(tl * 1.3) * 2, 0.86, alpha=1 - fade, gray=fade)
    blit(img, pol('mom_baby', 380, 460), 360, 700 - rise, -2, 0.92, alpha=1 - fade, gray=fade)
    a = 1 - fade
    ctx.text("AVISO", 360, 190, 110, WHT, 8, sc=eb((tl + 0.0) / 0.25), alpha=a)
    forbidden(img, 360, 190, 100, clamp((tl - 0.15) / 0.7))
    if tl > 1.86:
        ctx.text("CARIMBO", 360, 360, 100, YEL, 8, sc=eb((tl - 1.86) / 0.25), alpha=a)
        xmark(img, 360, 360, 90, p=clamp((tl - 2.1) / 0.5))
    return img


def sc7(ctx, tl, T):
    img = grad((74, 86, 128), (50, 58, 96))
    rect(img, 0, 900, W, H, (96, 70, 70))
    # window w skyline
    rr(img, 400, 180, 660, 560, 6, (250, 170, 120), 4)
    for i, (bx, bh) in enumerate([(420, 150), (470, 210), (520, 120), (575, 180)]):
        rect(img, bx, 560 - bh, bx + 44, 560, (110, 70, 110))
    circ(img, 590, 300, 30, (255, 230, 150))
    rr(img, 60, 800, 660, 856, 10, (176, 120, 78), 4)
    rect(img, 90, 856, 120, 1000, (150, 100, 64))
    rect(img, 600, 856, 630, 1000, (150, 100, 64))
    davi(img, 300, 1010, 1.5, mouth='smile', eyes=blink(tl), aL=30, aR=30, bob=math.sin(tl * 2) * 2)
    rr(img, 90, 700, 240, 800, 8, (60, 64, 90), 3)
    rr(img, 100, 710, 230, 790, 4, (170, 215, 250), 0)
    rr(img, 60, 800, 660, 856, 10, (176, 120, 78), 4)
    title(ctx, tl, 0.1, "DAVI, 34 ANOS")
    if tl > 2.9:
        p = eb((tl - 2.9) / 0.3)
        cx, cy = 560, 700
        rr(img, cx - 130 * p, cy - 130 * p, cx + 130 * p, cy + 130 * p, 20, (250, 220, 235), 4)
        if p > 0.9:
            rita(img, cx, 790, 0.75, mouth='smile', eyes=blink(tl + 1))
            ctx.text("DONA RITA", cx, cy - 190, 38, WHT, 5)
    if tl > 3.9:
        n = clamp((tl - 3.9) / 0.6)
        line(img, (360, 560), (360 + 0 * n, 560), WHT, 1)
        ctx.text("A 3 HORAS", 235, 450, 46, YEL, 6, sc=eb((tl - 3.9) / 0.25), rot=-3)
        clock(img, 90, 450, 34, tl * 40, tl * 480)
    if tl > 5.72:
        floating_hearts(img, tl, 5.72, 300, 640, n=5, spread=160, rise=220, s=17)
    return img


def sc8(ctx, tl, T):
    A = R((236, 214, 176), (236, 214, 176), wall=(232, 206, 220), floor=(176, 130, 110), fy=480, picture=True, win=True)
    img = grad((74, 86, 128), (60, 70, 110))
    rect(img, 0, 900, W, H, (96, 70, 70))
    # office clock + papers
    clock(img, 560, 640, 60, tl * 120, tl * 1400)
    for i in range(4):
        px = 90 + i * 140 + math.sin(tl * 2 + i) * 20
        py = 640 + ((tl * 90 + i * 70) % 260) - 130
        rr(img, px - 26, py - 34, px + 26, py + 34, 3, (255, 255, 255), 2)
    img[:540] = A[:540]
    rect(img, 0, 536, W, 546, OUT)
    ph_on = tl > 3.8
    rita(img, 360, 520, 0.95, mouth='smile' if tl < 4.7 else 'open', eyes='open',
         aL=150 if ph_on else 15, aR=15, look=-1 if not ph_on else 0, bob=math.sin(tl * 2.4) * 1.5)
    clock(img, 130, 200, 44, 300, 60)
    davi(img, 360, 1050, 1.2, mouth='o' if not ph_on else 'smile', eyes='open', brow=1 if not ph_on else 0, aL=20 if not ph_on else 150, aR=60 + 30 * math.sin(tl * 7) if not ph_on else 20)
    rr(img, 70, 900, 650, 950, 10, (176, 120, 78), 4)
    rect(img, 90, 950, 120, 1060, (150, 100, 64))
    rect(img, 600, 950, 630, 1060, (150, 100, 64))
    if ph_on:
        p = eb((tl - 4.3) / 0.25)
        bubble(img, ctx, 360, 612, ["Mãe, domingo que", "vem eu passo aí."], p, size=38, tail=0)
    return img


def sc9(ctx, tl, T):
    img = bokeh(tl, base=((30, 34, 70), (60, 50, 110)))
    cyc = 0.8
    k = int(tl // cyc)
    p = (tl % cyc) / cyc
    nums = ["12", "19", "26", "3", "10"]
    num = nums[min(k, 4)]
    sx = 1.0
    if p < 0.15 and k > 0:
        sx = 1 - p / 0.15
        num = nums[min(k - 1, 4)]
    elif p < 0.3 and k > 0:
        sx = (p - 0.15) / 0.15
    sx = max(0.04, sx)
    w = 420 * sx
    calendar_page(img, 360, 560, w, 500)
    if sx > 0.7:
        ctx.text("DOMINGO", 360, 400, 50, WHT, 4)
        ctx.text(num, 360, 590, 190, DK, 0)
        if p > 0.5 and not (p < 0.3):
            xmark(img, 360, 600, 120, p=clamp((p - 0.5) / 0.3))
    rita(img, 160, 1040, 0.9, mouth='sad', eyes='open', brow=-1, look=1) if tl > 1.6 else None
    return img


def sc10(ctx, tl, T):
    img = R((42, 46, 98), (42, 46, 98), wall=(42, 46, 98), floor=(60, 52, 96), fy=980, night_=True, picture=False)
    davi(img, 330, 1090, 1.5, mouth='flat', eyes='open', brow=1, look=1 if tl % 2 < 1 else -1, aL=40, aR=40)
    rr(img, 60, 840, 700, 1060, 24, (120, 150, 222), 4)
    rect(img, 60, 836, 700, 868, (150, 180, 240))
    rr(img, 560, 760, 680, 840, 8, (160, 100, 60), 3)
    poly(img, [(600, 620), (640, 620), (700, 760), (540, 760)], (250, 240, 170))
    ell(img, 620, 610, 40, 20, (230, 90, 90), 3)
    # ZZZ crossed
    ctx.text("ZZZ", 530, 470 - (tl * 12) % 30, 70, (150, 160, 255), 5)
    forbidden(img, 530, 470, 70, clamp((tl - 0.3) / 0.6))
    if tl > 1.45:
        p = eb((tl - 1.45) / 0.3)
        ell(img, 480, 470 + 40, 130 * p, 70 * p, (255, 255, 255), 3)
        circ(img, 420, 590, 12 * p, (255, 255, 255), 3)
        circ(img, 392, 640, 8 * p, (255, 255, 255), 3)
        if p > 0.9:
            ctx.text("+ − × ÷", 480, 510, 52, DK, 0)
    return img


def sc11(ctx, tl, T):
    img = sunset()
    hills(img, 880, (90, 150, 100))
    house(img, 520, 880, 300, 230)
    fence(img, 20, 300, 950)
    rita(img, 300, 1000, 1.5, mouth='smile', eyes='happy', aL=12, aR=150, bob=math.sin(tl * 3) * 3)
    hx, hy = hand_pos(300, 1000, 1.5, 1, 150)
    bx, by = 430 + math.sin(tl * 2) * 8, 480
    line(img, (hx, hy), (bx, by + 85), (60, 40, 60), 4)
    circ(img, bx, by, 90, (80, 150, 240), 4)
    ctx.text("68", bx, by, 90, WHT, 6)
    title(ctx, tl, 0.1, "68 ANOS", y=170, size=92)
    return img


CALC = None


def calc_body(img, ctx):
    rr(img, 110, 150, 610, 600, 36, (60, 64, 96), 4)
    rr(img, 140, 180, 580, 330, 14, (190, 232, 170), 3)
    for r_ in range(3):
        for c_ in range(4):
            rr(img, 150 + c_ * 108, 370 + r_ * 74, 150 + c_ * 108 + 90, 370 + r_ * 74 + 58, 14, (200, 205, 225) if c_ < 3 else (250, 160, 90), 2)


def grid34(img, tl, t0, y0, label=None, sq=64, scale=1.0, ctx=None, cx=None, cy=None, mix=0.0):
    n = 0
    for r_ in range(5):
        for c_ in range(7):
            if n >= 34:
                return
            tt = (tl - t0) - n * 0.04
            if tt >= 0:
                gx = 100 + c_ * 76 + sq / 2
                gy = y0 + r_ * 76 + sq / 2
                if cx is not None:
                    gx += (cx - gx) * mix
                    gy += (cy - gy) * mix
                p = eb(tt / 0.2)
                s2 = sq * p / 2
                rr(img, gx - s2, gy - s2, gx + s2, gy + s2, 8, (252, 250, 244), 3)
                rect(img, gx - s2 + 1, gy - s2 + 1, gx + s2 - 1, gy - s2 + 14 * p, (220, 60, 70))
                if label and ctx and p > 0.9 and mix < 0.2:
                    ctx.text(label, gx, gy + 8, 26, DK, 0)
            n += 1


def sc12(ctx, tl, T):
    img = bokeh(tl)
    calc_body(img, ctx)
    if tl < 1.8:
        s = "85 − 68 = 17"
    elif tl < 4.9:
        s = "17 × 2"
    else:
        s = "= 34"
    ctx.text(s, 560, 255, 62, (30, 70, 40), 0, anchor='rm')
    if tl < 1.8:
        ctx.text("ANOS RESTANTES", 160, 205, 22, (30, 70, 40), 0, anchor='lm')
    elif tl < 4.9:
        ctx.text("VISITAS POR ANO: 2", 160, 205, 22, (30, 70, 40), 0, anchor='lm')
    grid34(img, tl, 5.55, 640)
    return img


def sc13(ctx, tl, T):
    img = bokeh(tl)
    if tl < 2.6:
        mix = eo((tl - 1.78) / 0.8) if tl > 1.78 else 0
        grid34(img, tl + 99, 0, 250, label="3h", ctx=ctx, cx=360, cy=620, mix=mix)
        # stagger the labels
    if tl > 2.2:
        v = I(102 * eo((tl - 2.2) / 0.7))
        ctx.text(f"{v} h", 360, 330, 150, YEL, 8, sc=1 if tl > 2.9 else 0.8 + 0.2 * eo((tl - 2.2) / 0.3))
    if tl > 3.3:
        ctx.text("≈ 4 DIAS", 360, 520, 110, RED, 8, sc=eb((tl - 3.3) / 0.3))
    for i in range(4):
        t0 = 3.6 + i * 0.3
        if tl > t0:
            p = eb((tl - t0) / 0.25)
            cx = 130 + i * 152
            calendar_page(img, cx, 790, 110 * p, 130 * p)
            if p > 0.9:
                ctx.text(str(i + 1), cx, 805, 60, DK, 0)
    return img


def sc14(ctx, tl, T):
    img = bokeh(tl)
    ctx.text("4 DIAS", 360, 330, 170, RED, 10, sc=eb(tl / 0.35))
    if tl > 1.47:
        ctx.text("UMA VIDA INTEIRA", 360, 560, 54, WHT, 6)
        p = eo((tl - 1.47) / 1.2)
        rr(img, 60, 620, 60 + 600 * p, 690, 20, (110, 120, 180), 3)
        if tl > 2.7:
            pulse = 1 + 0.25 * math.sin(tl * 9)
            rr(img, 56, 612, 56 + 14 * pulse, 698, 6, (255, 70, 90), 3)
            poly(img, [(62, 720), (46, 760), (78, 760)], (255, 70, 90), 3)
            ctx.text("4 dias", 130, 790, 44, RED, 5)
    return img


def sc15(ctx, tl, T):
    img = R((236, 216, 176), (236, 216, 176), wall=(232, 214, 176), floor=(150, 110, 90), fy=940, win=False, picture=True)
    d = eo((tl - 0.9) / 0.5)
    rr(img, 480, 430, 680, 960, 6, (255, 226, 120) if d > 0 else (150, 96, 66), 4)
    if d > 0:
        rr(img, 480, 430, 480 + 200 * (1 - 0.7 * d), 960, 4, (150, 96, 66), 4)
        poly(img, [(560, 960), (700, 960), (720, 1080), (500, 1080)], (255, 236, 160))
    xk = 110 + 330 * eo(tl / 2.0)
    walk = tl * 12 if tl < 2.0 else 0
    davi(img, xk, 1010, 1.45, mouth='flat', eyes='open', brow=1, walk=walk, aL=15, aR=150)
    kx, ky = hand_pos(xk, 1010, 1.45, 1, 150)
    circ(img, kx + 6, ky - 28, 16, (250, 210, 60), 3)
    line(img, (kx + 6, ky - 12), (kx + 6, ky + 14), (250, 210, 60), 7, 3)
    if 0.4 < tl < 1.3:
        star(img, kx + 28, ky - 50, 16, (255, 250, 200))
    return img


def sc16(ctx, tl, T):
    img = night()
    for i in range(30):
        circ(img, (i * 97) % W, (i * 53) % 560, 2 + i % 2, (255, 255, 230))
    circ(img, 590, 230, 46, (250, 240, 190))
    for i in range(4):
        x = ((i * 260 - tl * 80) % 1100) - 190
        ell(img, x, 800, 260, 120, (28, 36, 70))
    rect(img, 0, 800, W, H, (28, 36, 70))
    rect(img, 0, 860, W, 1100, (60, 62, 80))
    for i in range(7):
        x = (i * 160 - (tl * 900) % 160)
        rr(img, x, 970, x + 90, 986, 4, (240, 220, 120), 0)
    by = 4 * math.sin(tl * 14)
    poly(img, [(520, 900), (720, 840), (720, 980)], (96, 100, 120))
    rr(img, 190, 840 + by, 540, 930 + by, 30, (232, 90, 80), 4)
    rr(img, 250, 770 + by, 470, 850 + by, 30, (232, 90, 80), 4)
    rr(img, 268, 784 + by, 360, 842 + by, 10, (170, 220, 250), 2)
    rr(img, 372, 784 + by, 452, 842 + by, 10, (170, 220, 250), 2)
    circ(img, 314, 806 + by, 24, SKIN, 3)
    for wx in (270, 470):
        circ(img, wx, 935 + by, 40, (40, 40, 52), 3)
        a = tl * 18
        line(img, (wx - 28 * math.cos(a), 935 + by - 28 * math.sin(a)), (wx + 28 * math.cos(a), 935 + by + 28 * math.sin(a)), (200, 200, 210), 6)
        circ(img, wx, 935 + by, 10, (200, 200, 210))
    clock(img, 220, 175, 40, tl * 25, tl * 300)
    title(ctx, tl, 0.1, "3 HORAS", x=430, y=175)
    if tl > 1.55:
        note(img, 330, 560, 3.0)
        forbidden(img, 360, 520, 120, clamp((tl - 1.6) / 0.6))
    return img


def sc17(ctx, tl, T):
    img = night()
    for i in range(24):
        circ(img, (i * 89) % W, (i * 47) % 420, 2, (255, 255, 230))
    hills(img, 880, (40, 80, 80))
    d = eo((tl - 0.4) / 0.5)
    house(img, 360, 960, 520, 360, wall=(220, 208, 186), roof=(120, 50, 60), door_open=d, lit=True)
    if d > 0.7:
        poly(img, [(330, 960), (390, 960), (470, 1100), (250, 1100)], (255, 236, 160))
        rita(img, 360, 960, 0.72, mouth='smile', eyes='open', aL=15, aR=15)
    davi(img, 130, 1060, 0.9, mouth='smile', eyes='open', aL=10, aR=10)
    return img


def porch(img):
    img[:] = grad((70, 44, 88), (140, 80, 100))
    rr(img, 110, 250, 610, 1010, 20, (255, 224, 150), 4)


def sc18(ctx, tl, T):
    img = grad((70, 44, 88), (140, 80, 100))
    rr(img, 90, 230, 630, 1010, 20, (255, 224, 150), 4)
    rect(img, 0, 1010, W, H, (120, 80, 70))
    rita(img, 210, 1010, 1.5, mouth='o' if tl < 1.6 else 'smile', eyes='open', brow=-1 if tl < 1.6 else 0, aL=15, aR=15)
    davi(img, 510, 1010, 1.55, mouth='smile', eyes='open' if tl < 2.6 else 'happy', aL=12, aR=12)
    if tl < 1.67:
        bubble(img, ctx, 250, 470, ["Aconteceu", "alguma coisa?"], eb(tl / 0.2), size=40, tail=-20)
    elif tl < 2.61:
        bubble(img, ctx, 500, 460, ["Nada, mãe."], eb((tl - 1.67) / 0.2), size=44, tail=20)
    else:
        bubble(img, ctx, 500, 460, ["Só vim."], eb((tl - 2.61) / 0.2), size=48, tail=20)
        heart(img, 580, 390, 20)
    return img


def hug(img, tl, bg=None):
    img[:] = grad((250, 190, 140), (150, 90, 130))
    rect(img, 0, 1010, W, H, (110, 170, 100))
    sw = math.sin(tl * 2) * 4
    davi(img, 310 + sw, 1010, 1.55, mouth='smile', eyes='happy', aL=-20, aR=-75, tilt=0.4)
    rita(img, 425 + sw, 1010, 1.4, mouth='smile', eyes='happy', aL=-75, aR=-30, tilt=-0.5)


def sc19(ctx, tl, T):
    img = np.zeros((H, W, 3), np.uint8)
    hug(img, tl)
    floating_hearts(img, tl, 0.3, 360, 700, n=6, spread=300, rise=380, s=18)
    if tl > 2.29:
        p = eb((tl - 2.29) / 0.25)
        calendar_page(img, 560, 230, 190 * p, 190 * p)
        if p > 0.9:
            ctx.text("34", 560, 250, 84, DK, 0)
            xmark(img, 560, 250, 70, p=clamp((tl - 2.7) / 0.5))
    return img


def sc20(ctx, tl, T):
    img = np.zeros((H, W, 3), np.uint8)
    hug(img, tl + 5)
    floating_hearts(img, tl, 0.0, 360, 700, n=7, spread=340, rise=420, s=20)
    p = eb(tl / 0.3)
    circ(img, 360, 300, 125 * p, (80, 200, 120), 6)
    if p > 0.9:
        ctx.text("1ª", 360, 300, 150, WHT, 8)
        ctx.text("VISITA", 360, 450, 60, GRN, 6)
    if tl > 1.7:
        q = eb((tl - 1.7) / 0.35)
        blit(img, pol('hug', 460, 560), 360, 640, -4, 0.35 + 0.65 * q)
    return img


def sc21(ctx, tl, T):
    img = bokeh(tl)
    rr(img, 160, 170, 560, 1040, 50, (60, 64, 96), 5)
    rr(img, 180, 200, 540, 1010, 30, (244, 246, 252), 0)
    ctx.text("Contatos", 360, 250, 44, DK, 0)
    names = ["Mãe", "Pai", "Vovó", "Amigo"]
    sel = int(tl * 2.6) % 4 if tl < 1.4 else 0
    cols = [(240, 160, 130), (130, 180, 240), (200, 160, 240), (130, 220, 160)]
    for i, nm in enumerate(names):
        y = 360 + i * 150
        if i == sel:
            rr(img, 190, y - 55, 530, y + 55, 14, (200, 225, 255), 0)
        circ(img, 250, y, 36, cols[i], 3)
        ctx.text(nm, 310, y, 40, DK, 0, anchor='lm')
    return img


CAL_HI = [4, 22, 9, 27, 13, 18, 6, 30, 11, 24, 15, 19]


def month(img, ctx, header, tl, mode):
    calendar_page(img, 360, 560, 600, 700)
    ctx.text(header, 360, 300, 56, WHT, 4)
    cells = {}
    for d in range(1, 32):
        i = d - 1
        cx = 105 + (i % 7) * 85
        cy = 420 + (i // 7) * 100 + 60
        cells[d] = (cx, cy)
        ctx.text(str(d), cx, cy, 36, DK, 0)
    return cells


def sc22(ctx, tl, T):
    img = bokeh(tl)
    cells = month(img, ctx, "QUANDO?", tl, 0)
    idx = CAL_HI[int(tl / 0.18) % len(CAL_HI)] if tl < 2.4 else 17
    cx, cy = cells[idx]
    cv2.circle(img, (I(cx), I(cy)), 36, C(img, (235, 50, 70)), 6, cv2.LINE_AA)
    if tl > 2.4:
        ctx.text("?", cx, cy - 70, 80, RED, 6, sc=eb((tl - 2.4) / 0.25))
    return img


def sc23(ctx, tl, T):
    img = bokeh(tl)
    cells = month(img, ctx, "DOMINGO", tl, 1)
    for k, d in enumerate([1, 8, 15, 22, 29]):
        tt = tl - 0.15 - k * 0.3
        if tt > 0:
            cx, cy = cells[d]
            xmark(img, cx, cy, 28, p=clamp(tt / 0.25))
    return img


def sc24(ctx, tl, T):
    img = sunset()
    hills(img, 880, (90, 150, 100))
    house(img, 360, 880, 340, 250, lit=True)
    fence(img, 20, 700, 960)
    sw = math.sin(tl * 2) * 3
    davi(img, 300 + sw, 1010, 1.2, mouth='smile', eyes='happy', aL=-20, aR=-75, tilt=0.4)
    rita(img, 410 + sw, 1010, 1.1, mouth='smile', eyes='happy', aL=-75, aR=-30, tilt=-0.5)
    floating_hearts(img, tl, 0.0, 360, 800, n=7, spread=260, rise=320, s=20)
    title(ctx, tl, 0.0, "VAI HOJE.", y=190, size=130)
    return img


SCENES = [
    (0.0, 3.02, sc1, False), (3.02, 8.39, sc2, False), (8.39, 11.03, sc3, False), (11.03, 14.14, sc4, False),
    (14.14, 19.99, sc5, False), (19.99, 25.02, sc6, False), (25.02, 32.12, sc7, False), (32.12, 38.34, sc8, False),
    (38.34, 41.52, sc9, True), (41.52, 44.22, sc10, True), (44.22, 46.84, sc11, False), (46.84, 54.27, sc12, False),
    (54.27, 60.17, sc13, False), (60.17, 64.14, sc14, False), (64.14, 66.63, sc15, True), (66.63, 69.43, sc16, False),
    (69.43, 71.41, sc17, False), (71.41, 75.0, sc18, False), (75.0, 79.84, sc19, False), (79.84, 82.75, sc20, False),
    (82.75, 84.68, sc21, False), (84.68, 88.03, sc22, False), (88.03, 90.61, sc23, False), (90.61, 92.01, sc24, False),
]


def render(t):
    for a, b, fn, spin in SCENES:
        if a <= t < b:
            break
    tl, T = t - a, b - a
    ctx = Ctx()
    ctx.gray = 0.0
    ctx.flash = 0.0
    img = fn(ctx, tl, T)
    if ctx.gray > 0:
        g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        g3 = np.repeat(g[:, :, None], 3, axis=2)
        img = (img * (1 - ctx.gray) + g3 * ctx.gray).astype(np.uint8)
    img = draw_texts(img, ctx.texts)
    z = 1.0 + 0.04 * (tl / T)
    if z > 1.001:
        M = cv2.getRotationMatrix2D((W / 2, H * 0.5), 0, z)
        img = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    if spin and tl < 0.35:
        p = tl / 0.35
        ang = (1 - eo(p)) * 160
        sc = 1 + (1 - p) * 0.5
        acc = np.zeros(img.shape, np.float32)
        for k in range(4):
            M = cv2.getRotationMatrix2D((W / 2, H / 2), ang * (1 + k * 0.07), sc)
            acc += cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        img = (acc / 4).astype(np.uint8)
    caption(ctx, t)
    img = draw_texts(img, ctx.over)
    if ctx.flash > 0:
        img = (img * (1 - ctx.flash) + 255 * ctx.flash).astype(np.uint8)
    return img


def small(img):
    return cv2.resize(img, (576, 1024), interpolation=cv2.INTER_AREA)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "test":
        ts = [float(x) for x in sys.argv[2:]]
        tiles = [small(render(t)) for t in ts]
        tiles = [cv2.resize(x, (288, 512)) for x in tiles]
        cols = 5
        rows = (len(tiles) + cols - 1) // cols
        sheet = np.zeros((rows * 512, cols * 288, 3), np.uint8)
        for i, tl_ in enumerate(tiles):
            r, c = divmod(i, cols)
            sheet[r * 512:(r + 1) * 512, c * 288:(c + 1) * 288] = tl_
        cv2.imwrite(os.path.join(BASE, "test.jpg"), cv2.cvtColor(sheet, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 88])
    elif mode == "seg":
        a, b, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "576x1024", "-r", str(FPS), "-i", "-",
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-g", "30", out]
        pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for f in range(a, b):
            pr.stdin.write(small(render(f / FPS)).tobytes())
        pr.stdin.close()
        pr.wait()
        print("seg done", a, b, flush=True)
    else:
        out = sys.argv[2]
        N = int(DUR * FPS)
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "576x1024", "-r", str(FPS), "-i", "-",
               "-i", AUDIO, "-af", "apad", "-t", str(DUR),
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out]
        pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for f in range(N):
            pr.stdin.write(small(render(f / FPS)).tobytes())
            if f % 150 == 0:
                print("frame", f, "/", N, flush=True)
        pr.stdin.close()
        pr.wait()
        print("done", flush=True)

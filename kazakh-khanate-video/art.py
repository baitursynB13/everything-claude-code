#!/usr/bin/env python3
"""12 сахнаның иллюстрациясын SVG ретінде салады (силуэт стилі) -> art/NN.svg.
Содан кейін `node render.js` оларды clips/NN.jpg етіп шығарады."""
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent
W, H = 1080, 1920


# ---------- негізгі элементтер ----------
def grad(gid, stops, radial=False, **kw):
    s = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>'
                for o, c, a in [(st + (1,))[:3] for st in stops])
    if radial:
        return f'<radialGradient id="{gid}">{s}</radialGradient>'
    a = dict(x1=0, y1=0, x2=0, y2=1)
    a.update(kw)
    attr = " ".join(f'{k}="{v}"' for k, v in a.items())
    return f'<linearGradient id="{gid}" {attr}>{s}</linearGradient>'


class Scene:
    def __init__(self, seed):
        self.defs, self.body, self.n = [], [], 0
        self.rnd = random.Random(seed)

    def gid(self):
        self.n += 1
        return f"g{self.n}"

    def add(self, s):
        self.body.append(s)

    def sky(self, stops):
        g = self.gid()
        self.defs.append(grad(g, stops))
        self.add(f'<rect width="{W}" height="{H}" fill="url(#{g})"/>')

    def glow(self, x, y, r, color, op=1.0):
        g = self.gid()
        self.defs.append(grad(g, [(0, color, op), (0.35, color, op * 0.45), (1, color, 0)], radial=True))
        self.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#{g})"/>')

    def sun(self, x, y, r, color="#fff3c4", glow="#ffc35a"):
        self.glow(x, y, r * 7, glow, 0.75)
        self.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>')

    def clouds(self, y0, y1, color, n=9, op=0.5, size=1.0):
        for _ in range(n):
            x, y = self.rnd.uniform(-100, W + 100), self.rnd.uniform(y0, y1)
            rx = self.rnd.uniform(160, 420) * size
            self.add(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{rx:.0f}" ry="{rx * self.rnd.uniform(.12, .22):.0f}" '
                     f'fill="{color}" opacity="{op * self.rnd.uniform(.5, 1):.2f}" filter="url(#blur)"/>')

    def stars(self, n=120, ymax=900):
        for _ in range(n):
            self.add(f'<circle cx="{self.rnd.uniform(0, W):.0f}" cy="{self.rnd.uniform(0, ymax):.0f}" '
                     f'r="{self.rnd.uniform(.8, 2.4):.1f}" fill="#fff" opacity="{self.rnd.uniform(.3, .9):.2f}"/>')

    def hills(self, y, amp, color, freq=1.0, to=H):
        ph = [self.rnd.uniform(0, 6.28) for _ in range(3)]
        pts = []
        for x in range(-20, W + 40, 20):
            t = x / W * 6.28 * freq
            pts.append((x, y + amp * (math.sin(t + ph[0]) * .6 + math.sin(t * 2.3 + ph[1]) * .3
                                      + math.sin(t * 5.1 + ph[2]) * .1)))
        d = "M" + " L".join(f"{x},{yy:.0f}" for x, yy in pts) + f" L{W + 40},{to} L-20,{to} Z"
        self.add(f'<path d="{d}" fill="{color}"/>')
        return lambda x: y + amp * (math.sin(x / W * 6.28 * freq + ph[0]) * .6
                                    + math.sin(x / W * 6.28 * freq * 2.3 + ph[1]) * .3
                                    + math.sin(x / W * 6.28 * freq * 5.1 + ph[2]) * .1)

    def mountains(self, y, h, color, snow=None, peaks=5, to=H):
        x, pts, tops = -80, [], []
        step = (W + 160) / peaks
        while x < W + 80:
            px = x + step * self.rnd.uniform(.35, .65)
            py = y - h * self.rnd.uniform(.55, 1)
            pts += [(x, y + self.rnd.uniform(-20, 20)), (px - step * .2, py + h * .35 + self.rnd.uniform(-20, 20)),
                    (px, py), (px + step * .22, py + h * .4 + self.rnd.uniform(-20, 20))]
            tops.append((px, py, step))
            x += step
        d = "M" + " L".join(f"{a:.0f},{b:.0f}" for a, b in pts) + f" L{W + 80},{to} L-80,{to} Z"
        self.add(f'<path d="{d}" fill="{color}"/>')
        if snow:
            for px, py, st in tops:
                k = h * .3
                self.add(f'<path d="M{px:.0f},{py:.0f} L{px - st * .15:.0f},{py + k:.0f} L{px - st * .05:.0f},{py + k * .75:.0f} '
                         f'L{px + st * .02:.0f},{py + k * 1.05:.0f} L{px + st * .09:.0f},{py + k * .7:.0f} '
                         f'L{px + st * .17:.0f},{py + k * 1.0:.0f} Z" fill="{snow}"/>')

    def haze(self, y, h, color, op=0.5):
        g = self.gid()
        self.defs.append(grad(g, [(0, color, 0), (.5, color, op), (1, color, 0)]))
        self.add(f'<rect y="{y - h / 2}" width="{W}" height="{h}" fill="url(#{g})"/>')

    def shade(self, y0, color="#000", op=0.75):
        """төменгі жақты қарайту — субтитр анық оқылуы үшін"""
        g = self.gid()
        self.defs.append(grad(g, [(0, color, 0), (1, color, op)]))
        self.add(f'<rect y="{y0}" width="{W}" height="{H - y0}" fill="url(#{g})"/>')

    def particles(self, n, color, rmax=3, y0=0, y1=H, op=.7, streak=0):
        for _ in range(n):
            x, y, r = self.rnd.uniform(0, W), self.rnd.uniform(y0, y1), self.rnd.uniform(.8, rmax)
            o = self.rnd.uniform(.2, op)
            if streak:
                self.add(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x - streak:.0f}" y2="{y + streak * .35:.0f}" '
                         f'stroke="{color}" stroke-width="{r:.1f}" opacity="{o:.2f}" stroke-linecap="round"/>')
            else:
                self.add(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="{color}" opacity="{o:.2f}"/>')

    def at(self, shape, x, y, s=1.0, flip=False, rot=0):
        sx = -s if flip else s
        self.add(f'<g transform="translate({x:.0f},{y:.0f}) rotate({rot}) scale({sx:.3f},{s:.3f})">{shape}</g>')

    def svg(self):
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
<filter id="blur" x="-30%" y="-80%" width="160%" height="260%"><feGaussianBlur stdDeviation="22"/></filter>
<filter id="soft"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="paint" x="0" y="0" width="100%" height="100%">
<feTurbulence type="fractalNoise" baseFrequency="0.011 0.02" numOctaves="3" seed="7" result="n"/>
<feDisplacementMap in="SourceGraphic" in2="n" scale="16" xChannelSelector="R" yChannelSelector="G"/></filter>
<filter id="grain" x="0" y="0" width="100%" height="100%">
<feTurbulence type="fractalNoise" baseFrequency="0.75" numOctaves="2" seed="3"/>
<feColorMatrix values="0 0 0 0 .5  0 0 0 0 .45  0 0 0 0 .4  .9 0 0 0 -.25"/></filter>
<radialGradient id="vig" cx=".5" cy=".45" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/>
<stop offset="1" stop-color="#000" stop-opacity=".7"/></radialGradient>
{"".join(self.defs)}
</defs>
<g><rect x="-40" y="-40" width="{W + 80}" height="{H + 80}" fill="#000"/>{"".join(self.body)}</g>
<rect width="{W}" height="{H}" filter="url(#grain)" opacity=".22"/>
<rect width="{W}" height="{H}" fill="url(#vig)"/>
</svg>'''


# ---------- фигуралар (жер нүктесі 0,0; жоғары қарай теріс y) ----------
def horse(c, gait=0):
    g = gait
    return (f'<g fill="{c}" stroke="{c}" stroke-linecap="round">'
            f'<ellipse cx="0" cy="-62" rx="37" ry="17"/>'
            f'<path d="M20,-74 L40,-110 L54,-104 L40,-56 Z"/>'
            f'<path d="M38,-112 L66,-97 L64,-87 L46,-95 Z"/><path d="M41,-112 L44,-124 L50,-110 Z"/>'
            f'<path d="M22,-112 Q30,-96 24,-76" stroke-width="5" fill="none"/>'
            f'<path d="M25,-56 L{29 + g * 5:.0f},-27 L{28 + g * 13:.0f},0" stroke-width="7" fill="none" stroke-linejoin="round"/>'
            f'<path d="M17,-56 L{17 - g * 5:.0f},-27 L{14 - g * 14:.0f},0" stroke-width="7" fill="none" stroke-linejoin="round"/>'
            f'<path d="M-25,-58 L{-33 - g * 4:.0f},-28 L{-28 - g * 13:.0f},0" stroke-width="8" fill="none" stroke-linejoin="round"/>'
            f'<path d="M-19,-58 L{-22 + g * 5:.0f},-28 L{-15 + g * 14:.0f},0" stroke-width="8" fill="none" stroke-linejoin="round"/>'
            f'<ellipse cx="-24" cy="-56" rx="15" ry="16"/><ellipse cx="22" cy="-58" rx="13" ry="15"/>'
            f'<path d="M-34,-72 Q-60,-62 -54,-22" stroke-width="7" fill="none"/></g>')


def man(c, hat="fur", y=0, robe=None, w=1.0):
    r = robe or c
    hats = {
        "fur": f'<path d="M-9,-64 L11,-64 L8,-80 L-5,-80 Z" fill="{c}"/>',
        "cap": f'<path d="M-8,-64 L10,-64 L2,-86 Z" fill="{c}"/><line x1="2" y1="-86" x2="9" y2="-98" stroke="{c}" stroke-width="2"/>',
        "turban": f'<ellipse cx="1" cy="-68" rx="11" ry="7" fill="{c}"/>',
        "helm": f'<path d="M-8,-63 Q1,-84 10,-63 Z" fill="{c}"/><line x1="1" y1="-76" x2="1" y2="-90" stroke="{c}" stroke-width="2"/>',
        "none": "",
    }
    return (f'<g transform="translate(0,{y})"><path d="M{-11 * w},0 L{-8 * w},-46 Q0,-56 {8 * w},-46 L{11 * w},0 Z" fill="{r}"/>'
            f'<circle cx="1" cy="-58" r="7.5" fill="{c}"/>{hats[hat]}</g>')


def rider(c, hat="fur", spear=False, tug=False, gait=0, robe=None):
    extra = ""
    if spear:
        extra += f'<line x1="12" y1="-92" x2="24" y2="-200" stroke="{c}" stroke-width="2.6"/>'
    if tug:
        extra += (f'<line x1="12" y1="-92" x2="16" y2="-230" stroke="{c}" stroke-width="3"/>'
                  f'<path d="M16,-230 Q-6,-222 -12,-186 Q0,-204 16,-206 Z" fill="{c}"/>')
    leg = f'<line x1="2" y1="-80" x2="9" y2="-48" stroke="{robe or c}" stroke-width="8" stroke-linecap="round"/>'
    return horse(c, gait) + f'<g transform="translate(0,-70)">{man(c, hat, robe=robe)}</g>' + leg + extra


def camel(c, load=True):
    ld = f'<rect x="-22" y="-116" width="44" height="26" rx="6" fill="{c}"/>' if load else ""
    return (f'<g fill="{c}" stroke="{c}" stroke-linecap="round"><ellipse cx="0" cy="-70" rx="40" ry="18"/>'
            f'<ellipse cx="-14" cy="-90" rx="14" ry="15"/><ellipse cx="15" cy="-90" rx="14" ry="15"/>'
            f'<path d="M34,-70 Q58,-70 55,-120" stroke-width="11" fill="none"/><ellipse cx="64" cy="-124" rx="13" ry="6.5"/>'
            f'<line x1="26" y1="-60" x2="28" y2="0" stroke-width="6"/><line x1="18" y1="-60" x2="14" y2="0" stroke-width="6"/>'
            f'<line x1="-26" y1="-60" x2="-30" y2="0" stroke-width="6"/><line x1="-18" y1="-60" x2="-15" y2="0" stroke-width="6"/>'
            f'{ld}</g>')


def yurt(wall, roof, door="#2a1a12", band="#8a3324"):
    return (f'<rect x="-62" y="-46" width="124" height="46" fill="{wall}"/>'
            f'<path d="M-66,-46 Q-50,-98 0,-104 Q50,-98 66,-46 Z" fill="{roof}"/>'
            f'<rect x="-10" y="-110" width="20" height="8" rx="3" fill="{door}"/>'
            f'<rect x="-62" y="-48" width="124" height="6" fill="{band}"/>'
            f'<rect x="-12" y="-38" width="24" height="38" fill="{door}"/>')


def cart(c):
    return (f'<g fill="{c}" stroke="{c}"><rect x="-50" y="-34" width="100" height="8"/>'
            f'<path d="M-40,-34 Q-30,-84 0,-88 Q30,-84 40,-34 Z"/>'
            f'<circle cx="-30" cy="-16" r="16" fill="none" stroke-width="5"/><circle cx="30" cy="-16" r="16" fill="none" stroke-width="5"/>'
            f'<line x1="50" y1="-30" x2="86" y2="-40" stroke-width="4"/></g>')


def tug(c, h=220):
    return (f'<line x1="0" y1="0" x2="0" y2="{-h}" stroke="{c}" stroke-width="4"/>'
            f'<circle cx="0" cy="{-h}" r="6" fill="{c}"/>'
            f'<path d="M0,{-h + 6} Q-26,{-h + 22} -30,{-h + 70} Q-12,{-h + 44} 0,{-h + 40} Z" fill="{c}"/>')


def flag(c, cloth, h=240, torn=False):
    p = (f"M0,{-h} L70,{-h + 12} L52,{-h + 28} L78,{-h + 44} L40,{-h + 52} L60,{-h + 70} L0,{-h + 62} Z" if torn
         else f"M0,{-h} Q40,{-h - 8} 78,{-h + 6} Q60,{-h + 34} 80,{-h + 60} Q40,{-h + 52} 0,{-h + 62} Z")
    return f'<line x1="0" y1="0" x2="0" y2="{-h - 8}" stroke="{c}" stroke-width="4"/><path d="{p}" fill="{cloth}"/>'


def eagle(c):
    return (f'<path d="M0,0 Q-30,-28 -78,-12 Q-40,-10 -9,8 L-6,22 L0,14 L6,22 L9,8 Q40,-10 78,-12 Q30,-28 0,0 Z" fill="{c}"/>')


def fortress(c):
    cren = "".join(f'<rect x="{x}" y="-98" width="14" height="12"/>' for x in range(-196, 200, 28))
    tw = "".join(f'<rect x="{x - 26}" y="-150" width="52" height="150"/>'
                 + "".join(f'<rect x="{x - 26 + k}" y="-162" width="12" height="14"/>' for k in (0, 20, 40))
                 for x in (-200, 0, 200))
    return f'<g fill="{c}"><rect x="-200" y="-88" width="400" height="88"/>{cren}{tw}<path d="M-16,0 L-16,-44 Q0,-62 16,-44 L16,0 Z" fill="#000" opacity=".5"/></g>'


def sheep(c):
    return f'<ellipse cx="0" cy="-12" rx="13" ry="8" fill="{c}"/><circle cx="12" cy="-16" r="4.5" fill="{c}"/>'


def fire(sc, x, y, s=1.0):
    sc.glow(x, y - 10 * s, 150 * s, "#ff9a3c", 0.8)
    sc.at('<path d="M-14,0 Q-20,-26 -4,-44 Q-4,-28 6,-34 Q0,-56 10,-66 Q24,-36 16,0 Z" fill="#ffd27a"/>'
          '<path d="M-7,0 Q-9,-16 0,-28 Q9,-16 8,0 Z" fill="#fff6d8"/>', x, y, s)


def smoke(sc, x, y, color="#ddd", op=.35, n=7):
    for i in range(n):
        sc.add(f'<ellipse cx="{x + i * 14 + sc.rnd.uniform(-8, 8):.0f}" cy="{y - i * 44:.0f}" rx="{16 + i * 9}" ry="{12 + i * 6}" '
               f'fill="{color}" opacity="{op * (1 - i / (n + 1)):.2f}" filter="url(#soft)"/>')


def caravan(sc, c, x0, y0, s0, x1, y1, s1, n, flip=False, kinds="rcpwr", gait=True):
    """алыстан (x1,y1,s1) жақынға (x0,y0,s0) созылған көш"""
    for i in reversed(range(n)):
        t = i / max(1, n - 1)
        t2 = t ** 0.6
        x, y, s = x0 + (x1 - x0) * t2, y0 + (y1 - y0) * t2, s0 + (s1 - s0) * t2
        k = kinds[i % len(kinds)]
        g = sc.rnd.uniform(-.8, .8) if gait else 0
        shape = {"r": rider(c, sc.rnd.choice(["fur", "cap"]), gait=g), "c": camel(c),
                 "p": man(c, "fur") + f'<g transform="translate(26,0) scale(.8)">{man(c, "none")}</g>',
                 "w": cart(c) + f'<g transform="translate(118,0)">{horse(c, g)}</g>'}[k]
        sc.at(shape, x, y, s, flip)


def crowd(sc, c, y, x0, x1, s, n, hats=("fur", "cap", "none", "fur"), jitter=10, spears=0.0):
    for i in range(n):
        x = x0 + (x1 - x0) * (i + sc.rnd.uniform(-.3, .3)) / max(1, n - 1)
        sh = man(c, sc.rnd.choice(hats))
        if sc.rnd.random() < spears:
            sh += f'<line x1="12" y1="0" x2="14" y2="-120" stroke="{c}" stroke-width="2.5"/>'
        sc.at(sh, x, y + sc.rnd.uniform(-jitter, jitter), s * sc.rnd.uniform(.9, 1.1))


# ---------- 12 сахна ----------
def s01():
    sc = Scene(1)
    sc.sky([(0, "#1d2433"), (.35, "#4a4658"), (.52, "#c7794a"), (.6, "#f4c46e"), (1, "#f4c46e")])
    sc.clouds(80, 620, "#12151f", 12, .8, 1.3)
    sc.sun(600, 1120, 60)
    sc.clouds(700, 1000, "#f0a35a", 6, .45)
    sc.hills(1150, 30, "#7a5a45", .7)
    caravan(sc, "#3a2a24", 300, 1290, .55, 980, 1150, .08, 26, flip=True)
    sc.haze(1180, 160, "#f2b56a", .45)
    f = sc.hills(1330, 60, "#17110f", .5)
    sc.at(rider("#0c0908", "fur", gait=.2), 430, f(430) + 6, 2.6)
    sc.at(rider("#0c0908", "cap", gait=-.2), 700, f(700) + 6, 2.35, flip=True)
    sc.particles(90, "#ffd9a0", 3, 900, 1500, .5, streak=26)
    sc.shade(1300)
    return sc


def s02():
    sc = Scene(2)
    sc.sky([(0, "#15181d"), (.45, "#3b4046"), (.62, "#7b7468"), (1, "#7b7468")])
    sc.clouds(60, 900, "#0b0d10", 16, .85, 1.4)
    sc.glow(540, 1050, 520, "#b9a98a", .5)
    sc.hills(1140, 20, "#4a4640", .6)
    sc.at(rider("#2c2a27", gait=.4), 880, 1150, .28)
    sc.at(rider("#2c2a27", "cap", gait=-.3), 940, 1154, .25)
    f = sc.hills(1230, 30, "#1d1b19", .5)
    # қираған хан ордасы
    sc.add('<g fill="#121110"><path d="M250,1235 L330,960 L420,900 L540,870 L600,905 L570,960 L680,930 L790,1010 L850,1235 Z"/>'
           '<path d="M520,870 L536,790 L552,872 Z"/></g>'
           '<path d="M420,1235 L470,1040 L610,1010 L650,1235 Z" fill="#050505"/>'
           '<path d="M600,905 L640,980 L575,965 Z M330,960 L372,1010 L300,1070 Z" fill="#3b3833"/>')
    sc.at(flag("#121110", "#5a2a22", 330, torn=True), 200, f(200) + 4, 1, rot=-12)
    sc.at(flag("#121110", "#4a3f2a", 300, torn=True), 905, f(905) + 4, 1, flip=True, rot=9)
    sc.at(tug("#121110", 250), 760, 1240, 1, rot=38)
    sc.at(cart("#121110"), 150, 1330, 1.5, rot=-14)
    sc.add('<circle cx="840" cy="1335" r="36" fill="none" stroke="#121110" stroke-width="8"/>'
           '<path d="M804,1335 L876,1335 M840,1299 L840,1371" stroke="#121110" stroke-width="5"/>')
    sc.hills(1360, 18, "#0d0c0b", .4)
    sc.particles(110, "#cfc6b4", 2.6, 700, 1500, .45, streak=34)
    sc.shade(1250)
    return sc


def s03():
    sc = Scene(3)
    sc.sky([(0, "#0b0f1c"), (.5, "#1c2036"), (.66, "#4b3340"), (1, "#4b3340")])
    sc.stars(140, 800)
    sc.clouds(300, 800, "#070912", 6, .6)
    sc.hills(1080, 16, "#191621", .5)
    sc.at(fortress("#110f18"), 240, 1088, 1.0)          # Тура қаласы
    sc.at(fortress("#110f18"), 900, 1090, .7)
    for x in (120, 250, 380, 860, 940):
        sc.glow(x, 1040, 26, "#ffb35a", .7)
    sc.hills(1210, 14, "#0e0b0d", .4)
    sc.glow(540, 1120, 520, "#ff9838", .55)
    # хан ордасы
    sc.add('<path d="M170,1250 L230,990 Q330,820 540,790 Q750,820 850,990 L910,1250 Z" fill="#1a0f0c"/>'
           '<path d="M230,990 Q540,930 850,990 L846,1010 Q540,952 234,1010 Z" fill="#c8963c"/>'
           '<path d="M515,792 L540,700 L565,792 Z" fill="#1a0f0c"/><circle cx="540" cy="696" r="12" fill="#c8963c"/>')
    g = sc.gid()
    sc.defs.append(grad(g, [(0, "#ffe2a0"), (.5, "#f08a2c"), (1, "#7a2a12")], radial=True))
    sc.add(f'<path d="M370,1250 L400,1040 Q540,960 680,1040 L710,1250 Z" fill="url(#{g})"/>')
    # тақтағы хан
    sc.add('<g fill="#120807"><rect x="470" y="1100" width="140" height="150"/><path d="M462,1100 L478,1010 L602,1010 L618,1100 Z"/>'
           '<path d="M492,1250 L500,1130 Q540,1100 580,1130 L588,1250 Z"/><circle cx="540" cy="1096" r="24"/>'
           '<path d="M512,1082 L568,1082 L560,1040 L520,1040 Z"/></g>'
           '<path d="M514,1082 L566,1082 L564,1070 L516,1070 Z" fill="#e0aa48"/>')
    for i, x in enumerate((250, 320, 760, 830)):
        sc.at(man("#090605", "helm") + '<line x1="14" y1="0" x2="16" y2="-150" stroke="#090605" stroke-width="3"/>'
              '<path d="M16,-150 L11,-168 L21,-168 Z" fill="#090605"/>', x, 1300 + (i % 2) * 14, 2.3, flip=x > 540)
    sc.at(tug("#090605", 330), 150, 1290, 1.2)
    sc.at(tug("#090605", 330), 930, 1290, 1.2, flip=True)
    fire(sc, 205, 1240, 1.3)
    fire(sc, 875, 1240, 1.3)
    sc.hills(1330, 10, "#070505", .3)
    sc.shade(1260)
    return sc


def s04():
    sc = Scene(4)
    sc.sky([(0, "#07090f"), (.55, "#151927"), (.7, "#2a2330"), (1, "#2a2330")])
    sc.stars(160, 760)
    # аспандағы алып хан көлеңкесі
    sc.add('<g fill="#04050a" opacity=".85" filter="url(#blur)"><path d="M300,1100 L330,620 Q540,480 750,620 L780,1100 Z"/>'
           '<circle cx="540" cy="480" r="110"/><path d="M430,430 L650,430 L620,300 L580,360 L540,280 L500,360 L460,300 Z"/></g>')
    sc.hills(1120, 22, "#0f1018", .6)
    sc.at(yurt("#17131a", "#1d1820", "#ffb35a", "#3a2622"), 170, 1190, 1.6)
    sc.at(yurt("#17131a", "#1d1820", "#ffb35a", "#3a2622"), 930, 1180, 1.3)
    sc.glow(170, 1160, 70, "#ffb35a", .5)
    sc.hills(1250, 16, "#0a0a0f", .4)
    sc.glow(540, 1270, 430, "#ff9234", .7)
    c = "#050406"
    for i, (x, y, s) in enumerate([(300, 1300, 2.2), (385, 1275, 2.0), (700, 1275, 2.0), (790, 1300, 2.2),
                                   (230, 1340, 2.4), (860, 1340, 2.4)]):
        sc.at(man(c, ["fur", "cap", "fur", "none"][i % 4], w=1.5).replace('-46', '-34').replace('-56', '-44'),
              x, y, s, flip=x > 540)
    sc.at(man(c, "fur", w=1.25), 480, 1262, 3.0)                    # Керей
    sc.at(man(c, "cap", w=1.1), 610, 1262, 2.85, flip=True)         # Жәнібек
    fire(sc, 545, 1330, 1.9)
    sc.particles(40, "#ffb45a", 2.4, 1000, 1300, .8)
    sc.hills(1400, 10, "#030304", .3)
    sc.shade(1330)
    return sc


def s05():
    sc = Scene(5)
    sc.sky([(0, "#1a0d12"), (.4, "#5a1c1c"), (.58, "#b3432a"), (.66, "#e08a3c"), (1, "#e08a3c")])
    sc.clouds(100, 800, "#12080c", 13, .8, 1.3)
    sc.sun(300, 1075, 70, "#ffd9a0", "#ff6a2a")
    f = sc.hills(1090, 34, "#240f0f", .6)
    c = "#0d0607"
    for x in (560, 660, 760, 850, 940, 1020):                      # қырдағы хан жасақтары
        sc.at(rider(c, "helm", spear=True, gait=sc.rnd.uniform(-.3, .3)), x, f(x) + 4, 1.05 + (x - 560) / 1500, flip=True)
    sc.at(flag(c, "#7a1a14", 240), 500, f(500), 1.0)
    sc.hills(1230, 18, "#1a0b0b", .5)
    for x, s in ((150, 1.5), (420, 1.2), (900, 1.4)):
        sc.at(yurt("#22100e", "#2c1512", "#0a0504", "#40160f"), x, 1262, s)
    smoke(sc, 430, 1140, "#2a1414", .6)
    smoke(sc, 915, 1120, "#2a1414", .6)
    sc.hills(1300, 12, "#100607", .4)
    sc.at(man(c, "none", w=1.2), 520, 1372, 2.3, rot=38)            # бас иген қария
    sc.add(f'<line x1="556" y1="1372" x2="566" y2="1290" stroke="{c}" stroke-width="5"/>')
    sc.at(man(c, "fur", w=1.2) + f'<g transform="translate(22,0) scale(.6)">{man(c, "none")}</g>', 300, 1368, 2.2)
    sc.at(man(c, "none", w=1.3) + f'<g transform="translate(-22,0) scale(.55)">{man(c, "none")}</g>', 690, 1372, 2.1, flip=True)
    sc.at(man(c, "helm") + f'<line x1="14" y1="0" x2="18" y2="-140" stroke="{c}" stroke-width="3"/>', 830, 1380, 2.9, flip=True)
    sc.particles(60, "#ff9a5a", 2.4, 900, 1400, .5)
    sc.shade(1300)
    return sc


def s06():
    sc = Scene(6)
    sc.sky([(0, "#2a1d18"), (.4, "#7a4a2a"), (.6, "#d9893c"), (1, "#d9893c")])
    sc.clouds(100, 900, "#1a110d", 12, .7, 1.4)
    sc.glow(760, 1040, 600, "#ffb04a", .7)
    sc.hills(1090, 16, "#5a3a26", .5)
    sc.at(fortress("#3a2418"), 800, 1096, .9)                        # Сығанақ
    smoke(sc, 760, 990, "#2a1a12", .6, 8)
    for _ in range(26):                                              # жебелер
        x, y = sc.rnd.uniform(100, 1000), sc.rnd.uniform(520, 980)
        sc.add(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x - 46:.0f}" y2="{y + sc.rnd.uniform(-22, 8):.0f}" stroke="#1a0f0a" stroke-width="2.4"/>')
    c2 = "#2e1c13"
    for i in range(9):                                               # шегінген әскер
        sc.at(rider(c2, "fur", gait=sc.rnd.uniform(.5, 1)), 60 + i * 52 + sc.rnd.uniform(-10, 10), 1170 + sc.rnd.uniform(-12, 12), .55, flip=True)
    sc.at(flag(c2, "#6a3a22", 220, torn=True), 330, 1180, .8, rot=-48)
    sc.haze(1190, 220, "#e8a860", .6)
    sc.hills(1250, 20, "#3a2416", .5)
    c = "#120a07"
    for i in range(7):                                               # ойрат атты әскері
        sc.at(rider(c, "helm", spear=i % 2 == 0, tug=i == 3, gait=sc.rnd.uniform(.6, 1)),
              1010 - i * 118 + sc.rnd.uniform(-14, 14), 1300 + sc.rnd.uniform(-16, 16), 1.5, flip=True, rot=-5)
    sc.haze(1330, 200, "#c98a4a", .55)
    for i in range(4):
        sc.at(rider("#070403", "helm", spear=True, gait=1), 1000 - i * 250, 1440 + (i % 2) * 20, 2.5, flip=True, rot=-6)
    sc.particles(140, "#f4c88a", 3.4, 1000, 1600, .5, streak=40)
    sc.shade(1330)
    return sc


def s07():
    sc = Scene(7)
    sc.sky([(0, "#1c1b33"), (.38, "#5a3f5a"), (.56, "#d9824a"), (.64, "#f6c06a"), (1, "#f6c06a")])
    sc.clouds(150, 760, "#2a2038", 9, .6, 1.2)
    sc.sun(820, 1085, 54)
    sc.hills(1110, 18, "#4a3340", .5)
    for _ in range(46):                                              # алыстағы хан ордасының оттары
        sc.glow(sc.rnd.uniform(560, 1060), sc.rnd.uniform(1118, 1170), sc.rnd.uniform(8, 16), "#ffb24a", .9)
    sc.haze(1150, 120, "#e89a5a", .4)
    sc.hills(1210, 22, "#2a1d26", .5)
    caravan(sc, "#150e12", 120, 1300, .62, 700, 1232, .2, 13, flip=True)
    f = sc.hills(1350, 50, "#0c080a", .45)
    sc.at(rider("#050304", "fur", gait=.1), 400, f(400) + 6, 2.7)
    sc.at(rider("#050304", "cap", gait=-.1), 660, f(660) + 6, 2.45)
    sc.particles(60, "#ffd9a0", 2.6, 950, 1450, .45, streak=22)
    sc.shade(1340)
    return sc


def s08():
    sc = Scene(8)
    sc.sky([(0, "#232c3a"), (.5, "#5d6c7e"), (.7, "#a9b6c2"), (1, "#a9b6c2")])
    sc.clouds(60, 700, "#1a212c", 12, .7, 1.4)
    sc.mountains(1000, 520, "#55657a", "#dfe8f0", 4)
    sc.haze(960, 260, "#b9c5d0", .55)
    sc.mountains(1130, 330, "#34414f", "#c9d5df", 5)
    sc.haze(1140, 180, "#aebbc7", .5)
    sc.hills(1210, 26, "#8d9aa8", .6)
    c = "#141a22"
    caravan(sc, c, 180, 1340, .95, 960, 1216, .16, 17, flip=False, kinds="pcrwpc")
    sc.at(rider(c, "fur", gait=.3), 300, 1378, 1.55, flip=True)
    sc.at(rider(c, "cap", gait=-.3), 130, 1392, 1.65, flip=True)
    sc.hills(1420, 16, "#dbe3ea", .4)
    sc.particles(420, "#ffffff", 3.2, 0, 1700, .8, streak=30)
    sc.add(f'<rect width="{W}" height="{H}" fill="#9fb4c8" opacity=".14"/>')
    sc.shade(1380, "#0c1118", .8)
    return sc


def s09():
    sc = Scene(9)
    sc.sky([(0, "#3d6f9e"), (.5, "#9cc3d8"), (.7, "#e9e2c4"), (1, "#e9e2c4")])
    sc.clouds(140, 560, "#ffffff", 7, .55)
    sc.mountains(1020, 480, "#6f8fa8", "#f4f7fa", 4)
    sc.haze(1000, 200, "#dfe6da", .5)
    sc.mountains(1120, 240, "#4f7068", None, 6)
    sc.hills(1180, 22, "#5d7a48", .6)
    sc.at(yurt("#e9dfc8", "#d2c2a0", "#3a2418", "#7a2f6a"), 850, 1215, 1.9)
    sc.at(yurt("#e9dfc8", "#d2c2a0", "#3a2418", "#7a2f6a"), 1010, 1200, 1.2)
    sc.at(flag("#2a1d18", "#6a2a7a", 300), 730, 1222, 1.0)
    f = sc.hills(1260, 14, "#3f5a30", .4)
    c = "#16110e"
    crowd(sc, c, 1296, 700, 1040, 2.1, 6, hats=("turban", "helm"), spears=.7)     # моғол сарбаздары
    crowd(sc, c, 1300, 40, 330, 2.0, 5, hats=("fur", "cap"))
    sc.at(horse(c), 150, 1330, 1.7)
    sc.at(man("#1c1020", "turban", w=1.5, robe="#3a1f4a"), 640, 1340, 3.3, flip=True)   # Есен-Бұқа
    sc.at(man(c, "fur", w=1.35, robe="#1c2a4a"), 430, 1342, 3.2)                        # Керей
    sc.at(man(c, "cap", w=1.2, robe="#1f3a2a"), 320, 1350, 3.0)                         # Жәнібек
    sc.add('<rect x="505" y="1232" width="46" height="26" rx="4" fill="#c8963c"/>')     # сый
    sc.hills(1400, 12, "#22331a", .4)
    sc.shade(1330, "#0a1208", .8)
    return sc


def s10():
    sc = Scene(10)
    sc.sky([(0, "#4a78a8"), (.42, "#e7b77a"), (.6, "#f7dc9c"), (1, "#f7dc9c")])
    sc.clouds(160, 620, "#fff0d0", 7, .55)
    sc.sun(230, 880, 56)
    sc.mountains(1010, 430, "#7d8fae", "#fff4e0", 4)
    sc.haze(1000, 220, "#f3d6a0", .55)
    sc.mountains(1100, 200, "#5f7d5c", None, 6)
    sc.hills(1150, 24, "#6f9448", .6)
    g = sc.gid()
    sc.defs.append(grad(g, [(0, "#fbe6b0"), (1, "#7fb0c8")]))
    sc.add(f'<path d="M620,1150 Q560,1200 700,1250 Q900,1310 600,1400 Q380,1470 520,1640 L860,1640 Q700,1480 900,1400 '
           f'Q1140,1300 800,1236 Q680,1200 660,1150 Z" fill="url(#{g})"/>')
    for x, y in ((120, 1200), (200, 1215), (300, 1196), (400, 1226), (90, 1245), (330, 1250), (960, 1196), (1010, 1212)):
        sc.at(sheep("#f4ecd8"), x, y, 1.0, flip=x % 2 == 0)
    for x, y in ((930, 1250), (1010, 1262)):
        sc.at(horse("#3a2a1c"), x, y, .55)
    sc.hills(1270, 14, "#4f7a34", .4, to=1300)
    for x, y, s in ((170, 1330, 1.7), (400, 1310, 1.25), (300, 1400, 2.2)):
        sc.at(yurt("#f6efe0", "#e3d6ba", "#3a2418", "#a8392a"), x, y, s)
        smoke(sc, x + 4, y - 112 * s, "#ffffff", .5)
    c = "#2a1d14"
    sc.at(man(c, "none", w=1.3, robe="#7a2a22"), 470, 1410, 1.8)
    fire(sc, 520, 1408, .9)
    for x, y in ((560, 1440), (600, 1452), (150, 1450)):               # ойнаған балалар
        sc.at(man(c, "none"), x, y, 1.1)
    sc.at(eagle("#2a1d14"), 760, 620, .8, rot=-8)
    sc.shade(1380, "#14200c", .8)
    return sc


def s11():
    sc = Scene(11)
    sc.sky([(0, "#3f6fa0"), (.45, "#f0b86a"), (.62, "#fbe0a0"), (1, "#fbe0a0")])
    sc.clouds(180, 700, "#fff2d6", 8, .55)
    sc.sun(540, 1010, 64)
    sc.hills(1090, 22, "#9a8a4a", .5)
    for x in (430, 500, 570, 640, 470, 610):
        sc.at(yurt("#f4ead4", "#dccba8", "#3a2418", "#a8392a"), x, 1118 + (x % 3) * 8, .5)
    sc.at(tug("#3a2a1c", 200), 540, 1110, .8)
    sc.haze(1130, 140, "#f6d490", .5)
    sc.hills(1190, 20, "#6a6a34", .5)
    c = "#1c140e"
    caravan(sc, c, 60, 1350, 1.25, 430, 1196, .3, 9, flip=False, kinds="rrcpr")
    caravan(sc, c, 1020, 1350, 1.25, 650, 1196, .3, 9, flip=True, kinds="rcrwp")
    sc.at(rider(c, "fur", tug=True, gait=.3), 230, 1380, 2.0)
    sc.at(rider(c, "cap", gait=-.3) + flag(c, "#3a6ea8", 250).replace('x1="0"', 'x1="12"').replace('x2="0"', 'x2="12"'),
          850, 1380, 2.0, flip=True)
    sc.hills(1400, 14, "#2a2a14", .4)
    sc.at(eagle("#1c140e"), 560, 520, 1.5, rot=6)
    sc.particles(50, "#fff0c0", 2.6, 900, 1450, .5, streak=18)
    sc.shade(1360, "#141008", .8)
    return sc


def s12():
    sc = Scene(12)
    sc.sky([(0, "#2f5f96"), (.4, "#f2b25a"), (.6, "#ffe6a0"), (1, "#ffe6a0")])
    for a in range(-80, 81, 16):                                       # күн сәулелері
        sc.add(f'<path d="M540,960 L{540 + 1900 * math.sin(math.radians(a - 3)):.0f},{960 - 1900 * math.cos(math.radians(a - 3)):.0f} '
               f'L{540 + 1900 * math.sin(math.radians(a + 3)):.0f},{960 - 1900 * math.cos(math.radians(a + 3)):.0f} Z" fill="#fff4c4" opacity=".16"/>')
    sc.sun(540, 960, 80)
    sc.clouds(200, 620, "#fff2d6", 6, .5)
    sc.hills(1110, 18, "#a08a48", .5)
    c0 = "#5a4426"
    crowd(sc, c0, 1140, 20, 1060, .7, 40, jitter=8, spears=.2)
    for x in (120, 300, 780, 960):
        sc.at(tug(c0, 200), x, 1140, .8)
    sc.haze(1150, 120, "#f8d894", .5)
    c = "#16100a"
    # төбе, ақ киіз және хан
    sc.add(f'<path d="M180,1420 Q540,1150 900,1420 Z" fill="{c}"/>')
    for x in (410, 470, 610, 670):
        sc.at(man(c, "fur" if x != 610 else "cap", w=1.2)
              + f'<line x1="0" y1="-44" x2="{14 if x < 540 else -14}" y2="-92" stroke="{c}" stroke-width="6" stroke-linecap="round"/>',
              x, 1300, 2.3, flip=x > 540)
    sc.add('<path d="M395,1085 Q540,1110 685,1085 L690,1104 Q540,1130 390,1104 Z" fill="#fbf6ea"/>')
    sc.at(man(c, "fur", w=1.5, robe="#1c2a4a"), 540, 1094, 2.6)
    sc.add('<path d="M523,925 L557,925 L556,915 L524,915 Z" fill="#e0aa48"/>')
    crowd(sc, c, 1392, 20, 330, 2.3, 6, jitter=14, spears=.3)
    crowd(sc, c, 1392, 750, 1060, 2.3, 6, jitter=14, spears=.3)
    for x, fl in ((90, False), (250, False), (830, True), (990, True)):
        sc.at(tug(c, 300), x, 1400, 1.5, flip=fl)
    sc.hills(1440, 12, "#0c0805", .3)
    sc.at(eagle("#16100a"), 540, 470, 1.9)
    sc.particles(50, "#fff4c4", 2.6, 700, 1400, .5)
    sc.shade(1380, "#0c0805", .85)
    return sc


if __name__ == "__main__":
    out = ROOT / "art"
    out.mkdir(exist_ok=True)
    for i, fn in enumerate([s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12], 1):
        (out / f"{i:02}.svg").write_text(fn().svg(), encoding="utf-8")
    print("12 svg ->", out)

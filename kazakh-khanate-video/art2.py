#!/usr/bin/env python3
"""2-бөлімнің 12 сахнасы -> art2/NN.svg  (содан кейін: node render.js art2 clips2)"""
import math
from art import (ROOT, W, H, Scene, grad, horse, man, rider, camel, yurt, cart, tug, flag,
                 eagle, fortress, sheep, fire, smoke, caravan, crowd)

WHITE = "#f4ecd8"


def seated(c, hat="fur", robe=None):
    return (f'<path d="M-17,0 L-10,-30 Q0,-39 10,-30 L17,0 Z" fill="{robe or c}"/>'
            f'<g transform="translate(0,15)">{man(c, hat, w=0)}</g>')


def kneel(c, hat="helm"):
    return (f'<path d="M-14,0 L-4,-26 Q8,-36 16,-22 L20,0 Z" fill="{c}"/>'
            f'<g transform="translate(14,26) rotate(28)">{man(c, hat, w=0)}</g>')


def kasym(c, robe="#7a1c1c", falcon=True):
    f = (f'<line x1="6" y1="-40" x2="30" y2="-48" stroke="{robe}" stroke-width="6" stroke-linecap="round"/>'
         f'<path d="M26,-50 Q30,-70 40,-66 L44,-60 L38,-58 Q40,-50 34,-48 Z" fill="{c}"/>') if falcon else ""
    return (man(c, "none", w=1.5, robe=robe) + f
            + f'<path d="M-9,-64 L11,-64 L6,-92 L-4,-92 Z" fill="{WHITE}"/><rect x="-9" y="-68" width="20" height="5" fill="#e0aa48"/>')


def kasym_rider(c, robe="#7a1c1c"):
    return (horse(c, .5) + f'<g transform="translate(0,-70)">{kasym(c, robe)}</g>'
            + f'<line x1="2" y1="-80" x2="9" y2="-48" stroke="{robe}" stroke-width="8" stroke-linecap="round"/>')


def yurt_frame(c):
    lat = "".join(f'<line x1="{x}" y1="0" x2="{x + 22}" y2="-46"/><line x1="{x + 22}" y1="0" x2="{x}" y2="-46"/>'
                  for x in range(-62, 50, 22))
    return (f'<g stroke="{c}" stroke-width="3" fill="none">{lat}'
            f'<path d="M-64,-46 Q-50,-96 0,-102 M-30,-46 Q-24,-90 0,-102 M0,-46 L0,-102"/></g>')


def camp(sc, n, y0, y1, s0, s1, x0=40, x1=1040, wall=WHITE, roof="#e3d6ba", band="#a8392a", door="#3a2418"):
    rows = max(2, n // 6)
    for r in range(rows):
        t = r / (rows - 1)
        y, s = y0 + (y1 - y0) * t, s0 + (s1 - s0) * t
        k = max(2, int(n / rows * (1.5 - t)))
        for i in range(k):
            x = x0 + (x1 - x0) * (i + sc.rnd.uniform(.1, .9)) / k
            sc.at(yurt(wall, roof, door, band), x, y + sc.rnd.uniform(-6, 6), s * sc.rnd.uniform(.85, 1.1))


def lightning(sc, x, y):
    sc.glow(x, y + 120, 260, "#cfd8ff", .35)
    sc.add(f'<path d="M{x},{y} L{x - 26},{y + 90} L{x + 4},{y + 96} L{x - 34},{y + 210} L{x - 8},{y + 216} L{x - 40},{y + 300}" '
           f'stroke="#f2f4ff" stroke-width="4" fill="none" stroke-linejoin="round"/>')


def s01():
    sc = Scene(21)
    sc.sky([(0, "#10131c"), (.35, "#3a3344"), (.54, "#c06a3c"), (.62, "#f0b060"), (1, "#f0b060")])
    sc.sun(210, 1090, 56)
    sc.clouds(60, 640, "#07080d", 12, .85, 1.5)
    for _ in range(9):                                                 # көкжиектегі дауыл
        x, y = sc.rnd.uniform(520, 1150), sc.rnd.uniform(640, 1040)
        sc.add(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{sc.rnd.uniform(220, 380):.0f}" ry="{sc.rnd.uniform(90, 150):.0f}" '
               f'fill="#0a0b12" opacity=".8" filter="url(#blur)"/>')
    lightning(sc, 860, 760)
    lightning(sc, 1000, 820)
    sc.hills(1120, 16, "#5a4038", .5)
    for _ in range(40):
        x = sc.rnd.uniform(560, 1080)
        sc.add(f'<line x1="{x:.0f}" y1="1000" x2="{x - 30:.0f}" y2="1120" stroke="#0a0b12" stroke-width="2" opacity=".35"/>')
    sc.hills(1230, 20, "#33241f", .5)
    camp(sc, 9, 1262, 1300, .34, .5, 430, 1040, "#d8c8a8", "#b8a584")
    for x in (520, 700, 880):
        sc.glow(x, 1296, 40, "#ffb35a", .8)
    c = "#0b0807"
    sc.add(f'<path d="M-20,1920 L-20,1210 Q120,1160 300,1180 L420,1200 Q470,1260 430,1330 Q380,1420 420,1560 L460,1920 Z" fill="{c}"/>')
    sc.at(man(c, "fur", w=1.5), 190, 1186, 3.4)
    sc.at(man(c, "cap", w=1.25), 330, 1192, 3.2)
    sc.hills(1480, 14, "#070505", .4)
    sc.particles(70, "#ffd9a0", 2.6, 900, 1450, .45, streak=26)
    sc.shade(1330)
    return sc


def s02():
    sc = Scene(22)
    sc.sky([(0, "#14121a"), (.4, "#3a2c30"), (.58, "#8a5a3c"), (.66, "#b98a5a"), (1, "#b98a5a")])
    sc.clouds(80, 760, "#0a090d", 13, .8, 1.4)
    sc.glow(540, 1020, 560, "#d9a060", .45)
    c = "#120d0c"
    f1 = sc.hills(1030, 22, "#4a3830", .5)                              # ойраттар — көкжиекте
    for i in range(13):
        x = 250 + i * 48 + sc.rnd.uniform(-10, 10)
        sc.at(rider("#241a17", "helm", spear=True), x, f1(x) + 3, .42, flip=i % 2 == 0)
    sc.haze(1050, 140, "#c99a6a", .45)
    f2 = sc.hills(1140, 30, "#33261f", .6)
    for i in range(6):                                                  # Әбілқайыр әскері — сол жақта
        x = 30 + i * 52
        sc.at(rider(c, "fur", spear=i % 2 == 0), x, f2(x) + 4, .8)
    sc.at(flag(c, "#8a1c16", 250), 110, f2(110), .9)
    sc.at(flag(c, "#8a1c16", 230), 250, f2(250), .8)
    for i in range(6):                                                  # Моғол әскері — оң жақта
        x = 1050 - i * 52
        sc.at(rider(c, "turban", spear=i % 2 == 1), x, f2(x) + 4, .8, flip=True)
    sc.at(flag(c, "#5a2a7a", 250), 970, f2(970), .9, flip=True)
    sc.at(flag(c, "#5a2a7a", 230), 830, f2(830), .8, flip=True)
    sc.haze(1180, 160, "#b98a5a", .4)
    sc.hills(1250, 16, "#241a15", .4)
    sc.glow(540, 1300, 300, "#ffb35a", .5)                              # ортадағы шағын қазақ ауылы
    for x, y, s in ((440, 1300, .9), (560, 1290, .75), (650, 1312, 1.0), (520, 1340, 1.15)):
        sc.at(yurt(WHITE, "#e3d6ba", "#3a2418", "#a8392a"), x, y, s)
    fire(sc, 600, 1345, .7)
    sc.at(tug(c, 200), 470, 1345, .7)
    sc.hills(1400, 12, "#0e0a08", .4)
    sc.particles(80, "#e8c8a0", 2.6, 900, 1450, .4, streak=30)
    sc.shade(1340)
    return sc


def s03():
    sc = Scene(23)
    sc.sky([(0, "#170b10"), (.4, "#4a1618"), (.58, "#a83a26"), (.66, "#d9803c"), (1, "#d9803c")])
    sc.clouds(100, 760, "#0e0609", 12, .8, 1.3)
    sc.sun(800, 1080, 64, "#ffd9a0", "#ff6a2a")
    f = sc.hills(1100, 20, "#2c1210", .5)
    c0 = "#1a0b0a"
    for i in range(14):                                                 # тоқтаған әскер
        x = 20 + i * 44 + sc.rnd.uniform(-8, 8)
        sc.at(rider(c0, "fur", spear=i % 3 == 0), x, f(x) + 3, .5, flip=True)
    for i in range(3):
        sc.at(camel(c0), 700 + i * 70, f(700 + i * 70) + 3, .5, flip=True)
    sc.haze(1140, 140, "#d9803c", .35)
    sc.hills(1220, 14, "#1c0c0b", .4)
    c = "#0c0505"
    # хан шатыры
    sc.add(f'<path d="M330,1300 L380,1130 Q540,1010 700,1130 L750,1300 Z" fill="{c}"/>'
           f'<path d="M380,1130 Q540,1090 700,1130 L698,1146 Q540,1106 382,1146 Z" fill="#b8862c"/>'
           f'<path d="M520,1022 L540,950 L560,1022 Z" fill="{c}"/>')
    g = sc.gid()
    sc.defs.append(grad(g, [(0, "#ffd9a0"), (.6, "#c8641c"), (1, "#4a160c")], radial=True))
    sc.add(f'<path d="M480,1300 L500,1180 Q540,1150 580,1180 L600,1300 Z" fill="url(#{g})"/>')
    sc.at(flag(c, "#7a1a14", 240), 300, 1300, 1.1, rot=-20)             # еңкейген ту
    for x, fl in ((180, False), (270, False), (400, False), (680, True), (800, True), (900, True)):
        sc.at(kneel(c), x, 1350 + (x % 3) * 8, 2.6, flip=fl)
    sc.at(horse(c), 960, 1330, 1.6, flip=True)
    sc.hills(1400, 10, "#070303", .3)
    sc.particles(60, "#ff9a5a", 2.4, 900, 1400, .45, streak=18)
    sc.shade(1330)
    return sc


def s04():
    sc = Scene(24)
    sc.sky([(0, "#2a3558"), (.4, "#8a6a7a"), (.56, "#eaa25a"), (.64, "#fbd78a"), (1, "#fbd78a")])
    sc.clouds(140, 700, "#3a3550", 8, .5, 1.2)
    sc.sun(820, 1040, 60)
    f0 = sc.hills(1100, 18, "#8a6a4a", .5)
    c0 = "#4a3626"
    for x in (60, 150, 250):                                            # тарап жатқан орда
        sc.at(yurt_frame(c0), x, f0(x) + 2, .7)
    sc.at(flag(c0, "#7a3a2a", 220, torn=True), 200, f0(200), .7, rot=-14)
    sc.at(flag(c0, "#7a3a2a", 220, torn=True), 330, f0(330), .6, rot=10)
    sc.haze(1130, 120, "#f6c880", .5)
    sc.hills(1200, 20, "#5a4430", .5)
    c = "#16100b"
    caravan(sc, "#2a1e15", 760, 1270, .7, 120, 1206, .16, 16, flip=False, kinds="rcpwrp")
    caravan(sc, c, 640, 1360, 1.0, 40, 1300, .5, 8, flip=False, kinds="prwc")
    sc.add(f'<path d="M560,1920 L600,1330 Q760,1150 960,1160 L1100,1180 L1100,1920 Z" fill="{c}"/>')
    sc.at(man(c, "fur", w=1.5), 860, 1166, 3.2, flip=True)
    sc.at(man(c, "cap", w=1.25), 980, 1170, 3.0, flip=True)
    sc.at(tug(c, 260), 760, 1196, 1.3)
    sc.hills(1460, 12, "#0a0705", .3)
    sc.particles(60, "#fff0c0", 2.6, 900, 1450, .45, streak=22)
    sc.shade(1360)
    return sc


def s05():
    sc = Scene(25)
    sc.sky([(0, "#4a7aac"), (.42, "#eab878"), (.6, "#f9dfa0"), (1, "#f9dfa0")])
    sc.clouds(160, 600, "#fff0d0", 7, .55)
    sc.sun(820, 860, 58)
    sc.mountains(1000, 440, "#7d8fae", "#fff4e0", 4)
    sc.haze(1000, 220, "#f3d6a0", .55)
    sc.mountains(1090, 190, "#5f7d5c", None, 6)
    sc.hills(1130, 18, "#7a9a4c", .6)
    camp(sc, 30, 1150, 1330, .3, 1.15)
    for x, y in ((90, 1210), (160, 1225), (980, 1200), (1030, 1220), (930, 1230), (60, 1250)):
        sc.at(sheep("#fbf4e2"), x, y, .9)
    c = "#2a1d14"
    sc.at(tug(c, 330), 540, 1330, 1.3)
    for i, x in enumerate((700, 790, 880)):                             # саудагерлер керуені
        sc.at(camel(c), x, 1400, 1.3, flip=True)
    sc.at(man(c, "turban", robe="#3a5a8a"), 960, 1402, 1.9, flip=True)
    sc.at(man(c, "fur", robe="#7a2a22"), 250, 1404, 1.9)
    sc.at(man(c, "none", robe="#3f6a3a"), 330, 1408, 1.7, flip=True)
    for x in (410, 450, 150):
        sc.at(man(c, "none"), x, 1420, 1.0)
    fire(sc, 380, 1404, .8)
    sc.at(eagle(c), 300, 600, .9, rot=8)
    sc.hills(1450, 10, "#2a3d1a", .3)
    sc.shade(1380, "#14200c", .8)
    return sc


def s06():
    sc = Scene(26)
    sc.sky([(0, "#1a1c3a"), (.4, "#5a4468"), (.56, "#c8785a"), (.64, "#f0b878"), (1, "#f0b878")])
    sc.stars(70, 520)
    sc.clouds(260, 760, "#3a2c4a", 7, .5, 1.2)
    sc.sun(540, 1030, 96, "#ffe9c0", "#ff9a5a")
    sc.hills(1090, 18, "#5a3f4a", .5)
    camp(sc, 14, 1120, 1190, .26, .42, 60, 1020, "#cbb9a0", "#a8957a")
    for _ in range(16):
        sc.glow(sc.rnd.uniform(60, 1020), sc.rnd.uniform(1120, 1190), 16, "#ffb35a", .9)
    sc.haze(1170, 140, "#e89a6a", .4)
    c = "#0b0709"
    sc.add(f'<path d="M-20,1920 L-20,1420 Q300,1380 540,1250 Q780,1380 1100,1420 L1100,1920 Z" fill="{c}"/>')
    sc.at(man(c, "fur", w=1.5) + f'<line x1="-14" y1="0" x2="-18" y2="-70" stroke="{c}" stroke-width="2.5"/>', 470, 1284, 3.3)
    sc.at(man(c, "cap", w=1.3) + f'<line x1="14" y1="0" x2="18" y2="-66" stroke="{c}" stroke-width="2.5"/>', 620, 1284, 3.1, flip=True)
    sc.at(eagle(c), 760, 560, 1.3, rot=-8)
    sc.particles(40, "#ffe0b0", 2.4, 900, 1400, .4)
    sc.shade(1380)
    return sc


def s07():
    sc = Scene(27)
    g = sc.gid()
    sc.defs.append(grad(g, [(0, "#7a3a14"), (.5, "#3a180c"), (1, "#0e0605")], radial=True))
    sc.add(f'<rect width="{W}" height="{H}" fill="#0e0605"/><ellipse cx="540" cy="1000" rx="900" ry="900" fill="url(#{g})"/>')
    # киіз үй іші: уықтар мен кереге
    for a in range(-70, 71, 10):
        x = 540 + 900 * math.sin(math.radians(a))
        sc.add(f'<line x1="540" y1="160" x2="{x:.0f}" y2="820" stroke="#1a0b06" stroke-width="7" opacity=".8"/>')
    sc.add('<circle cx="540" cy="160" r="70" fill="#1c2238"/><circle cx="540" cy="160" r="70" fill="none" stroke="#1a0b06" stroke-width="12"/>')
    for x in range(-60, 1140, 60):
        sc.add(f'<line x1="{x}" y1="820" x2="{x + 120}" y2="1120" stroke="#1a0b06" stroke-width="5" opacity=".8"/>'
               f'<line x1="{x + 120}" y1="820" x2="{x}" y2="1120" stroke="#1a0b06" stroke-width="5" opacity=".8"/>')
    sc.add('<rect y="810" width="1080" height="16" fill="#8a2a1c"/>')
    # қабырғадағы көлеңкелер
    sc.add('<g fill="#080303" opacity=".5" filter="url(#blur)"><path d="M120,1120 L160,760 Q230,700 300,760 L340,1120 Z"/>'
           '<path d="M740,1120 L780,740 Q850,680 920,740 L960,1120 Z"/></g>')
    sc.add('<rect y="1120" width="1080" height="800" fill="#1c0c08"/><ellipse cx="540" cy="1330" rx="470" ry="120" fill="#5a1c16"/>'
           '<ellipse cx="540" cy="1330" rx="470" ry="120" fill="none" stroke="#b8862c" stroke-width="5"/>')
    sc.glow(540, 1150, 420, "#ffa040", .5)
    c = "#0a0504"
    sc.add(f'<g fill="{c}"><rect x="455" y="1060" width="170" height="150"/><path d="M445,1060 L465,950 L615,950 L635,1060 Z"/></g>')
    sc.at(seated(c, "fur", "#5a1414"), 540, 1215, 4.6)                 # Бұрындық хан
    for x, fl, h in ((160, False, "fur"), (270, False, "cap"), (350, False, "fur"), (730, True, "fur"), (810, True, "cap"), (920, True, "fur")):
        arm = f'<line x1="6" y1="-40" x2="26" y2="-62" stroke="{c}" stroke-width="5" stroke-linecap="round"/>'
        sc.at(man(c, h, w=1.3) + arm, x, 1370 + abs(540 - x) * .05, 3.3, flip=fl)
    fire(sc, 80, 1180, 1.2)
    fire(sc, 1000, 1180, 1.2)
    sc.particles(30, "#ffb45a", 2.2, 700, 1200, .7)
    sc.shade(1340)
    return sc


def s08():
    sc = Scene(28)
    sc.sky([(0, "#1c2026"), (.5, "#4a525a"), (.68, "#8d9296"), (1, "#8d9296")])
    sc.clouds(60, 900, "#101317", 16, .8, 1.5)
    f = sc.hills(1090, 16, "#555a5c", .5)
    for i in range(11):                                                 # көкжиекте жиналған жау
        x = 300 + i * 46 + sc.rnd.uniform(-10, 10)
        sc.at(rider("#22262a", "helm", spear=True), x, f(x) + 3, .36, flip=i % 2 == 0)
    sc.haze(1110, 140, "#9aa0a4", .5)
    sc.hills(1190, 16, "#3c4042", .5)
    c = "#121416"
    caravan(sc, "#24282b", 60, 1270, .7, 430, 1200, .25, 7, flip=True, kinds="rwcp")     # солға кеткендер
    caravan(sc, "#24282b", 1020, 1270, .7, 650, 1200, .25, 7, flip=False, kinds="rcwp")  # оңға кеткендер
    sc.hills(1290, 12, "#26292b", .4)
    sc.at(yurt_frame(c), 380, 1360, 1.6)
    sc.at(yurt("#3a3d40", "#44484b", "#0c0d0e", "#2a2c2e"), 720, 1356, 1.4)
    sc.at(flag(c, "#3d4245", 300, torn=True), 540, 1370, 1.2, rot=6)
    sc.at(tug(c, 260), 250, 1372, 1.1, rot=-16)
    sc.at(cart(c), 900, 1380, 1.3, rot=8)
    sc.hills(1410, 10, "#0d0e10", .3)
    sc.particles(110, "#d0d4d8", 2.6, 700, 1500, .4, streak=34)
    sc.shade(1340, "#06080a", .8)
    return sc


def s09():
    sc = Scene(29)
    sc.sky([(0, "#2c3f6e"), (.4, "#a8708a"), (.56, "#f2a25a"), (.64, "#ffdc90"), (1, "#ffdc90")])
    for a in range(-80, 81, 20):
        sc.add(f'<path d="M540,1060 L{540 + 1900 * math.sin(math.radians(a - 3)):.0f},{1060 - 1900 * math.cos(math.radians(a - 3)):.0f} '
               f'L{540 + 1900 * math.sin(math.radians(a + 3)):.0f},{1060 - 1900 * math.cos(math.radians(a + 3)):.0f} Z" fill="#fff4c4" opacity=".12"/>')
    sc.sun(540, 1060, 74)
    sc.clouds(200, 700, "#4a3a5a", 6, .4, 1.2)
    sc.hills(1110, 16, "#9a7a4a", .5)
    c0 = "#3a2a1c"
    for i in range(16):
        x = 40 + i * 66 + sc.rnd.uniform(-10, 10)
        sc.at(rider(c0, sc.rnd.choice(["fur", "cap"]), spear=i % 3 == 0, tug=i % 5 == 2, gait=sc.rnd.uniform(.3, .9)),
              x, 1150 + sc.rnd.uniform(-8, 8), .55, flip=x > 540)
    sc.haze(1160, 140, "#f8cc80", .5)
    sc.hills(1230, 16, "#5a4426", .5)
    c = "#120c08"
    for i, x in enumerate((90, 250, 830, 990)):
        sc.at(rider(c, "fur" if i % 2 else "cap", tug=i in (0, 3), spear=i in (1, 2), gait=.7), x, 1330 + (i % 2) * 14, 1.5, flip=x > 540)
    sc.hills(1380, 14, "#1c140c", .4)
    sc.at(kasym_rider("#0a0705"), 540, 1440, 3.3)
    sc.at(eagle(c), 300, 520, 1.2, rot=10)
    sc.particles(70, "#fff0c0", 2.8, 900, 1500, .45, streak=24)
    sc.shade(1400, "#0c0805", .85)
    return sc


def s10():
    sc = Scene(30)
    sc.sky([(0, "#2a1f2c"), (.4, "#8a3f2a"), (.58, "#e8893c"), (.66, "#f8c06a"), (1, "#f8c06a")])
    sc.clouds(100, 800, "#1a1016", 11, .7, 1.4)
    sc.sun(260, 1060, 70, "#ffe4b0", "#ff8a3a")
    f = sc.hills(1090, 16, "#6a4428", .5)
    for i in range(8):                                                  # қашқан жау
        x = 700 + i * 48
        sc.at(rider("#3a2416", "helm", gait=1), x, f(x) + 3, .36 - i * .015)
    sc.haze(1130, 180, "#f0a85a", .55)
    sc.hills(1210, 18, "#4a2e1a", .5)
    c1 = "#22140c"
    cloths = ["#2f6fb0", "#a8392a", "#e0aa48", "#3f7a4a", "#f4ecd8"]
    for i in range(9):
        x = 40 + i * 118 + sc.rnd.uniform(-14, 14)
        sh = rider(c1, sc.rnd.choice(["fur", "cap"]), spear=i % 2 == 0, gait=sc.rnd.uniform(.6, 1))
        if i % 2:
            sh += f'<g transform="translate(12,-92)">{flag(c1, cloths[i % 5], 120)}</g>'
        sc.at(sh, x, 1270 + sc.rnd.uniform(-12, 12), .95, rot=4)
    sc.haze(1290, 160, "#d98a4a", .5)
    c = "#0e0805"
    for i in range(5):
        x = 60 + i * 215
        sh = rider(c, ["fur", "cap"][i % 2], spear=i % 2 == 1, tug=i == 3, gait=1)
        if i in (0, 4):
            sh += f'<g transform="translate(12,-92)">{flag(c, cloths[i % 5 + 0], 130)}</g>'
        sc.at(sh, x, 1420 + (i % 2) * 18, 2.0, rot=5)
    sc.at(kasym_rider("#070403"), 520, 1400, 2.7, rot=4)
    sc.particles(140, "#f8d090", 3.2, 1000, 1600, .5, streak=40)
    sc.shade(1390)
    return sc


def s11():
    sc = Scene(31)
    sc.sky([(0, "#3f73a8"), (.5, "#a8cbe0"), (.68, "#f0e6c0"), (1, "#f0e6c0")])
    sc.clouds(140, 620, "#ffffff", 8, .55)
    sc.mountains(1040, 360, "#7f9ab4", "#f6f8fa", 4)
    sc.haze(1040, 180, "#e6e6cc", .5)
    sc.hills(1110, 18, "#7a9a4c", .5)
    camp(sc, 10, 1140, 1180, .5, .7)
    c = "#1c140e"
    for x, cl in ((90, "#2f6fb0"), (990, "#a8392a")):
        sc.at(flag(c, cl, 300), x, 1200, 1.1, flip=x > 540)
    sc.at(tug(c, 300), 300, 1196, 1.0)
    sc.at(tug(c, 300), 780, 1196, 1.0, flip=True)
    sc.hills(1210, 12, "#5f8238", .4)
    # билер кеңесі — шеңбер
    robes = ["#22303f", "#3a2a1c", "#2c3a26", "#3a2030", "#33291a"]
    back = [(540 + 400 * math.cos(math.radians(a)), 1330 + 90 * math.sin(math.radians(a))) for a in range(200, 341, 20)]
    for i, (x, y) in enumerate(back):
        if abs(x - 540) > 90:
            sc.at(seated(c, ["fur", "cap", "fur"][i % 3], robes[i % 5]), x, y, 2.4, flip=x > 540)
    sc.add('<ellipse cx="540" cy="1290" rx="120" ry="26" fill="#fbf6ea"/>')
    sc.at(seated(c, "none", "#7a1c1c"), 540, 1292, 4.2)                # Қасым хан
    sc.add(f'<path d="M514,1088 L568,1088 L556,1018 L528,1018 Z" fill="{WHITE}"/><rect x="514" y="1080" width="54" height="12" fill="#e0aa48"/>')
    front = [(540 + 430 * math.cos(math.radians(a)), 1350 + 110 * math.sin(math.radians(a))) for a in range(15, 166, 25)]
    for i, (x, y) in enumerate(front):
        sc.at(seated("#0e0a07", ["cap", "fur", "fur"][i % 3]), x, y, 3.0, flip=x > 540)
    sc.at(eagle(c), 700, 520, 1.3, rot=-6)
    sc.shade(1400, "#0a1208", .85)
    return sc


def s12():
    sc = Scene(32)
    sc.sky([(0, "#2f5f96"), (.4, "#f2b25a"), (.6, "#ffe6a0"), (1, "#ffe6a0")])
    for a in range(-80, 81, 16):
        sc.add(f'<path d="M700,980 L{700 + 1900 * math.sin(math.radians(a - 3)):.0f},{980 - 1900 * math.cos(math.radians(a - 3)):.0f} '
               f'L{700 + 1900 * math.sin(math.radians(a + 3)):.0f},{980 - 1900 * math.cos(math.radians(a + 3)):.0f} Z" fill="#fff4c4" opacity=".15"/>')
    sc.sun(700, 980, 80)
    sc.clouds(200, 620, "#fff2d6", 6, .5)
    sc.mountains(1060, 220, "#b89a6a", "#fff4dc", 5)
    sc.haze(1060, 160, "#fbe0a0", .6)
    sc.hills(1100, 14, "#a89250", .5)
    camp(sc, 48, 1112, 1300, .16, .8, 300, 1070, "#f6ecd2", "#dcc9a0")
    c0 = "#3a2a18"
    for i in range(18):
        x = 320 + i * 42
        sc.at(rider(c0, "fur", tug=i % 4 == 0, spear=i % 4 == 2), x, 1330 + sc.rnd.uniform(-6, 6), .5, flip=i % 2 == 0)
    for x, y in ((420, 1220), (480, 1236), (900, 1210), (960, 1228), (700, 1250), (760, 1262)):
        sc.at(sheep("#fbf4e2"), x, y, .7)
    sc.haze(1330, 120, "#f8d894", .35)
    c = "#120c07"
    sc.add(f'<path d="M-20,1920 L-20,1250 Q140,1200 330,1240 Q440,1280 470,1400 L520,1920 Z" fill="{c}"/>')
    sc.at(kasym(c), 200, 1232, 4.2)
    sc.at(tug(c, 330), 60, 1250, 1.5)
    crowd(sc, c, 1440, 520, 1060, 2.0, 8, jitter=12, spears=.4)
    sc.at(eagle(c), 520, 450, 2.0, rot=-4)
    sc.particles(50, "#fff4c4", 2.6, 700, 1400, .5)
    sc.shade(1400, "#0c0805", .85)
    return sc


if __name__ == "__main__":
    out = ROOT / "art2"
    out.mkdir(exist_ok=True)
    for i, fn in enumerate([s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12], 1):
        (out / f"{i:02}.svg").write_text(fn().svg(), encoding="utf-8")
    print("12 svg ->", out)

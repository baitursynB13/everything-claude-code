#!/usr/bin/env python3
"""Озвучкадағы фразалардың нақты уақыты (үзілістер + сөйлеуді тану арқылы табылған)
бойынша әр субтитр жолының уақытын есептеп, timings.json жазады.

GROUPS: (басы, соңы, осы аралықта айтылатын субтитр жолдарының саны).
Жолдар build.SCENES ретімен алынады; аралық ішінде әріп санына қарай бөлінеді.
"""
import json
import re
from build import SCENES, ROOT

DURATION = 89.234
GROUPS = [
    (0.18, 1.94, 1), (2.53, 4.64, 2), (4.98, 6.67, 2), (7.20, 9.60, 2), (10.05, 10.87, 1),
    (11.24, 12.20, 1), (12.53, 14.25, 2), (14.62, 16.08, 1),
    (16.53, 18.45, 2), (18.71, 20.18, 2), (20.33, 23.42, 3),
    (23.73, 26.46, 3), (26.71, 29.74, 3), (29.90, 30.83, 1),
    (31.20, 32.62, 1), (32.85, 34.42, 1), (34.86, 36.79, 2), (37.10, 37.93, 1), (38.13, 39.19, 1),
    (39.48, 44.03, 4), (44.33, 45.53, 1), (45.82, 47.31, 1),
    (47.68, 50.04, 2), (50.34, 52.66, 3),
    (53.25, 55.05, 1), (55.21, 55.83, 1), (56.09, 57.81, 1), (58.09, 58.87, 1), (58.99, 60.86, 2),
    (61.14, 63.54, 2), (63.72, 65.07, 1), (65.24, 67.46, 2),
    (67.73, 72.55, 5), (72.84, 74.94, 1),
    (75.20, 76.88, 2), (77.02, 78.51, 1), (78.63, 80.42, 2),
    (80.61, 85.05, 3), (85.19, 85.98, 1), (86.28, 87.78, 1), (87.94, 88.87, 1),
]
SPOKEN = {"XV": "он бесінші", "1457": "мың төрт жүз елу жетінші",
          "1465": "мың төрт жүз алпыс бесінші"}


def weight(text):
    for k, v in SPOKEN.items():
        text = text.replace(k, v)
    return len(re.sub(r"[^\w]", "", text)) + 1.0


import importlib
import sys
PART = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] != "1" else ""
if PART:
    _m = importlib.import_module(f"script{PART}")
    SCENES, GROUPS, DURATION, SPOKEN = _m.SCENES, _m.GROUPS, _m.DURATION, _m.SPOKEN
cues = [t for _, lines in SCENES for t, _ in lines]
assert sum(g[2] for g in GROUPS) == len(cues), (sum(g[2] for g in GROUPS), len(cues))
out, k = [], 0
for a, b, n in GROUPS:
    part = cues[k:k + n]
    tot, acc = sum(map(weight, part)), 0.0
    for text in part:
        s = a + acc / tot * (b - a)
        acc += weight(text)
        out.append([round(s, 3), round(a + acc / tot * (b - a), 3), text])
    k += n
# қысқа үзілісте субтитр жыпылықтамасын: келесі жолға дейін ұстап тұру
for i in range(len(out) - 1):
    if out[i + 1][0] - out[i][1] < 0.4:
        out[i][1] = out[i + 1][0]
(ROOT / f"timings{PART}.json").write_text(
    json.dumps({"duration": DURATION, "cues": out}, ensure_ascii=False, indent=1) + "\n",
    encoding="utf-8")
print(len(out), "cues ->", ROOT / f"timings{PART}.json")

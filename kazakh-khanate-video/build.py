#!/usr/bin/env python3
"""Қазақ хандығы, 1-бөлім: субтитр (SRT/ASS) және 9:16 видео жинау.

Қолдану:
    python3 build.py                 # субтитр + видео (out/)
    python3 build.py --audio vo.mp3  # озвучканы қосып, ұзындығын соған келтіру

Фон: clips/01.mp4 ... clips/12.mp4 (немесе .png/.jpg) болса соны алады,
болмаса сахна нөмірі жазылған қара фон қояды.
"""
import argparse
import importlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
CLIPS = ROOT / "clips"
W, H, FPS = 1080, 1920, 30
CPS = 13.5          # оқу жылдамдығы, таңба/сек (озвучка келгенше болжам)
MIN_DUR = 0.9
P = 0.6             # [pause]

# (сахна атауы, [(субтитр жолы, кейінгі пауза сек)])
SCENES = [
    ("Хук", [
        ("Олар босқындар еді.", P),
        ("Тұтас халық", 0), ("қатыгез хандан құтылып,", 0),
        ("еркін болу үшін", 0), ("жолға шықты.", P),
        ("Қазақ хандығы", 0), ("осылай дүниеге келді.", 0.3),
        ("Бірінші бөлім.", 0.5),
    ]),
    ("Алтын Орда", [
        ("XV ғасыр.", 0.3), ("Алтын Орда", 0), ("быраңдап ыдырады.", 0.3),
        ("Дала бір биліксіз қалды.", 0.4),
    ]),
    ("Әбілқайыр хан", [
        ("Сібірде Әбілқайыр хан", 0), ("көтерілді.", 0.2),
        ("Он жеті жасында", 0), ("билікке келіп,", 0),
        ("астанасы Тура болған", 0), ("Көшпелі өзбек хандығын", 0),
        ("құрды.", 0.4),
    ]),
    ("Қарсылық", [
        ("Бірақ далада", 0), ("басқа Шыңғыс тұқымдары да", 0), ("болды.", 0.2),
        ("Орыс ханның ұрпақтары", 0), ("өздерін заңды билеушіміз", 0),
        ("деп санап,", 0), ("бағынғысы келмеді.", 0.4),
    ]),
    ("Қатыгездік", [
        ("Әбілқайыр күшті еді,", 0), ("бірақ қатыгез болды.", 0.3),
        ("Халық қорқыныш ішінде", 0), ("өмір сүрді,", 0),
        ("ал сұлтандар", 0), ("кету сәтін күтті.", 0.4),
    ]),
    ("Сығанақ шайқасы", [
        ("1457 жылы ойраттар", 0), ("Сығанақ түбінде", 0),
        ("Әбілқайырдың әскерін", 0), ("талқандады!", P),
        ("Оның даңқы құлады,", 0), ("халық қорғансыз қалды.", 0.4),
    ]),
    ("Шешім", [
        ("Сонда Керей мен Жәнібек", 0), ("шешім қабылдады.", P),
        ("Олар халықты", 0), ("хан билігінен", 0), ("алыс алып кетті.", 0.4),
    ]),
    ("Ұзақ жол", [
        ("Бұл ұзақ әрі қауіпті", 0), ("жол болды.", 0.2),
        ("Олар отбасымен, малымен,", 0), ("киіз үйімен", 0),
        ("алда не күтіп тұрғанын", 0), ("білмей жүрді.", 0.4),
    ]),
    ("Есен-Бұқа хан", [
        ("Моғолстанда Есен-Бұқа", 0), ("билік құрып тұрған.", 0.2),
        ("Оған одақтастар керек еді,", 0), ("сондықтан босқындарға", 0),
        ("қалуға рұқсат берді.", 0.4),
    ]),
    ("Шу мен Қозыбасы", [
        ("Олар қазіргі", 0), ("Қазақстан жеріндегі", 0),
        ("Шу мен Қозыбасы", 0), ("өзендерінің аңғарына", 0),
        ("қоныстанды.", 0.3), ("Осында жаңа өмір басталды.", 0.4),
    ]),
    ("«Қазақ»", [
        ("Адамдар оларға", 0), ("мыңдап келді!", 0.2),
        ("Оларды «қазақ» деп атады,", 0), ("яғни «еркін»", 0),
        ("деген мағынада.", 0.4),
    ]),
    ("Финал", [
        ("Шамамен 1465 жылы", 0), ("жаңа мемлекет пайда болып,", 0),
        ("оның тұңғыш ханы", 0), ("Керей болды!", P),
        ("Қазақ хандығының тарихы", 0), ("осылай басталды.", 1.2),
    ]),
]


def timeline(scale=1.0):
    """-> (cues [(start, end, text)], scenes [(start, end, title)])"""
    cues, scenes, t = [], [], 0.0
    for title, lines in SCENES:
        s0 = t
        for text, pause in lines:
            d = max(MIN_DUR, len(text) / CPS) * scale
            cues.append((t, t + d, text))
            t += d + pause * scale
        scenes.append((s0, t, title))
    return cues, scenes


def timeline_from_file(path, total):
    """timings.json (align.py) -> нақты озвучкаға байланған уақыттар."""
    data = json.loads(path.read_text(encoding="utf-8"))["cues"]
    cues = [tuple(c) for c in data]
    scenes, k, start = [], 0, 0.0
    for n, (title, lines) in enumerate(SCENES):
        k += len(lines)
        # сахна келесі сахнаның бірінші сөзінен сәл бұрын ауысады
        end = total if n == len(SCENES) - 1 else max(cues[k - 1][1], cues[k][0] - 0.15)
        scenes.append((start, end, title))
        start = end
    return cues, scenes


def ts(t, sep=","):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    if sep == ",":
        return f"{h:02}:{m:02}:{s:02},{ms:03}"
    return f"{h}:{m:02}:{s:02}.{ms // 10:02}"


def write_srt(cues, path):
    path.write_text("".join(
        f"{i}\n{ts(a)} --> {ts(b)}\n{text}\n\n"
        for i, (a, b, text) in enumerate(cues, 1)), encoding="utf-8")


def write_ass(cues, scenes, path, labels):
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,DejaVu Sans,68,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,6,3,2,50,50,400,1
Style: Label,DejaVu Sans,40,&H0080C8F0,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,0,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    if labels:
        for i, (a, b, title) in enumerate(scenes, 1):
            ev.append(f"Dialogue: 0,{ts(a, '.')},{ts(b, '.')},Label,,0,0,0,,"
                      f"{i:02}\\N{title}")
    for a, b, text in cues:
        # жеңіл «pop» анимациясы
        fx = r"{\fad(60,40)\fscx92\fscy92\t(0,90,\fscx100\fscy100)}"
        ev.append(f"Dialogue: 1,{ts(a, '.')},{ts(b, '.')},Sub,,0,0,0,,{fx}{text}")
    path.write_text(head + "\n".join(ev) + "\n", encoding="utf-8")


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"ffmpeg error:\n{r.stderr[-2000:]}")


def find_clip(i):
    for ext in ("mp4", "mov", "webm", "png", "jpg", "jpeg", "webp"):
        p = CLIPS / f"{i:02}.{ext}"
        if p.exists():
            return p
    return None


def render_scene(i, dur, dst):
    clip = find_clip(i)
    n = max(1, round(dur * FPS))
    fit = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    enc = ["-frames:v", str(n), "-r", str(FPS), "-an", "-c:v", "libx264",
           "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", str(dst)]
    if clip is None:
        shade = ["0x1a1410", "0x141a1f"][i % 2]
        run(["ffmpeg", "-y", "-f", "lavfi", "-i",
             f"color=c={shade}:s={W}x{H}:r={FPS}", "-vf", "vignette"] + enc)
    elif clip.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):
        zexpr = f"1+0.14*on/{n}" if i % 2 else f"1.14-0.14*on/{n}"
        zoom = (f"scale={W * 2}:{H * 2}:force_original_aspect_ratio=increase,"
                f"crop={W * 2}:{H * 2},zoompan=z='{zexpr}':d={n}:"
                f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}")
        run(["ffmpeg", "-y", "-i", str(clip), "-vf", zoom] + enc)
    else:
        run(["ffmpeg", "-y", "-stream_loop", "-1", "-i", str(clip),
             "-vf", f"{fit},fps={FPS}"] + enc)
    return clip is not None


def audio_len(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", help="озвучка файлы (mp3/wav)")
    ap.add_argument("--part", type=int, default=1, help="бөлім нөмірі (2+ -> scriptN.py, clipsN/)")
    args = ap.parse_args()
    global SCENES, CLIPS
    sfx = "" if args.part == 1 else str(args.part)
    if sfx:
        SCENES = importlib.import_module(f"script{sfx}").SCENES
        CLIPS = ROOT / f"clips{sfx}"
    OUT.mkdir(exist_ok=True)
    tmp = OUT / "tmp"
    tmp.mkdir(exist_ok=True)

    tfile = ROOT / f"timings{sfx}.json"
    if args.audio and tfile.exists():
        cues, scenes = timeline_from_file(tfile, audio_len(args.audio))
    elif args.audio:
        cues, scenes = timeline(audio_len(args.audio) / timeline()[1][-1][1])
    else:
        cues, scenes = timeline()

    parts, have = [], 0
    for i, (a, b, _) in enumerate(scenes, 1):
        dst = tmp / f"s{i:02}.mp4"
        have += render_scene(i, b - a, dst)
        parts.append(dst)
    labels = have < len(scenes)

    write_srt(cues, OUT / f"subtitles{sfx}.srt")
    ass = OUT / f"subtitles{sfx}.ass"
    write_ass(cues, scenes, ass, labels)

    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst)]
    if args.audio:
        cmd += ["-i", args.audio]
    cmd += ["-vf", f"ass={ass}", "-c:v", "libx264",
            "-preset", "medium", "-crf", "23", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart"]
    cmd += ["-c:a", "aac", "-b:a", "192k"] if args.audio else ["-an"]
    final = OUT / f"kazakh-khanate-part{args.part}.mp4"
    run(cmd + [str(final)])
    for p in tmp.iterdir():
        p.unlink()
    tmp.rmdir()
    print(f"{final}  {scenes[-1][1]:.1f}s  cues={len(cues)}  clips={have}/{len(scenes)}")


if __name__ == "__main__":
    main()

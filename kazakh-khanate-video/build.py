#!/usr/bin/env python3
"""Қазақ хандығы, 1-бөлім: субтитр (SRT/ASS) және 9:16 видео жинау.

Қолдану:
    python3 build.py                 # субтитр + видео (out/)
    python3 build.py --audio vo.mp3  # озвучканы қосып, ұзындығын соған келтіру

Фон: clips/01.mp4 ... clips/12.mp4 (немесе .png/.jpg) болса соны алады,
болмаса сахна нөмірі жазылған қара фон қояды.
"""
import argparse
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
Style: Sub,DejaVu Sans,74,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,6,3,2,70,70,520,1
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
        zoom = (f"scale={W * 2}:{H * 2}:force_original_aspect_ratio=increase,"
                f"crop={W * 2}:{H * 2},zoompan=z='1+0.12*on/{n}':d={n}:"
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
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    tmp = OUT / "tmp"
    tmp.mkdir(exist_ok=True)

    scale = 1.0
    if args.audio:
        scale = audio_len(args.audio) / timeline()[1][-1][1]
    cues, scenes = timeline(scale)

    parts, have = [], 0
    for i, (a, b, _) in enumerate(scenes, 1):
        dst = tmp / f"s{i:02}.mp4"
        have += render_scene(i, b - a, dst)
        parts.append(dst)
    labels = have < len(scenes)

    write_srt(cues, OUT / "subtitles.srt")
    write_ass(cues, scenes, OUT / "subtitles.ass", labels)

    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst)]
    if args.audio:
        cmd += ["-i", args.audio]
    cmd += ["-vf", f"ass={OUT / 'subtitles.ass'}", "-c:v", "libx264",
            "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart"]
    cmd += ["-c:a", "aac", "-b:a", "192k", "-shortest"] if args.audio else ["-an"]
    final = OUT / "kazakh-khanate-part1.mp4"
    run(cmd + [str(final)])
    for p in tmp.iterdir():
        p.unlink()
    tmp.rmdir()
    print(f"{final}  {scenes[-1][1]:.1f}s  cues={len(cues)}  clips={have}/12")


if __name__ == "__main__":
    main()

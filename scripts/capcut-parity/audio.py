"""CapCut's voice filters and characters that Concat lacked, as FFmpeg
chains, with their fixtures computed the way the template engine renders
them. Run directly: python audio.py <packages-dir>."""
import os
import sys

LEDGER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated.txt")


def fixed(x, n):
    return f"{x:.{n}f}"


def pitch_chain(st, extra):
    ratio = 2 ** (st / 12)
    return f"aresample=48000,asetrate={fixed(48000 * ratio, 6)},aresample=48000,atempo={fixed(1 / ratio, 8)}" + (("," + extra) if extra else "") + ",alimiter=limit=0.94"


PITCH_TEMPLATE = "aresample=48000,asetrate={fixed(48000 * ratio, 6)},aresample=48000,atempo={fixed(1 / ratio, 8)}"

# slug, name, category, description, pitch (min, max, default) or None, extra chain (fixed), knob for non-pitch
VOICES = [
    ("fussy-male", "Fussy male", "Character", "A fussy, nasal low voice.", (-6, -1, -3), "equalizer=f=1200:t=q:w=1.5:g=5,highpass=f=150"),
    ("bestie", "Bestie", "Character", "A bright, chirpy higher voice.", (1, 6, 3), "equalizer=f=3500:t=q:w=1:g=3"),
    ("queen", "Queen", "Character", "A higher, regal voice with a touch of hall.", (1, 5, 2), "aecho=0.8:0.7:60:0.25"),
    ("squirrel", "Squirrel", "Character", "A tiny, very high, quick voice.", (6, 12, 9), "highpass=f=200"),
    ("trickster", "Trickster", "Character", "A sly, wavering high voice.", (2, 8, 5), "vibrato=f=6:d=0.25"),
    ("elf", "Elf", "Character", "A high, airy voice that shimmers.", (3, 9, 6), "chorus=0.6:0.8:40:0.4:0.3:2"),
    ("elfy", "Elfy", "Character", "A light, slightly higher voice.", (2, 6, 4), "equalizer=f=4000:t=q:w=1:g=2"),
    ("santa", "Santa", "Character", "A deep, warm, jolly voice with a little room.", (-7, -2, -4), "equalizer=f=150:t=q:w=1:g=4,aecho=0.8:0.6:40:0.2"),
    ("jessie", "Jessie", "Character", "A slightly higher, bright voice.", (1, 4, 2), "equalizer=f=2500:t=q:w=1:g=2"),
    ("good-guy", "Good Guy", "Character", "A slightly deeper, warm voice.", (-4, -1, -2), "equalizer=f=200:t=q:w=1:g=3"),
    ("low", "Low", "Voice", "The voice pitched down and darkened.", (-8, -2, -5), "lowpass=f=3500"),
    ("high", "High", "Voice", "The voice pitched up and brightened.", (2, 8, 4), "highpass=f=180"),
]

# slug, name, category, description, (key, label, min, max, default, step, unit), let, chain template, chain(value)
FILTERS = [
    ("big-house", "Big House", "Space", "The voice in a big, echoing house.",
     ("size", "Size", 1, 10, 6, 0.5, ""),
     "aecho=0.8:0.85:{round(40 + size * 12)}|{round(70 + size * 18)}:0.4|0.3,alimiter=limit=0.94",
     lambda v: f"aecho=0.8:0.85:{round(40 + v * 12)}|{round(70 + v * 18)}:0.4|0.3,alimiter=limit=0.94"),
    ("energetic", "Energetic", "Voice", "A punchy, bright, upfront voice.",
     ("drive", "Drive", 1, 10, 5, 0.5, ""),
     "equalizer=f=3000:t=q:w=1:g={fixed(drive * 0.8, 1)},acompressor=threshold=0.1:ratio={fixed(2 + drive * 0.4, 1)}:attack=5:release=60,alimiter=limit=0.94",
     lambda v: f"equalizer=f=3000:t=q:w=1:g={fixed(v * 0.8, 1)},acompressor=threshold=0.1:ratio={fixed(2 + v * 0.4, 1)}:attack=5:release=60,alimiter=limit=0.94"),
    ("low-battery", "Low Battery", "Voice", "A voice running down like a toy with a flat battery, sagging and wobbling.",
     ("drain", "Drain", 1, 10, 5, 0.5, ""),
     "vibrato=f={fixed(0.5 + drain * 0.15, 2)}:d={fixed(0.2 + drain * 0.06, 2)},lowpass=f={round(5000 - drain * 300)},alimiter=limit=0.94",
     lambda v: f"vibrato=f={fixed(0.5 + v * 0.15, 2)}:d={fixed(0.2 + v * 0.06, 2)},lowpass=f={round(5000 - v * 300)},alimiter=limit=0.94"),
    ("tremble", "Tremble", "Voice", "A trembling, shaky voice.",
     ("depth", "Depth", 1, 10, 5, 0.5, ""),
     "vibrato=f=8:d={fixed(0.1 + depth * 0.07, 2)},tremolo=f=6:d={fixed(0.1 + depth * 0.04, 2)},alimiter=limit=0.94",
     lambda v: f"vibrato=f=8:d={fixed(0.1 + v * 0.07, 2)},tremolo=f=6:d={fixed(0.1 + v * 0.04, 2)},alimiter=limit=0.94"),
    ("electronic", "Electronic", "Voice", "A buzzing, electronic voice.",
     ("depth", "Depth", 1, 10, 5, 0.5, ""),
     "aphaser=type=t:speed={fixed(0.5 + depth * 0.3, 2)}:decay=0.7,acrusher=bits={round(16 - depth)}:mix=0.4,alimiter=limit=0.94",
     lambda v: f"aphaser=type=t:speed={fixed(0.5 + v * 0.3, 2)}:decay=0.7,acrusher=bits={round(16 - v)}:mix=0.4,alimiter=limit=0.94"),
    ("mic-hog", "Mic Hog", "Voice", "Someone hogging the mic: too close, loud and clipping.",
     ("drive", "Drive", 1, 10, 5, 0.5, ""),
     "equalizer=f=200:t=q:w=1:g={fixed(drive * 0.6, 1)},acompressor=threshold=0.05:ratio=8:attack=2:release=40,volume={fixed(1 + drive * 0.15, 2)},alimiter=limit=0.94",
     lambda v: f"equalizer=f=200:t=q:w=1:g={fixed(v * 0.6, 1)},acompressor=threshold=0.05:ratio=8:attack=2:release=40,volume={fixed(1 + v * 0.15, 2)},alimiter=limit=0.94"),
    ("synth", "Synth", "Voice", "A synthesised voice, chorused and swept.",
     ("depth", "Depth", 1, 10, 5, 0.5, ""),
     "chorus=0.7:0.9:55|60:0.4|0.32:0.25|0.4:2|2.3,flanger=delay=3:depth={fixed(depth * 0.8, 1)}:speed=0.5,alimiter=limit=0.94",
     lambda v: f"chorus=0.7:0.9:55|60:0.4|0.32:0.25|0.4:2|2.3,flanger=delay=3:depth={fixed(v * 0.8, 1)}:speed=0.5,alimiter=limit=0.94"),
]


def py_round(x):
    # The template's round: halves away from zero.
    import math
    return int(math.floor(abs(x) + 0.5)) * (1 if x >= 0 else -1)


def write(root, slug, manifest, fixtures):
    folder = os.path.join(root, f"concat.{slug}")
    mine = set(open(LEDGER).read().split()) if os.path.exists(LEDGER) else set()
    if os.path.exists(folder) and slug not in mine:
        raise SystemExit(f"{folder} exists and was not generated here")
    if slug not in mine:
        open(LEDGER, "a").write(slug + "\n")
    os.makedirs(folder, exist_ok=True)
    open(os.path.join(folder, "effect.toml"), "w", encoding="utf-8", newline="\n").write(manifest)
    open(os.path.join(folder, "fixtures.toml"), "w", encoding="utf-8", newline="\n").write(fixtures)


def fixtures(cases):
    out = []
    for name, at, chain in cases:
        out += ["[[case]]", f'name = "{name}"']
        if at:
            out.append(f'at = "{at}"')
        out += [f'chain = "{chain}"', ""]
    return "\n".join(out)


def main(root):
    order = 40
    for slug, name, cat, desc, (lo, hi, default), extra in VOICES:
        order += 1
        m = f'''[effect]
id = "concat.{slug}"
name = "{name}"
kind = "audio"
category = "{cat}"
order = {order}
intensity = "pitch"
description = "{desc}"

[[param]]
key = "pitch"
label = "Pitch"
min = {lo}
max = {hi}
default = {default}
step = 0.5
unit = "st"

[ffmpeg]
let = [
  "ratio = pow(2, pitch / 12)",
]
chain = "{PITCH_TEMPLATE},{extra},alimiter=limit=0.94"
'''
        f = fixtures([("default", None, pitch_chain(default, extra)), ("minimum", "min", pitch_chain(lo, extra)), ("maximum", "max", pitch_chain(hi, extra))])
        write(root, slug, m, f)
    for slug, name, cat, desc, (key, label, lo, hi, default, step, unit), template, chain in FILTERS:
        order += 1
        m = f'''[effect]
id = "concat.{slug}"
name = "{name}"
kind = "audio"
category = "{cat}"
order = {order}
intensity = "{key}"
description = "{desc}"

[[param]]
key = "{key}"
label = "{label}"
min = {lo}
max = {hi}
default = {default}
step = {step}

[ffmpeg]
chain = "{template}"
'''
        f = fixtures([("default", None, chain(default)), ("minimum", "min", chain(lo)), ("maximum", "max", chain(hi))])
        write(root, slug, m, f)
    print("wrote", len(VOICES) + len(FILTERS), "audio packages")


round = py_round

if __name__ == "__main__":
    main(sys.argv[1])

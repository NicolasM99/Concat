"""Writes docs/CAPCUT_PARITY.md: every CapCut catalogue entry and the Concat
package that covers it. python parity_doc.py <catalog.json> <packages-dir> <out.md>"""
import json
import os
import re
import sys

catalog, root, out = sys.argv[1:4]
d = json.load(open(catalog, encoding="utf-8"))

pk = {}
for folder in os.listdir(root):
    t = open(os.path.join(root, folder, "effect.toml"), encoding="utf-8").read()
    name = re.search(r'^name = "(.*)"', t, re.M).group(1)
    kind = re.search(r'^kind = "(.*)"', t, re.M).group(1)
    cat = re.search(r'^category = "(.*)"', t, re.M)
    cat = cat.group(1) if cat else ""
    pk.setdefault((kind, name.lower().strip()), []).append((folder, cat))

MAP = {("transition", "mix"): "concat.dissolve", ("transition", "black fade"): "concat.fade-black",
       ("transition", "white flash"): "concat.fade-white", ("transition", "dissolve"): "concat.dissolve",
       ("transition", "burn"): "concat.film-burn", ("transition", "pull in"): "concat.zoom-transition",
       ("transition", "pull out"): "concat.zoom-transition", ("transition", "cw swirl"): "concat.swirl",
       ("transition", "right"): "concat.push", ("transition", "left"): "concat.push", ("transition", "up"): "concat.push",
       ("transition", "radial blur"): "concat.zoom-blur-transition", ("transition", "blur"): "concat.blur-dissolve",
       ("transition", "woosh"): "concat.whip-pan", ("transition", "wipe right"): "concat.linear-wipe",
       ("transition", "wipe left"): "concat.linear-wipe", ("transition", "wipe up"): "concat.linear-wipe",
       ("transition", "stretch ll"): "concat.stretch-ii", ("transition", "slide"): "concat.slide",
       ("transition", "cube"): "concat.cube", ("transition", "clock wipe"): "concat.clock-wipe",
       ("transition", "glitch"): "concat.glitch-transition",
       ("effect", "vignette"): "concat.vignette", ("effect", "motion blur"): "concat.motion-blur",
       ("effect", "fisheye"): "concat.fisheye", ("effect", "bubbles 2"): "concat.bubbles",
       ("effect", "halo"): "concat.halo", ("effect", "halo 2"): "concat.halo-2", ("effect", "flipped"): "concat.flipped",
       ("effect", "electro border"): "concat.electro-border", ("effect", "lightning"): "concat.lightning-fx",
       ("effect", "axis rotation"): "concat.axis-rotation-fx"}
OUT = {"Woman", "Woman 2", "Woman 3", "Woman 4", "Man", "Man 2", "Man 3", "Man 4", "Gorilla Face",
       "Pop-Out", "Revolving Text", "Folk"}
WHY = {"Pop-Out": "needs the subject cut out of the frame",
       "Revolving Text": "needs text set on the effect", "Folk": "speech-to-song needs a singing model",
       "Gorilla Face": "an AR face mask"}

ANIM_SLOT = {"CapCut_Intro_type": ("animation", "In"), "CapCut_Outro_type": ("animation", "Out"),
             "CapCut_Group_animation_type": ("animation", "Combo"), "CapCut_Text_intro": ("animation", "Text In"),
             "CapCut_Text_outro": ("animation", "Text Out"), "CapCut_Text_loop_anim": ("animation", "Text Loop")}


def norm(name):
    return name.replace("_", " ").replace("  ", " & ").strip().lower()


def find(kind, name, category=None):
    key = (kind, name.lower().strip())
    if key in MAP:
        return MAP[key]
    for folder, cat in pk.get(key, []):
        if category is None or cat == category:
            return folder
    return None


lines = ["# CapCut parity", "",
         "What of CapCut's catalogue this build of Concat carries, and the package that carries it.",
         "The list is CapCut's own, as VectCutAPI's `pyJianYingDraft` metadata records it (`capcut_*_meta.py`).",
         "Everything here is drawn by Concat's own GPU shaders and FFmpeg chains: no CapCut asset is copied.", ""]
summary = []
sections = []


def section(title, rows, total):
    covered = sum(1 for _, pid, _ in rows if pid)
    summary.append((title, covered, total))
    body = [f"## {title}", "", "| CapCut | Concat package | Note |", "|---|---|---|"]
    for name, pid, note in rows:
        body.append(f"| {name} | {'`' + pid + '`' if pid else '-'} | {note} |")
    sections.append("\n".join(body) + "\n")


def unique(items):
    seen = set()
    for x in items:
        n = x["name"].strip()
        if n.lower() in seen:
            continue
        seen.add(n.lower())
        yield x, n


rows = []
items = list(unique(d["transition"]))
for x, n in items:
    rows.append((n, find("transition", n), ""))
section("Transitions", rows, len(items))

for cls, title in (("CapCut_Video_scene_effect_type", "Video effects"), ("CapCut_Video_character_effect_type", "Body effects")):
    rows = []
    items = list(unique([x for x in d["effect"] if x["class"] == cls]))
    for x, n in items:
        pid = find("effect", n) or find("effect", n, None)
        note = ""
        if cls == "CapCut_Video_character_effect_type" and pid:
            note = "approximated: drawn around the picture's outlines or a point placed on the subject"
        if n in OUT:
            pid, note = None, WHY.get(n, "an AI face or gender transform")
        rows.append((n, pid, note))
    section(title, rows, len(items))

for cls, (kind, cat) in ANIM_SLOT.items():
    rows = []
    items = list(unique([x for x in d["animation"] + d["text_animation"] if x["class"] == cls]))
    for x, n in items:
        name = n.replace("_", " ").strip()
        name = {"Cube 3 1": "Cube 3 II", "Cube 2 1": "Cube 2 II"}.get(name, name)
        pid = None
        for folder, c in pk.get(("animation", name.lower()), []) + pk.get(("animation", norm(n)), []):
            if c == cat:
                pid = folder
                break
        if pid is None:
            # Names CapCut spells with doubled underscores or a leading one.
            alt = re.sub(r"^ ", "", n.replace("__", " & ").replace("_", " ")).strip().lower()
            for folder, c in pk.get(("animation", alt), []):
                if c == cat:
                    pid = folder
        rows.append((name, pid, ""))
    section(f"Animations: {cat}", rows, len(items))

rows = []
items = list(unique(d["audio"]))
EXISTING = {"Sweet": "concat.sweet", "Vinyl": "concat.vinyl", "Lo-Fi": "concat.lofi", "Megaphone": "concat.megaphone",
            "Echo": "concat.echo", "Deep": "concat.deep", "Chipmunk": "concat.chipmunk", "Distorted": "concat.distorted",
            "Robot": "concat.robot"}
for x, n in items:
    pid = EXISTING.get(n) or find("audio", n)
    rows.append((n, None if n in OUT else pid, WHY.get(n, "") if n in OUT else ""))
section("Voice effects", rows, len(items))

MASKS = {"Split": ("linear", "Linear"), "Filmstrip": ("mirror", "Mirror"), "Circle": ("circle", "Circle"),
         "Rectangle": ("rectangle", "Rectangle"), "Stars": ("star", "Star"), "Heart": ("heart", "Heart")}
rows = []
for x, n in unique(d["mask"]):
    m = MASKS.get(n)
    rows.append((n, f"mask: {m[1]}" if m else None, "" if m else "not yet: a mask shaped by text or drawn freehand"))
summary.append(("Masks", sum(1 for _, p, _ in rows if p), len(rows)))
sections.append("## Masks\n\nConcat's clip mask (`ClipMask`) predates this work.\n\n| CapCut | Concat | Note |\n|---|---|---|\n"
                + "\n".join(f"| {a} | {b or '-'} | {c} |" for a, b, c in rows) + "\n")

lines += ["## Summary", "", "| Catalogue | Covered | CapCut |", "|---|---|---|"]
lines += [f"| {t} | {c} | {n} |" for t, c, n in summary]
lines += ["", "CapCut's filter library (its colour looks) is not in VectCutAPI's CapCut metadata, so it is not",
          "listed here; Concat ships its own looks on the Filters page.", "",
          "## How it is built", "",
          "- Transitions and effects are packages under `src/crates/concat-effects/packages`, a folder each:",
          "  `effect.toml`, an `effect.wgsl` shader and `fixtures.toml` probes pinned on a GPU.",
          "- Animations are a new package kind, `animation`: an `[animation]` table whose motion is",
          "  expressions of `t` and whose optional look is another package's knobs. See",
          "  `src/crates/concat-effects/src/animation.rs`. A clip stores `{ id, duration }` per slot in",
          "  `animations` (`in`, `out`, `combo`, `loop`), set from the library's Animations page or the API's",
          "  `updateClip`.",
          "- The packages were generated from the specs in `scripts/capcut-parity/`; see its README.", ""]
open(out, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n" + "\n".join(sections))
for t, c, n in summary:
    print(f"{t}: {c}/{n}")

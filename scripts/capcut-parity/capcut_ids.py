"""Writes the CapCut id table the project importer reads.

usage: python capcut_ids.py <catalog.json> <packages-dir> <out.rs>

Every transition, effect and animation VectCutAPI's metadata names, keyed by
CapCut's resource and effect ids, to the Concat package that stands in for
it - plus the ids seen in real drafts that the metadata does not know, each
mapped by hand. CapCut stores a name in the interface's language, so the id
is what identifies an item; the importer falls back to words in the name
(capcut/names.rs) for an id this table lacks.
"""
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
    pk.setdefault((kind, name.lower().strip()), []).append((folder, cat.group(1) if cat else ""))

SAME = {"mix": "concat.dissolve", "black fade": "concat.fade-black", "white flash": "concat.fade-white",
        "dissolve": "concat.dissolve", "burn": "concat.film-burn", "pull in": "concat.zoom-transition",
        "pull out": ("concat.zoom-transition", "direction=1"), "cw swirl": "concat.swirl",
        "right": "concat.slide-mirror-right",
        "left": "concat.slide-mirror-left",
        "up": "concat.slide-mirror-up", "down": "concat.slide-mirror-down", "radial blur": "concat.zoom-blur-transition",
        "blur": "concat.blur-dissolve", "woosh": "concat.whip-pan", "wipe right": ("concat.linear-wipe", "direction=0"),
        "wipe left": ("concat.linear-wipe", "direction=1"), "wipe up": ("concat.linear-wipe", "direction=2"),
        "stretch ll": "concat.stretch-ii", "slide": "concat.slide", "cube": "concat.cube",
        "clock wipe": "concat.clock-wipe", "glitch": "concat.glitch-transition"}
EFFECT_SAME = {"vignette": "concat.vignette", "motion blur": "concat.motion-blur", "fisheye": "concat.fisheye",
               "bubbles 2": "concat.bubbles", "halo": "concat.halo", "halo 2": "concat.halo-2",
               "flipped": "concat.flipped", "electro border": "concat.electro-border",
               "lightning": "concat.lightning-fx", "axis rotation": "concat.axis-rotation-fx"}
ANIM = {"CapCut_Intro_type": "In", "CapCut_Outro_type": "Out", "CapCut_Group_animation_type": "Combo",
        "CapCut_Text_intro": "Text In", "CapCut_Text_outro": "Text Out", "CapCut_Text_loop_anim": "Text Loop"}

# Ids from real drafts the metadata does not list, by what the item does.
MANUAL = [
    # transitions
    ("6724227330190873100", "concat.slide-mirror-down", ""),  # Down
    ("6724227090872275463", "concat.slide-mirror-up", ""),  # Up
    ("6724227599616184836", "concat.slide-mirror-right", ""),  # Right
    ("6724227717195108867", "concat.slide-mirror-left", ""),  # Left
    ("7291211157254181377", "concat.pull-in-ii", ""),              # Zoom In II
    ("7488094700159782145", "concat.zoom-blur-transition", ""),     # Speed zoom out
    ("7159450506648097281", "concat.blurry-bubbles", ""),           # Blurry bubbles
    ("7618907808662113554", "concat.slide", "direction=3"),         # Bounce fall
    ("7317281163750412801", "concat.slide", "direction=0"),         # Slide left
    ("6952697917563998722", "concat.flash-cut", ""),         # Flash II
    ("7564617241841437953", "concat.heat-dissolve", ""),              # Heat wave flash
    # clip and text animations
    ("7241878375516606978", "concat.in-slide-left", ""),            # Side slide
    ("7565842231504997633", "concat.text-in-quick-unfold", ""),                  # Quick unfold
    ("7642665703748766983", "concat.text-in-basic-in", ""),               # Basic in
    ("7591705801023048976", "concat.text-in-pop-up", ""),           # Bold in
    ("7591715953348496657", "concat.text-in-simple-sprout", ""),             # Simple sprout
    ("7594796714926542096", "concat.text-in-sequential-reveal", ""),       # Sequential reveal
    ("7597009340931034375", "concat.text-in-school-trip", ""),        # School trip
    ("7330184537214816769", "concat.text-caption-zoom-out", ""),         # caption: centre zoom out
    ("7252982471115936258", "concat.text-caption-enlarge", ""),          # caption: enlarge
    ("7324601184377901569", "concat.text-in-pop-up", ""),           # caption: short phrase scale
    ("7135040682032370178", "concat.text-in-bounce-in", ""),        # caption: bounce out
    # video effects
    ("7399471115933961478", "concat.spooky-camera", ""),            # Spooky camera
    ("7595605670351867154", "concat.glitch", ""),                   # Cyberpunk distortion
    ("7544944909845826833", "concat.color-glitch-fx", ""),          # Graphic error
    ("7399465441057328389", "concat.zoom-lens", ""),                # Zoom lens
    ("7399466631983828230", "concat.jitter", ""),                   # Static transform
]


def find(kind, name, category=None):
    hits = pk.get((kind, name.lower().strip()), [])
    for folder, cat in hits:
        if category is None or cat == category:
            return folder
    return None


rows = {}
for x in d["transition"]:
    n = x["name"].lower().strip()
    hit = SAME.get(n) or find("transition", x["name"])
    if not hit:
        continue
    pid, params = hit if isinstance(hit, tuple) else (hit, "")
    for key in ("resource_id", "effect_id"):
        if x.get(key):
            rows.setdefault(str(x[key]), (pid, params))
for x in d["effect"]:
    n = x["name"].lower().strip()
    pid = EFFECT_SAME.get(n) or find("effect", x["name"])
    if pid:
        for key in ("resource_id", "effect_id"):
            if x.get(key):
                rows.setdefault(str(x[key]), (pid, ""))
for x in d["animation"] + d["text_animation"]:
    cat = ANIM.get(x["class"])
    if not cat:
        continue
    name = x["name"].replace("__", " & ").replace("_", " ").strip()
    name = {"Cube 3 1": "Cube 3 II", "Cube 2 1": "Cube 2 II", "3D card 1": "3D card 1"}.get(name, name)
    pid = find("animation", name, cat)
    if pid:
        for key in ("resource_id", "effect_id"):
            if x.get(key):
                rows.setdefault(str(x[key]), (pid, ""))
for rid, pid, params in MANUAL:
    rows[rid] = (pid, params)

missing = [pid for pid, _ in rows.values() if not os.path.isdir(os.path.join(root, pid))]
if missing:
    raise SystemExit(f"table names packages that are not there: {sorted(set(missing))}")

lines = ["// SPDX-License-Identifier: AGPL-3.0-or-later",
         "// SPDX-FileCopyrightText: 2026 Jareer and Concat contributors", "",
         "//! CapCut's resource and effect ids, to the Concat package that stands in",
         "//! for each and the knobs it is set to. Written by",
         "//! scripts/capcut-parity/capcut_ids.py; edit that, not this.", "",
         "/// `(CapCut id, package, knobs as \"key=value,...\")`, sorted by id.",
         "pub(super) static IDS: &[(&str, &str, &str)] = &["]
for rid in sorted(rows):
    pid, params = rows[rid]
    lines.append(f'    ("{rid}", "{pid}", "{params}"),')
lines.append("];")
open(out, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
print(len(rows), "ids")

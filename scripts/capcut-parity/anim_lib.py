"""Helpers for animation specs: expressions of t, mirrored for Outs."""
import re

EO = "(1 - pow(1 - t, 3))"          # ease out: fast then settling
EB = "(1 + 2.70158 * pow(t - 1, 3) + 1.70158 * pow(t - 1, 2))"  # overshoots, then settles
U = "(1 - t)"

def lin(a, b, e=EO):
    """From a at t=0 to b at t=1 along ease e."""
    return f"({a} + ({b} - ({a})) * {e})"

def decay(amp, freq):
    """An oscillation that dies away by the end."""
    return f"({amp} * sin(t * {freq}) * (1 - t))"

def pivot(px, py, deg):
    """Offsets that make a turn by `deg` (an expression) about the point
    (px, py) of the picture - frame fractions from its centre - rather than
    its centre. The picture is taken as square: close enough for a swing."""
    a = f"(({deg}) * pi / 180)"
    cx, cy = -px, -py
    x = f"({px} + {cx} * cos({a}) - {cy} * sin({a}) - ({px} + {cx}))"
    y = f"({py} + {cx} * sin({a}) + {cy} * cos({a}) - ({py} + {cy}))"
    return x, y

def mirror(expr):
    """The same motion played backwards: an In turned into an Out."""
    return re.sub(r"\bt\b", "(1 - t)", expr)

KEYS = ("scale", "x", "y", "rotation", "opacity", "sx", "sy")

def A(slug, name, slot, order, description, duration=0.5, text=False, look=None, category=None, card=None, glyphs=None, **motion):
    cat = category or {"in": "In", "out": "Out", "combo": "Combo", "loop": "Loop"}[slot]
    if text:
        cat = "Text " + cat
    a = {"slot": slot, "duration": duration}
    if text:
        a["text"] = True
    for k in KEYS:
        if k in motion:
            a[k] = motion[k]
    if look:
        a["look"] = look
    if glyphs:
        a["glyphs"] = glyphs
    spec = {"slug": slug, "name": name, "kind": "animation", "category": cat, "order": order,
            "description": description, "animation": a, "params": []}
    if card:
        spec["card"] = card
    return spec

def out_of(spec_in, slug, name, order, description, duration=None):
    """An Out made from an In: the same motion, backwards."""
    a = spec_in["animation"]
    motion = {k: mirror(a[k]) for k in KEYS if k in a}
    look = None
    if a.get("look"):
        lid, knobs = a["look"]
        look = (lid, {k: mirror(v) for k, v in knobs.items()})
    return A(slug, name, "out", order, description, duration or a["duration"], a.get("text", False), look, **motion)

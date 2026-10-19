"""Writes Concat effect packages from compact specs.

usage: python gen.py <packages-dir> <spec-module> [<spec-module> ...]

A spec module defines PACKAGES: a list of dicts with
  slug, name, kind, category, order, description, wgsl,
  params (list of dicts: key,label,min,max,default,step,unit,values,labels),
  optional: shelves, xfade, fallback, intensity, passes (list of (target, [sx, sy])),
            space, card (dict), probes (list overriding the default ones)
Existing folders are overwritten only when they carry the GENERATED marker.
"""

import importlib.util
import os
import sys

HEADER = ""
LEDGER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated.txt")

FROM = [0.8, 0.5, 0.3, 1]
TO = [0.05, 0.15, 0.4, 1]
EFFECT_IN = [0.3, 0.2, 0.12, 1]


def toml_value(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        return repr(v)
    if isinstance(v, str):
        return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if isinstance(v, (list, tuple)):
        return "[" + ", ".join(toml_value(x) for x in v) + "]"
    raise TypeError(v)


def manifest(p):
    out = ["format = 2", "", "[effect]"]
    out.append(f'id = "concat.{p["slug"]}"')
    out.append(f"name = {toml_value(p['name'])}")
    out.append(f'kind = "{p["kind"]}"')
    out.append(f"category = {toml_value(p['category'])}")
    if p.get("shelves"):
        out.append(f"shelves = {toml_value(p['shelves'])}")
    out.append(f"order = {p.get('order', 100)}")
    if p.get("intensity"):
        out.append(f"intensity = {toml_value(p['intensity'])}")
    out.append(f"description = {toml_value(p['description'])}")
    for prm in p.get("params", []):
        out += ["", "[[param]]"]
        out.append(f"key = {toml_value(prm['key'])}")
        out.append(f"label = {toml_value(prm['label'])}")
        if prm.get("values"):
            out.append('type = "enum"')
        elif prm.get("type"):
            out.append(f"type = {toml_value(prm['type'])}")
        for k in ("min", "max", "default", "step"):
            if k in prm:
                out.append(f"{k} = {toml_value(prm[k])}")
        if prm.get("unit"):
            out.append(f"unit = {toml_value(prm['unit'])}")
        if prm.get("animate"):
            out.append("animate = true")
        if prm.get("values"):
            out.append(f"values = {toml_value(prm['values'])}")
            out.append(f"labels = {toml_value(prm['labels'])}")
    out.append("")
    if p["kind"] == "animation":
        a = p["animation"]
        out.append("[animation]")
        for k in ("slot", "duration", "text", "scale", "x", "y", "rotation", "opacity", "sx", "sy"):
            if k in a:
                out.append(f"{k} = {toml_value(a[k])}")
        if a.get("look"):
            lid, knobs = a["look"]
            out += ["", "[animation.effect]", f"id = {toml_value(lid)}"]
            if knobs:
                out.append("params = { " + ", ".join(f"{k} = {toml_value(v)}" for k, v in knobs.items()) + " }")
        if p.get("card"):
            out += ["", "[card]"] + [f"{k} = {toml_value(v)}" for k, v in p["card"].items()]
        return HEADER + "\n".join(out) + "\n"
    if p["kind"] == "transition":
        out.append("[transition]")
        out.append('entry = "effect.wgsl"')
        if p.get("xfade"):
            out.append(f"xfade = {toml_value(p['xfade'])}")
        out.append(f"fallback = {toml_value(p.get('fallback', 'cross-fade'))}")
    else:
        out.append("[wgsl]")
        out.append('entry = "effect.wgsl"')
        if p.get("space"):
            out.append(f"space = {toml_value(p['space'])}")
        for target, shrink in p.get("passes", []):
            out += ["", "[[wgsl.pass]]", f'target = "{target}"']
            if shrink:
                out.append(f"shrink = {toml_value(shrink)}")
    if p.get("card"):
        out += ["", "[card]"]
        card = p["card"]
        for k, v in card.items():
            if k == "params":
                continue
            out.append(f"{k} = {toml_value(v)}")
        if card.get("params"):
            out += ["", "[card.params]"]
            for k, v in card["params"].items():
                out.append(f"{toml_value(k) if '.' in k else k} = {toml_value(v)}")
    return HEADER + "\n".join(out) + "\n"


def default_probes(p):
    has_params = bool(p.get("params"))
    probes = []
    ats = [("default", None)] + ([("minimum", "min"), ("maximum", "max")] if has_params else [])
    for name, at in ats:
        pr = {"name": name}
        if at:
            pr["at"] = at
        if p["kind"] == "transition":
            pr["input"] = FROM
            pr["to"] = TO
            pr["progress"] = 0.37
        else:
            pr["input"] = EFFECT_IN
        pr["expect"] = [0, 0, 0, 0]
        probes.append(pr)
    return probes


def fixtures(p):
    probes = p.get("probes") or default_probes(p)
    out = [
        "# Colours in the working space: linear light, 1.0 the white of an SDR",
        "# picture. Pinned from what the shader renders on a GPU.",
    ]
    for pr in probes:
        out += ["", "[[probe]]"]
        for k in ("name", "at", "input", "to", "progress", "expect", "tolerance"):
            if k in pr:
                out.append(f"{k} = {toml_value(pr[k])}")
        if pr.get("params"):
            out.append("[probe.params]")
            for k, v in pr["params"].items():
                out.append(f"{k} = {toml_value(v)}")
    return "\n".join(out) + "\n"


DISPLAY_ONLY = {"screen", "vibrance", "s_curve", "fade", "lift_gamma_gain", "shadows", "highlights",
                "midtones", "split_tone", "tint_midtones", "kelvin", "vignette", "mono", "matte",
                "film_curve", "hue_rotate", "hsl_band", "halation", "hue_of", "chroma_of", "hue_mask",
                "skin_mask", "soften", "grain_at", "edge_at"}
LINEAR_ONLY = {"exposure", "to_log", "from_log", "planckian", "white_cones"}
RESERVED = {"look", "sample", "effect", "transition", "texel", "luma", "lut", "hash", "held",
            "from_at", "to_at", "into_space", "sample_premultiplied", "contrast", "saturation",
            "white_balance", "to_display", "from_display"} | DISPLAY_ONLY | LINEAR_ONLY


def settle_space(p):
    import re
    body = p["wgsl"]
    defined = set(re.findall(r"\bfn\s+([a-z_0-9]+)\s*\(", body))
    clash = defined & (RESERVED - {"effect", "transition"})
    if clash:
        raise SystemExit(f"{p['slug']}: redefines host functions {sorted(clash)}")
    called = set(re.findall(r"\b([a-z_0-9]+)\s*\(", body)) - defined
    display = called & DISPLAY_ONLY
    linear = called & LINEAR_ONLY
    if p["kind"] == "transition":
        if display:
            raise SystemExit(f"{p['slug']}: a transition cannot call display-only {sorted(display)}")
        return
    if display and linear:
        raise SystemExit(f"{p['slug']}: calls display-only {sorted(display)} and linear-only {sorted(linear)}")
    if display and not p.get("space"):
        p["space"] = "display"


def write(root, p):
    if p["kind"] != "animation":
        settle_space(p)
    folder = os.path.join(root, f"concat.{p['slug']}")
    man = os.path.join(folder, "effect.toml")
    mine = set(open(LEDGER).read().split()) if os.path.exists(LEDGER) else set()
    if os.path.exists(man) and p["slug"] not in mine:
        raise SystemExit(f"{folder} exists and was not generated here")
    if p["slug"] not in mine:
        with open(LEDGER, "a") as f:
            f.write(p["slug"] + "\n")
    os.makedirs(folder, exist_ok=True)
    with open(man, "w", encoding="utf-8", newline="\n") as f:
        f.write(manifest(p))
    if p["kind"] == "animation":
        return
    with open(os.path.join(folder, "effect.wgsl"), "w", encoding="utf-8", newline="\n") as f:
        f.write(p["wgsl"].strip("\n") + "\n")
    fx = os.path.join(folder, "fixtures.toml")
    # Blessed values survive a regeneration unless the spec's shader changed
    # (bless.py rewrites them); a new package starts with placeholders.
    if not os.path.exists(fx):
        with open(fx, "w", encoding="utf-8", newline="\n") as f:
            f.write(fixtures(p))


def main():
    root = sys.argv[1]
    count = 0
    slugs = set()
    for path in sys.argv[2:]:
        spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3], path)
        mod = importlib.util.module_from_spec(spec)
        sys.path.insert(0, os.path.dirname(path))
        spec.loader.exec_module(mod)
        for p in mod.PACKAGES:
            if p["slug"] in slugs:
                raise SystemExit(f"duplicate slug {p['slug']}")
            slugs.add(p["slug"])
            write(root, p)
            count += 1
    print(f"wrote {count} packages")


if __name__ == "__main__":
    main()

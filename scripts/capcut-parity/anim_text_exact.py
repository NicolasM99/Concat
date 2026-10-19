"""CapCut's own title animations, ported from the packages CapCut downloads
into its cache (Cache/effect/<resource id>/): their After Effects keyframe
tables and Lua staggers written as expressions over each glyph and the
block. They replace the stand-ins of the same name in anim_text.py."""
from anim_lib import A


def bez(x, x1, y1, x2, y2):
    return f"bezier({x}, {x1}, {y1}, {x2}, {y2})"


def keys(f, spans, ease):
    """A keyframe table read at frame `f`: `spans` is (from, to, a, b) in
    frames and values, each eased along `ease` (x1, y1, x2, y2)."""
    expr = str(spans[-1][3])
    for f0, f1, a, b in reversed(spans):
        u = f"(({f}) - {f0}) / {f1 - f0}"
        expr = f"if({f} < {f1}, {a} + ({b} - ({a})) * {bez(u, *ease)}, {expr})"
    return expr


# Volteo / Flipping (7221379732166676993): each character unfolds on its
# vertical axis - x scale 0, 100, 90, 100, 95, 100 % at AE frames 0, 4, 6, 8,
# 10, 12 - one after another, each starting a sixth of its own span after
# the one before it (spaces and line breaks counted).
FLIP_SPAN = "(1 / (1 + (n - 1) / 6))"
FLIP_LOCAL = f"window(t, i / 6 * {FLIP_SPAN}, i / 6 * {FLIP_SPAN} + {FLIP_SPAN})"
FLIPPING = A("text-in-flipping", "Flipping", "in", 30,
             "The letters unfold one after another on their vertical axes, bouncing open.",
             text=True, glyphs={
                 "sx": keys(f"(12 * {FLIP_LOCAL})", [(0, 4, 0, 1), (4, 6, 1, 0.9), (6, 8, 0.9, 1),
                                                    (8, 10, 1, 0.95), (10, 12, 0.95, 1)],
                            (0.33333333, 0, 0.66666667, 1)),
             })

# Concentración / Concentrate (7044433622119485954): each character falls
# in from large - (1.2 + (i/n)^0.25) times its size over - on a curve that
# hardens along the line, starting at (i - 1.7) / n of the way (1-based i),
# while the block fades up over 70 % and a blur over it clears.
CON_I = "(i + 1)"
CON_START = f"(({CON_I} - 1.7) / n)"
CON_R = f"clamp((t - {CON_START}) / (1 - {CON_START}), 0, 1)"
CON_K = "(i / (n - 1 + 0.0001))"
CON_SCALE = (f"if(t >= 0.999999, 1, if(t <= {CON_START}, 0, 1 + (0.2 + pow({CON_I} / n, 0.25)) * "
             f"{bez(f'(1 - {CON_R})', f'(0.5 - 0.15 * {CON_K})', f'(0.35 + 0.15 * {CON_K})', f'(0.41 + 0.57 * {CON_K})', f'(0.98 - 0.57 * {CON_K})')}))")
CONCENTRATE = A("text-in-concentrate", "Concentrate", "in", 31,
                "The letters fall in from large, one after another, as the title fades up out of a blur.",
                text=True, glyphs={
                    "sx": CON_SCALE,
                    "sy": CON_SCALE,
                    "block_opacity": "clamp(t / 0.7, 0, 1)",
                    "block_blur": f"0.11 * {bez('(1 - t)', 0.24, 0.53, 0.42, 0.97)}",
                })

# Ondulación / Flutter (7094880213590348290): along each line the letters
# fade up and grow from 95 %, each a quarter of the line later than the
# first, behind a blur front that sweeps left to right (CapCut's noise
# ripple under it is left out).
FL_START = "(li / (ln - 1 + 0.001) * 0.25)"
FL_E = bez(f"clamp((t - {FL_START}) / (1 - {FL_START}), 0, 1)", 0.22, 0.6, 0.52, 0.93)
FL_FRONT = "clamp(t / 0.781, 0, 1)"
FLUTTER = A("text-in-flutter", "Flutter", "in", 32,
            "The letters ripple in along each line, fading up and settling, behind a sweeping blur.",
            text=True, glyphs={
                "sx": f"(0.95 + 0.05 * {FL_E})",
                "sy": f"(0.95 + 0.05 * {FL_E})",
                "opacity": FL_E,
                "blur": f"0.33 * clamp((u - (2 * {FL_FRONT} - 1)) / ({FL_FRONT} + 0.2 - (2 * {FL_FRONT} - 1)), 0, 1)",
            })

# Rebote hacia dentro / Bounce In (6887766069587481090): the block grows
# from nothing to 110 % by 57 %, then settles to its size.
BOUNCE = (f"if(t <= 0.57, 1.1 * {bez('(t / 0.57)', 0, 0, 0.51, 1)}, "
          f"1.1 + (1 - 1.1) * {bez('((t - 0.57) / 0.43)', 0.2, 0, 0.13, 1)})")
BOUNCE_IN = A("text-in-bounce-in", "Bounce In", "in", 33,
              "The title springs up from nothing past its size and settles.",
              text=True, glyphs={"block_scale": BOUNCE})

# Deslizar hacia la izquierda / Slide Left (7403255792146584081) and
# Deslizar hacia arriba / Slide Up (6763470111253729803): the block slides
# 1.33 of its own width (height) into place, fading up, on a quadratic ease
# out.
QUAD = "(1 - pow(1 - t, 2))"
SLIDE_LEFT = A("text-in-slide-left", "Slide Left", "in", 34,
               "The title slides in from the right, a third further than its width, fading up.",
               text=True, glyphs={"block_dx": f"1.33 * w * (1 - {QUAD})", "block_opacity": QUAD})
SLIDE_UP = A("text-in-slide-up", "Slide Up", "in", 35,
             "The title slides up into place from a third further than its height, fading up.",
             text=True, glyphs={"block_dy": f"1.33 * h * (1 - {QUAD})", "block_opacity": QUAD})

# Aparición hacia abajo / Showing Down (7149113292747706881): the block -
# words and plate - slides down out of its own top edge into place.
SHOWING_DOWN = A("text-in-showing-down", "Showing Down", "in", 36,
                 "The title slides down out of its own top edge into place.",
                 text=True, glyphs={"block_dy": f"-(1 - {bez('t', 0, 0, 0.5, 1)}) * h", "clip_top": True})

EXACT = {spec["slug"]: spec for spec in (FLIPPING, CONCENTRATE, FLUTTER, BOUNCE_IN, SLIDE_LEFT, SLIDE_UP, SHOWING_DOWN)}

# The five whose packages CapCut ships encrypted, measured off CapCut's own
# render frame by frame instead (1080x1920, 30 fps, 0.5 s): close, not
# copied numbers.
def _seq(start, spread, span):
    return f"window(t, {start} + {spread} * i / max(n - 1, 1), {start} + {spread} * i / max(n - 1, 1) + {span})"


EASE = "(1 - pow(1 - {x}, 3))"

SCHOOL_TRIP = A("text-in-school-trip", "School Trip", "in", 37,
                "The letters pop in one after another, each widening from a sliver.",
                text=True, glyphs={"sx": EASE.format(x=_seq(0.05, 0.75, 0.13)),
                                   "opacity": f"min(1, 3 * {_seq(0.05, 0.75, 0.13)})"})
SEQUENTIAL_REVEAL = A("text-in-sequential-reveal", "Sequential Reveal", "in", 38,
                      "The letters fade on one after another, left to right.",
                      text=True, glyphs={"opacity": _seq(0.06, 0.62, 0.12)})
SIMPLE_SPROUT = A("text-in-simple-sprout", "Simple Sprout", "in", 39,
                  "Every letter sprouts from a speck where it stands.",
                  text=True, glyphs={"sx": EASE.format(x="window(t, 0.04, 0.27)"),
                                     "sy": EASE.format(x="window(t, 0.04, 0.27)"),
                                     "opacity": "window(t, 0.02, 0.12)"})
QUICK_UNFOLD = A("text-in-quick-unfold", "Quick Unfold", "in", 40,
                 "The title unfolds left to right, the letters streaking into place.",
                 text=True, glyphs={"sx": f"(0.3 + 0.7 * {EASE.format(x=_seq(0.05, 0.45, 0.15))})",
                                    "dx": f"(-0.3 * (1 - {EASE.format(x=_seq(0.05, 0.45, 0.15))}))",
                                    "opacity": f"min(1, 2 * {_seq(0.05, 0.45, 0.15)})",
                                    "blur": f"(0.12 * (1 - {_seq(0.05, 0.45, 0.15)}))"})
BASIC_IN = A("text-in-basic-in", "Basic In", "in", 41,
             "The title grows up from small as it fades in.",
             text=True, glyphs={"block_scale": "(0.15 + 0.85 * (1 - pow(1 - min(t / 0.7, 1), 2)))",
                                "block_opacity": "min(1, t / 0.45)"})

MEASURED = [SCHOOL_TRIP, SEQUENTIAL_REVEAL, SIMPLE_SPROUT, QUICK_UNFOLD, BASIC_IN]

# Captions: the motion follows each word as it is spoken (ws, we).
# Alejamiento central / Center Zoom Out (7330184537214816769): a word is
# hidden until it is said, then shrinks from 130 % to its size about the
# caption's middle while it fades up from 70 %.
_P = "clamp((t * d - ws) / max(we - ws, 0.001), 0, 1)"
_S = f"max(1.3 - 0.3 * {bez(f'min(18 * {_P} / 12, 1)', 0.025, 0.132587546, 0.26, 1)}, 1)"
CAPTION_ZOOM_OUT = A("text-caption-zoom-out", "Caption Zoom Out", "in", 42,
                     "Each word appears as it is spoken, shrinking into place about the caption's middle.",
                     text=True, glyphs={
                         "sx": f"if(t * d < ws, 0, {_S})",
                         "sy": f"if(t * d < ws, 0, {_S})",
                         "dx": f"({_S} - 1) * gx",
                         "dy": f"({_S} - 1) * gy",
                         "opacity": f"min(0.7 + 0.3 * {bez(f'min(12 * {_P} / 4, 1)', 0.166666667, 0.166666667, 0.26, 1)}, 1)",
                     })
# Ampliar / Enlarge (7252982471115936258): on CapCut's own render of a
# caption whose words came from a longer sentence the words sit still, so
# it stands still here.
CAPTION_ENLARGE = A("text-caption-enlarge", "Caption Enlarge", "in", 43,
                    "The caption as it is, word for word.", text=True, glyphs={"opacity": "1"})
MEASURED += [CAPTION_ZOOM_OUT, CAPTION_ENLARGE]

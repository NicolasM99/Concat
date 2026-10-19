from anim_lib import *

BLUR = "concat.gaussian-blur"

def swing_in(slug, name, order, px, py, deg):
    x, y = pivot(px, py, f"{deg} * (1 - {EO})")
    return A(slug, name, "in", order, f"The clip swings into place about its {name.lower().replace('swing ', '')} corner.",
             x=x, y=y, rotation=f"{deg} * (1 - {EO})", opacity="min(1, t * 3)")

INS = [
    A("in-fade-in", "Fade In", "in", 1, "The clip fades up from nothing.", opacity="t"),
    A("in-zoom-1", "Zoom 1", "in", 2, "The clip grows into place from half its size.", scale=lin(0.5, 1), opacity="min(1, t * 2)"),
    # CapCut's own, from its package: see fx_reveal.py's zoom-2-blur.
    A("in-zoom-2", "Zoom 2", "in", 3, "The clip grows back from small, mirrored round itself, out of a zoom blur.", look=("concat.zoom-2-blur", {"progress": "100 * t"})),
    A("in-zoom-in", "Zoom In", "in", 4, "The clip zooms in from a speck.", scale=lin(0.05, 1)),
    # CapCut's own, from its package: linear 150 % to 100 %, opaque by 20 %.
    A("in-zoom-out", "Zoom Out", "in", 5, "The clip zooms out to its place from closer, fading up.", scale="(1.5 - 0.5 * t)", opacity="min(1, t / 0.2)"),
    A("in-mini-zoom", "Mini Zoom", "in", 6, "The clip settles in with a small zoom and a fade.", scale=lin(1.1, 1), opacity="t"),
    A("in-rock-vertically", "Rock Vertically", "in", 7, "The clip rocks up and down as it arrives.", y=decay(0.08, 25), opacity="min(1, t * 3)"),
    A("in-rock-horizontally", "Rock Horizontally", "in", 8, "The clip rocks side to side as it arrives.", x=decay(0.08, 25), opacity="min(1, t * 3)"),
    A("in-slide-down", "Slide Down", "in", 9, "The clip slides down into place from above.", y=f"-(1 - {EO})"),
    A("in-slide-up", "Slide Up", "in", 10, "The clip slides up into place from below.", y=f"(1 - {EO})"),
    A("in-slide-right", "Slide Right", "in", 11, "The clip slides in from the left.", x=f"-(1 - {EO})"),
    A("in-slide-left", "Slide Left", "in", 12, "The clip slides in from the right.", x=f"(1 - {EO})"),
    A("in-rotate", "Rotate", "in", 13, "The clip spins in, growing as it turns.", rotation=f"-360 * (1 - {EO})", scale=lin(0.2, 1)),
    A("in-rotation-opening", "Rotation Opening", "in", 14, "The clip turns open into place.", rotation=f"90 * (1 - {EO})", scale=lin(0.6, 1), opacity="t"),
    A("in-spin-up-1", "Spin Up 1", "in", 15, "The clip spins up into place from below.", rotation=f"-180 * (1 - {EO})", y=f"0.5 * (1 - {EO})", opacity="min(1, t * 2)"),
    A("in-spin-up-2", "Spin Up 2", "in", 16, "The clip spins up into place, growing as it rises.", rotation=f"360 * (1 - {EO})", y=f"0.4 * (1 - {EO})", scale=lin(0.4, 1)),
    A("in-spin-left", "Spin Left", "in", 17, "The clip spins in from the right.", rotation=f"-90 * (1 - {EO})", x=f"0.6 * (1 - {EO})", opacity="min(1, t * 2)"),
    A("in-roll-right", "Roll Right", "in", 18, "The clip rolls in from the left like a wheel.", x=f"-(1 - {EO})", rotation=f"-360 * (1 - {EO})"),
    A("in-whirl", "Whirl", "in", 19, "The clip whirls in from the centre, turning twice.", rotation=f"720 * (1 - {EO})", scale=EO),
    A("in-swing", "Swing", "in", 20, "The clip swings into place like a pendulum coming to rest.", rotation=decay(25, 18), opacity="min(1, t * 3)"),
    swing_in("in-swing-top-right", "Swing Top Right", 21, 0.5, -0.5, -60),
    swing_in("in-swing-top-left", "Swing Top Left", 22, -0.5, -0.5, 60),
    swing_in("in-swing-bottom", "Swing Bottom", 23, 0.0, 0.5, 70),
    swing_in("in-swing-right", "Swing Right", 24, 0.5, 0.0, -70),
    swing_in("in-swing-bottom-left", "Swing Bottom Left", 25, -0.5, 0.5, -60),
    swing_in("in-swing-bottom-right", "Swing Bottom Right", 26, 0.5, 0.5, 60),
    A("in-flip", "Flip", "in", 27, "The clip flips round into view on its vertical axis.", sx=f"sin({EO} * pi / 2)", opacity="min(1, t * 4)"),
    A("in-shake-1", "Shake 1", "in", 28, "The clip shakes side to side as it appears.", x=decay(0.05, 45), opacity="min(1, t * 3)"),
    A("in-shake-2", "Shake 2", "in", 29, "The clip shakes in every direction as it appears.", x=decay(0.05, 45), y=decay(0.04, 37), opacity="min(1, t * 3)"),
    A("in-shake-3", "Shake 3", "in", 30, "The clip arrives with a hard shake and a twist.", x=decay(0.06, 50), rotation=decay(6, 40), scale=lin(1.15, 1), opacity="min(1, t * 3)"),
    A("in-shake-down", "Shake Down", "in", 31, "The clip drops in from above and shakes as it lands.", y=f"(-(1 - {EO}) * 0.4 + {decay(0.03, 50)})", opacity="min(1, t * 3)"),
    A("in-vibrating-panels", "Vibrating Panels", "in", 32, "The clip buzzes into place, vibrating fast.", x=decay(0.03, 80), sx=f"(1 + {decay(0.05, 70)})", sy=f"(1 - {decay(0.05, 70)})", opacity="t"),
    A("in-retro-fadein", "Retro Fadein", "in", 33, "The clip fades in out of a grey, faded print.", opacity="t", look=("concat.gray-mask", {"progress": "100 * (1 - t)"})),
    A("in-retro-fadein-2", "Retro Fadein 2", "in", 34, "The clip fades in through rolling CRT bands.", opacity="t", look=("concat.crt-bands", {"progress": "100 * (1 - t)"})),
    A("in-flame-risen", "Flame Risen", "in", 35, "The clip burns on from the bottom up.", duration=0.8, look=("concat.reveal-flame", {"progress": "100 * t"})),
    A("in-screen-wipe", "Screen Wipe", "in", 36, "The clip is wiped on from the left.", look=("concat.reveal-wipe", {"progress": "100 * t"})),
    A("in-rgb-scanlines", "RGB Scanlines", "in", 37, "The clip resolves out of split colour and scan lines.", opacity="min(1, t * 2)", look=("concat.rgb-scanlines", {"progress": "100 * (1 - t)"})),
    A("in-crt-bands", "CRT Bands", "in", 38, "The clip flickers on through jittering CRT bands.", opacity="min(1, t * 2)", look=("concat.crt-bands", {"progress": "100 * (1 - t)"})),
    A("in-anime-frame", "Anime Frame", "in", 39, "The clip bursts in with speed lines and a flash.", scale=lin(1.2, 1), look=("concat.anime-frame", {"progress": "100 * (1 - t)"})),
    A("in-gray-mask", "Gray Mask", "in", 40, "Colour floods into the clip from grey.", look=("concat.gray-mask", {"progress": "100 * (1 - t)"})),
    A("in-blinds", "Blinds", "in", 41, "The clip appears as blinds open.", look=("concat.reveal-blinds", {"progress": "100 * t"})),
    A("in-puzzle", "Puzzle", "in", 42, "The clip fills in tile by tile like a puzzle.", look=("concat.reveal-tiles", {"progress": "100 * t"})),
    A("in-wiper", "Wiper", "in", 43, "The clip is swept on by a wiper turning round.", look=("concat.reveal-clock", {"progress": "100 * t"})),
    A("in-blur", "Blur In", "in", 44, "The clip sharpens out of a blur.", opacity="min(1, t * 2)", look=(BLUR, {"radius": "1 + 40 * (1 - t)"})),
]

by = {spec["slug"]: spec for spec in INS}

OUTS = [
    out_of(by["in-fade-in"], "out-fade-out", "Fade Out", 1, "The clip fades away to nothing."),
    out_of(by["in-rgb-scanlines"], "out-rgb-scanlines", "RGB Scanlines", 2, "The clip breaks up into split colour and scan lines."),
    A("out-blurred-fadein", "Blurred Fadein", "out", 3, "The clip blurs as it fades away.", opacity="(1 - t)", look=(BLUR, {"radius": "1 + 40 * t"})),
    A("out-blurred-fadein-1", "Blurred Fadein 1", "out", 4, "The clip blurs and swells as it fades away.", opacity="(1 - t)", scale="(1 + 0.2 * t)", look=(BLUR, {"radius": "1 + 40 * t"})),
    out_of(by["in-slide-up"], "out-slide-down", "Slide Down", 5, "The clip slides down out of the frame."),
    out_of(by["in-slide-down"], "out-slide-up", "Slide Up", 6, "The clip slides up out of the frame."),
    out_of(by["in-slide-left"], "out-slide-right", "Slide Right", 7, "The clip slides out to the right."),
    out_of(by["in-slide-right"], "out-slide-left", "Slide Left", 8, "The clip slides out to the left."),
    out_of(by["in-zoom-out"], "out-zoom-in", "Zoom In", 9, "The clip zooms in past the viewer and fades."),
    out_of(by["in-zoom-in"], "out-zoom-out", "Zoom Out", 10, "The clip zooms away to a speck."),
    out_of(by["in-crt-bands"], "out-crt-bands", "CRT Bands", 11, "The clip flickers out through CRT bands."),
    out_of(by["in-flame-risen"], "out-flame-risen", "Flame Risen", 12, "The clip burns away from the bottom up."),
    out_of(by["in-screen-wipe"], "out-screen-wipe", "Screen Wipe", 13, "The clip is wiped off to the left."),
    out_of(by["in-rotation-opening"], "out-rotation-closing", "Rotation Closing", 14, "The clip turns closed and fades."),
    out_of(by["in-rotate"], "out-rotate", "Rotate", 15, "The clip spins away, shrinking."),
    out_of(by["in-anime-frame"], "out-anime-frame", "Anime Frame", 16, "The clip bursts away with speed lines and a flash."),
    A("out-rotate-out-1", "Rotate Out 1", "out", 17, "The clip turns away to one side and fades.", rotation="90 * pow(t, 3)", x="0.5 * pow(t, 3)", opacity="(1 - t)"),
    A("out-rotate-out-2", "Rotate Out 2", "out", 18, "The clip spins away and shrinks to nothing.", rotation="-360 * pow(t, 2)", scale="(1 - pow(t, 2))"),
    out_of(by["in-mini-zoom"], "out-mini-zoom", "Mini Zoom", 19, "The clip fades with a small zoom."),
    out_of(by["in-gray-mask"], "out-gray-mask", "Gray Mask", 20, "The clip drains to grey."),
    out_of(by["in-whirl"], "out-whirl", "Whirl", 21, "The clip whirls away into the centre."),
    out_of(by["in-vibrating-panels"], "out-vibrating-panels", "Vibrating Panels", 22, "The clip buzzes away, vibrating fast."),
    out_of(by["in-flip"], "out-flip", "Flip", 23, "The clip flips away on its vertical axis."),
    out_of(by["in-blur"], "out-blur", "Blur Out", 24, "The clip dissolves into a blur."),
]

# Combos span the clip: t runs 0..1 across it. ARR rises over the first
# quarter, LEAVE over the last; the middle is the clip as placed unless the
# combo moves throughout.
ARR = "clamp(t / 0.25, 0, 1)"
LEAVE = "clamp((t - 0.75) / 0.25, 0, 1)"
E_ARR = f"(1 - pow(1 - {ARR}, 3))"
E_LEAVE = f"pow({LEAVE}, 3)"

def combo(slug, name, order, description, **motion):
    return A("combo-" + slug, name, "combo", order, description, duration=2.0, **motion)

def through(axis, sign, name, order, desc, extra=None):
    """In from one side, out the other."""
    m = {axis: f"({sign} * (1 - {E_ARR}) - ({sign}) * {E_LEAVE})"}
    m.update(extra or {})
    return (name, order, desc, m)

COMBO_SPECS = [
    ("zoom-1", "Zoom 1", "The clip zooms in at the start and out at the end.", dict(scale=f"(0.3 + 0.7 * {E_ARR} - 0.7 * {E_LEAVE})")),
    ("zoom-2", "Zoom 2", "The clip arrives large, settles, then swells away.", dict(scale=f"(1.6 - 0.6 * {E_ARR} + 0.6 * {E_LEAVE})", opacity=f"(min(1, {ARR} * 2) * (1 - {LEAVE}))")),
    ("stretch-and-distort", "Stretch and distort", "The clip stretches wide, squashes tall, and settles before stretching away.", dict(sx=f"(1 + 0.4 * sin(t * pi * 4) * (1 - abs(t - 0.5) * 2))", sy=f"(1 - 0.3 * sin(t * pi * 4) * (1 - abs(t - 0.5) * 2))")),
    ("distort-and-stretch", "Distort and stretch", "The clip squashes and stretches in turn throughout.", dict(sx=f"(1 + 0.25 * sin(t * pi * 6))", sy=f"(1 - 0.25 * sin(t * pi * 6))")),
    ("bounce-1", "Bounce 1", "The clip bounces in from above and bounces out again.", dict(y=f"(-abs(cos(t * pi * 3)) * 0.4 * (1 - {E_ARR}) - 0.8 * {E_LEAVE})", scale=f"(1 - 0.1 * abs(sin(t * pi * 6)))")),
    ("bounce-2", "Bounce 2", "The clip bounces in place the whole time.", dict(y="(-abs(sin(t * pi * 6)) * 0.12)")),
    ("sway-out", "Sway Out", "The clip sways and drifts away.", dict(rotation="(10 * sin(t * pi * 4))", x="(0.3 * pow(t, 2))", opacity="(1 - pow(t, 4))")),
    ("sway-in", "Sway In", "The clip sways in from the side and settles.", dict(rotation="(10 * sin(t * pi * 4) * (1 - t))", x="(-0.3 * pow(1 - t, 2))", opacity="min(1, t * 4)")),
    ("3d-card-1", "3D card 1", "The clip turns like a card in space, showing its edge.", dict(sx="abs(cos(t * pi))", rotation="(8 * sin(t * pi * 2))")),
    ("3d-card-2", "3D card 2", "The clip flips over like a card twice.", dict(sx="abs(cos(t * pi * 2))")),
    ("3d-card-3", "3D card 3", "The clip tilts back and forth like a card held up.", dict(sy="(0.7 + 0.3 * abs(cos(t * pi * 2)))", rotation="(6 * sin(t * pi * 2))")),
    ("3d-card-4", "3D card 4", "The clip turns half round and back.", dict(sx="(0.5 + 0.5 * cos(t * pi * 2))")),
    ("3d-card-5", "3D card 5", "The clip turns on its horizontal axis like a flipping card.", dict(sy="abs(cos(t * pi))")),
    ("3d-card-6", "3D card 6", "The clip spins like a card on a string, shrinking at each turn.", dict(sx="abs(cos(t * pi * 3))", scale="(0.85 + 0.15 * abs(cos(t * pi * 3)))")),
    ("slide-and-wave", "Slide and wave", "The clip slides in and waves as it goes.", dict(x=f"(-(1 - {E_ARR}) + {E_LEAVE})", rotation="(8 * sin(t * pi * 6))")),
    ("wave-and-slide", "Wave and slide", "The clip waves in place, then slides away.", dict(rotation="(8 * sin(t * pi * 6) * (1 - t))", x=f"{E_LEAVE}")),
    ("pendulum-1", "Pendulum 1", "The clip swings like a pendulum from above.", dict(rotation="(20 * sin(t * pi * 4))", x="(0.1 * sin(t * pi * 4))")),
    ("pendulum-2", "Pendulum 2", "The clip swings like a pendulum, dying away.", dict(rotation="(30 * sin(t * pi * 5) * (1 - t))")),
    ("wobble", "Wobble", "The clip wobbles like jelly.", dict(sx="(1 + 0.08 * sin(t * pi * 10))", sy="(1 - 0.08 * sin(t * pi * 10))", rotation="(3 * sin(t * pi * 7))")),
    ("enlarge-and-bounce", "Enlarge and bounce", "The clip grows with a bounce and shrinks away.", dict(scale=f"({EB.replace('t', ARR)} * (1 - {E_LEAVE}))")),
    ("bendzoom", "BendZoom", "The clip zooms in with a bend and back out.", dict(scale=f"(1 + 0.4 * sin(t * pi))", rotation="(15 * sin(t * pi * 2))")),
    ("spin-rise", "Spin Rise", "The clip spins as it rises up and away.", dict(rotation="(360 * t)", y=f"(0.5 * (1 - {E_ARR}) - 0.6 * {E_LEAVE})")),
    ("spin", "Spin", "The clip spins round once over the clip.", dict(rotation="(360 * t)")),
    ("shrink-and-bounce", "Shrink and bounce", "The clip shrinks down and bounces back.", dict(scale="(1 - 0.3 * abs(sin(t * pi * 3)))")),
    ("smartphone-1", "Smartphone 1", "The clip tilts as if on a phone turned in the hand.", dict(rotation="(12 * sin(t * pi * 2))", scale="(0.85 + 0.15 * cos(t * pi * 2))")),
    ("smartphone-2", "Smartphone 2", "The clip drifts and tilts like a phone screen.", dict(rotation="(8 * sin(t * pi * 2))", x="(0.08 * sin(t * pi * 2))", scale="0.9")),
    ("smartphone-3", "Smartphone 3", "The clip rotates a quarter turn and back like a phone.", dict(rotation="(90 * sin(t * pi))", scale="(1 - 0.35 * sin(t * pi))")),
    ("distort-right", "Distort Right", "The clip stretches off to the right and snaps back.", dict(sx="(1 + 0.4 * sin(t * pi))", x="(0.2 * sin(t * pi))")),
    ("distort-left", "Distort Left", "The clip stretches off to the left and snaps back.", dict(sx="(1 + 0.4 * sin(t * pi))", x="(-0.2 * sin(t * pi))")),
    ("trisect-1", "Trisect 1", "The clip arrives in three steps and leaves the same way.", dict(x=f"(-(1 - floor({ARR} * 3) / 3) + floor({LEAVE} * 3) / 3)")),
    ("trisect-2", "Trisect 2", "The clip drops in three steps and rises out the same way.", dict(y=f"(-(1 - floor({ARR} * 3) / 3) + floor({LEAVE} * 3) / 3)")),
    ("fall-spin", "Fall Spin", "The clip falls in spinning and falls out again.", dict(y=f"(-(1 - {E_ARR}) + {E_LEAVE})", rotation=f"(-180 * (1 - {E_ARR}) + 180 * {E_LEAVE})")),
    ("spinning-top-1", "Spinning top 1", "The clip spins and wobbles like a top.", dict(rotation="(720 * t)", x="(0.05 * sin(t * pi * 8))")),
    ("spinning-top-2", "Spinning top 2", "The clip spins faster and faster like a top, then falls.", dict(rotation="(1080 * t * t)", scale="(1 - 0.3 * t)")),
    ("fall-right", "Fall Right", "The clip falls in from the top left and out to the right.", dict(x=f"(-(1 - {E_ARR}) + {E_LEAVE})", y=f"(-(1 - {E_ARR}) * 0.5 + {E_LEAVE} * 0.5)", rotation=f"(30 * {E_LEAVE})")),
    ("pan-right", "Pan Right", "The view pans across the clip to the right.", dict(x="(0.15 - 0.3 * t)", scale="1.3")),
    ("pan-left", "Pan Left", "The view pans across the clip to the left.", dict(x="(-0.15 + 0.3 * t)", scale="1.3")),
    ("slip-and-slide-1", "Slip and slide 1", "The clip slips in sideways, overshooting, and slides out.", dict(x=f"((1 - {EB.replace('t', ARR)}) + {E_LEAVE})")),
    ("slip-and-slide-2", "Slip and slide 2", "The clip slips up into place and slides down out.", dict(y=f"((1 - {EB.replace('t', ARR)}) + {E_LEAVE})")),
    ("roll-inout-1", "Roll InOut 1", "The clip rolls in from the left and out to the right.", dict(x=f"(-(1 - {E_ARR}) + {E_LEAVE})", rotation=f"(-360 * (1 - {E_ARR}) + 360 * {E_LEAVE})")),
    ("roll-inout-2", "Roll InOut 2", "The clip rolls in from the right and out to the left.", dict(x=f"((1 - {E_ARR}) - {E_LEAVE})", rotation=f"(360 * (1 - {E_ARR}) - 360 * {E_LEAVE})")),
    ("right-zoom", "Right Zoom", "The clip zooms in toward its right side.", dict(scale="(1 + 0.4 * t)", x="(-0.15 * t)")),
    ("left-zoom", "Left Zoom", "The clip zooms in toward its left side.", dict(scale="(1 + 0.4 * t)", x="(0.15 * t)")),
    ("slice-rotate-1", "Slice & Rotate 1", "The clip turns in slices of a quarter turn.", dict(rotation="(90 * floor(t * 4))", scale="(0.8 + 0.2 * abs(cos(t * pi * 4)))")),
    ("slice-rotate-2", "Slice & Rotate 2", "The clip snaps round in eighth turns.", dict(rotation="(45 * floor(t * 8))")),
    ("cube", "Cube", "The clip turns like the face of a cube coming round and going.", dict(sx=f"({E_ARR} * (1 - {E_LEAVE}))", x=f"(-0.5 * (1 - {E_ARR}) + 0.5 * {E_LEAVE})")),
    ("cube-2", "Cube 2", "The clip turns in like a cube's face from above.", dict(sy=f"({E_ARR} * (1 - {E_LEAVE}))", y=f"(-0.5 * (1 - {E_ARR}) + 0.5 * {E_LEAVE})")),
    ("cube-3", "Cube 3", "The clip turns in like a cube's face from the right.", dict(sx=f"({E_ARR} * (1 - {E_LEAVE}))", x=f"(0.5 * (1 - {E_ARR}) - 0.5 * {E_LEAVE})")),
    ("cube-2-1", "Cube 2 II", "The clip turns in like a cube's face from below.", dict(sy=f"({E_ARR} * (1 - {E_LEAVE}))", y=f"(0.5 * (1 - {E_ARR}) - 0.5 * {E_LEAVE})")),
    ("cube-3-1", "Cube 3 II", "The clip keeps turning like a cube, face after face.", dict(sx="abs(cos(t * pi * 2))", x="(0.3 * sin(t * pi * 2))")),
    ("pirate-ship-1", "Pirate ship 1", "The clip rocks like a ship at sea.", dict(rotation="(15 * sin(t * pi * 4))", y="(0.04 * sin(t * pi * 8))")),
    ("pirate-ship-2", "Pirate ship 2", "The clip rocks harder, like a ship in a swell.", dict(rotation="(25 * sin(t * pi * 3))", y="(0.08 * sin(t * pi * 6))")),
    ("pirate-ship-3", "Pirate ship 3", "The clip swings like a fairground ship.", dict(rotation="(40 * sin(t * pi * 2))", x="(0.15 * sin(t * pi * 2))")),
    ("pirate-ship-4", "Pirate ship 4", "The clip swings high like a fairground ship at full tilt.", dict(rotation="(60 * sin(t * pi * 2))", x="(0.2 * sin(t * pi * 2))", y="(-0.1 * abs(sin(t * pi * 2)))")),
    ("bisect-1", "Bisect 1", "The clip arrives and leaves in two steps.", dict(x=f"(-(1 - floor({ARR} * 2) / 2) + floor({LEAVE} * 2) / 2)")),
    ("bisect-2", "Bisect 2", "The clip drops and rises in two steps.", dict(y=f"(-(1 - floor({ARR} * 2) / 2) + floor({LEAVE} * 2) / 2)")),
    ("bisect-domino-1", "Bisect Domino 1", "The clip topples in like a domino and topples out.", dict(rotation=f"(-90 * (1 - {E_ARR}) + 90 * {E_LEAVE})", y=f"(0.3 * (1 - {E_ARR}) + 0.3 * {E_LEAVE})")),
    ("bisect-domino-2", "Bisect Domino 2", "The clip topples in from the other side like a domino.", dict(rotation=f"(90 * (1 - {E_ARR}) - 90 * {E_LEAVE})", y=f"(0.3 * (1 - {E_ARR}) + 0.3 * {E_LEAVE})")),
    ("magic-cube-1", "Magic Cube 1", "The clip twists like a face of a magic cube.", dict(rotation="(90 * pow(sin(t * pi), 2))", sx="(1 - 0.3 * sin(t * pi * 2))")),
    ("magic-cube-2", "Magic Cube 2", "The clip twists back and forth like a magic cube's face.", dict(rotation="(45 * sin(t * pi * 4))", sy="(1 - 0.2 * abs(sin(t * pi * 4)))")),
    ("yoyo-1", "Yoyo 1", "The clip drops and springs back up like a yoyo.", dict(y="(0.5 * pow(sin(t * pi * 2), 2))", rotation="(180 * sin(t * pi * 2))")),
    ("yoyo-2", "Yoyo 2", "The clip spins down and back up like a yoyo.", dict(y="(0.4 * abs(sin(t * pi * 3)))", rotation="(360 * t * 3)")),
    ("fall-bottom-right", "Fall Bottom Right", "The clip falls away to the bottom right.", dict(x=f"(-(1 - {E_ARR}) * 0.5 + {E_LEAVE})", y=f"(-(1 - {E_ARR}) * 0.5 + {E_LEAVE})", rotation=f"(45 * {E_LEAVE})")),
    ("fall-bottom-left", "Fall Bottom Left", "The clip falls away to the bottom left.", dict(x=f"((1 - {E_ARR}) * 0.5 - {E_LEAVE})", y=f"(-(1 - {E_ARR}) * 0.5 + {E_LEAVE})", rotation=f"(-45 * {E_LEAVE})")),
    ("fall-left", "Fall Left", "The clip falls in from the top right and out to the left.", dict(x=f"((1 - {E_ARR}) - {E_LEAVE})", y=f"(-(1 - {E_ARR}) * 0.5 + {E_LEAVE} * 0.5)", rotation=f"(-30 * {E_LEAVE})")),
    ("funhouse-mirror-1", "Funhouse mirror 1", "The clip stretches tall and thin, then short and wide, like a funhouse mirror.", dict(sx="(1 + 0.35 * sin(t * pi * 2))", sy="(1 - 0.35 * sin(t * pi * 2))")),
    ("funhouse-mirror-2", "Funhouse mirror 2", "The clip pulls in and out like a warping mirror.", dict(sx="(1 + 0.2 * sin(t * pi * 6))", sy="(1 + 0.2 * cos(t * pi * 6))")),
    ("revolving-checker-1", "Revolving Checker 1", "The clip revolves in quarter steps.", dict(rotation="(90 * floor(t * 4) + 90 * pow(fract_t, 3))".replace("fract_t", "(t * 4 - floor(t * 4))"))),
    ("revolving-checker-2", "Revolving Checker 2", "The clip revolves the other way in quarter steps, pulsing.", dict(rotation="(-90 * floor(t * 4))", scale="(0.85 + 0.15 * cos(t * pi * 8))")),
    ("checker-slide-1", "Checker Slide 1", "The clip slides in steps across the frame.", dict(x="(0.3 * (floor(t * 4) / 3 - 0.5))")),
    ("checker-slide-2", "Checker Slide 2", "The clip slides up in steps.", dict(y="(-0.3 * (floor(t * 4) / 3 - 0.5))")),
    ("waltzer-1", "Waltzer 1", "The clip twirls round in a circle like a waltzer car.", dict(x="(0.1 * cos(t * pi * 4))", y="(0.1 * sin(t * pi * 4))", rotation="(30 * sin(t * pi * 4))")),
    ("waltzer-2", "Waltzer 2", "The clip whirls round in a wider circle.", dict(x="(0.2 * cos(t * pi * 2))", y="(0.15 * sin(t * pi * 2))", rotation="(360 * t)", scale="0.8")),
    ("waltzer-3", "Waltzer 3", "The clip twirls round faster and faster.", dict(x="(0.1 * cos(t * t * pi * 8))", y="(0.1 * sin(t * t * pi * 8))", rotation="(720 * t * t)")),
    ("waltzer-4", "Waltzer 4", "The clip whirls in a loop, tilting as it goes.", dict(x="(0.15 * sin(t * pi * 4))", y="(0.1 * sin(t * pi * 2))", rotation="(20 * cos(t * pi * 4))")),
    ("smaller", "Smaller", "The clip shrinks steadily over the clip.", dict(scale="(1 - 0.5 * t)")),
    ("zoom-spin", "Zoom Spin", "The clip spins as it zooms in and out.", dict(rotation="(360 * t)", scale="(1 - 0.5 * sin(t * pi))")),
    ("spin-in", "Spin In", "The clip spins in from nothing and stays.", dict(rotation=f"(-360 * (1 - {E_ARR}))", scale=f"{E_ARR}")),
    ("spin-out", "Spin Out", "The clip stays, then spins away to nothing.", dict(rotation=f"(360 * {E_LEAVE})", scale=f"(1 - {E_LEAVE})")),
    ("flip-2", "Flip 2", "The clip flips over on its vertical axis twice.", dict(sx="abs(cos(t * pi * 2))")),
    ("flip-3", "Flip 3", "The clip flips over on its horizontal axis twice.", dict(sy="abs(cos(t * pi * 2))")),
    ("flip-4", "Flip 4", "The clip flips over three times, shrinking at each flip.", dict(sx="abs(cos(t * pi * 3))", scale="(0.85 + 0.15 * abs(cos(t * pi * 3)))")),
    ("flip-5", "Flip 5", "The clip flips in at the start and out at the end.", dict(sx=f"({E_ARR} * (1 - {E_LEAVE}))")),
    ("flip-6", "Flip 6", "The clip flips top over bottom in at the start and out at the end.", dict(sy=f"({E_ARR} * (1 - {E_LEAVE}))")),
    ("flip-ii", "Flip II", "The clip flips once over the clip, with a tilt.", dict(sx="abs(cos(t * pi))", rotation="(10 * sin(t * pi))")),
    ("fan-out", "Fan Out", "The clip fans open from a corner and closes again.", dict(rotation=f"(-60 * (1 - {E_ARR}) + 60 * {E_LEAVE})", x=f"(-0.3 * (1 - {E_ARR}) - 0.3 * {E_LEAVE})", y=f"(0.3 * (1 - {E_ARR}) + 0.3 * {E_LEAVE})")),
    ("triplets-1", "Triplets 1", "The clip jumps between three places in turn.", dict(x="(0.25 * (floor(t * 3) - 1))", scale="0.7")),
    ("triplets-2", "Triplets 2", "The clip jumps between three heights in turn.", dict(y="(0.25 * (floor(t * 3) - 1))", scale="0.7")),
    ("quarter-1", "Quarter 1", "The clip visits each quarter of the frame in turn.", dict(x="(if(floor(t * 4) == 1, 0.25, if(floor(t * 4) == 2, 0.25, -0.25)))", y="(if(floor(t * 4) >= 2, 0.25, -0.25))", scale="0.5")),
    ("quarter-2", "Quarter 2", "The clip turns a quarter at a time.", dict(rotation="(90 * floor(t * 4))", scale="0.7")),
    ("rise-spin", "Rise Spin", "The clip rises in, spins, and drops away.", dict(y=f"((1 - {E_ARR}) * 0.6 + {E_LEAVE} * 0.6)", rotation="(360 * t)")),
    ("puzzle", "Puzzle", "The clip jumps into place piece by piece and out again.", dict(x="(0.05 * (floor(t * 6) - floor(t * 6 / 2) * 2 - 0.5))", rotation="(5 * (floor(t * 6) - floor(t * 6 / 2) * 2 - 0.5))")),
    ("sliding-doors-1", "Sliding Doors 1", "The clip slides in like a door and slides out the other way.", dict(sx=f"({E_ARR} * (1 - {E_LEAVE}))", x=f"(-0.5 * (1 - {E_ARR}) + 0.5 * {E_LEAVE})")),
    ("split-up-down-1", "Split up & down 1", "The clip splits in from above and leaves below.", dict(y=f"(-(1 - {E_ARR}) + {E_LEAVE})")),
    ("split-up-down-2", "Split up & down 2", "The clip splits in from below and leaves above.", dict(y=f"((1 - {E_ARR}) - {E_LEAVE})")),
    ("crystal-1", "Crystal 1", "The clip turns like a crystal catching the light.", dict(rotation="(45 * sin(t * pi))", scale="(1 - 0.2 * sin(t * pi))", sx="(1 - 0.15 * sin(t * pi * 2))")),
    ("crystal-2", "Crystal 2", "The clip turns and glints like a cut crystal.", dict(rotation="(-45 * sin(t * pi))", sy="(1 - 0.15 * sin(t * pi * 2))")),
    ("angle-1", "Angle 1", "The clip leans at an angle and straightens.", dict(rotation="(15 * cos(t * pi))")),
    ("angle-2", "Angle 2", "The clip leans the other way and straightens.", dict(rotation="(-15 * cos(t * pi))")),
    ("blinds", "Blinds", "The clip flickers like blinds turning.", dict(sy="(0.6 + 0.4 * abs(cos(t * pi * 4)))")),
    ("zoomroll", "ZoomRoll", "The clip rolls round as it zooms in and back out.", dict(rotation="(360 * t)", scale="(1 + 0.5 * sin(t * pi))")),
    ("spin-fall", "Spin Fall", "The clip spins in place, then falls away.", dict(rotation="(540 * t)", y=f"(0.8 * {E_LEAVE})", opacity=f"(1 - {LEAVE})")),
    ("rollercoaster-1", "Rollercoaster 1", "The clip dips and climbs like a rollercoaster car.", dict(y="(0.2 * sin(t * pi * 2))", rotation="(20 * cos(t * pi * 2))", x="(0.3 * (t - 0.5))")),
    ("rollercoaster-2", "Rollercoaster 2", "The clip loops the loop like a rollercoaster.", dict(x="(0.2 * sin(t * pi * 2))", y="(-0.2 * (1 - cos(t * pi * 2)))", rotation="(360 * t)")),
]

TRAINS = [
    through("x", "-1", "Train 1", 0, "The clip runs in from the left and out to the right like a train."),
    through("x", "1", "Train 2", 0, "The clip runs in from the right and out to the left like a train."),
    through("y", "-1", "Train 3", 0, "The clip runs down in from above and out below."),
    through("y", "1", "Train 4", 0, "The clip runs up in from below and out above."),
]

COMBOS = [combo(slug, name, i + 1, desc, **m) for i, (slug, name, desc, m) in enumerate(COMBO_SPECS)]
COMBOS += [combo(name.lower().replace(" ", "-"), name, 200 + i, desc, **m) for i, (name, _, desc, m) in enumerate(TRAINS)]

PACKAGES = INS + OUTS + COMBOS

for spec in PACKAGES:
    if spec["slug"] == "combo-spin-out":
        spec["card"] = {"progress": 0.9}

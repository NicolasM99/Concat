from lib_wgsl import *

DIAG = ["Bottom Left", "Bottom Right", "Top Left", "Top Right"]

def slide_diag(default):
    return """
struct Params { direction: f32, blur: f32 }
""" + INB + """
fn axis(direction: f32) -> vec2<f32> {
    if (direction < 0.5) {
        return vec2<f32>(-1.0, 1.0);
    } else if (direction < 1.5) {
        return vec2<f32>(1.0, 1.0);
    } else if (direction < 2.5) {
        return vec2<f32>(-1.0, -1.0);
    }
    return vec2<f32>(1.0, -1.0);
}

// Both shots travel together toward a corner, smeared along the way.
fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let dir = axis(params.direction);
    let smear = dir * sin(3.14159265 * progress) * params.blur / 100.0 * 0.06;
    var sum = vec4<f32>(0.0);
    for (var i = -3; i <= 3; i++) {
        let q = uv + smear * (f32(i) / 3.0);
        let to_uv = q + dir * (1.0 - p);
        let from_uv = q - dir * p;
        sum += select(from_at(from_uv), to_at(to_uv), inb(to_uv));
    }
    return sum / 7.0;
}
"""

AXIS_BLUR = DIRBLUR + """
struct Params { amount: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = sin(3.14159265 * progress);
    let d = AXIS * e * params.amount / 100.0 * 0.12;
    let m = smoothstep(0.35, 0.65, progress);
    return mix(blur_from(uv, d), blur_to(uv, d), m);
}
"""

ROTATE = ROT + MIRROR + """
struct Params { blur: f32 }

// The frame turns a quarter with a smear of its own turning; past halfway
// the incoming shot turns the rest of the way into place.
fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let quarter = 1.5707963 * SIGN;
    let angle = select(-quarter * (1.0 - p), quarter * p, p < 0.5) ;
    let e = sin(3.14159265 * progress);
    let spread = e * params.blur / 100.0 * 0.25 * SIGN;
    var sum = vec4<f32>(0.0);
    for (var i = -3; i <= 3; i++) {
        let a = angle + spread * f32(i) / 3.0;
        let q = mirror_uv(rot_uv(uv, vec2<f32>(0.5), a, 1.0 + 0.3 * e));
        sum += select(to_at(q), from_at(q), p < 0.5);
    }
    return sum / 7.0;
}
"""

SWIRL_CCW = """
struct Params { twist: f32 }

fn swirl_uv(uv: vec2<f32>, amount: f32) -> vec2<f32> {
    let c = (uv - vec2<f32>(0.5)) * frame.size;
    let d = length(c) / frame.size.y;
    let a = amount * (1.0 - smoothstep(0.0, 0.7, d));
    let s = sin(a);
    let co = cos(a);
    return vec2<f32>(c.x * co - c.y * s, c.x * s + c.y * co) / frame.size + vec2<f32>(0.5);
}

// The swirl of Swirl, turning the other way round.
fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let k = -sin(p * 3.14159265) * params.twist * 0.06;
    let a = from_at(swirl_uv(uv, k));
    let b = to_at(swirl_uv(uv, -k));
    return mix(a, b, p);
}
"""

def flip(axis_x):
    coord = "x" if axis_x else "y"
    other = "y" if axis_x else "x"
    return """
struct Params { depth: f32 }
""" + INB + """
// A card turning about its {axis} axis: the near half grows, the far half
// shrinks into perspective, and past the edge-on moment its back is the
// incoming shot.
fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    var theta = p * 3.14159265;
    let back = theta > 1.5707963;
    if (back) {
        theta = theta - 3.14159265;
    }
    let k = params.depth / 100.0 * 1.2;
    let c = uv - vec2<f32>(0.5);
    let den = cos(theta) - c.{c} * sin(theta) * k;
    if (abs(den) < 1e-4) {
        return vec4<f32>(0.0, 0.0, 0.0, 1.0);
    }
    let local = c.{c} / den;
    let depth = 1.0 + local * sin(theta) * k;
    var q: vec2<f32>;
    q.{c} = local + 0.5;
    q.{o} = c.{o} * depth + 0.5;
    if (!inb(q)) {
        return vec4<f32>(0.0, 0.0, 0.0, 1.0);
    }
    let shade = mix(0.55, 1.0, abs(cos(theta)));
    let colour = select(from_at(q), to_at(q), back);
    return vec4<f32>(colour.rgb * shade, colour.a);
}
""".replace("{c}", coord).replace("{o}", other).replace("{axis}", "vertical" if axis_x else "horizontal")

PACKAGES = [
T("bottom-left", "Bottom Left II", "Slide", 30,
  "Both shots slide together toward a corner of the frame, smeared with motion as they go.",
  slide_diag(0), [p("direction", "Direction", 0, 3, 0, values=[0, 1, 2, 3], labels=DIAG), p("blur", "Blur", 0, 100, 60)],
  xfade="slidedown"),

T("vertical-blur-transition", "Vertical Blur", "Blur", 31,
  "The cut smears both shots up and down and they resolve on the incoming one.",
  AXIS_BLUR.replace("AXIS", "vec2<f32>(0.0, 1.0)"), [p("amount", "Amount", 0, 100, 60)], xfade="fade"),

T("vertical-blur-ii", "Vertical Blur II", "Blur", 32,
  "A heavier vertical smear: the outgoing shot streaks away top to bottom as the incoming one streaks in.",
  AXIS_BLUR.replace("AXIS", "vec2<f32>(0.0, 1.8)"), [p("amount", "Amount", 0, 100, 80)], xfade="fade"),

T("horizontal-blur", "Horizontal Blur", "Blur", 33,
  "The cut smears both shots sideways and they resolve on the incoming one.",
  AXIS_BLUR.replace("AXIS", "vec2<f32>(1.0, 0.0)"), [p("amount", "Amount", 0, 100, 60)], xfade="hblur"),

T("rotate-cw-ii", "Rotate CW II", "Spin", 34,
  "The frame turns a quarter clockwise in a blur of its own spin and lands on the incoming shot.",
  ROTATE.replace("SIGN", "1.0"), [p("blur", "Blur", 0, 100, 70)]),

T("rotate-ccw-ii", "Rotate CCW II", "Spin", 35,
  "The frame turns a quarter anticlockwise in a blur of its own spin and lands on the incoming shot.",
  ROTATE.replace("SIGN", "-1.0"), [p("blur", "Blur", 0, 100, 70)]),

T("anti-cw-swirl", "Anti-CW Swirl", "Spin", 36,
  "The cut twists both pictures anticlockwise around its centre and untwists into the next shot.",
  SWIRL_CCW, [p("twist", "Twist", 0, 100, 70)], shelves=["Distortion & Glitch"]),

T("flip", "Flip", "Spin", 37,
  "The frame turns over like a card on its vertical axis, the incoming shot on its back.",
  flip(True), [p("depth", "Depth", 0, 100, 50)]),

T("flip-ii", "Flip II", "Spin", 38,
  "The frame turns over like a card on its horizontal axis, the incoming shot on its back.",
  flip(False), [p("depth", "Depth", 0, 100, 50)]),

T("axis-rotation", "Axis Rotation", "Spin", 39,
  "The frame pulls back, swings round its vertical axis to the incoming shot and comes forward again.",
  INB + """
struct Params { depth: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let shrink = 1.0 - 0.3 * sin(3.14159265 * p);
    var theta = p * 3.14159265;
    let back = theta > 1.5707963;
    if (back) {
        theta = theta - 3.14159265;
    }
    let k = params.depth / 100.0 * 1.2;
    let c = (uv - vec2<f32>(0.5)) / shrink;
    let den = cos(theta) - c.x * sin(theta) * k;
    let bg = vec4<f32>(0.01, 0.01, 0.012, 1.0);
    if (abs(den) < 1e-4) {
        return bg;
    }
    let lx = c.x / den;
    let q = vec2<f32>(lx + 0.5, c.y * (1.0 + lx * sin(theta) * k) + 0.5);
    if (!inb(q)) {
        return bg;
    }
    let shade = mix(0.5, 1.0, abs(cos(theta)));
    let colour = select(from_at(q), to_at(q), back);
    return vec4<f32>(colour.rgb * shade, colour.a);
}
""", [p("depth", "Depth", 0, 100, 60)]),

T("inhale", "Inhale", "Zoom", 40,
  "The outgoing shot is drawn in, pinched and shrinking, to a point at the centre, uncovering the incoming one.",
  INB + """
struct Params { pinch: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let s = max(1.0 - p, 0.0001);
    let c = (uv - vec2<f32>(0.5)) * frame.size / frame.size.y;
    let r = length(c);
    let bend = 1.0 + p * params.pinch / 100.0 * 2.0;
    let rr = pow(r / s, bend) * s;
    let dir = select(c / r, vec2<f32>(0.0), r < 1e-5);
    let q = (dir * rr / s) * frame.size.y / frame.size + vec2<f32>(0.5);
    let z = 1.0 + 0.1 * (1.0 - p);
    let b = to_at((uv - vec2<f32>(0.5)) / z + vec2<f32>(0.5));
    if (inb(q) && p < 0.999) {
        return mix(from_at(q), b, smoothstep(0.8, 1.0, p));
    }
    return b;
}
""", [p("pinch", "Pinch", 0, 100, 60)], xfade="zoomin"),

T("shake-transition", "Shake 3", "Basic", 41,
  "Both shots shake hard, like a handheld camera knocked, as one cuts to the other.",
  """
struct Params { strength: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = sin(3.14159265 * progress) * params.strength / 100.0;
    let t = floor(progress * 40.0);
    let off = (vec2<f32>(hash(vec2<f32>(t, 1.0), 2.0), hash(vec2<f32>(t, 2.0), 2.0)) - vec2<f32>(0.5)) * 0.08 * e;
    let z = 1.0 + 0.1 * e;
    let q = (uv - vec2<f32>(0.5)) / z + vec2<f32>(0.5) + off;
    var sum = vec4<f32>(0.0);
    for (var i = -2; i <= 2; i++) {
        let s = q + off * f32(i) * 0.3;
        sum += select(from_at(s), to_at(s), progress >= 0.5);
    }
    return sum / 5.0;
}
""", [p("strength", "Strength", 0, 100, 60)]),

T("open-horizontally", "Open Horizontally", "Slide", 42,
  "The outgoing shot splits down the middle and its halves slide apart to either side.",
  """
struct Params { gap: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let half = p * 0.5;
    if (uv.x < 0.5 - half) {
        return from_at(vec2<f32>(uv.x + half, uv.y));
    }
    if (uv.x > 0.5 + half) {
        return from_at(vec2<f32>(uv.x - half, uv.y));
    }
    let z = 1.0 + 0.15 * (1.0 - p) * params.gap / 100.0;
    let b = to_at((uv - vec2<f32>(0.5)) / z + vec2<f32>(0.5));
    let shade = 1.0 - 0.5 * (1.0 - p) * params.gap / 100.0;
    return vec4<f32>(b.rgb * shade, b.a);
}
""", [p("gap", "Depth", 0, 100, 50)], xfade="horzopen"),

T("open-vertically", "Open Vertically", "Slide", 43,
  "The outgoing shot splits across the middle and its halves slide apart up and down.",
  """
struct Params { gap: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let half = p * 0.5;
    if (uv.y < 0.5 - half) {
        return from_at(vec2<f32>(uv.x, uv.y + half));
    }
    if (uv.y > 0.5 + half) {
        return from_at(vec2<f32>(uv.x, uv.y - half));
    }
    let z = 1.0 + 0.15 * (1.0 - p) * params.gap / 100.0;
    let b = to_at((uv - vec2<f32>(0.5)) / z + vec2<f32>(0.5));
    let shade = 1.0 - 0.5 * (1.0 - p) * params.gap / 100.0;
    return vec4<f32>(b.rgb * shade, b.a);
}
""", [p("gap", "Depth", 0, 100, 50)], xfade="vertopen"),

T("open", "Open", "Wipe", 44,
  "A rectangle of the incoming shot opens from the centre out to the frame's edges.",
  """
struct Params { softness: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let d = abs(uv - vec2<f32>(0.5)) * 2.0;
    let soft = max(params.softness / 100.0, 0.005) * 0.2;
    let edge = p * (1.0 + 2.0 * soft);
    let m = smoothstep(edge - soft, edge, max(d.x, d.y));
    return mix(to_at(uv), from_at(uv), m);
}
""", [p("softness", "Softness", 0, 100, 10)], xfade="rectcrop"),

T("switch", "Switch", "Slide", 45,
  "The two shots trade places: the outgoing one slides back and aside as the incoming one comes forward from the other side.",
  INB + """
struct Params { spread: f32 }

fn card(uv: vec2<f32>, centre_x: f32, scale: f32) -> vec2<f32> {
    return (uv - vec2<f32>(centre_x, 0.5)) / scale + vec2<f32>(0.5);
}

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let e = sin(3.14159265 * p);
    let k = params.spread / 100.0;
    let fx = 0.5 - e * 0.3 * k;
    let tx = 0.5 + e * 0.3 * k;
    let fs = 1.0 - 0.35 * p - 0.1 * e;
    let ts = 0.65 + 0.35 * p - 0.1 * e;
    let fq = card(uv, fx, fs);
    let tq = card(uv, tx, ts);
    let bg = vec4<f32>(0.02, 0.02, 0.025, 1.0);
    let f = select(bg, vec4<f32>(from_at(fq).rgb * mix(1.0, 0.5, p), 1.0), inb(fq));
    let t = select(bg, vec4<f32>(to_at(tq).rgb * mix(0.5, 1.0, p), 1.0), inb(tq));
    // The nearer card, the larger, is drawn over the other.
    if (p < 0.5) {
        return select(t, f, inb(fq));
    }
    return select(f, t, inb(tq));
}
""", [p("spread", "Spread", 0, 100, 70)]),

T("stretch", "Stretch", "Distort", 46,
  "The outgoing shot stretches wide and smears away; the incoming one arrives stretched and springs back to shape.",
  """
struct Params { amount: f32 }

fn stretched(uv: vec2<f32>, sx: f32, to_side: bool) -> vec4<f32> {
    var sum = vec4<f32>(0.0);
    for (var i = 0; i < 6; i++) {
        let s = sx * (1.0 + f32(i) * 0.04 * (sx - 1.0));
        let q = vec2<f32>((uv.x - 0.5) / s + 0.5, uv.y);
        sum += select(from_at(q), to_at(q), to_side);
    }
    return sum / 6.0;
}

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let k = params.amount / 100.0 * 6.0;
    if (progress < 0.5) {
        let t = progress * 2.0;
        return stretched(uv, 1.0 + k * t * t, false);
    }
    let t = (1.0 - progress) * 2.0;
    return stretched(uv, 1.0 + k * t * t, true);
}
""", [p("amount", "Amount", 0, 100, 60)], xfade="squeezeh"),

T("stretch-ii", "Stretch II", "Distort", 47,
  "The outgoing shot stretches tall and smears away; the incoming one arrives stretched and springs back to shape.",
  """
struct Params { amount: f32 }

fn stretched(uv: vec2<f32>, sy: f32, to_side: bool) -> vec4<f32> {
    var sum = vec4<f32>(0.0);
    for (var i = 0; i < 6; i++) {
        let s = sy * (1.0 + f32(i) * 0.04 * (sy - 1.0));
        let q = vec2<f32>(uv.x, (uv.y - 0.5) / s + 0.5);
        sum += select(from_at(q), to_at(q), to_side);
    }
    return sum / 6.0;
}

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let k = params.amount / 100.0 * 6.0;
    if (progress < 0.5) {
        let t = progress * 2.0;
        return stretched(uv, 1.0 + k * t * t, false);
    }
    let t = (1.0 - progress) * 2.0;
    return stretched(uv, 1.0 + k * t * t, true);
}
""", [p("amount", "Amount", 0, 100, 60)], xfade="squeezev"),

T("stretch-right", "Stretch Right", "Distort", 48,
  "The outgoing shot is pulled out to the right; the incoming one is pulled in after it from the left.",
  """
struct Params { amount: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let k = 1.0 + params.amount / 100.0 * 2.0;
    let edge = p;
    if (uv.x >= edge) {
        // The outgoing shot, its left edge dragged right and stretched.
        let local = (uv.x - edge) / max(1.0 - edge, 1e-4);
        let x = pow(local, mix(1.0, k, sin(3.14159265 * p)));
        return from_at(vec2<f32>(x, uv.y));
    }
    let local = uv.x / max(edge, 1e-4);
    let x = 1.0 - pow(1.0 - local, mix(1.0, k, sin(3.14159265 * p)));
    return to_at(vec2<f32>(x, uv.y));
}
""", [p("amount", "Amount", 0, 100, 60)], xfade="slideright"),

T("stretch-left", "Stretch Left", "Distort", 49,
  "The outgoing shot is pulled out to the left; the incoming one is pulled in after it from the right.",
  """
struct Params { amount: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let k = 1.0 + params.amount / 100.0 * 2.0;
    let edge = 1.0 - p;
    let bend = mix(1.0, k, sin(3.14159265 * p));
    if (uv.x <= edge) {
        let local = uv.x / max(edge, 1e-4);
        let x = 1.0 - pow(1.0 - local, bend);
        return from_at(vec2<f32>(x, uv.y));
    }
    let local = (uv.x - edge) / max(1.0 - edge, 1e-4);
    let x = pow(local, bend);
    return to_at(vec2<f32>(x, uv.y));
}
""", [p("amount", "Amount", 0, 100, 60)], xfade="slideleft"),

T("squeeze", "Squeeze", "Distort", 50,
  "The outgoing shot is squeezed to a sliver at the centre and the incoming one expands out of it.",
  INB + """
struct Params { direction: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let horizontal = params.direction < 0.5;
    let bg = vec4<f32>(0.0, 0.0, 0.0, 1.0);
    if (p < 0.5) {
        let s = max(1.0 - p * 2.0, 1e-4);
        var q = uv;
        if (horizontal) {
            q.x = (uv.x - 0.5) / s + 0.5;
        } else {
            q.y = (uv.y - 0.5) / s + 0.5;
        }
        return select(bg, from_at(q), inb(q));
    }
    let s = max((p - 0.5) * 2.0, 1e-4);
    var q = uv;
    if (horizontal) {
        q.x = (uv.x - 0.5) / s + 0.5;
    } else {
        q.y = (uv.y - 0.5) / s + 0.5;
    }
    return select(bg, to_at(q), inb(q));
}
""", [p("direction", "Direction", 0, 1, 0, values=[0, 1], labels=["Horizontal", "Vertical"])], xfade="squeezeh"),

T("whirlpool", "Whirlpool", "Spin", 51,
  "The outgoing shot spirals down into the centre like water down a drain and the incoming one spirals up out of it.",
  """
struct Params { turns: f32 }

fn whirl(uv: vec2<f32>, amount: f32, zoom: f32) -> vec2<f32> {
    let c = (uv - vec2<f32>(0.5)) * frame.size / frame.size.y;
    let r = length(c);
    let a = amount * (1.0 - smoothstep(0.0, 0.9, r)) * 6.2831853;
    let s = sin(a);
    let co = cos(a);
    let t = vec2<f32>(c.x * co - c.y * s, c.x * s + c.y * co) * zoom;
    return t * frame.size.y / frame.size + vec2<f32>(0.5);
}

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let k = params.turns;
    let fa = from_at(whirl(uv, p * k, 1.0 + p * 2.0));
    let ta = to_at(whirl(uv, -(1.0 - p) * k, 1.0 + (1.0 - p) * 2.0));
    return mix(fa, ta, smoothstep(0.3, 0.7, p));
}
""", [p("turns", "Turns", 0, 3, 1.5, step=0.1, unit="")]),

T("distortion", "Distortion", "Distort", 52,
  "A heat-haze ripple warps the outgoing shot into the incoming one.",
  NOISE + """
struct Params { amount: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = sin(3.14159265 * progress) * params.amount / 100.0;
    let q = uv * 6.0 + vec2<f32>(0.0, progress * 3.0);
    let off = (vec2<f32>(fbm(q), fbm(q + vec2<f32>(5.2, 1.3))) - vec2<f32>(0.5)) * 0.12 * e;
    return mix(from_at(uv + off), to_at(uv - off), smoothstep(0.25, 0.75, progress));
}
""", [p("amount", "Amount", 0, 100, 60)]),

T("color-swirl", "Color Swirl", "Spin", 53,
  "Both shots swirl together through a wheel of colour into the next shot.",
  RAINBOW + """
struct Params { twist: f32 }

fn swirl_uv(uv: vec2<f32>, amount: f32) -> vec2<f32> {
    let c = (uv - vec2<f32>(0.5)) * frame.size;
    let d = length(c) / frame.size.y;
    let a = amount * (1.0 - smoothstep(0.0, 0.7, d));
    let s = sin(a);
    let co = cos(a);
    return vec2<f32>(c.x * co - c.y * s, c.x * s + c.y * co) / frame.size + vec2<f32>(0.5);
}

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let e = sin(p * 3.14159265);
    let k = e * params.twist * 0.06;
    let c = mix(from_at(swirl_uv(uv, k)), to_at(swirl_uv(uv, -k)), p);
    let d = (uv - vec2<f32>(0.5)) * frame.size / frame.size.y;
    let hue = fract(atan2(d.y, d.x) / 6.2831853 + length(d) * 2.0 - p * 2.0);
    return vec4<f32>(mix(c.rgb, rainbow(hue) * (luma(c.rgb) * 1.5 + 0.1), e * 0.6), c.a);
}
""", [p("twist", "Twist", 0, 100, 70)], shelves=["Distortion & Glitch"]),

T("cartoon-swirl", "Cartoon Swirl", "Spin", 54,
  "A cartoon spiral spins across the cut, the pictures flattened to poster colours as they pass.",
  """
struct Params { bands: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let e = sin(p * 3.14159265);
    let d = (uv - vec2<f32>(0.5)) * frame.size / frame.size.y;
    let r = length(d);
    let a = atan2(d.y, d.x) / 6.2831853;
    let spiral = fract(a * 2.0 + r * max(params.bands, 1.0) - p * 4.0);
    let cover = smoothstep(1.0 - e * 1.2, 1.0 - e * 1.2 + 0.05, 1.0 - r * 0.8);
    let base = select(from_at(uv), to_at(uv), p >= 0.5);
    let levels = 4.0;
    let poster = from_display(floor(clamp(to_display(base.rgb), vec3<f32>(0.0), vec3<f32>(1.0)) * levels + 0.5) / levels);
    let ink = select(vec3<f32>(1.0, 0.85, 0.2), vec3<f32>(0.05, 0.05, 0.08), spiral < 0.5);
    let rgb = mix(mix(base.rgb, poster, e), ink, cover);
    return vec4<f32>(rgb, base.a);
}
""", [p("bands", "Bands", 1, 12, 6, unit="")]),
]

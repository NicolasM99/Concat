from lib_wgsl import *

def wave(sign):
    coord = "uv.x" if sign > 0 else "1.0 - uv.x"
    return """
struct Params { waves: f32, height: f32 }

// A wavy edge crosses the frame, the outgoing shot rippling where it meets it.
fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let amp = params.height / 100.0 * 0.08;
    let edge = p * (1.0 + 2.0 * amp + 0.04) - amp - 0.02 + amp * sin(uv.y * params.waves * 6.2831853 + progress * 8.0);
    let x = COORD;
    let near = exp(-pow((x - edge) / 0.08, 2.0));
    let wobble = vec2<f32>(0.0, sin(x * 40.0 - progress * 20.0) * 0.01 * near);
    let m = smoothstep(edge - 0.01, edge + 0.01, x);
    return mix(to_at(uv - wobble), from_at(uv + wobble), m);
}
""".replace("COORD", coord)

SLICES = INB + """
struct Params { slices: f32 }

// The incoming shot arrives in slices, each sliding in from alternate
// sides a beat after the one before.
fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let n = max(params.slices, 2.0);
    let along = ALONG;
    let across = ACROSS;
    let i = floor(across * n);
    let delay = i / n * 0.5;
    let t = smoothstep(0.0, 1.0, clamp((progress - delay) / 0.5, 0.0, 1.0));
    let side = select(-1.0, 1.0, fract(i * 0.5) < 0.25);
    let shift = (1.0 - t) * side;
    let moved = along + shift;
    if (moved >= 0.0 && moved <= 1.0 && t > 0.0) {
        return to_at(REBUILD);
    }
    return from_at(uv);
}
"""

def slices(kind):
    if kind == "h":
        return SLICES.replace("ALONG", "uv.x").replace("ACROSS", "uv.y").replace("REBUILD", "vec2<f32>(moved, uv.y)")
    if kind == "v":
        return SLICES.replace("ALONG", "uv.y").replace("ACROSS", "uv.x").replace("REBUILD", "vec2<f32>(uv.x, moved)")
    # diagonal: slices across the diagonal, sliding along it
    return INB + """
struct Params { slices: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let n = max(params.slices, 2.0);
    let across = (uv.x + uv.y) * 0.5;
    let i = floor(across * n);
    let delay = i / n * 0.5;
    let t = smoothstep(0.0, 1.0, clamp((progress - delay) / 0.5, 0.0, 1.0));
    let side = select(-1.0, 1.0, fract(i * 0.5) < 0.25);
    let q = uv + vec2<f32>(1.0, -1.0) * (1.0 - t) * side;
    if (inb(q) && t > 0.0) {
        return to_at(q);
    }
    return from_at(uv);
}
"""

PAGE = """
struct Params { radius: f32 }

const PI: f32 = 3.14159265;
""" + INB + """
// A page curl: the outgoing shot is a sheet lifted from the bottom-right
// corner and rolled over a cylinder that travels to the top-left, its pale
// back laid over what is still flat, the incoming shot beneath.
fn page(q: vec2<f32>) -> bool {
    return inb(q);
}

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let dn = normalize(vec2<f32>(1.0, 1.0));
    let r = max(params.radius / 100.0, 0.01) * 0.25;
    let smax = dot(vec2<f32>(1.0, 1.0), dn);
    let pos = mix(smax + 0.02, -r * PI - 0.02, smoothstep(0.0, 1.0, progress));
    let s = dot(uv, dn);
    let dist = s - pos;
    let paper = vec3<f32>(0.85, 0.84, 0.8);
    if (dist < 0.0) {
        // Flat: the back of the turned page may lie over it.
        let sb = 2.0 * pos + PI * r - s;
        let qb = uv + dn * (sb - s);
        if (page(qb) && sb > pos) {
            let c = from_at(qb);
            return vec4<f32>(mix(c.rgb, paper, 0.75) * 0.95, 1.0);
        }
        return from_at(uv);
    }
    if (dist <= r) {
        let a = asin(clamp(dist / r, 0.0, 1.0));
        let sb = pos + (PI - a) * r;
        let qb = uv + dn * (sb - s);
        if (page(qb)) {
            let c = from_at(qb);
            return vec4<f32>(mix(c.rgb, paper, 0.75) * mix(0.75, 1.0, cos(a)), 1.0);
        }
        let sf = pos + a * r;
        let qf = uv + dn * (sf - s);
        if (page(qf)) {
            let c = from_at(qf);
            return vec4<f32>(c.rgb * mix(1.0, 0.55, a / (PI * 0.5)), c.a);
        }
    }
    // Uncovered: the incoming shot, shadowed close to the roll.
    let shadow = 1.0 - 0.5 * exp(-max(dist - r, 0.0) / (r * 0.8));
    let b = to_at(uv);
    let lifted = step(r, dist);
    return vec4<f32>(b.rgb * mix(1.0, shadow, lifted), b.a);
}
"""

FOLD = """
struct Params { depth: f32 }

// The right half of the outgoing shot folds over onto the left like a
// sheet of paper; the back of the flap is the left half of the incoming
// shot, and the right half of it lies beneath.
fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let theta = smoothstep(0.0, 1.0, progress) * 3.14159265;
    let k = params.depth / 100.0 * 1.5;
    let dx = uv.x - 0.5;
    let den = cos(theta) - dx * sin(theta) * k;
    if (abs(den) > 1e-4) {
        let u = dx / den;
        if (u >= 0.0 && u <= 0.5) {
            let depth = 1.0 + u * sin(theta) * k;
            let y = (uv.y - 0.5) * depth + 0.5;
            if (y >= 0.0 && y <= 1.0) {
                let shade = mix(0.55, 1.0, abs(cos(theta)));
                if (cos(theta) >= 0.0) {
                    let c = from_at(vec2<f32>(0.5 + u, y));
                    return vec4<f32>(c.rgb * shade, c.a);
                }
                let c = to_at(vec2<f32>(0.5 - u, y));
                return vec4<f32>(c.rgb * shade, c.a);
            }
        }
    }
    if (uv.x > 0.5) {
        return to_at(uv);
    }
    return from_at(uv);
}
"""

PACKAGES = [
T("wave-right", "Wave Right", "Wipe", 60,
  "A rippling wave carries the incoming shot across the frame from left to right.",
  wave(1), [p("waves", "Waves", 1, 8, 3, unit=""), p("height", "Height", 0, 100, 40)], xfade="wiperight"),

T("wave-left", "Wave Left", "Wipe", 61,
  "A rippling wave carries the incoming shot across the frame from right to left.",
  wave(-1), [p("waves", "Waves", 1, 8, 3, unit=""), p("height", "Height", 0, 100, 40)], xfade="wipeleft"),

T("dots-right", "Dots Right", "Wipe", 62,
  "A field of dots grows from left to right, each one a window onto the incoming shot, until they join.",
  """
struct Params { dots: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let n = max(params.dots, 4.0);
    let cells = vec2<f32>(n, n * frame.size.y / frame.size.x);
    let cell = floor(uv * cells);
    let centre = (cell + vec2<f32>(0.5)) / cells;
    let d = length((uv - centre) * cells);
    let grow = clamp(progress * 2.4 - centre.x * 1.4, 0.0, 1.0) * 0.75;
    let m = smoothstep(grow - 0.05, grow + 0.05, d);
    return mix(to_at(uv), from_at(uv), m);
}
""", [p("dots", "Dots", 4, 40, 16, unit="")], xfade="dissolve"),

T("circular-slices-ii", "Circular Slices II", "Wipe", 63,
  "Concentric rings turn in alternate directions, each turning over to the incoming shot in its own time.",
  ROT + """
struct Params { rings: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let n = max(params.rings, 2.0);
    let d = (uv - vec2<f32>(0.5)) * frame.size / frame.size.y;
    let r = length(d);
    let ring = floor(r * n * 1.2);
    let delay = min(ring / (n * 1.2), 1.0) * 0.5;
    let t = smoothstep(0.0, 1.0, clamp((progress - delay) / 0.5, 0.0, 1.0));
    let side = select(-1.0, 1.0, fract(ring * 0.5) < 0.25);
    let spin = sin(3.14159265 * t) * 0.8 * side;
    let q = rot_uv(uv, vec2<f32>(0.5), spin, 1.0);
    return select(from_at(q), to_at(q), t >= 0.5);
}
""", [p("rings", "Rings", 2, 12, 5, unit="")], xfade="radial"),

T("split", "Split", "Slide", 64,
  "The outgoing shot splits in two halves that slide off up and down, uncovering the incoming one.",
  """
struct Params { direction: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    if (params.direction < 0.5) {
        let up = uv.x < 0.5;
        let y = select(uv.y - p, uv.y + p, up);
        if (y >= 0.0 && y <= 1.0) {
            return from_at(vec2<f32>(uv.x, y));
        }
        return to_at(uv);
    }
    let left = uv.y < 0.5;
    let x = select(uv.x - p, uv.x + p, left);
    if (x >= 0.0 && x <= 1.0) {
        return from_at(vec2<f32>(x, uv.y));
    }
    return to_at(uv);
}
""", [p("direction", "Direction", 0, 1, 0, values=[0, 1], labels=["Vertical", "Horizontal"])]),

T("split-iii", "Split III", "Slide", 65,
  "The outgoing shot breaks into three strips that slide away in opposite directions.",
  """
struct Params { stagger: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let strip = min(floor(uv.x * 3.0), 2.0);
    let delay = strip * params.stagger / 100.0 * 0.15;
    let t = smoothstep(0.0, 1.0, clamp((progress - delay) / (1.0 - 0.3 * params.stagger / 100.0), 0.0, 1.0));
    let dir = select(1.0, -1.0, strip == 1.0);
    let y = uv.y + t * dir;
    if (y >= 0.0 && y <= 1.0) {
        return from_at(vec2<f32>(uv.x, y));
    }
    return to_at(uv);
}
""", [p("stagger", "Stagger", 0, 100, 50)]),

T("split-iv", "Split IV", "Slide", 66,
  "The outgoing shot breaks into four quarters that fly off to the corners.",
  """
struct Params { spin: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let quarter = vec2<f32>(select(-1.0, 1.0, uv.x >= 0.5), select(-1.0, 1.0, uv.y >= 0.5));
    let q = uv - quarter * p * 0.5;
    let inside = (q.x - 0.5) * quarter.x >= 0.0 && (q.y - 0.5) * quarter.y >= 0.0 && q.x >= 0.0 && q.x <= 1.0 && q.y >= 0.0 && q.y <= 1.0;
    if (inside) {
        return from_at(q);
    }
    let z = 1.0 + 0.2 * (1.0 - p) * params.spin / 100.0;
    return to_at((uv - vec2<f32>(0.5)) / z + vec2<f32>(0.5));
}
""", [p("spin", "Depth", 0, 100, 50)]),

T("horizontal-slice", "Horizontal Slice", "Slide", 67,
  "The incoming shot slides in as horizontal slices, alternate ones from opposite sides.",
  slices("h"), [p("slices", "Slices", 2, 20, 6, unit="")], xfade="hlslice"),

T("vertical-slices", "Vertical Slices", "Slide", 68,
  "The incoming shot slides in as vertical slices, alternate ones from above and below.",
  slices("v"), [p("slices", "Slices", 2, 20, 6, unit="")], xfade="vuslice"),

T("diagonal-slices", "Diagonal Slices", "Slide", 69,
  "The incoming shot slides in as diagonal slices, alternate ones from opposite corners.",
  slices("d"), [p("slices", "Slices", 2, 20, 6, unit="")], xfade="diagtl"),

T("horizontal-lines", "Horizontal Lines", "Wipe", 70,
  "Thin horizontal lines draw the incoming shot in, alternate lines from opposite sides.",
  """
struct Params { lines: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let n = max(params.lines, 4.0);
    let line = floor(uv.y * n);
    let even = fract(line * 0.5) < 0.25;
    let x = select(1.0 - uv.x, uv.x, even);
    let jitter = hash(vec2<f32>(line, 0.0), 3.0) * 0.3;
    let edge = progress * 1.3 - jitter;
    let m = step(edge, x);
    return mix(to_at(uv), from_at(uv), m);
}
""", [p("lines", "Lines", 4, 80, 24, unit="")], xfade="hlwind"),

T("shutter", "Shutter", "Wipe", 71,
  "Shutter slats close over the outgoing shot and open on the incoming one.",
  """
struct Params { slats: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let n = max(params.slats, 2.0);
    let local = fract(uv.y * n);
    let close = sin(3.14159265 * smoothstep(0.0, 1.0, progress));
    let covered = abs(local - 0.5) * 2.0 > 1.0 - close * 1.02;
    let base = select(from_at(uv), to_at(uv), progress >= 0.5);
    let slat = vec3<f32>(0.02) + vec3<f32>(0.04) * (1.0 - abs(local - 0.5) * 2.0);
    return select(base, vec4<f32>(slat, 1.0), covered);
}
""", [p("slats", "Slats", 2, 24, 8, unit="")]),

T("shutter-ii", "Shutter II", "Wipe", 72,
  "Vertical blinds turn one after another from the outgoing shot to the incoming one.",
  """
struct Params { blinds: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let n = max(params.blinds, 2.0);
    let i = floor(uv.x * n);
    let local = fract(uv.x * n);
    let t = clamp(progress * 1.6 - i / n * 0.6, 0.0, 1.0);
    let w = abs(cos(t * 3.14159265));
    let inside = abs(local - 0.5) * 2.0 <= w;
    let q = vec2<f32>((i + 0.5 + (local - 0.5) / max(w, 1e-4)) / n, uv.y);
    let shade = mix(0.5, 1.0, w);
    let c = select(from_at(q), to_at(q), t >= 0.5);
    return select(vec4<f32>(0.0, 0.0, 0.0, 1.0), vec4<f32>(c.rgb * shade, c.a), inside);
}
""", [p("blinds", "Blinds", 2, 24, 8, unit="")]),

T("blocks", "Blocks", "Wipe", 73,
  "The frame breaks into blocks that pop over to the incoming shot in a scattered order.",
  INB + """
struct Params { blocks: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let n = max(params.blocks, 2.0);
    let cells = vec2<f32>(n, max(floor(n * frame.size.y / frame.size.x + 0.5), 1.0));
    let cell = floor(uv * cells);
    let start = hash(cell, 11.0) * 0.6;
    let t = clamp((progress - start) / 0.4, 0.0, 1.0);
    let pop = 1.0 - 0.25 * sin(3.14159265 * t);
    let local = (fract(uv * cells) - vec2<f32>(0.5)) / pop + vec2<f32>(0.5);
    if (!inb(local)) {
        return vec4<f32>(0.0, 0.0, 0.0, 1.0);
    }
    let q = (cell + local) / cells;
    return select(from_at(q), to_at(q), t >= 0.5);
}
""", [p("blocks", "Blocks", 2, 30, 10, unit="")], xfade="pixelize"),

T("cutout-flip", "Cutout Flip", "Spin", 74,
  "Tiles of the frame flip over one after another in a sweep, each showing the incoming shot on its back.",
  """
struct Params { tiles: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let n = max(params.tiles, 2.0);
    let cells = vec2<f32>(n, max(floor(n * frame.size.y / frame.size.x + 0.5), 1.0));
    let cell = floor(uv * cells);
    let centre = (cell + vec2<f32>(0.5)) / cells;
    let t = clamp(progress * 2.0 - (centre.x + centre.y) * 0.5, 0.0, 1.0);
    let w = abs(cos(t * 3.14159265));
    let local = fract(uv * cells) - vec2<f32>(0.5);
    if (abs(local.x) > w * 0.5) {
        return vec4<f32>(0.0, 0.0, 0.0, 1.0);
    }
    let q = (cell + vec2<f32>(local.x / max(w, 1e-4), local.y) + vec2<f32>(0.5)) / cells;
    let c = select(from_at(q), to_at(q), t >= 0.5);
    return vec4<f32>(c.rgb * mix(0.5, 1.0, w), c.a);
}
""", [p("tiles", "Tiles", 2, 16, 6, unit="")]),

T("windmill", "Windmill", "Wipe", 75,
  "Windmill blades sweep round the centre, each blade uncovering a slice of the incoming shot.",
  """
struct Params { blades: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let n = max(params.blades, 2.0);
    let d = (uv - vec2<f32>(0.5)) * frame.size / frame.size.y;
    let a = fract(atan2(d.y, d.x) / 6.2831853 + 0.25);
    let local = fract(a * n);
    let m = smoothstep(0.0, 0.01, local - smoothstep(0.0, 1.0, progress));
    return mix(to_at(uv), from_at(uv), m);
}
""", [p("blades", "Blades", 2, 12, 4, unit="")], xfade="radial"),

T("curling-wave", "Curling Wave", "Wipe", 76,
  "A curling wave rolls across the frame, bending the outgoing shot under as the incoming one follows.",
  """
struct Params { curl: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let amp = params.curl / 100.0;
    let edge = p * 1.4 - 0.2 + 0.06 * amp * sin(uv.y * 9.0 + p * 12.0);
    let d = uv.x - edge;
    if (d > 0.0) {
        // Ahead of the wave the outgoing shot bulges and is drawn under.
        let pull = exp(-d / 0.12) * 0.12 * amp;
        let q = vec2<f32>(uv.x - pull, uv.y + sin(uv.x * 30.0) * pull * 0.3);
        let crest = exp(-d / 0.02) * 0.6 * amp;
        let c = from_at(q);
        return vec4<f32>(c.rgb * (1.0 - exp(-d / 0.05) * 0.4 * amp) + vec3<f32>(crest), c.a);
    }
    let foam = exp(d / 0.015) * 0.5 * amp;
    let b = to_at(uv);
    return vec4<f32>(b.rgb + vec3<f32>(foam), b.a);
}
""", [p("curl", "Curl", 0, 100, 60)], xfade="wiperight"),

T("page-turning", "Page Turning", "Slide", 77,
  "The outgoing shot is turned like a page from its bottom-right corner, uncovering the incoming one.",
  PAGE, [p("radius", "Curl", 5, 100, 40)], xfade="coverleft"),

T("fold-over", "Fold Over", "Slide", 78,
  "The right half of the outgoing shot folds over onto the left like paper, the incoming shot printed on its back.",
  FOLD, [p("depth", "Depth", 0, 100, 50)]),

T("mosaic-transition", "Mosaic", "Glitch", 79,
  "The outgoing shot breaks into ever larger tiles and the incoming one resolves out of them.",
  """
struct Params { size: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = sin(3.14159265 * progress);
    let px = max(1.0, e * params.size / 100.0 * frame.size.x / 8.0);
    let cell = frame.size / px;
    let q = (floor(uv * cell) + vec2<f32>(0.5)) / cell;
    let quv = select(q, uv, px <= 1.0);
    return mix(from_at(quv), to_at(quv), smoothstep(0.4, 0.6, progress));
}
""", [p("size", "Tile size", 0, 100, 60)], xfade="pixelize"),

T("blink-transition", "Blink", "Basic", 80,
  "The frame blinks like an eye closing on the outgoing shot and opening on the incoming one.",
  DISCBLUR + """
struct Params { softness: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let close = sin(3.14159265 * smoothstep(0.0, 1.0, progress));
    let x = (uv.x - 0.5) * 2.0;
    let bulge = 0.12 * (1.0 - x * x);
    let lid = close * (0.5 + 0.13);
    let top = lid - bulge * (1.0 - close);
    let soft = max(params.softness / 100.0, 0.005) * 0.08;
    let m = smoothstep(top - soft, top, uv.y) * smoothstep(top - soft, top, 1.0 - uv.y);
    let blur = close * close * 0.02;
    let base = select(disc_from(uv, blur), disc_to(uv, blur), progress >= 0.5);
    return vec4<f32>(base.rgb * m, base.a);
}
""", [p("softness", "Softness", 0, 100, 40)], xfade="fadeblack"),

T("particles", "Particles", "Dissolve", 81,
  "The outgoing shot breaks into specks of light that drift away, leaving the incoming one.",
  """
struct Params { size: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let px = max(params.size, 2.0);
    let cells = frame.size / px;
    let drift = vec2<f32>(0.25, -0.15);
    var colour = to_at(uv);
    // A speck leaves its cell when the sweep reaches it and drifts off,
    // fading; look back along the drift for the specks passing here.
    for (var k = 0; k < 5; k++) {
        let back = uv - drift * f32(k) * 0.04;
        let cell = floor(back * cells);
        let centre = (cell + vec2<f32>(0.5)) / cells;
        let leave = centre.x * 0.6 + hash(cell, 5.0) * 0.3;
        let age = progress * 1.1 - leave;
        if (age > 0.0 && age < 0.4) {
            let at = centre + drift * age;
            let d = length((uv - at) * cells);
            let a = smoothstep(0.5, 0.2, d) * (1.0 - age / 0.4);
            let c = from_at(centre);
            colour = vec4<f32>(mix(colour.rgb, c.rgb * 1.6 + vec3<f32>(0.2), a), colour.a);
        }
    }
    let cell = floor(uv * cells);
    let centre = (cell + vec2<f32>(0.5)) / cells;
    let leave = centre.x * 0.6 + hash(cell, 5.0) * 0.3;
    if (progress * 1.1 < leave) {
        return from_at(uv);
    }
    return colour;
}
""", [p("size", "Speck size", 2, 24, 6, unit="px")], xfade="dissolve"),

T("flame", "Flame", "Light", 82,
  "The outgoing shot burns away from below in a ragged edge of fire, the incoming one behind the flames.",
  NOISE + """
struct Params { heat: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let aspect = frame.size.x / frame.size.y;
    let n = fbm(vec2<f32>(uv.x * aspect * 4.0, uv.y * 4.0 - progress * 3.0));
    let field = (1.0 - uv.y) * 0.6 + n * 0.4;
    let edge = progress * 1.3 - 0.15;
    let d = field - edge;
    let heat = params.heat / 100.0;
    if (d < 0.0) {
        let b = to_at(uv);
        let ember = exp(d / 0.03) * heat;
        return vec4<f32>(b.rgb + vec3<f32>(2.0, 0.6, 0.1) * ember, b.a);
    }
    let a = from_at(uv);
    let glow = exp(-d / 0.04) * heat;
    let char = smoothstep(0.06, 0.0, d);
    let rgb = a.rgb * (1.0 - char * 0.9) + vec3<f32>(3.0, 1.2, 0.25) * glow;
    return vec4<f32>(rgb, a.a);
}
""", [p("heat", "Heat", 0, 100, 70)], xfade="fadewhite"),

T("snow-transition", "Snow", "Light", 83,
  "A flurry of snow thickens to a white-out over the outgoing shot and settles away from the incoming one.",
  NOISE + """
struct Params { flakes: f32 }

fn flakes(uv: vec2<f32>, scale: f32, t: f32, seed: f32) -> f32 {
    let aspect = frame.size.x / frame.size.y;
    let q = vec2<f32>(uv.x * aspect, uv.y - t) * scale;
    let cell = floor(q);
    let at = cell + vec2<f32>(hash(cell, seed), hash(cell, seed + 1.0));
    let d = length(q - at);
    let present = step(0.5, hash(cell, seed + 2.0));
    return smoothstep(0.12, 0.02, d) * present;
}

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = sin(3.14159265 * progress);
    let base = mix(from_at(uv), to_at(uv), smoothstep(0.4, 0.6, progress));
    let k = params.flakes / 100.0;
    let s = flakes(uv, 12.0, progress * 1.5, 1.0) + flakes(uv, 20.0, progress * 1.0, 7.0) * 0.7 + flakes(uv, 32.0, progress * 0.7, 13.0) * 0.5;
    let fog = clamp((fbm(uv * 3.0 + vec2<f32>(progress, 0.0)) + e * 1.3 - 1.0) / 0.3, 0.0, 1.0);
    let rgb = mix(base.rgb, vec3<f32>(0.95, 0.97, 1.0), clamp(fog + s * k * e * 2.0, 0.0, 1.0));
    return vec4<f32>(rgb, base.a);
}
""", [p("flakes", "Flakes", 0, 100, 70)], xfade="fadewhite"),

T("white-ink", "White Ink", "Dissolve", 84,
  "Blots of white ink spread until they cover the outgoing shot, then draw back off the incoming one.",
  NOISE + """
struct Params { blots: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let aspect = frame.size.x / frame.size.y;
    let q = vec2<f32>(uv.x * aspect, uv.y) * max(params.blots, 1.0);
    let n = fbm(q) * 0.7 + vnoise(q * 0.5 + vec2<f32>(3.0)) * 0.3;
    let e = sin(3.14159265 * progress);
    let cover = smoothstep(1.0 - e * 1.1, 1.0 - e * 1.1 + 0.02, n);
    let base = select(from_at(uv), to_at(uv), progress >= 0.5);
    return vec4<f32>(mix(base.rgb, vec3<f32>(0.95), cover), base.a);
}
""", [p("blots", "Blot size", 1, 10, 3, unit="")], xfade="fadewhite"),

T("cloud", "Cloud", "Dissolve", 85,
  "Clouds drift in across the outgoing shot and blow away to show the incoming one.",
  NOISE + """
struct Params { thickness: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let aspect = frame.size.x / frame.size.y;
    let q = vec2<f32>(uv.x * aspect * 1.5 - progress * 2.5, uv.y * 2.0);
    let n = fbm(q);
    let e = sin(3.14159265 * progress) * (0.7 + params.thickness / 100.0 * 0.6);
    let cover = clamp((n + e - 0.9) / 0.35, 0.0, 1.0);
    let shade = mix(0.7, 1.0, fbm(q * 2.0 + vec2<f32>(1.7)));
    let base = mix(from_at(uv), to_at(uv), smoothstep(0.42, 0.58, progress));
    return vec4<f32>(mix(base.rgb, vec3<f32>(0.92, 0.94, 0.98) * shade, cover), base.a);
}
""", [p("thickness", "Thickness", 0, 100, 60)]),

T("blue-lines", "Blue Lines", "Light", 86,
  "Glowing blue scan lines sweep down the frame, laying the incoming shot down behind them.",
  """
struct Params { glow: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let edge = progress * 1.2 - 0.1;
    let m = step(uv.y, edge);
    let base = mix(from_at(uv), to_at(uv), m);
    let d = uv.y - edge;
    let k = params.glow / 100.0;
    let lead = exp(-d * d / 0.0004) * 2.0;
    let trail = select(0.0, exp(d / 0.08) * 0.6, d < 0.0);
    let lines = step(0.5, fract(uv.y * frame.size.y / 4.0)) * trail;
    let rgb = base.rgb + vec3<f32>(0.1, 0.45, 1.6) * (lead + lines) * k;
    return vec4<f32>(rgb, base.a);
}
""", [p("glow", "Glow", 0, 100, 70)], xfade="wipedown"),

T("recorder", "Recorder", "Basic", 87,
  "A camcorder viewfinder: corner marks, a blinking REC light and a burst of static at the cut.",
  """
struct Params { static_amount: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let base = select(from_at(uv), to_at(uv), progress >= 0.5);
    let e = sin(3.14159265 * progress);
    let px = uv * frame.size / frame.size.y;
    let w = frame.size.x / frame.size.y;
    // Corner brackets.
    let m = 0.06;
    let len = 0.08;
    let t = 0.006;
    let cx = min(px.x - m, w - m - px.x);
    let cy = min(px.y - m, 1.0 - m - px.y);
    let bracket = (abs(cx) < t && cy >= -t && cy < len) || (abs(cy) < t && cx >= -t && cx < len);
    // The REC light, blinking.
    let dot = length(px - vec2<f32>(m + 0.04, m + 0.04)) < 0.018 && fract(progress * 3.0) < 0.6;
    var rgb = base.rgb;
    let show = smoothstep(0.0, 0.15, e);
    rgb = mix(rgb, vec3<f32>(1.0), select(0.0, show, bracket));
    rgb = mix(rgb, vec3<f32>(1.0, 0.05, 0.05), select(0.0, show, dot));
    let burst = exp(-pow((progress - 0.5) / 0.07, 2.0)) * params.static_amount / 100.0;
    let n = hash(floor(uv * frame.size / 2.0), floor(progress * 60.0));
    rgb = mix(rgb, vec3<f32>(n), burst);
    let scan = 1.0 - 0.12 * e * step(0.5, fract(uv.y * frame.size.y / 3.0));
    return vec4<f32>(rgb * scan, base.a);
}
""", [p("static_amount", "Static", 0, 100, 70)]),

T("color-glitch", "Color Glitch", "Glitch", 88,
  "The cut stutters through blocks of shifted colour and torn lines.",
  HUE + """
struct Params { amount: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = sin(3.14159265 * progress) * params.amount / 100.0;
    let t = floor(progress * 20.0);
    let row = floor(uv.y * 30.0);
    let tear = select(0.0, (hash(vec2<f32>(row, t), 1.0) - 0.5) * 0.2, hash(vec2<f32>(row, t), 2.0) < e * 0.5);
    let q = vec2<f32>(fract(uv.x + tear), uv.y);
    let pick = select(progress >= 0.5, hash(vec2<f32>(row, t), 3.0) < progress, e > 0.1);
    let c = select(from_at(q), to_at(q), pick);
    let block = floor(uv * vec2<f32>(6.0, 10.0));
    let tint_on = hash(block, t + 4.0) < e * 0.35;
    let turned = turn_hue(c.rgb, 120.0 + 120.0 * floor(hash(block, t + 5.0) * 2.0));
    let rgb = select(c.rgb, turned * 1.3, tint_on);
    return vec4<f32>(rgb, c.a);
}
""", [p("amount", "Amount", 0, 100, 70)]),

T("like-transition", "Like", "Fun", 90,
  "A burst of little hearts pops up all over the frame and the incoming shot is there when they clear.",
  HEART + """
struct Params { hearts: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let n = max(params.hearts, 3.0);
    let aspect = frame.size.x / frame.size.y;
    let cells = vec2<f32>(n, max(floor(n / aspect + 0.5), 1.0));
    let cell = floor(uv * cells);
    let born = hash(cell, 1.0) * 0.5;
    let t = clamp((progress - born) / 0.5, 0.0, 1.0);
    let size = sin(3.14159265 * t) * (0.6 + 0.6 * hash(cell, 2.0));
    let centre = cell + vec2<f32>(0.5) + (vec2<f32>(hash(cell, 3.0), hash(cell, 4.0)) - vec2<f32>(0.5)) * 0.4;
    let local = (uv * cells - centre) * vec2<f32>(1.0, cells.y / cells.x * aspect);
    let d = heart_sdf(vec2<f32>(local.x, -local.y) / max(size, 1e-3));
    let base = select(from_at(uv), to_at(uv), progress >= 0.5);
    let pink = mix(vec3<f32>(1.0, 0.08, 0.3), vec3<f32>(1.0, 0.4, 0.6), hash(cell, 5.0));
    let m = smoothstep(0.02, -0.02, d) * step(0.001, size);
    return vec4<f32>(mix(base.rgb, pink, m), base.a);
}
""", [p("hearts", "Hearts", 3, 16, 7, unit="")]),

T("super-like-transition", "Super Like", "Fun", 91,
  "A big heart beats once in the middle of the frame and opens out to the incoming shot.",
  HEART + """
struct Params { softness: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let d0 = (uv - vec2<f32>(0.5)) * frame.size / frame.size.y;
    let beat = 1.0 + 0.15 * sin(clamp(p * 3.0, 0.0, 1.0) * 3.14159265);
    let size = p * p * 3.2 * beat;
    let d = heart_sdf(vec2<f32>(d0.x, -d0.y) / max(size, 1e-3)) * size;
    let soft = max(params.softness / 100.0, 0.002) * 0.05;
    let inside = smoothstep(soft, -soft, d);
    let rim = exp(-abs(d) / 0.01) * sin(3.14159265 * p);
    let base = mix(from_at(uv), to_at(uv), inside);
    return vec4<f32>(base.rgb + vec3<f32>(1.0, 0.2, 0.45) * rim * 1.5, base.a);
}
""", [p("softness", "Softness", 0, 100, 20)], xfade="circleopen"),

T("little-devil", "Little Devil", "Fun", 92,
  "A mischievous red flicker: the frame tints devil-red, little horns flash and the cut snaps to the next shot.",
  """
struct Params { mischief: f32 }

fn horn(p: vec2<f32>, base: vec2<f32>, lean: f32) -> f32 {
    // A curved triangle: wide at the base, a point that leans outward.
    let q = p - base;
    let h = clamp(-q.y / 0.12, 0.0, 1.0);
    let centre = lean * h * h * 0.05;
    let half_width = 0.035 * (1.0 - h);
    return select(0.0, 1.0, q.y <= 0.0 && q.y > -0.12 && abs(q.x - centre) < half_width);
}

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = sin(3.14159265 * progress) * params.mischief / 100.0;
    let t = floor(progress * 16.0);
    let jolt = (hash(vec2<f32>(t, 1.0), 1.0) - 0.5) * 0.03 * e;
    let q = uv + vec2<f32>(jolt, 0.0);
    let base = select(from_at(q), to_at(q), progress >= 0.5);
    let l = luma(base.rgb);
    let red = vec3<f32>(l * 1.6 + 0.05, l * 0.25, l * 0.35);
    var rgb = mix(base.rgb, red, e * 0.8);
    let px = (uv - vec2<f32>(0.5, 0.3)) * frame.size / frame.size.y;
    let horns = max(horn(px, vec2<f32>(-0.12, 0.0), -1.0), horn(px, vec2<f32>(0.12, 0.0), 1.0));
    let flash = select(0.0, 1.0, fract(progress * 4.0) < 0.5) * e;
    rgb = mix(rgb, vec3<f32>(0.9, 0.02, 0.05), horns * flash);
    return vec4<f32>(rgb, base.a);
}
""", [p("mischief", "Mischief", 0, 100, 80)]),
]

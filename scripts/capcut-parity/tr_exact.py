from lib_wgsl import *

# CapCut's own transitions, ported from the packages CapCut downloads into
# its cache (Cache/effect/<resource id>/), pass for pass. CapCut works on
# the encoded picture, so the blurs here mix in the display encoding.

SLIDE_DIRS = p("direction", "Direction", 0, 3, 0, values=[0, 1, 2, 3], labels=["Down", "Up", "Right", "Left"])

PACKAGES = [
# Down, Up, Right and Left (6724227330190873100, 6724227090872275463,
# 6724227599616184836, 6724227717195108867): the outgoing shot slides off
# with a mirror image of it filling the gap, the incoming one slides in the
# same way, switched hard at the midpoint, under a 31-tap blur along the
# motion that peaks there. Down counts its centre tap twice and so runs
# about 3 % bright, as CapCut's does.
T("slide-mirror-blur", "Slide Mirror Blur", "Slide", 60,
  "The shots slide one way with mirror images filling the gap, blurred along the motion, cutting at the middle.", """
struct Params { direction: f32 }

fn quint(t: f32) -> f32 {
    if (t < 0.5) {
        return 16.0 * t * t * t * t * t;
    }
    let u = t - 1.0;
    return 1.0 + 16.0 * u * u * u * u * u;
}

// The coordinate along the motion and the one across it.
fn along_of(uv: vec2<f32>, direction: f32) -> f32 {
    return select(uv.x, uv.y, direction < 1.5);
}

fn placed(uv: vec2<f32>, a: f32, direction: f32) -> vec2<f32> {
    if (direction < 1.5) {
        return vec2<f32>(uv.x, a);
    }
    return vec2<f32>(a, uv.y);
}

// The picture after the first pass, at `uv`: the outgoing shot before the
// eased midpoint, the incoming one from it.
fn slid(uv: vec2<f32>, e: f32, direction: f32) -> vec4<f32> {
    let a = along_of(uv, direction);
    let s1 = clamp(2.0 * e, 0.0, 1.0);
    let s2 = (clamp(e, 0.5, 1.0) - 0.5) * 2.0;
    if (e < 0.5) {
        var q: f32;
        if (direction < 0.5 || (direction > 1.5 && direction < 2.5)) {
            // Down and Right fold the shot back over the edge it leaves.
            q = select(a - s1, s1 - a, a <= s1);
        } else {
            // Up and Left carry it on and mirror it at the far edge.
            q = a + s1;
            if (q > 1.0) {
                q = 2.0 - q;
            }
        }
        return from_at(placed(uv, q, direction));
    }
    var q: f32;
    if (direction < 0.5 || (direction > 1.5 && direction < 2.5)) {
        q = 1.0 - select(a - s2, s2 - a, a <= s2);
    } else {
        q = a + s2;
        if (q > 1.0) {
            q = 2.0 - q;
        }
        q = 1.0 - q;
    }
    return to_at(placed(uv, q, direction));
}

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = quint(clamp(progress, 0.0, 1.0));
    let k = select(clamp(2.0 * e, 0.0, 1.0) * 1.25,
                   1.25 - 1.25 * ((clamp(e, 0.5, 1.0) - 0.5) * 2.0), progress >= 0.5);
    let texel = select(1.0 / frame.size.x, 1.0 / frame.size.y, params.direction < 1.5);
    let step_along = texel * 1.25 * k;
    let centre = slid(uv, e, params.direction);
    var sum = to_display(centre.rgb);
    var alpha = centre.a;
    var weight = 1.0;
    for (var n = 1; n <= 15; n = n + 1) {
        let w = exp(-f32(n) / 800.0);
        let d = f32(n) * step_along;
        let ahead = slid(placed(uv, along_of(uv, params.direction) + d, params.direction), e, params.direction);
        let behind = slid(placed(uv, along_of(uv, params.direction) - d, params.direction), e, params.direction);
        sum = sum + w * (to_display(ahead.rgb) + to_display(behind.rgb));
        alpha = alpha + w * (ahead.a + behind.a);
        weight = weight + 2.0 * w;
    }
    if (params.direction < 0.5) {
        // Down's centre counted twice over the same weight.
        let bright = clamp((sum + to_display(centre.rgb)) / weight, vec3<f32>(0.0), vec3<f32>(1.0));
        return vec4<f32>(from_display(bright), clamp((alpha + centre.a) / weight, 0.0, 1.0));
    }
    return vec4<f32>(from_display(sum / weight), 1.0);
}
""", [SLIDE_DIRS]),
]

# A transition in a project carries no knobs, so each of CapCut's four is a
# package of its own: the shader above with its direction fixed.
_slide = PACKAGES.pop()
for _value, _slug, _name, _toward in ((0, "down", "Down", "down"), (1, "up", "Up", "up"),
                                       (2, "right", "Right", "to the right"), (3, "left", "Left", "to the left")):
    _wgsl = _slide["wgsl"].replace("struct Params { direction: f32 }\n", "").replace("params.direction", f"{_value}.0")
    PACKAGES.append(T(f"slide-mirror-{_slug}", f"Slide Mirror {_name}", "Slide", 60 + _value,
                      f"The shots slide {_toward} with mirror images filling the gap, blurred along the motion, cutting at the middle.",
                      _wgsl))

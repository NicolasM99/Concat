"""Burbujas desenfocadas / Blurry Bubbles (7159450506648097281), ported from
CapCut's package; see tr_exact.py. CapCut blurs each shot across, then
down, with a 17-tap Gaussian, then draws a 98-tap golden-angle bokeh over
it; here the bokeh is exact and the Gaussian under it is a five-tap cross
of the same reach, which a 98-tap bokeh over it all but hides."""
from lib_wgsl import T

BLURRY_BUBBLES = """
const LAST_R: f32 = 14.14300308806351;
const AMOUNT: f32 = 539.35;

fn shot(uv: vec2<f32>, incoming: bool) -> vec3<f32> {
    let q = vec2<f32>(uv.x, 1.0 - uv.y);
    if (incoming) {
        return to_display(to_at(q).rgb);
    }
    return to_display(from_at(q).rgb);
}

// The Gaussian's reach, as a cross of five taps.
fn soft(uv: vec2<f32>, incoming: bool, reach: vec2<f32>) -> vec3<f32> {
    let c = shot(uv, incoming) * 0.20;
    let x = vec2<f32>(reach.x, 0.0);
    let y = vec2<f32>(0.0, reach.y);
    let side = shot(uv + x, incoming) + shot(uv - x, incoming) + shot(uv + y, incoming) + shot(uv - y, incoming);
    return (c + side * 0.2) / 1.0;
}

fn smooth_any(e0: f32, e1: f32, x: f32) -> f32 {
    let t = clamp((x - e0) / (e1 - e0), 0.0, 1.0);
    return t * t * (3.0 - 2.0 * t);
}

fn bokeh(uv: vec2<f32>, incoming: bool, blur_size: f32, blur_size2: f32) -> vec3<f32> {
    let s = 720.0 / min(frame.size.x, frame.size.y);
    let wn = ceil(frame.size.x * s);
    let hn = ceil(frame.size.y * s);
    let res = vec2<f32>(wn * 0.5, hn * 0.5);
    let ratio = res.x / res.y;
    let my_ratio = max(res.x, res.y) / min(res.x, res.y);
    let reach = vec2<f32>(blur_size / wn, blur_size / hn) * 1.25 * 4.0;
    var a = vec2<f32>(0.0, 0.35 * blur_size2 * my_ratio) / res;
    var r = 1.0;
    var acc = vec3<f32>(0.0);
    var div = vec3<f32>(0.0);
    for (var i = 0; i < 98; i = i + 1) {
        a.x = a.x * ratio;
        a = vec2<f32>(-0.73735 * a.x - 0.67539 * a.y, 0.67539 * a.x - 0.73735 * a.y);
        a.x = a.x / ratio;
        let d = r / LAST_R;
        let c = soft(uv + (r - 1.0) * mix(1.5, 1.0, d) * a, incoming, reach);
        let w = (pow(max(c, vec3<f32>(0.0)), vec3<f32>(9.0)) * AMOUNT + 0.4) * smooth_any(1.0, 0.9, d) * smooth_any(0.8, 0.9, d);
        acc = acc + c * w;
        div = div + w;
        r = r + 1.0 / r;
    }
    return acc / max(div, vec3<f32>(1e-6));
}

fn transition(uv_top: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = clamp(progress, 0.0, 1.0);
    let uv = vec2<f32>(uv_top.x, 1.0 - uv_top.y);
    let intensity = select(clamp((1.0 - p) / 0.5, 0.0, 1.0), clamp(p / 0.5, 0.0, 1.0), p <= 0.5);
    let blur_size = 0.48 * intensity;
    let blur_size2 = 1.25 * intensity;
    var mixed = 0.0;
    if (p > 0.6) {
        mixed = 1.0;
    } else if (p >= 0.4) {
        mixed = (p - 0.4) / 0.2;
    }
    var out = vec3<f32>(0.0);
    if (mixed < 1.0) {
        out = out + bokeh(uv, false, blur_size, blur_size2) * (1.0 - mixed);
    }
    if (mixed > 0.0) {
        out = out + bokeh(uv, true, blur_size, blur_size2) * mixed;
    }
    return vec4<f32>(from_display(out), 1.0);
}
"""

PACKAGES = [
    T("blurry-bubbles", "Blurry Bubbles", "Blur", 62,
      "Both shots melt into a bokeh of soft bubbles, crossing over in the middle.", BLURRY_BUBBLES),
]

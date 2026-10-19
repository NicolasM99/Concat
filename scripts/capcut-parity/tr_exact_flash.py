"""The picture half of CapCut's two flash transitions, ported from their
packages; see tr_exact.py. The flash itself is footage CapCut ships with
each - a run of 70 frames for Flash II, a video for Heat Wave Flash - which
an import lays over the cut on a lane of its own in Screen."""
from lib_wgsl import T

PACKAGES = [
    # Destello II / Flash II (6952697917563998722): a hard cut at the
    # midpoint, hidden under the flash.
    T("flash-cut", "Flash Cut", "Light", 63,
      "A hard cut at the middle of the transition, for a flash laid over it.", card={"progress": 0.75}, wgsl="""
fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    if (progress > 0.5) {
        return to_at(uv);
    }
    return from_at(uv);
}
"""),
    # Flash de ola de calor / Heat Wave Flash (7564617241841437953): After
    # Effects' dip of two layers fading over nothing - the incoming shot at x
    # under the outgoing one at 1 - x, so x^2 of it shows - from 0.6 to 0.87 s
    # of the package's 1.47 s comp.
    T("heat-dissolve", "Heat Dissolve", "Light", 64,
      "The shots dissolve through a dim dip, for a heat-wave flash laid over it.", card={"progress": 0.5}, wgsl="""
fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = clamp(progress, 0.0, 1.0);
    let x = clamp((p * 44.0 / 30.0 - 0.6) / (0.866667 - 0.6), 0.0, 1.0);
    let a = to_display(from_at(uv).rgb);
    let b = to_display(to_at(uv).rgb);
    return vec4<f32>(from_display(b * x * x + a * (1.0 - x)), 1.0);
}
"""),
]

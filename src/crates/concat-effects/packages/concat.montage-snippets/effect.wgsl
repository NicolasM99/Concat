struct Params { cuts: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let n = max(params.cuts, 2.0);
    let seg = min(floor(progress * n), n - 1.0);
    let local = fract(progress * n);
    // The first snippet is the outgoing shot, the last the incoming one,
    // and between them the incoming one wins more often as the cut goes on.
    var to_side = hash(vec2<f32>(seg, 3.0), 0.5) < mix(0.2, 0.9, progress);
    if (seg < 0.5) {
        to_side = false;
    }
    if (seg > n - 1.5) {
        to_side = true;
    }
    let env = sin(3.14159265 * progress);
    let z = 1.0 + 0.15 * (1.0 - local) * (1.0 - local) * env;
    let suv = (uv - vec2<f32>(0.5)) / z + vec2<f32>(0.5);
    let c = select(from_at(suv), to_at(suv), to_side);
    let flash = exp(-local * 10.0) * 0.9 * env;
    return vec4<f32>(c.rgb + vec3<f32>(flash), c.a);
}

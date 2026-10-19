struct Params { rate: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let n = max(params.rate, 2.0);
    let phase = progress * progress * n;
    let on = fract(phase) < 0.5;
    var c = select(from_at(uv), to_at(uv), on);
    if (progress > 0.9) {
        c = to_at(uv);
    }
    let flash = (1.0 - fract(phase * 2.0)) * 0.5 * sin(3.14159265 * progress);
    return vec4<f32>(c.rgb + vec3<f32>(flash), c.a);
}

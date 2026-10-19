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

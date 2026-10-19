struct Params { softness: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let d = abs(uv - vec2<f32>(0.5)) * 2.0;
    let soft = max(params.softness / 100.0, 0.005) * 0.2;
    let edge = p * (1.0 + 2.0 * soft);
    let m = smoothstep(edge - soft, edge, max(d.x, d.y));
    return mix(to_at(uv), from_at(uv), m);
}

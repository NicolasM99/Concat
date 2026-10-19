struct Params { blades: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let n = max(params.blades, 2.0);
    let d = (uv - vec2<f32>(0.5)) * frame.size / frame.size.y;
    let a = fract(atan2(d.y, d.x) / 6.2831853 + 0.25);
    let local = fract(a * n);
    let m = smoothstep(0.0, 0.01, local - smoothstep(0.0, 1.0, progress));
    return mix(to_at(uv), from_at(uv), m);
}

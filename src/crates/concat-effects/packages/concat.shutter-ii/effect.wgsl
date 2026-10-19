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

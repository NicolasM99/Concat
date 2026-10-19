struct Params { amount: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = sin(3.14159265 * progress) * params.amount / 100.0;
    let t = floor(progress * 24.0);
    let block = floor(uv * vec2<f32>(8.0, 14.0));
    let h = hash(block, t);
    let shift = select(0.0, (hash(block + vec2<f32>(5.0), t) - 0.5) * 0.3, h < e * 0.6);
    let suv = vec2<f32>(fract(uv.x + shift), uv.y);
    let pick = select(progress >= 0.5, hash(block, t + 9.0) < progress, e > 0.05);
    var c = select(from_at(suv), to_at(suv), pick);
    if (h > 1.0 - e * 0.2) {
        c = vec4<f32>(vec3<f32>(1.0) - min(c.rgb, vec3<f32>(1.0)), c.a);
    }
    let line = step(0.5, fract(uv.y * frame.size.y * 0.5)) * 0.15 * e;
    return vec4<f32>(c.rgb * (1.0 - line), c.a);
}

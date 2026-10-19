fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = clamp(progress, 0.0, 1.0);
    let x = clamp((p * 44.0 / 30.0 - 0.6) / (0.866667 - 0.6), 0.0, 1.0);
    let a = to_display(from_at(uv).rgb);
    let b = to_display(to_at(uv).rgb);
    return vec4<f32>(from_display(b * x * x + a * (1.0 - x)), 1.0);
}

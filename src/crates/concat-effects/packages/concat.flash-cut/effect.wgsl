fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    if (progress > 0.5) {
        return to_at(uv);
    }
    return from_at(uv);
}

struct Params { stagger: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let strip = min(floor(uv.x * 3.0), 2.0);
    let delay = strip * params.stagger / 100.0 * 0.15;
    let t = smoothstep(0.0, 1.0, clamp((progress - delay) / (1.0 - 0.3 * params.stagger / 100.0), 0.0, 1.0));
    let dir = select(1.0, -1.0, strip == 1.0);
    let y = uv.y + t * dir;
    if (y >= 0.0 && y <= 1.0) {
        return from_at(vec2<f32>(uv.x, y));
    }
    return to_at(uv);
}

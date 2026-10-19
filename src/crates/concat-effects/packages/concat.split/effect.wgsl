struct Params { direction: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    if (params.direction < 0.5) {
        let up = uv.x < 0.5;
        let y = select(uv.y - p, uv.y + p, up);
        if (y >= 0.0 && y <= 1.0) {
            return from_at(vec2<f32>(uv.x, y));
        }
        return to_at(uv);
    }
    let left = uv.y < 0.5;
    let x = select(uv.x - p, uv.x + p, left);
    if (x >= 0.0 && x <= 1.0) {
        return from_at(vec2<f32>(x, uv.y));
    }
    return to_at(uv);
}

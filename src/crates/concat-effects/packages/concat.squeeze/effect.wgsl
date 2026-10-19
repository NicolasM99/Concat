fn inb(uv: vec2<f32>) -> bool {
    return uv.x >= 0.0 && uv.x <= 1.0 && uv.y >= 0.0 && uv.y <= 1.0;
}

struct Params { direction: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let horizontal = params.direction < 0.5;
    let bg = vec4<f32>(0.0, 0.0, 0.0, 1.0);
    if (p < 0.5) {
        let s = max(1.0 - p * 2.0, 1e-4);
        var q = uv;
        if (horizontal) {
            q.x = (uv.x - 0.5) / s + 0.5;
        } else {
            q.y = (uv.y - 0.5) / s + 0.5;
        }
        return select(bg, from_at(q), inb(q));
    }
    let s = max((p - 0.5) * 2.0, 1e-4);
    var q = uv;
    if (horizontal) {
        q.x = (uv.x - 0.5) / s + 0.5;
    } else {
        q.y = (uv.y - 0.5) / s + 0.5;
    }
    return select(bg, to_at(q), inb(q));
}

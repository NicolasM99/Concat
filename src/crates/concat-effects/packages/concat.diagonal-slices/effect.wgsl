fn inb(uv: vec2<f32>) -> bool {
    return uv.x >= 0.0 && uv.x <= 1.0 && uv.y >= 0.0 && uv.y <= 1.0;
}

struct Params { slices: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let n = max(params.slices, 2.0);
    let across = (uv.x + uv.y) * 0.5;
    let i = floor(across * n);
    let delay = i / n * 0.5;
    let t = smoothstep(0.0, 1.0, clamp((progress - delay) / 0.5, 0.0, 1.0));
    let side = select(-1.0, 1.0, fract(i * 0.5) < 0.25);
    let q = uv + vec2<f32>(1.0, -1.0) * (1.0 - t) * side;
    if (inb(q) && t > 0.0) {
        return to_at(q);
    }
    return from_at(uv);
}

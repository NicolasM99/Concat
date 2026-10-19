fn inb(uv: vec2<f32>) -> bool {
    return uv.x >= 0.0 && uv.x <= 1.0 && uv.y >= 0.0 && uv.y <= 1.0;
}

struct Params { slices: f32 }

// The incoming shot arrives in slices, each sliding in from alternate
// sides a beat after the one before.
fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let n = max(params.slices, 2.0);
    let along = uv.y;
    let across = uv.x;
    let i = floor(across * n);
    let delay = i / n * 0.5;
    let t = smoothstep(0.0, 1.0, clamp((progress - delay) / 0.5, 0.0, 1.0));
    let side = select(-1.0, 1.0, fract(i * 0.5) < 0.25);
    let shift = (1.0 - t) * side;
    let moved = along + shift;
    if (moved >= 0.0 && moved <= 1.0 && t > 0.0) {
        return to_at(vec2<f32>(uv.x, moved));
    }
    return from_at(uv);
}

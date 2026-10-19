struct Params { amount: f32 }

fn stretched(uv: vec2<f32>, sx: f32, to_side: bool) -> vec4<f32> {
    var sum = vec4<f32>(0.0);
    for (var i = 0; i < 6; i++) {
        let s = sx * (1.0 + f32(i) * 0.04 * (sx - 1.0));
        let q = vec2<f32>((uv.x - 0.5) / s + 0.5, uv.y);
        sum += select(from_at(q), to_at(q), to_side);
    }
    return sum / 6.0;
}

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let k = params.amount / 100.0 * 6.0;
    if (progress < 0.5) {
        let t = progress * 2.0;
        return stretched(uv, 1.0 + k * t * t, false);
    }
    let t = (1.0 - progress) * 2.0;
    return stretched(uv, 1.0 + k * t * t, true);
}

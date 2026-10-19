struct Params { direction: f32, blur: f32 }

fn inb(uv: vec2<f32>) -> bool {
    return uv.x >= 0.0 && uv.x <= 1.0 && uv.y >= 0.0 && uv.y <= 1.0;
}

fn axis(direction: f32) -> vec2<f32> {
    if (direction < 0.5) {
        return vec2<f32>(-1.0, 1.0);
    } else if (direction < 1.5) {
        return vec2<f32>(1.0, 1.0);
    } else if (direction < 2.5) {
        return vec2<f32>(-1.0, -1.0);
    }
    return vec2<f32>(1.0, -1.0);
}

// Both shots travel together toward a corner, smeared along the way.
fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let dir = axis(params.direction);
    let smear = dir * sin(3.14159265 * progress) * params.blur / 100.0 * 0.06;
    var sum = vec4<f32>(0.0);
    for (var i = -3; i <= 3; i++) {
        let q = uv + smear * (f32(i) / 3.0);
        let to_uv = q + dir * (1.0 - p);
        let from_uv = q - dir * p;
        sum += select(from_at(from_uv), to_at(to_uv), inb(to_uv));
    }
    return sum / 7.0;
}

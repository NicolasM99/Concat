fn blur_from(uv: vec2<f32>, dir: vec2<f32>) -> vec4<f32> {
    var sum = vec4<f32>(0.0);
    for (var i = -4; i <= 4; i++) {
        sum += from_at(uv + dir * (f32(i) / 4.0));
    }
    return sum / 9.0;
}

fn blur_to(uv: vec2<f32>, dir: vec2<f32>) -> vec4<f32> {
    var sum = vec4<f32>(0.0);
    for (var i = -4; i <= 4; i++) {
        sum += to_at(uv + dir * (f32(i) / 4.0));
    }
    return sum / 9.0;
}

struct Params { amount: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = sin(3.14159265 * progress);
    let d = vec2<f32>(1.0, 0.0) * e * params.amount / 100.0 * 0.12;
    let m = smoothstep(0.35, 0.65, progress);
    return mix(blur_from(uv, d), blur_to(uv, d), m);
}

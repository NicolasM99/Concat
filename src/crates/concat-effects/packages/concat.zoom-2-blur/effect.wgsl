struct Params { progress: f32 }

fn mirrored(x: f32) -> f32 {
    return 1.0 - abs(abs(x) - 1.0);
}

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let p = clamp(params.progress / 100.0, 0.0, 1.0);
    let s = 0.4 + 0.6 * (1.0 - pow(1.0 - p, 4.0));
    let blur = 0.4 * (max(1.0 - p, 0.4) - 0.4);
    let u = vec2<f32>(0.5) + (uv - vec2<f32>(0.5)) / s;
    if (u.x < -1.0 || u.x > 2.0 || u.y < -1.0 || u.y > 2.0) {
        return vec4<f32>(0.0);
    }
    let pixel = vec3<f32>(uv * frame.size + vec2<f32>(0.5), 0.5);
    let offset = fract(sin(dot(pixel, vec3<f32>(12.9898, 78.233, 151.7182))) * 43758.5453);
    var acc = vec4<f32>(0.0);
    var total = 0.0;
    for (var t = 0; t <= 25; t = t + 1) {
        let pc = (f32(t) + offset) / 25.0;
        let w = 4.0 * (pc - pc * pc);
        let c = u + (vec2<f32>(0.5) - u) * pc * blur;
        acc = acc + sample(vec2<f32>(mirrored(c.x), mirrored(c.y))) * w;
        total = total + w;
    }
    return acc / total;
}

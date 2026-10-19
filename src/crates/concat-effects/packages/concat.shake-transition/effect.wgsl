struct Params { strength: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = sin(3.14159265 * progress) * params.strength / 100.0;
    let t = floor(progress * 40.0);
    let off = (vec2<f32>(hash(vec2<f32>(t, 1.0), 2.0), hash(vec2<f32>(t, 2.0), 2.0)) - vec2<f32>(0.5)) * 0.08 * e;
    let z = 1.0 + 0.1 * e;
    let q = (uv - vec2<f32>(0.5)) / z + vec2<f32>(0.5) + off;
    var sum = vec4<f32>(0.0);
    for (var i = -2; i <= 2; i++) {
        let s = q + off * f32(i) * 0.3;
        sum += select(from_at(s), to_at(s), progress >= 0.5);
    }
    return sum / 5.0;
}

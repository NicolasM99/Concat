fn vnoise(p: vec2<f32>) -> f32 {
    let i = floor(p);
    let f = fract(p);
    let u = f * f * (3.0 - 2.0 * f);
    let a = hash(i, 1.0);
    let b = hash(i + vec2<f32>(1.0, 0.0), 1.0);
    let c = hash(i + vec2<f32>(0.0, 1.0), 1.0);
    let d = hash(i + vec2<f32>(1.0, 1.0), 1.0);
    return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
}

fn fbm(p: vec2<f32>) -> f32 {
    var sum = 0.0;
    var amp = 0.5;
    var q = p;
    for (var i = 0; i < 5; i++) {
        sum += amp * vnoise(q);
        q = q * 2.03 + vec2<f32>(17.1, 9.2);
        amp *= 0.5;
    }
    return sum / 0.96875;
}

struct Params { density: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let aspect = frame.size.x / frame.size.y;
    let q = vec2<f32>(uv.x * aspect, uv.y) * 3.0;
    let n = fbm(q + vec2<f32>(-progress * 1.2, -progress * 0.7));
    let e = sin(3.14159265 * progress);
    let cover = clamp((n + e * (0.6 + params.density / 100.0) - 1.0) / 0.25, 0.0, 1.0);
    let base = mix(from_at(uv), to_at(uv), smoothstep(0.42, 0.58, progress));
    return vec4<f32>(mix(base.rgb, vec3<f32>(0.9), cover), base.a);
}

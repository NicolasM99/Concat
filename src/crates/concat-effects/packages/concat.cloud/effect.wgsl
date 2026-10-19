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

struct Params { thickness: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let aspect = frame.size.x / frame.size.y;
    let q = vec2<f32>(uv.x * aspect * 1.5 - progress * 2.5, uv.y * 2.0);
    let n = fbm(q);
    let e = sin(3.14159265 * progress) * (0.7 + params.thickness / 100.0 * 0.6);
    let cover = clamp((n + e - 0.9) / 0.35, 0.0, 1.0);
    let shade = mix(0.7, 1.0, fbm(q * 2.0 + vec2<f32>(1.7)));
    let base = mix(from_at(uv), to_at(uv), smoothstep(0.42, 0.58, progress));
    return vec4<f32>(mix(base.rgb, vec3<f32>(0.92, 0.94, 0.98) * shade, cover), base.a);
}

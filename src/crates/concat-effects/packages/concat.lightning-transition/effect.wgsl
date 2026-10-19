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

struct Params { glow: f32 }

fn bolt(uv: vec2<f32>, seed: f32) -> f32 {
    let x = 0.5 + (fbm(vec2<f32>(uv.y * 4.0, seed)) - 0.5) * 0.5 + (vnoise(vec2<f32>(uv.y * 30.0, seed)) - 0.5) * 0.04;
    let d = abs(uv.x - x) * frame.size.x / frame.size.y;
    return 0.002 / (d + 0.002);
}

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let to_side = progress >= 0.5;
    let base = select(from_at(uv), to_at(uv), to_side);
    let strike = exp(-pow((progress - 0.5) / 0.08, 2.0)) + 0.5 * exp(-pow((progress - 0.35) / 0.03, 2.0));
    let dark = sin(3.14159265 * progress) * 0.6;
    let night = base.rgb * (1.0 - dark) * vec3<f32>(0.8, 0.85, 1.1);
    let b = bolt(uv, floor(progress * 6.0)) * strike;
    let k = params.glow / 100.0;
    let rgb = night + vec3<f32>(0.7, 0.8, 1.0) * (b * 3.0 + strike * 0.8 * k);
    return vec4<f32>(rgb, base.a);
}

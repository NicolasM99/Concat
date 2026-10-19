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

struct Params { progress: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let n = fbm(vec2<f32>(uv.x * 6.0, uv.y * 3.0 + frame.time * 2.0));
    let field = (1.0 - uv.y) * 0.8 + n * 0.2;
    let edge = params.progress / 100.0 * 1.25;
    let d = edge - field;
    let m = step(0.0, d);
    let glow = exp(-abs(d) / 0.03) * step(params.progress, 99.9);
    return vec4<f32>(c.rgb + vec3<f32>(2.0, 0.7, 0.1) * glow, max(c.a * m, glow * c.a));
}

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

struct Params { heat: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let aspect = frame.size.x / frame.size.y;
    let n = fbm(vec2<f32>(uv.x * aspect * 4.0, uv.y * 4.0 - progress * 3.0));
    let field = (1.0 - uv.y) * 0.6 + n * 0.4;
    let edge = progress * 1.3 - 0.15;
    let d = field - edge;
    let heat = params.heat / 100.0;
    if (d < 0.0) {
        let b = to_at(uv);
        let ember = exp(d / 0.03) * heat;
        return vec4<f32>(b.rgb + vec3<f32>(2.0, 0.6, 0.1) * ember, b.a);
    }
    let a = from_at(uv);
    let glow = exp(-d / 0.04) * heat;
    let char = smoothstep(0.06, 0.0, d);
    let rgb = a.rgb * (1.0 - char * 0.9) + vec3<f32>(3.0, 1.2, 0.25) * glow;
    return vec4<f32>(rgb, a.a);
}

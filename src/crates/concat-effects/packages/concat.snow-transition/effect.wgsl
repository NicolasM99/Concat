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

struct Params { flakes: f32 }

fn flakes(uv: vec2<f32>, scale: f32, t: f32, seed: f32) -> f32 {
    let aspect = frame.size.x / frame.size.y;
    let q = vec2<f32>(uv.x * aspect, uv.y - t) * scale;
    let cell = floor(q);
    let at = cell + vec2<f32>(hash(cell, seed), hash(cell, seed + 1.0));
    let d = length(q - at);
    let present = step(0.5, hash(cell, seed + 2.0));
    return smoothstep(0.12, 0.02, d) * present;
}

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = sin(3.14159265 * progress);
    let base = mix(from_at(uv), to_at(uv), smoothstep(0.4, 0.6, progress));
    let k = params.flakes / 100.0;
    let s = flakes(uv, 12.0, progress * 1.5, 1.0) + flakes(uv, 20.0, progress * 1.0, 7.0) * 0.7 + flakes(uv, 32.0, progress * 0.7, 13.0) * 0.5;
    let fog = clamp((fbm(uv * 3.0 + vec2<f32>(progress, 0.0)) + e * 1.3 - 1.0) / 0.3, 0.0, 1.0);
    let rgb = mix(base.rgb, vec3<f32>(0.95, 0.97, 1.0), clamp(fog + s * k * e * 2.0, 0.0, 1.0));
    return vec4<f32>(rgb, base.a);
}

fn mirror_uv(uv: vec2<f32>) -> vec2<f32> {
    let m = abs(fract(uv * 0.5) * 2.0 - vec2<f32>(1.0));
    return vec2<f32>(1.0) - m;
}

fn moved(uv: vec2<f32>, offset: vec2<f32>, angle: f32, scale: f32) -> vec2<f32> {
    let c = (uv - vec2<f32>(0.5)) * frame.size;
    let s = sin(angle);
    let co = cos(angle);
    let r = vec2<f32>(c.x * co - c.y * s, c.x * s + c.y * co) / max(scale, 0.0001);
    return mirror_uv(r / frame.size + vec2<f32>(0.5) - offset);
}

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

fn rainbow(h: f32) -> vec3<f32> {
    let c = vec3<f32>(0.5) + 0.5 * cos(6.2831853 * (vec3<f32>(h) + vec3<f32>(0.0, 0.33, 0.67)));
    return c * c;
}

fn heart_sdf(q: vec2<f32>) -> f32 {
    let p = vec2<f32>(abs(q.x), q.y + 0.55);
    if (p.y + p.x > 1.0) {
        return sqrt(dot(p - vec2<f32>(0.25, 0.75), p - vec2<f32>(0.25, 0.75))) - 0.35355;
    }
    let a = dot(p - vec2<f32>(0.0, 1.0), p - vec2<f32>(0.0, 1.0));
    let t = max(p.x + p.y, 0.0) * 0.5;
    let b = dot(p - vec2<f32>(t), p - vec2<f32>(t));
    return sqrt(min(a, b)) * sign(p.x - p.y);
}

fn glint(d: vec2<f32>, size: f32) -> f32 {
    let a = abs(d) / max(size, 1e-4);
    let star = max(0.0, 1.0 - (a.x * 8.0 + a.y)) + max(0.0, 1.0 - (a.y * 8.0 + a.x));
    let core = exp(-dot(a, a) * 40.0);
    return star * 0.6 + core;
}

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    var light = 0.0;
    let origin = vec2<f32>(0.5, 0.95);
    for (var i = 0; i < 24; i++) {
        let fi = f32(i);
        let born = hash(vec2<f32>(fi, 0.0), 1.0);
        let life = fract(frame.time * 1.5 + born);
        let round = floor(frame.time * 1.5 + born);
        let a = -1.5707963 + (hash(vec2<f32>(fi, round), 2.0) - 0.5) * 2.4;
        let v = vec2<f32>(cos(a), sin(a)) * (0.4 + 0.6 * hash(vec2<f32>(fi, round), 3.0));
        let pos = origin + v * life * 0.6 + vec2<f32>(0.0, 0.5) * life * life;
        let d = (uv - pos) * vec2<f32>(frame.size.x / frame.size.y, 1.0);
        let along = normalize(v + vec2<f32>(0.0, life));
        let streak = exp(-pow(dot(d, vec2<f32>(-along.y, along.x)) / 0.002, 2.0)) * smoothstep(0.03, 0.0, abs(dot(d, along)));
        light += streak * (1.0 - life);
    }
    return vec4<f32>(c.rgb + vec3<f32>(1.0, 0.6, 0.2) * light * 3.0, c.a);
}

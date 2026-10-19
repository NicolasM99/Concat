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

fn split(uv: vec2<f32>, o: vec2<f32>) -> vec4<f32> {
    let g = sample(uv);
    return vec4<f32>(sample(uv + o).r, g.g, sample(uv - o).b, g.a);
}

fn scanlines(uv: vec2<f32>, amount: f32) -> f32 {
    return 1.0 - amount * step(0.5, fract(uv.y * frame.size.y / 3.0));
}

fn static_at(uv: vec2<f32>, t: f32) -> f32 {
    return hash(floor(uv * frame.size / 2.0), fract(t * 0.137) * 1000.0);
}

struct Params { look: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = split(uv, vec2<f32>(0.002, 0.0));
    var rgb = mix(c.rgb, soften(uv, 2.0), 0.3) * scanlines(uv, 0.1 * params.look / 100.0);
    rgb = saturation(rgb, 1.15);
    let px = uv * frame.size / frame.size.y;
    let w = frame.size.x / frame.size.y;
    let m = 0.06;
    let len = 0.08;
    let t = 0.005;
    let cx = min(px.x - m, w - m - px.x);
    let cy = min(px.y - m, 1.0 - m - px.y);
    let bracket = (abs(cx) < t && cy >= -t && cy < len) || (abs(cy) < t && cx >= -t && cx < len);
    let dot = length(px - vec2<f32>(m + 0.045, m + 0.045)) < 0.016 && fract(frame.time) < 0.6;
    rgb = select(rgb, vec3<f32>(1.0), bracket);
    rgb = select(rgb, vec3<f32>(1.0, 0.05, 0.05), dot);
    // A battery block at the top right.
    let b = px - vec2<f32>(w - m - 0.1, m + 0.03);
    let battery = abs(b.x) < 0.035 && abs(b.y) < 0.015 && (abs(b.x) > 0.03 || abs(b.y) > 0.01 || b.x < 0.01);
    rgb = select(rgb, vec3<f32>(1.0), battery);
    return vec4<f32>(rgb, c.a);
}

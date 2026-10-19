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

struct Params { strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = floor(frame.time * 24.0);
    let px = params.strength / 100.0 * 12.0;
    let off = (vec2<f32>(hash(vec2<f32>(t, 1.0), 3.0), hash(vec2<f32>(t, 2.0), 3.0)) - vec2<f32>(0.5)) * px / frame.size;
    return sample(moved(uv, off, 0.0, 1.0 + px * 2.0 / frame.size.y));
}

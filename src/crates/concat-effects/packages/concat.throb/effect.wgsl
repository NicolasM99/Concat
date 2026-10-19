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

struct Params { strength: f32, luminance: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let ph = 0.5 - 0.5 * cos(frame.time * 4.0);
    let k = params.strength / 100.0;
    let c = sample(moved(uv, vec2<f32>(0.0), 0.0, 1.0 + ph * 0.06 * k));
    return vec4<f32>(c.rgb * (1.0 + ph * params.luminance / 100.0 * 0.6), c.a);
}

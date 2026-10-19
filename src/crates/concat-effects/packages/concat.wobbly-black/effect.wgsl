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

struct Params { size: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = (uv - vec2<f32>(0.5)) * 2.0;
    let a = atan2(d.y, d.x);
    let wob = 0.04 * sin(a * 5.0 + frame.time * 3.0) + 0.03 * sin(a * 3.0 - frame.time * 2.0);
    let edge = 1.0 - params.size / 100.0 * 0.25 + wob;
    let m = smoothstep(edge, edge - 0.03, max(abs(d.x), abs(d.y)) * 0.9 + length(d) * 0.1);
    return vec4<f32>(c.rgb * m, c.a);
}

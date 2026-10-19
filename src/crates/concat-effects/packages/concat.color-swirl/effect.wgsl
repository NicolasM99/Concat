fn rainbow(h: f32) -> vec3<f32> {
    let c = vec3<f32>(0.5) + 0.5 * cos(6.2831853 * (vec3<f32>(h) + vec3<f32>(0.0, 0.33, 0.67)));
    return c * c;
}

struct Params { twist: f32 }

fn swirl_uv(uv: vec2<f32>, amount: f32) -> vec2<f32> {
    let c = (uv - vec2<f32>(0.5)) * frame.size;
    let d = length(c) / frame.size.y;
    let a = amount * (1.0 - smoothstep(0.0, 0.7, d));
    let s = sin(a);
    let co = cos(a);
    return vec2<f32>(c.x * co - c.y * s, c.x * s + c.y * co) / frame.size + vec2<f32>(0.5);
}

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let e = sin(p * 3.14159265);
    let k = e * params.twist * 0.06;
    let c = mix(from_at(swirl_uv(uv, k)), to_at(swirl_uv(uv, -k)), p);
    let d = (uv - vec2<f32>(0.5)) * frame.size / frame.size.y;
    let hue = fract(atan2(d.y, d.x) / 6.2831853 + length(d) * 2.0 - p * 2.0);
    return vec4<f32>(mix(c.rgb, rainbow(hue) * (luma(c.rgb) * 1.5 + 0.1), e * 0.6), c.a);
}

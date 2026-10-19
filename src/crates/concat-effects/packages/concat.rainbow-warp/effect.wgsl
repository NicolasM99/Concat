fn rainbow(h: f32) -> vec3<f32> {
    let c = vec3<f32>(0.5) + 0.5 * cos(6.2831853 * (vec3<f32>(h) + vec3<f32>(0.0, 0.33, 0.67)));
    return c * c;
}

struct Params { warp: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = sin(3.14159265 * progress);
    let k = params.warp / 100.0;
    let off = vec2<f32>(sin(uv.y * 14.0 + progress * 12.0), cos(uv.x * 11.0 + progress * 9.0)) * 0.035 * e * k;
    let a = from_at(uv + off);
    let b = to_at(uv - off);
    let c = mix(a, b, smoothstep(0.3, 0.7, progress));
    let tint = rainbow(fract(uv.x * 1.3 + uv.y * 0.7 + progress * 2.0));
    let rgb = mix(c.rgb, c.rgb * 0.6 + tint * 0.7, e * 0.7 * k);
    return vec4<f32>(rgb, c.a);
}

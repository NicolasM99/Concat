struct Params { bands: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let e = sin(p * 3.14159265);
    let d = (uv - vec2<f32>(0.5)) * frame.size / frame.size.y;
    let r = length(d);
    let a = atan2(d.y, d.x) / 6.2831853;
    let spiral = fract(a * 2.0 + r * max(params.bands, 1.0) - p * 4.0);
    let cover = smoothstep(1.0 - e * 1.2, 1.0 - e * 1.2 + 0.05, 1.0 - r * 0.8);
    let base = select(from_at(uv), to_at(uv), p >= 0.5);
    let levels = 4.0;
    let poster = from_display(floor(clamp(to_display(base.rgb), vec3<f32>(0.0), vec3<f32>(1.0)) * levels + 0.5) / levels);
    let ink = select(vec3<f32>(1.0, 0.85, 0.2), vec3<f32>(0.05, 0.05, 0.08), spiral < 0.5);
    let rgb = mix(mix(base.rgb, poster, e), ink, cover);
    return vec4<f32>(rgb, base.a);
}

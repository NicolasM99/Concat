struct Params { flashes: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let base = select(from_at(uv), to_at(uv), progress >= 0.5);
    let e = sin(3.14159265 * progress);
    let grey = mix(base.rgb, vec3<f32>(luma(base.rgb)), smoothstep(0.0, 0.4, e));
    let n = max(params.flashes, 1.0) * 2.0;
    let k = floor(progress * n);
    let f = fract(progress * n);
    let flash = select(vec3<f32>(0.0), vec3<f32>(1.0), fract(k * 0.5) < 0.25);
    let amount = e * (1.0 - f) * 0.9;
    return vec4<f32>(mix(grey, flash, amount), base.a);
}

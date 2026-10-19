struct Params { softness: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let a = from_at(uv);
    let l = clamp(to_display(vec3<f32>(luma(a.rgb))).x, 0.0, 1.0);
    let soft = max(params.softness / 100.0, 0.01);
    let edge = progress * (1.0 + 2.0 * soft) - soft;
    let m = smoothstep(l - soft, l + soft, edge);
    return mix(a, to_at(uv), m);
}

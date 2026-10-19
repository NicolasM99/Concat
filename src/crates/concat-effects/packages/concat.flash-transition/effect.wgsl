struct Params { brightness: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let base = select(from_at(uv), to_at(uv), progress >= 0.5);
    let e = exp(-pow((progress - 0.5) / 0.16, 2.0));
    let k = params.brightness / 100.0;
    let rgb = base.rgb * (1.0 + e * 8.0 * k) + vec3<f32>(e * 0.8 * k);
    return vec4<f32>(rgb, base.a);
}

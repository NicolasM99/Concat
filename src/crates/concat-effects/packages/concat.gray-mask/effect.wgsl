struct Params { progress: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let k = params.progress / 100.0;
    return vec4<f32>(mix(c.rgb, vec3<f32>(luma(c.rgb) * 0.6), k), c.a);
}

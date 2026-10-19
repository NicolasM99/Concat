struct Params { progress: f32, direction: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = select(abs(uv.y - 0.5), abs(uv.x - 0.5), params.direction < 0.5) * 2.0;
    return vec4<f32>(c.rgb, c.a * step(d, params.progress / 100.0));
}

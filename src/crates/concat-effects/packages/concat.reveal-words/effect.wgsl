struct Params { progress: f32, softness: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let order = reveal_order(uv);
    let soft = max(params.softness / 100.0, 0.001) * 0.3;
    let edge = params.progress / 100.0 * (1.0 + soft);
    let m = smoothstep(edge, edge - soft, order + 0.0001);
    return vec4<f32>(c.rgb, c.a * m);
}

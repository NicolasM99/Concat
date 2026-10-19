struct Params { progress: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = (uv - vec2<f32>(0.5)) * frame.size;
    let a = fract(atan2(d.x, -d.y) / 6.2831853 + 1.0);
    return vec4<f32>(c.rgb, c.a * step(a, params.progress / 100.0));
}

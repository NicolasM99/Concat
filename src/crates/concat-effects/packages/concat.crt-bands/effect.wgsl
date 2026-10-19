struct Params { progress: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let k = params.progress / 100.0;
    let band = floor(uv.y * 12.0 - frame.time * 8.0);
    let shift = (hash(vec2<f32>(band, floor(frame.time * 20.0)), 1.0) - 0.5) * 0.08 * k;
    let c = sample(vec2<f32>(uv.x + shift, uv.y));
    let bright = 1.0 + k * 0.8 * step(0.7, hash(vec2<f32>(band, 2.0), 3.0));
    return vec4<f32>(c.rgb * bright, c.a);
}

struct Params { progress: f32, tiles: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let n = max(params.tiles, 2.0);
    let cells = vec2<f32>(n, max(floor(n * frame.size.y / frame.size.x + 0.5), 1.0));
    let h = hash(floor(uv * cells), 3.0);
    return vec4<f32>(c.rgb, c.a * step(h, params.progress / 100.0 * 1.001));
}

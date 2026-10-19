struct Params { tiles: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let n = max(params.tiles, 2.0);
    let cells = vec2<f32>(n, max(floor(n * frame.size.y / frame.size.x + 0.5), 1.0));
    let cell = floor(uv * cells);
    let centre = (cell + vec2<f32>(0.5)) / cells;
    let t = clamp(progress * 2.0 - (centre.x + centre.y) * 0.5, 0.0, 1.0);
    let w = abs(cos(t * 3.14159265));
    let local = fract(uv * cells) - vec2<f32>(0.5);
    if (abs(local.x) > w * 0.5) {
        return vec4<f32>(0.0, 0.0, 0.0, 1.0);
    }
    let q = (cell + vec2<f32>(local.x / max(w, 1e-4), local.y) + vec2<f32>(0.5)) / cells;
    let c = select(from_at(q), to_at(q), t >= 0.5);
    return vec4<f32>(c.rgb * mix(0.5, 1.0, w), c.a);
}

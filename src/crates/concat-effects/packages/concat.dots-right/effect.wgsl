struct Params { dots: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let n = max(params.dots, 4.0);
    let cells = vec2<f32>(n, n * frame.size.y / frame.size.x);
    let cell = floor(uv * cells);
    let centre = (cell + vec2<f32>(0.5)) / cells;
    let d = length((uv - centre) * cells);
    let grow = clamp(progress * 2.4 - centre.x * 1.4, 0.0, 1.0) * 0.75;
    let m = smoothstep(grow - 0.05, grow + 0.05, d);
    return mix(to_at(uv), from_at(uv), m);
}

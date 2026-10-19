fn inb(uv: vec2<f32>) -> bool {
    return uv.x >= 0.0 && uv.x <= 1.0 && uv.y >= 0.0 && uv.y <= 1.0;
}

struct Params { blocks: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let n = max(params.blocks, 2.0);
    let cells = vec2<f32>(n, max(floor(n * frame.size.y / frame.size.x + 0.5), 1.0));
    let cell = floor(uv * cells);
    let start = hash(cell, 11.0) * 0.6;
    let t = clamp((progress - start) / 0.4, 0.0, 1.0);
    let pop = 1.0 - 0.25 * sin(3.14159265 * t);
    let local = (fract(uv * cells) - vec2<f32>(0.5)) / pop + vec2<f32>(0.5);
    if (!inb(local)) {
        return vec4<f32>(0.0, 0.0, 0.0, 1.0);
    }
    let q = (cell + local) / cells;
    return select(from_at(q), to_at(q), t >= 0.5);
}

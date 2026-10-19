struct Params { lines: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let n = max(params.lines, 4.0);
    let line = floor(uv.y * n);
    let even = fract(line * 0.5) < 0.25;
    let x = select(1.0 - uv.x, uv.x, even);
    let jitter = hash(vec2<f32>(line, 0.0), 3.0) * 0.3;
    let edge = progress * 1.3 - jitter;
    let m = step(edge, x);
    return mix(to_at(uv), from_at(uv), m);
}

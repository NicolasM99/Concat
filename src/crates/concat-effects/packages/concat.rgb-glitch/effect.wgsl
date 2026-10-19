struct Params { split: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = sin(3.14159265 * progress);
    let step_t = floor(progress * 18.0);
    let band = floor(uv.y * 12.0);
    let jump = (hash(vec2<f32>(band, step_t), 4.0) - 0.5) * 0.08 * e;
    let o = vec2<f32>(params.split / 100.0 * 0.04 * e + jump, 0.0);
    let to_side = progress >= 0.5;
    var r: vec4<f32>;
    var g: vec4<f32>;
    var b: vec4<f32>;
    if (to_side) {
        r = to_at(uv + o);
        g = to_at(uv + vec2<f32>(jump, 0.0));
        b = to_at(uv - o);
    } else {
        r = from_at(uv + o);
        g = from_at(uv + vec2<f32>(jump, 0.0));
        b = from_at(uv - o);
    }
    return vec4<f32>(r.r, g.g, b.b, g.a);
}

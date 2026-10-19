struct Params { progress: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let k = params.progress / 100.0;
    let o = vec2<f32>(0.02 * k, 0.0);
    let g = sample(uv);
    let r = sample(uv + o);
    let b = sample(uv - o);
    let lines = 1.0 - 0.5 * k * step(0.5, fract(uv.y * frame.size.y / 4.0));
    return vec4<f32>(vec3<f32>(r.r, g.g, b.b) * lines, max(g.a, max(r.a, b.a)));
}

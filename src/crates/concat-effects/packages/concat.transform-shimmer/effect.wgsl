fn glint(d: vec2<f32>, size: f32) -> f32 {
    let a = abs(d) / max(size, 1e-4);
    let star = max(0.0, 1.0 - (a.x * 8.0 + a.y)) + max(0.0, 1.0 - (a.y * 8.0 + a.x));
    let core = exp(-dot(a, a) * 40.0);
    return star * 0.6 + core;
}

struct Params { shimmer: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = sin(3.14159265 * progress);
    let z = 1.0 + 0.08 * e;
    let suv = (uv - vec2<f32>(0.5)) / z + vec2<f32>(0.5);
    let wave = smoothstep(progress - 0.25, progress + 0.25, uv.x * 0.7 + uv.y * 0.3);
    let c = mix(to_at(suv), from_at(suv), wave);
    let cells = vec2<f32>(14.0, 14.0 * frame.size.y / frame.size.x);
    let cell = floor(uv * cells);
    let centre = (cell + vec2<f32>(hash(cell, 5.0), hash(cell, 6.0))) / cells;
    let live = exp(-pow((uv.x * 0.7 + uv.y * 0.3 - progress) / 0.12, 2.0));
    let d = (uv - centre) * vec2<f32>(1.0, frame.size.y / frame.size.x);
    let star = glint(d, 0.5 / cells.x * (0.4 + hash(cell, 7.0))) * live * params.shimmer / 100.0;
    return vec4<f32>(c.rgb + vec3<f32>(1.0, 0.97, 0.9) * star * 2.5 + vec3<f32>(live * e * 0.15), c.a);
}

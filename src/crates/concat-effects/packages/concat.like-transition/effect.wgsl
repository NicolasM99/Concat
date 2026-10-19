fn heart_sdf(q: vec2<f32>) -> f32 {
    let p = vec2<f32>(abs(q.x), q.y + 0.55);
    if (p.y + p.x > 1.0) {
        return sqrt(dot(p - vec2<f32>(0.25, 0.75), p - vec2<f32>(0.25, 0.75))) - 0.35355;
    }
    let a = dot(p - vec2<f32>(0.0, 1.0), p - vec2<f32>(0.0, 1.0));
    let t = max(p.x + p.y, 0.0) * 0.5;
    let b = dot(p - vec2<f32>(t), p - vec2<f32>(t));
    return sqrt(min(a, b)) * sign(p.x - p.y);
}

struct Params { hearts: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let n = max(params.hearts, 3.0);
    let aspect = frame.size.x / frame.size.y;
    let cells = vec2<f32>(n, max(floor(n / aspect + 0.5), 1.0));
    let cell = floor(uv * cells);
    let born = hash(cell, 1.0) * 0.5;
    let t = clamp((progress - born) / 0.5, 0.0, 1.0);
    let size = sin(3.14159265 * t) * (0.6 + 0.6 * hash(cell, 2.0));
    let centre = cell + vec2<f32>(0.5) + (vec2<f32>(hash(cell, 3.0), hash(cell, 4.0)) - vec2<f32>(0.5)) * 0.4;
    let local = (uv * cells - centre) * vec2<f32>(1.0, cells.y / cells.x * aspect);
    let d = heart_sdf(vec2<f32>(local.x, -local.y) / max(size, 1e-3));
    let base = select(from_at(uv), to_at(uv), progress >= 0.5);
    let pink = mix(vec3<f32>(1.0, 0.08, 0.3), vec3<f32>(1.0, 0.4, 0.6), hash(cell, 5.0));
    let m = smoothstep(0.02, -0.02, d) * step(0.001, size);
    return vec4<f32>(mix(base.rgb, pink, m), base.a);
}

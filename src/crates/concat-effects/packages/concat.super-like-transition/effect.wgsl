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

struct Params { softness: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let d0 = (uv - vec2<f32>(0.5)) * frame.size / frame.size.y;
    let beat = 1.0 + 0.15 * sin(clamp(p * 3.0, 0.0, 1.0) * 3.14159265);
    let size = p * p * 3.2 * beat;
    let d = heart_sdf(vec2<f32>(d0.x, -d0.y) / max(size, 1e-3)) * size;
    let soft = max(params.softness / 100.0, 0.002) * 0.05;
    let inside = smoothstep(soft, -soft, d);
    let rim = exp(-abs(d) / 0.01) * sin(3.14159265 * p);
    let base = mix(from_at(uv), to_at(uv), inside);
    return vec4<f32>(base.rgb + vec3<f32>(1.0, 0.2, 0.45) * rim * 1.5, base.a);
}

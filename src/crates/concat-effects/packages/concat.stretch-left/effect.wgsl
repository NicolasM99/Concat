struct Params { amount: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let k = 1.0 + params.amount / 100.0 * 2.0;
    let edge = 1.0 - p;
    let bend = mix(1.0, k, sin(3.14159265 * p));
    if (uv.x <= edge) {
        let local = uv.x / max(edge, 1e-4);
        let x = 1.0 - pow(1.0 - local, bend);
        return from_at(vec2<f32>(x, uv.y));
    }
    let local = (uv.x - edge) / max(1.0 - edge, 1e-4);
    let x = pow(local, bend);
    return to_at(vec2<f32>(x, uv.y));
}

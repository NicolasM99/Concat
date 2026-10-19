struct Params { amount: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let k = 1.0 + params.amount / 100.0 * 2.0;
    let edge = p;
    if (uv.x >= edge) {
        // The outgoing shot, its left edge dragged right and stretched.
        let local = (uv.x - edge) / max(1.0 - edge, 1e-4);
        let x = pow(local, mix(1.0, k, sin(3.14159265 * p)));
        return from_at(vec2<f32>(x, uv.y));
    }
    let local = uv.x / max(edge, 1e-4);
    let x = 1.0 - pow(1.0 - local, mix(1.0, k, sin(3.14159265 * p)));
    return to_at(vec2<f32>(x, uv.y));
}

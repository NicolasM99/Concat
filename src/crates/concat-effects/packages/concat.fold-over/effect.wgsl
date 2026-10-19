struct Params { depth: f32 }

// The right half of the outgoing shot folds over onto the left like a
// sheet of paper; the back of the flap is the left half of the incoming
// shot, and the right half of it lies beneath.
fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let theta = smoothstep(0.0, 1.0, progress) * 3.14159265;
    let k = params.depth / 100.0 * 1.5;
    let dx = uv.x - 0.5;
    let den = cos(theta) - dx * sin(theta) * k;
    if (abs(den) > 1e-4) {
        let u = dx / den;
        if (u >= 0.0 && u <= 0.5) {
            let depth = 1.0 + u * sin(theta) * k;
            let y = (uv.y - 0.5) * depth + 0.5;
            if (y >= 0.0 && y <= 1.0) {
                let shade = mix(0.55, 1.0, abs(cos(theta)));
                if (cos(theta) >= 0.0) {
                    let c = from_at(vec2<f32>(0.5 + u, y));
                    return vec4<f32>(c.rgb * shade, c.a);
                }
                let c = to_at(vec2<f32>(0.5 - u, y));
                return vec4<f32>(c.rgb * shade, c.a);
            }
        }
    }
    if (uv.x > 0.5) {
        return to_at(uv);
    }
    return from_at(uv);
}

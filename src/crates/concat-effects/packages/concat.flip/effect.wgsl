struct Params { depth: f32 }

fn inb(uv: vec2<f32>) -> bool {
    return uv.x >= 0.0 && uv.x <= 1.0 && uv.y >= 0.0 && uv.y <= 1.0;
}

// A card turning about its vertical axis: the near half grows, the far half
// shrinks into perspective, and past the edge-on moment its back is the
// incoming shot.
fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    var theta = p * 3.14159265;
    let back = theta > 1.5707963;
    if (back) {
        theta = theta - 3.14159265;
    }
    let k = params.depth / 100.0 * 1.2;
    let c = uv - vec2<f32>(0.5);
    let den = cos(theta) - c.x * sin(theta) * k;
    if (abs(den) < 1e-4) {
        return vec4<f32>(0.0, 0.0, 0.0, 1.0);
    }
    let local = c.x / den;
    let depth = 1.0 + local * sin(theta) * k;
    var q: vec2<f32>;
    q.x = local + 0.5;
    q.y = c.y * depth + 0.5;
    if (!inb(q)) {
        return vec4<f32>(0.0, 0.0, 0.0, 1.0);
    }
    let shade = mix(0.55, 1.0, abs(cos(theta)));
    let colour = select(from_at(q), to_at(q), back);
    return vec4<f32>(colour.rgb * shade, colour.a);
}

fn inb(uv: vec2<f32>) -> bool {
    return uv.x >= 0.0 && uv.x <= 1.0 && uv.y >= 0.0 && uv.y <= 1.0;
}

struct Params { depth: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let shrink = 1.0 - 0.3 * sin(3.14159265 * p);
    var theta = p * 3.14159265;
    let back = theta > 1.5707963;
    if (back) {
        theta = theta - 3.14159265;
    }
    let k = params.depth / 100.0 * 1.2;
    let c = (uv - vec2<f32>(0.5)) / shrink;
    let den = cos(theta) - c.x * sin(theta) * k;
    let bg = vec4<f32>(0.01, 0.01, 0.012, 1.0);
    if (abs(den) < 1e-4) {
        return bg;
    }
    let lx = c.x / den;
    let q = vec2<f32>(lx + 0.5, c.y * (1.0 + lx * sin(theta) * k) + 0.5);
    if (!inb(q)) {
        return bg;
    }
    let shade = mix(0.5, 1.0, abs(cos(theta)));
    let colour = select(from_at(q), to_at(q), back);
    return vec4<f32>(colour.rgb * shade, colour.a);
}

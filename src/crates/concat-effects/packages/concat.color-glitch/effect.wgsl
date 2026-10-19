fn turn_hue(rgb: vec3<f32>, degrees: f32) -> vec3<f32> {
    let y = dot(rgb, vec3<f32>(0.299, 0.587, 0.114));
    let i = dot(rgb, vec3<f32>(0.596, -0.274, -0.322));
    let q = dot(rgb, vec3<f32>(0.211, -0.523, 0.312));
    let a = radians(degrees);
    let i2 = i * cos(a) - q * sin(a);
    let q2 = i * sin(a) + q * cos(a);
    return vec3<f32>(y + 0.956 * i2 + 0.621 * q2, y - 0.272 * i2 - 0.647 * q2, y - 1.106 * i2 + 1.703 * q2);
}

struct Params { amount: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = sin(3.14159265 * progress) * params.amount / 100.0;
    let t = floor(progress * 20.0);
    let row = floor(uv.y * 30.0);
    let tear = select(0.0, (hash(vec2<f32>(row, t), 1.0) - 0.5) * 0.2, hash(vec2<f32>(row, t), 2.0) < e * 0.5);
    let q = vec2<f32>(fract(uv.x + tear), uv.y);
    let pick = select(progress >= 0.5, hash(vec2<f32>(row, t), 3.0) < progress, e > 0.1);
    let c = select(from_at(q), to_at(q), pick);
    let block = floor(uv * vec2<f32>(6.0, 10.0));
    let tint_on = hash(block, t + 4.0) < e * 0.35;
    let turned = turn_hue(c.rgb, 120.0 + 120.0 * floor(hash(block, t + 5.0) * 2.0));
    let rgb = select(c.rgb, turned * 1.3, tint_on);
    return vec4<f32>(rgb, c.a);
}

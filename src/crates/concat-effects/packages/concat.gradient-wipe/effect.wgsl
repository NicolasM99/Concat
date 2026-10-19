struct Params { angle: f32, softness: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let a = radians(params.angle);
    let dir = vec2<f32>(cos(a), sin(a));
    let reach = 0.5 * (abs(dir.x) + abs(dir.y));
    let coord = (dot(uv - vec2<f32>(0.5), dir) / reach) * 0.5 + 0.5;
    let soft = max(params.softness / 100.0, 0.01) * 0.6;
    let edge = progress * (1.0 + 2.0 * soft) - soft;
    let m = smoothstep(edge - soft, edge + soft, coord);
    return mix(to_at(uv), from_at(uv), m);
}

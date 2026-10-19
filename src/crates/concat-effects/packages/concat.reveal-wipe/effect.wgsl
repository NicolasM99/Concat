fn along(uv: vec2<f32>, direction: f32) -> f32 {
    if (direction < 0.5) {
        return uv.x;
    } else if (direction < 1.5) {
        return 1.0 - uv.x;
    } else if (direction < 2.5) {
        return uv.y;
    }
    return 1.0 - uv.y;
}

struct Params { progress: f32, direction: f32, softness: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let soft = max(params.softness / 100.0, 0.001) * 0.2;
    let edge = params.progress / 100.0 * (1.0 + soft);
    let m = smoothstep(edge, edge - soft, along(uv, params.direction));
    return vec4<f32>(c.rgb, c.a * m);
}

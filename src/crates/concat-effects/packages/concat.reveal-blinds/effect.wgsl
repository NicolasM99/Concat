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

struct Params { progress: f32, direction: f32, count: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let local = fract(along(uv, params.direction) * max(params.count, 1.0));
    let m = step(local, params.progress / 100.0);
    return vec4<f32>(c.rgb, c.a * m);
}

struct Params { turns: f32 }

fn whirl(uv: vec2<f32>, amount: f32, zoom: f32) -> vec2<f32> {
    let c = (uv - vec2<f32>(0.5)) * frame.size / frame.size.y;
    let r = length(c);
    let a = amount * (1.0 - smoothstep(0.0, 0.9, r)) * 6.2831853;
    let s = sin(a);
    let co = cos(a);
    let t = vec2<f32>(c.x * co - c.y * s, c.x * s + c.y * co) * zoom;
    return t * frame.size.y / frame.size + vec2<f32>(0.5);
}

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let k = params.turns;
    let fa = from_at(whirl(uv, p * k, 1.0 + p * 2.0));
    let ta = to_at(whirl(uv, -(1.0 - p) * k, 1.0 + (1.0 - p) * 2.0));
    return mix(fa, ta, smoothstep(0.3, 0.7, p));
}

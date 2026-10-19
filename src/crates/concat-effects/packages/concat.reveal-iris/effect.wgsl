struct Params { progress: f32, softness: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = length((uv - vec2<f32>(0.5)) * frame.size) / (0.5 * length(frame.size));
    let soft = max(params.softness / 100.0, 0.001) * 0.2;
    let r = params.progress / 100.0 * (1.0 + soft);
    return vec4<f32>(c.rgb, c.a * smoothstep(r, r - soft, d));
}

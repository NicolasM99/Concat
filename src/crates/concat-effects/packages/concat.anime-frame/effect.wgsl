struct Params { progress: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let k = params.progress / 100.0;
    let d = (uv - vec2<f32>(0.5)) * frame.size / frame.size.y;
    let a = atan2(d.y, d.x);
    let lines = step(0.8, hash(vec2<f32>(floor(a * 60.0), floor(frame.time * 15.0)), 1.0)) * smoothstep(0.2, 0.6, length(d));
    return vec4<f32>(mix(c.rgb, vec3<f32>(1.0), clamp(lines * k + k * k * 0.3, 0.0, 1.0)), c.a);
}

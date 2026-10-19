struct Params { waves: f32, height: f32 }

// A wavy edge crosses the frame, the outgoing shot rippling where it meets it.
fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let amp = params.height / 100.0 * 0.08;
    let edge = p * (1.0 + 2.0 * amp + 0.04) - amp - 0.02 + amp * sin(uv.y * params.waves * 6.2831853 + progress * 8.0);
    let x = uv.x;
    let near = exp(-pow((x - edge) / 0.08, 2.0));
    let wobble = vec2<f32>(0.0, sin(x * 40.0 - progress * 20.0) * 0.01 * near);
    let m = smoothstep(edge - 0.01, edge + 0.01, x);
    return mix(to_at(uv - wobble), from_at(uv + wobble), m);
}

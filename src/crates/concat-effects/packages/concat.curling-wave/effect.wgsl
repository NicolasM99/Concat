struct Params { curl: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let amp = params.curl / 100.0;
    let edge = p * 1.4 - 0.2 + 0.06 * amp * sin(uv.y * 9.0 + p * 12.0);
    let d = uv.x - edge;
    if (d > 0.0) {
        // Ahead of the wave the outgoing shot bulges and is drawn under.
        let pull = exp(-d / 0.12) * 0.12 * amp;
        let q = vec2<f32>(uv.x - pull, uv.y + sin(uv.x * 30.0) * pull * 0.3);
        let crest = exp(-d / 0.02) * 0.6 * amp;
        let c = from_at(q);
        return vec4<f32>(c.rgb * (1.0 - exp(-d / 0.05) * 0.4 * amp) + vec3<f32>(crest), c.a);
    }
    let foam = exp(d / 0.015) * 0.5 * amp;
    let b = to_at(uv);
    return vec4<f32>(b.rgb + vec3<f32>(foam), b.a);
}

struct Params { width: f32, warmth: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let coord = (uv.x + uv.y * 0.6) / 1.6;
    let w = max(params.width / 100.0, 0.01) * 0.15;
    let edge = progress * (1.0 + 4.0 * w) - 2.0 * w;
    let m = smoothstep(edge - 0.01, edge + 0.01, coord);
    let base = mix(to_at(uv), from_at(uv), m);
    let band = exp(-pow((coord - edge) / w, 2.0)) * 3.0;
    let tint = mix(vec3<f32>(0.9, 0.95, 1.0), vec3<f32>(1.0, 0.8, 0.55), params.warmth / 100.0);
    return vec4<f32>(base.rgb + tint * band, base.a);
}

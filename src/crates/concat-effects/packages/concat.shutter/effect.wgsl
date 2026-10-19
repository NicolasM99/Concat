struct Params { slats: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let n = max(params.slats, 2.0);
    let local = fract(uv.y * n);
    let close = sin(3.14159265 * smoothstep(0.0, 1.0, progress));
    let covered = abs(local - 0.5) * 2.0 > 1.0 - close * 1.02;
    let base = select(from_at(uv), to_at(uv), progress >= 0.5);
    let slat = vec3<f32>(0.02) + vec3<f32>(0.04) * (1.0 - abs(local - 0.5) * 2.0);
    return select(base, vec4<f32>(slat, 1.0), covered);
}

struct Params { strength: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let base = mix(from_at(uv), to_at(uv), smoothstep(0.45, 0.55, progress));
    let e = sin(3.14159265 * progress) * params.strength / 100.0;
    let pale = mix(base.rgb, vec3<f32>(luma(base.rgb)), e * 0.8);
    let lifted = vec3<f32>(1.0) - (vec3<f32>(1.0) - min(pale, vec3<f32>(1.0))) * (1.0 - e);
    return vec4<f32>(lifted, base.a);
}

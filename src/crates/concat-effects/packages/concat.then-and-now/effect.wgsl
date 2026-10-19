struct Params { age: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let a = from_at(uv);
    let b = to_at(uv);
    let k = params.age / 100.0;
    let l = luma(a.rgb);
    let sepia = vec3<f32>(l * 1.08, l * 0.82, l * 0.55);
    let old = mix(a.rgb, sepia * (0.85 + 0.15 * hash(floor(uv * frame.size), 2.0)), k);
    let first = smoothstep(0.0, 0.5, progress);
    let second = smoothstep(0.5, 1.0, progress);
    var c = mix(mix(a.rgb, old, first), b.rgb, second);
    let flash = exp(-pow((progress - 0.5) / 0.06, 2.0));
    c = c + vec3<f32>(flash * 1.2);
    return vec4<f32>(c, mix(a.a, b.a, second));
}

struct Params { wear: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = sin(3.14159265 * progress);
    let roll = select(0.0, (progress - 0.5) * 2.0, abs(progress - 0.5) < 0.12) * e;
    let ruv = vec2<f32>(uv.x, fract(uv.y + roll));
    let base = select(from_at(ruv), to_at(ruv), progress >= 0.5);
    let k = params.wear / 100.0 * e;
    let l = luma(base.rgb);
    let sepia = mix(base.rgb, vec3<f32>(l * 1.05, l * 0.85, l * 0.6), k);
    let t = floor(progress * 30.0);
    let flicker = 1.0 + (hash(vec2<f32>(t, 0.0), 1.0) - 0.5) * 0.5 * k;
    let sx = hash(vec2<f32>(t, 1.0), 2.0);
    let scratch = smoothstep(0.002, 0.0, abs(uv.x - sx)) * step(0.5, hash(vec2<f32>(t, 2.0), 2.0));
    let dust = step(0.997, hash(floor(uv * frame.size / 3.0), t)) ;
    let bar = smoothstep(0.02, 0.0, abs(fract(uv.y + roll) - 0.0)) * step(0.01, abs(roll));
    var rgb = sepia * flicker * (1.0 - bar);
    rgb = mix(rgb, vec3<f32>(0.9), (scratch + dust) * k);
    return vec4<f32>(rgb, base.a);
}

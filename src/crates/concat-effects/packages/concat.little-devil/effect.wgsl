struct Params { mischief: f32 }

fn horn(p: vec2<f32>, base: vec2<f32>, lean: f32) -> f32 {
    // A curved triangle: wide at the base, a point that leans outward.
    let q = p - base;
    let h = clamp(-q.y / 0.12, 0.0, 1.0);
    let centre = lean * h * h * 0.05;
    let half_width = 0.035 * (1.0 - h);
    return select(0.0, 1.0, q.y <= 0.0 && q.y > -0.12 && abs(q.x - centre) < half_width);
}

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = sin(3.14159265 * progress) * params.mischief / 100.0;
    let t = floor(progress * 16.0);
    let jolt = (hash(vec2<f32>(t, 1.0), 1.0) - 0.5) * 0.03 * e;
    let q = uv + vec2<f32>(jolt, 0.0);
    let base = select(from_at(q), to_at(q), progress >= 0.5);
    let l = luma(base.rgb);
    let red = vec3<f32>(l * 1.6 + 0.05, l * 0.25, l * 0.35);
    var rgb = mix(base.rgb, red, e * 0.8);
    let px = (uv - vec2<f32>(0.5, 0.3)) * frame.size / frame.size.y;
    let horns = max(horn(px, vec2<f32>(-0.12, 0.0), -1.0), horn(px, vec2<f32>(0.12, 0.0), 1.0));
    let flash = select(0.0, 1.0, fract(progress * 4.0) < 0.5) * e;
    rgb = mix(rgb, vec3<f32>(0.9, 0.02, 0.05), horns * flash);
    return vec4<f32>(rgb, base.a);
}

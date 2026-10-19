struct Params { beams: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let base = mix(from_at(uv), to_at(uv), smoothstep(0.35, 0.65, progress));
    let e = sin(3.14159265 * progress);
    let n = i32(max(params.beams, 1.0));
    var light = 0.0;
    for (var i = 0; i < 8; i++) {
        if (i >= n) {
            break;
        }
        let fi = f32(i);
        let x = hash(vec2<f32>(fi, 1.0), 3.0) * 1.6 - 0.3 + (progress - 0.5) * (0.6 + fi * 0.2);
        let slant = (hash(vec2<f32>(fi, 2.0), 3.0) - 0.5) * 0.8;
        let d = uv.x - x - (uv.y - 0.5) * slant;
        let w = 0.02 + 0.05 * hash(vec2<f32>(fi, 4.0), 3.0);
        light += exp(-d * d / (w * w));
    }
    let rgb = base.rgb + vec3<f32>(1.0, 0.95, 0.85) * light * e * 1.4;
    return vec4<f32>(rgb, base.a);
}

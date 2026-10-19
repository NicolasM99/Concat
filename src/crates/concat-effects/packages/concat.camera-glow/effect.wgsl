fn disc_from(uv: vec2<f32>, r: f32) -> vec4<f32> {
    var sum = from_at(uv);
    let aspect = frame.size.y / frame.size.x;
    for (var i = 0; i < 12; i++) {
        let a = f32(i) * 0.5235988;
        let k = select(1.0, 0.5, i % 2 == 1);
        sum += from_at(uv + vec2<f32>(cos(a) * aspect, sin(a)) * r * k);
    }
    return sum / 13.0;
}

fn disc_to(uv: vec2<f32>, r: f32) -> vec4<f32> {
    var sum = to_at(uv);
    let aspect = frame.size.y / frame.size.x;
    for (var i = 0; i < 12; i++) {
        let a = f32(i) * 0.5235988;
        let k = select(1.0, 0.5, i % 2 == 1);
        sum += to_at(uv + vec2<f32>(cos(a) * aspect, sin(a)) * r * k);
    }
    return sum / 13.0;
}

struct Params { glow: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = sin(3.14159265 * progress);
    let r = 0.03 * e;
    let m = smoothstep(0.4, 0.6, progress);
    let soft = mix(disc_from(uv, r), disc_to(uv, r), m);
    let sharp = mix(from_at(uv), to_at(uv), m);
    let k = params.glow / 100.0;
    let rgb = mix(sharp.rgb, soft.rgb, e) * (1.0 + e * 1.5 * k) + soft.rgb * e * k;
    return vec4<f32>(rgb, sharp.a);
}

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

struct Params { softness: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let close = sin(3.14159265 * smoothstep(0.0, 1.0, progress));
    let x = (uv.x - 0.5) * 2.0;
    let bulge = 0.12 * (1.0 - x * x);
    let lid = close * (0.5 + 0.13);
    let top = lid - bulge * (1.0 - close);
    let soft = max(params.softness / 100.0, 0.005) * 0.08;
    let m = smoothstep(top - soft, top, uv.y) * smoothstep(top - soft, top, 1.0 - uv.y);
    let blur = close * close * 0.02;
    let base = select(disc_from(uv, blur), disc_to(uv, blur), progress >= 0.5);
    return vec4<f32>(base.rgb * m, base.a);
}

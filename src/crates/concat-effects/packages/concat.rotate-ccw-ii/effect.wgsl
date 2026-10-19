fn rot_uv(uv: vec2<f32>, centre: vec2<f32>, angle: f32, scale: f32) -> vec2<f32> {
    let c = (uv - centre) * frame.size;
    let s = sin(angle);
    let co = cos(angle);
    let r = vec2<f32>(c.x * co - c.y * s, c.x * s + c.y * co) / max(scale, 0.0001);
    return r / frame.size + centre;
}

fn mirror_uv(uv: vec2<f32>) -> vec2<f32> {
    let m = abs(fract(uv * 0.5) * 2.0 - vec2<f32>(1.0));
    return vec2<f32>(1.0) - m;
}

struct Params { blur: f32 }

// The frame turns a quarter with a smear of its own turning; past halfway
// the incoming shot turns the rest of the way into place.
fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let quarter = 1.5707963 * -1.0;
    let angle = select(-quarter * (1.0 - p), quarter * p, p < 0.5) ;
    let e = sin(3.14159265 * progress);
    let spread = e * params.blur / 100.0 * 0.25 * -1.0;
    var sum = vec4<f32>(0.0);
    for (var i = -3; i <= 3; i++) {
        let a = angle + spread * f32(i) / 3.0;
        let q = mirror_uv(rot_uv(uv, vec2<f32>(0.5), a, 1.0 + 0.3 * e));
        sum += select(to_at(q), from_at(q), p < 0.5);
    }
    return sum / 7.0;
}

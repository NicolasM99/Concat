fn inb(uv: vec2<f32>) -> bool {
    return uv.x >= 0.0 && uv.x <= 1.0 && uv.y >= 0.0 && uv.y <= 1.0;
}

struct Params { spread: f32 }

fn card(uv: vec2<f32>, centre_x: f32, scale: f32) -> vec2<f32> {
    return (uv - vec2<f32>(centre_x, 0.5)) / scale + vec2<f32>(0.5);
}

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let e = sin(3.14159265 * p);
    let k = params.spread / 100.0;
    let fx = 0.5 - e * 0.3 * k;
    let tx = 0.5 + e * 0.3 * k;
    let fs = 1.0 - 0.35 * p - 0.1 * e;
    let ts = 0.65 + 0.35 * p - 0.1 * e;
    let fq = card(uv, fx, fs);
    let tq = card(uv, tx, ts);
    let bg = vec4<f32>(0.02, 0.02, 0.025, 1.0);
    let f = select(bg, vec4<f32>(from_at(fq).rgb * mix(1.0, 0.5, p), 1.0), inb(fq));
    let t = select(bg, vec4<f32>(to_at(tq).rgb * mix(0.5, 1.0, p), 1.0), inb(tq));
    // The nearer card, the larger, is drawn over the other.
    if (p < 0.5) {
        return select(t, f, inb(fq));
    }
    return select(f, t, inb(tq));
}

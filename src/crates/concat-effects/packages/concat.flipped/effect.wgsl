fn rate() -> f32 {
    return 0.3 + params.speed / 100.0 * 3.0;
}

fn span() -> f32 {
    return mix(2.5, 0.25, params.speed / 100.0);
}

/// How far the clip is into its opening `span`, 0..1.
fn opening() -> f32 {
    return clamp(frame.clip_time / span(), 0.0, 1.0);
}

/// How far the clip is into its closing `span`, 0..1; 0 on a layer with no
/// end of its own.
fn closing() -> f32 {
    if (frame.clip_duration <= 0.0) {
        return 0.0;
    }
    return clamp((frame.clip_time - (frame.clip_duration - span())) / span(), 0.0, 1.0);
}

fn mirror_uv(uv: vec2<f32>) -> vec2<f32> {
    let m = abs(fract(uv * 0.5) * 2.0 - vec2<f32>(1.0));
    return vec2<f32>(1.0) - m;
}

fn moved(uv: vec2<f32>, offset: vec2<f32>, angle: f32, scale: f32) -> vec2<f32> {
    let c = (uv - vec2<f32>(0.5)) * frame.size;
    let s = sin(angle);
    let co = cos(angle);
    let r = vec2<f32>(c.x * co - c.y * s, c.x * s + c.y * co) / max(scale, 0.0001);
    return mirror_uv(r / frame.size + vec2<f32>(0.5) - offset);
}

struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let ph = fract(frame.time * rate() * 0.5);
    let w = cos(ph * 6.2831853);
    let x = (uv.x - 0.5) / select(-max(abs(w), 0.02), max(abs(w), 0.02), w >= 0.0) + 0.5;
    if (x < 0.0 || x > 1.0) {
        return vec4<f32>(0.0, 0.0, 0.0, 1.0);
    }
    let c = sample(vec2<f32>(x, uv.y));
    return vec4<f32>(c.rgb * mix(0.6, 1.0, abs(w)), c.a);
}

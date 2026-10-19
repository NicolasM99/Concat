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

struct Params { speed: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let ph = fract(frame.time * rate() * 0.8);
    let beat = exp(-ph * 14.0) + 0.7 * exp(-max(ph - 0.22, 0.0) * 14.0) * step(0.22, ph);
    let k = params.strength / 100.0;
    let c = sample(moved(uv, vec2<f32>(0.0), 0.0, 1.0 + beat * 0.07 * k));
    let edge = smoothstep(0.3, 0.85, length((uv - vec2<f32>(0.5)) * vec2<f32>(1.2, 1.0)));
    let red = mix(c.rgb, c.rgb * vec3<f32>(1.3, 0.5, 0.5) + vec3<f32>(0.15, 0.0, 0.02), edge * beat * k);
    return vec4<f32>(red, c.a);
}

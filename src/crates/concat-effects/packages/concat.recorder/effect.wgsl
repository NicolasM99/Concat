struct Params { static_amount: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let base = select(from_at(uv), to_at(uv), progress >= 0.5);
    let e = sin(3.14159265 * progress);
    let px = uv * frame.size / frame.size.y;
    let w = frame.size.x / frame.size.y;
    // Corner brackets.
    let m = 0.06;
    let len = 0.08;
    let t = 0.006;
    let cx = min(px.x - m, w - m - px.x);
    let cy = min(px.y - m, 1.0 - m - px.y);
    let bracket = (abs(cx) < t && cy >= -t && cy < len) || (abs(cy) < t && cx >= -t && cx < len);
    // The REC light, blinking.
    let dot = length(px - vec2<f32>(m + 0.04, m + 0.04)) < 0.018 && fract(progress * 3.0) < 0.6;
    var rgb = base.rgb;
    let show = smoothstep(0.0, 0.15, e);
    rgb = mix(rgb, vec3<f32>(1.0), select(0.0, show, bracket));
    rgb = mix(rgb, vec3<f32>(1.0, 0.05, 0.05), select(0.0, show, dot));
    let burst = exp(-pow((progress - 0.5) / 0.07, 2.0)) * params.static_amount / 100.0;
    let n = hash(floor(uv * frame.size / 2.0), floor(progress * 60.0));
    rgb = mix(rgb, vec3<f32>(n), burst);
    let scan = 1.0 - 0.12 * e * step(0.5, fract(uv.y * frame.size.y / 3.0));
    return vec4<f32>(rgb * scan, base.a);
}

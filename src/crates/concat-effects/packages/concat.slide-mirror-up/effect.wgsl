fn quint(t: f32) -> f32 {
    if (t < 0.5) {
        return 16.0 * t * t * t * t * t;
    }
    let u = t - 1.0;
    return 1.0 + 16.0 * u * u * u * u * u;
}

// The coordinate along the motion and the one across it.
fn along_of(uv: vec2<f32>, direction: f32) -> f32 {
    return select(uv.x, uv.y, direction < 1.5);
}

fn placed(uv: vec2<f32>, a: f32, direction: f32) -> vec2<f32> {
    if (direction < 1.5) {
        return vec2<f32>(uv.x, a);
    }
    return vec2<f32>(a, uv.y);
}

// The picture after the first pass, at `uv`: the outgoing shot before the
// eased midpoint, the incoming one from it.
fn slid(uv: vec2<f32>, e: f32, direction: f32) -> vec4<f32> {
    let a = along_of(uv, direction);
    let s1 = clamp(2.0 * e, 0.0, 1.0);
    let s2 = (clamp(e, 0.5, 1.0) - 0.5) * 2.0;
    if (e < 0.5) {
        var q: f32;
        if (direction < 0.5 || (direction > 1.5 && direction < 2.5)) {
            // Down and Right fold the shot back over the edge it leaves.
            q = select(a - s1, s1 - a, a <= s1);
        } else {
            // Up and Left carry it on and mirror it at the far edge.
            q = a + s1;
            if (q > 1.0) {
                q = 2.0 - q;
            }
        }
        return from_at(placed(uv, q, direction));
    }
    var q: f32;
    if (direction < 0.5 || (direction > 1.5 && direction < 2.5)) {
        q = 1.0 - select(a - s2, s2 - a, a <= s2);
    } else {
        q = a + s2;
        if (q > 1.0) {
            q = 2.0 - q;
        }
        q = 1.0 - q;
    }
    return to_at(placed(uv, q, direction));
}

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = quint(clamp(progress, 0.0, 1.0));
    let k = select(clamp(2.0 * e, 0.0, 1.0) * 1.25,
                   1.25 - 1.25 * ((clamp(e, 0.5, 1.0) - 0.5) * 2.0), progress >= 0.5);
    let texel = select(1.0 / frame.size.x, 1.0 / frame.size.y, 1.0 < 1.5);
    let step_along = texel * 1.25 * k;
    let centre = slid(uv, e, 1.0);
    var sum = to_display(centre.rgb);
    var alpha = centre.a;
    var weight = 1.0;
    for (var n = 1; n <= 15; n = n + 1) {
        let w = exp(-f32(n) / 800.0);
        let d = f32(n) * step_along;
        let ahead = slid(placed(uv, along_of(uv, 1.0) + d, 1.0), e, 1.0);
        let behind = slid(placed(uv, along_of(uv, 1.0) - d, 1.0), e, 1.0);
        sum = sum + w * (to_display(ahead.rgb) + to_display(behind.rgb));
        alpha = alpha + w * (ahead.a + behind.a);
        weight = weight + 2.0 * w;
    }
    if (1.0 < 0.5) {
        // Down's centre counted twice over the same weight.
        let bright = clamp((sum + to_display(centre.rgb)) / weight, vec3<f32>(0.0), vec3<f32>(1.0));
        return vec4<f32>(from_display(bright), clamp((alpha + centre.a) / weight, 0.0, 1.0));
    }
    return vec4<f32>(from_display(sum / weight), 1.0);
}

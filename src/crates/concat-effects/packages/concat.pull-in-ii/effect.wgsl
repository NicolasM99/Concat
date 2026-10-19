fn ease_x(x1: f32, x2: f32, s: f32) -> f32 {
    let r = 1.0 - s;
    return 3.0 * x1 * r * r * s + 3.0 * x2 * r * s * s + s * s * s;
}

fn bez10(x1: f32, y1: f32, x2: f32, y2: f32, x: f32) -> f32 {
    var lo = 0.0;
    var hi = 1.0;
    for (var k = 0; k < 10; k = k + 1) {
        let mid = (lo + hi) * 0.5;
        if (ease_x(x1, x2, mid) > x) {
            hi = mid;
        } else {
            lo = mid;
        }
    }
    return ease_x(y1, y2, (lo + hi) * 0.5);
}

// One keyframe span: v0 to v1 over frames f0..f1, eased.
fn span(f: f32, f0: f32, f1: f32, v0: f32, v1: f32, x1: f32, y1: f32, x2: f32, y2: f32) -> f32 {
    let e = bez10(x1, y1, x2, y2, clamp((f - f0) / (f1 - f0), 0.0, 1.0));
    return v0 + (v1 - v0) * e;
}

fn mirror2(x: vec2<f32>) -> vec2<f32> {
    return abs((x - 1.0) - 2.0 * floor((x - 1.0) / 2.0) - 1.0);
}

fn frame_at(p: f32) -> f32 {
    return p * 26.000256 + 6.000059;
}

fn opacity_at(f: f32) -> f32 {
    if (f < 10.000098) { return 0.0; }
    if (f < 19.000187) { return span(f, 10.000098, 19.000187, 0.0, 15.0, 0.981631948, -0.034657307, 0.79284447, 1.0); }
    if (f < 32.000315) { return span(f, 19.000187, 32.000315, 15.0, 0.0, 0.04981712, -0.000276598, 0.334699495, 1.0); }
    return 0.0;
}

fn optics_at(f: f32) -> f32 {
    if (f < 12.000118) { return 0.0; }
    if (f < 18.000167) { return span(f, 12.000118, 18.000167, 0.0, 80.0, 1.0, 0.001353903, 0.9999, 0.999998416); }
    if (f < 32.000315) { return span(f, 18.000167, 32.000315, 80.0, 0.0, 0.0001, 0.000009907, 0.0, 0.977482177); }
    return 0.0;
}

fn radial_at(f: f32) -> f32 {
    if (f < 12.000118) { return 0.0; }
    if (f < 17.000167) { return span(f, 12.000118, 17.000167, 0.0, 3.0, 0.33333333, 0.0, 0.66666667, 1.0); }
    if (f < 25.000246) { return span(f, 17.000167, 25.000246, 3.0, 0.0, 0.33333333, 0.0, 0.236802271, 0.996283288); }
    return 0.0;
}

fn scale_a_at(f: f32) -> f32 {
    if (f < 6.000059) { return 100.0; }
    if (f < 18.000177) { return span(f, 6.000059, 18.000177, 100.0, 170.0, 1.0, 0.0, 0.9999, 0.9999999); }
    return 170.0;
}

fn scale_b_at(f: f32) -> f32 {
    if (f < 18.000177) { return 98.0; }
    if (f < 26.000256) { return span(f, 18.000177, 26.000256, 98.0, 100.0, 0.20750752, 0.003777843, 0.0, 0.997456655); }
    return 100.0;
}

fn bulge_at(f: f32) -> f32 {
    if (f < 18.000177) { return -1.5; }
    if (f < 24.000236) { return span(f, 18.000177, 24.000236, -1.5, 0.0, 0.0001, 0.0, 0.0, 0.995419156); }
    return 0.0;
}

fn cubic2(a: vec2<f32>, b: vec2<f32>, c: vec2<f32>, d: vec2<f32>, s: f32) -> vec2<f32> {
    let r = 1.0 - s;
    return a * r * r * r + b * 3.0 * r * r * s + c * 3.0 * r * s * s + d * s * s * s;
}

// A spatial span: the eased fraction e read along the curve by its length,
// as the 200-step table of CapCut's player reads it.
fn along(a: vec2<f32>, b: vec2<f32>, c: vec2<f32>, d: vec2<f32>, e: f32) -> vec2<f32> {
    if (e <= 0.0) { return a; }
    if (e >= 1.0) { return d; }
    var total = 0.0;
    var last = a;
    for (var k = 1; k <= 200; k = k + 1) {
        let q = cubic2(a, b, c, d, f32(k) / 200.0);
        total = total + length(q - last);
        last = q;
    }
    total = total + 0.000001;
    var run = 0.0;
    last = a;
    for (var k = 1; k <= 200; k = k + 1) {
        let q = cubic2(a, b, c, d, f32(k) / 200.0);
        let step_len = length(q - last) / total;
        if (run + step_len >= e) {
            let s = f32(k - 1) / 200.0 + 0.005 * (e - run) / (step_len + 0.000001);
            return cubic2(a, b, c, d, s);
        }
        run = run + step_len;
        last = q;
    }
    return d;
}

// One position span: from a to b by way of controls c and d.
fn place_span(f: f32, f0: f32, f1: f32, x1: f32, y1: f32, x2: f32, y2: f32,
              a: vec2<f32>, b: vec2<f32>, c: vec2<f32>, d: vec2<f32>) -> vec2<f32> {
    let e = bez10(x1, y1, x2, y2, clamp((f - f0) / (f1 - f0), 0.0, 1.0));
    return along(a, c, d, b, e);
}

fn position_at(f: f32) -> vec2<f32> {
    if (f < 8.000079) { return vec2<f32>(250.0625, 145.0); }
    if (f < 13.000128) { return place_span(f, 8.000079, 13.000128, 0.333333, 0.0, 0.622222, 0.820002,
        vec2<f32>(250.0625, 145.0), vec2<f32>(241.28125, 148.9375), vec2<f32>(247.6875, 143.28125), vec2<f32>(241.303534112871, 147.988233566284)); }
    if (f < 16.500162) { return place_span(f, 13.000128, 16.500162, 0.158525, 0.039432, 0.555975, 0.878957,
        vec2<f32>(241.28125, 148.9375), vec2<f32>(250.932487843, 140.871307312), vec2<f32>(241.258965887129, 149.886766433716), vec2<f32>(254.181002495252, 141.203494636762)); }
    if (f < 20.000197) { return place_span(f, 16.500162, 20.000197, 0.106048, 0.068432, 0.476911, 0.645386,
        vec2<f32>(250.932487843, 140.871307312), vec2<f32>(248.85538316, 145.890548021), vec2<f32>(249.607990143262, 140.735866530287), vec2<f32>(248.458811017161, 145.099315673512)); }
    if (f < 23.000226) { return place_span(f, 20.000197, 23.000226, 0.278718, 0.276646, 0.626586, 0.633637,
        vec2<f32>(248.85538316, 145.890548021), vec2<f32>(251.792224564, 144.62579811), vec2<f32>(249.251955302839, 146.681780368488), vec2<f32>(251.365695633336, 144.564091567031)); }
    if (f < 26.000256) { return place_span(f, 23.000226, 26.000256, 0.090825, 0.189732, 0.523059, 0.0,
        vec2<f32>(251.792224564, 144.62579811), vec2<f32>(250.844397734, 145.552943044), vec2<f32>(252.218753494664, 144.687504652969), vec2<f32>(251.509804616763, 145.429879509502)); }
    if (f < 30.000295) { return place_span(f, 26.000256, 30.000295, 0.24036, 1.0, 0.660332, 1.0,
        vec2<f32>(250.844397734, 145.552943044), vec2<f32>(250.0625, 145.0), vec2<f32>(250.178990851237, 145.676006578498), vec2<f32>(250.067125572357, 144.997079481604)); }
    return vec2<f32>(250.0625, 145.0);
}

// A point in GL's bottom-left frame as the shot's top-left coordinate.
fn gl_to_top(q: vec2<f32>) -> vec2<f32> {
    return vec2<f32>(q.x, 1.0 - q.y);
}

// Pass 1: the outgoing shot zoomed, or the incoming one bulged, mirrored
// past its edges.
fn base(q_in: vec2<f32>, flag: bool, f: f32) -> vec3<f32> {
    var q = q_in;
    if (!flag) {
        q = (q - 0.5) / (scale_a_at(f) * 0.01 * 0.9) + 0.5;
        return to_display(from_at(gl_to_top(mirror2(q))).rgb);
    }
    let c = q - 0.5;
    var d = min(1.0, 1.0 - length(c * 2.0 / 1.5));
    d = smoothstep(-0.001, 0.001, d) * d;
    q = c + c * (2.0 - length(c)) * (-(bulge_at(f) * 0.25)) * sqrt(max(d, 0.0)) + 0.5;
    q = (q - 0.5) / (scale_b_at(f) * 0.01 * 0.9) + 0.5;
    return to_display(to_at(gl_to_top(mirror2(q))).rgb);
}

// Pass 2's lens warp, fifteen times over, then pass 1 there.
fn warped(q_in: vec2<f32>, flag: bool, f: f32) -> vec3<f32> {
    let ratio = frame.size / max(frame.size.x, frame.size.y);
    let sc = max(frame.size.x / frame.size.y, frame.size.y / frame.size.x);
    let k = pow(8.0 * (sc / (16.0 / 9.0)) * 0.7 * (optics_at(f) * 0.13) * 0.0059375, 3.0);
    var q = clamp(q_in, vec2<f32>(0.0), vec2<f32>(1.0));
    for (var n = 0; n < 15; n = n + 1) {
        q = (q - 0.5) * ratio;
        let d = length(q * 2.0);
        q = q * pow(d * d + 1.0, -k);
        q = q / ratio + 0.5;
    }
    return base(clamp(q, vec2<f32>(0.0), vec2<f32>(1.0)), flag, f);
}

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = clamp(progress, 0.0, 1.0);
    let f = frame_at(p);
    let flag = floor(p * 26.000256) >= 12.0;
    let pos = position_at(f) / vec2<f32>(500.0, 290.0) - 0.5;
    let white = opacity_at(f) * 0.01;
    let gl = vec2<f32>(uv.x, 1.0 - uv.y);
    // Pass 4: the shaking reframe, mirrored.
    let q = clamp(mirror2((gl - 0.5 + vec2<f32>(-pos.x, pos.y)) * 0.9 + 0.5), vec2<f32>(0.0), vec2<f32>(1.0));
    // Pass 3: the spin blur about the centre.
    let amount = radial_at(f) * 0.5 * 7.9;
    let quality = 0.2 * 2.6 * frame.size.x / 720.0;
    let s = abs(amount) * length(q - 0.5) * quality * 0.5 + 1.0;
    let a = 2.0 * s;
    let stp = 0.225 * amount / a;
    var sum = vec3<f32>(0.0);
    var count = 0.0;
    for (var i = 0; i < 128; i = i + 1) {
        if (f32(i) > a) {
            break;
        }
        let th = (-amount * 0.225 * 0.5 + f32(i) * stp) * 3.1415926 / 180.0;
        let v = q - 0.5;
        let turned = vec2<f32>(cos(th) * v.x - sin(th) * v.y, sin(th) * v.x + cos(th) * v.y) + 0.5;
        sum = sum + warped(turned, flag, f);
        count = count + 1.0;
    }
    let c = clamp(sum / max(count, 1.0) + vec3<f32>(white), vec3<f32>(0.0), vec3<f32>(1.0));
    return vec4<f32>(from_display(c), 1.0);
}

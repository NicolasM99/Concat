fn glint(d: vec2<f32>, size: f32) -> f32 {
    let a = abs(d) / max(size, 1e-4);
    let star = max(0.0, 1.0 - (a.x * 8.0 + a.y)) + max(0.0, 1.0 - (a.y * 8.0 + a.x));
    let core = exp(-dot(a, a) * 40.0);
    return star * 0.6 + core;
}

struct Params { sparkle: f32 }

fn zoom_from(uv: vec2<f32>, z: f32) -> vec4<f32> {
    var sum = vec4<f32>(0.0);
    for (var i = 0; i < 8; i++) {
        let s = z * (1.0 + f32(i) * 0.02 * (z - 1.0));
        sum += from_at((uv - vec2<f32>(0.5)) / s + vec2<f32>(0.5));
    }
    return sum / 8.0;
}

fn zoom_to(uv: vec2<f32>, z: f32) -> vec4<f32> {
    var sum = vec4<f32>(0.0);
    for (var i = 0; i < 8; i++) {
        let s = z * (1.0 + f32(i) * 0.02 * (z - 1.0));
        sum += to_at((uv - vec2<f32>(0.5)) / s + vec2<f32>(0.5));
    }
    return sum / 8.0;
}

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = sin(3.14159265 * progress);
    var c: vec4<f32>;
    if (progress < 0.5) {
        c = zoom_from(uv, 1.0 + progress * 2.0);
    } else {
        c = zoom_to(uv, 1.0 + (1.0 - progress) * 2.0);
    }
    let cells = vec2<f32>(9.0, 9.0 * frame.size.y / frame.size.x);
    let cell = floor(uv * cells);
    let centre = (cell + vec2<f32>(hash(cell, 1.0), hash(cell, 2.0))) / cells;
    let size = 0.6 / cells.x * (0.5 + hash(cell, 3.0));
    let twinkle = 0.5 + 0.5 * sin(progress * 30.0 + hash(cell, 4.0) * 6.28);
    let d = (uv - centre) * vec2<f32>(1.0, frame.size.y / frame.size.x);
    let star = glint(d, size) * twinkle * e * params.sparkle / 100.0;
    return vec4<f32>(c.rgb + vec3<f32>(1.0, 0.95, 0.8) * star * 2.0 + vec3<f32>(e * e * 0.3), c.a);
}

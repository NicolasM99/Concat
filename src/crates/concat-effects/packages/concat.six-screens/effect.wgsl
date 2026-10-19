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

fn vnoise(p: vec2<f32>) -> f32 {
    let i = floor(p);
    let f = fract(p);
    let u = f * f * (3.0 - 2.0 * f);
    let a = hash(i, 1.0);
    let b = hash(i + vec2<f32>(1.0, 0.0), 1.0);
    let c = hash(i + vec2<f32>(0.0, 1.0), 1.0);
    let d = hash(i + vec2<f32>(1.0, 1.0), 1.0);
    return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
}

fn fbm(p: vec2<f32>) -> f32 {
    var sum = 0.0;
    var amp = 0.5;
    var q = p;
    for (var i = 0; i < 5; i++) {
        sum += amp * vnoise(q);
        q = q * 2.03 + vec2<f32>(17.1, 9.2);
        amp *= 0.5;
    }
    return sum / 0.96875;
}

fn rainbow(h: f32) -> vec3<f32> {
    let c = vec3<f32>(0.5) + 0.5 * cos(6.2831853 * (vec3<f32>(h) + vec3<f32>(0.0, 0.33, 0.67)));
    return c * c;
}

fn heart_sdf(q: vec2<f32>) -> f32 {
    let p = vec2<f32>(abs(q.x), q.y + 0.55);
    if (p.y + p.x > 1.0) {
        return sqrt(dot(p - vec2<f32>(0.25, 0.75), p - vec2<f32>(0.25, 0.75))) - 0.35355;
    }
    let a = dot(p - vec2<f32>(0.0, 1.0), p - vec2<f32>(0.0, 1.0));
    let t = max(p.x + p.y, 0.0) * 0.5;
    let b = dot(p - vec2<f32>(t), p - vec2<f32>(t));
    return sqrt(min(a, b)) * sign(p.x - p.y);
}

struct Params { gap: f32 }

// The picture repeated in a grid, each copy the whole picture scaled to fit
// its cell, a thin gap between them.
fn effect(uv: vec2<f32>) -> vec4<f32> {
    let cells = vec2<f32>(3.0, 2.0);
    let cell = floor(uv * cells);
    var local = fract(uv * cells);
    let g = params.gap / 100.0 * 0.04 * cells;
    if (any(local < g * 0.5) || any(local > vec2<f32>(1.0) - g * 0.5)) {
        return vec4<f32>(1.0, 1.0, 1.0, 1.0);
    }
    local = (local - g * 0.5) / (vec2<f32>(1.0) - g);
    // Fill the cell from the middle of the picture, keeping its aspect.
    let cell_aspect = (frame.size.x / cells.x) / (frame.size.y / cells.y);
    let pic_aspect = frame.size.x / frame.size.y;
    var q = local - vec2<f32>(0.5);
    if (cell_aspect < pic_aspect) {
        q.x = q.x * cell_aspect / pic_aspect;
    } else {
        q.y = q.y * pic_aspect / cell_aspect;
    }
    local = q + vec2<f32>(0.5);
    if (false && (i32(cell.x) % 2 == 1)) {
        local.x = 1.0 - local.x;
    }
    return sample(local);
}

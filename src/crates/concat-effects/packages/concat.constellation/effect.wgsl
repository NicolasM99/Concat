struct Params { speed: f32, density: f32, size: f32, look: f32 }

// A field of particles drawn over the clip in three depths. Each depth is a
// grid that drifts with time; a cell holds at most one particle, placed,
// sized, turned and coloured by the cell's hash.

fn shape(p: vec2<f32>, t: f32) -> f32 {
    return exp(-dot(p, p) * 3.0);
}

fn palette(h: f32) -> vec3<f32> {
    return mix(vec3<f32>(0.3, 0.55, 1.0), vec3<f32>(0.7, 0.85, 1.0), h);
}

fn scene_look(rgb: vec3<f32>, k: f32) -> vec3<f32> {
    return rgb * mix(1.0, 0.55, k) * mix(vec3<f32>(1.0), vec3<f32>(0.8, 0.85, 1.1), k);
}

fn depth(uv: vec2<f32>, scale: f32, seed: f32, t: f32) -> vec4<f32> {
    let aspect = frame.size.x / frame.size.y;
    var q = (vec2<f32>(uv.x * aspect, uv.y) - vec2<f32>(0.0, 0.0)) * scale;
    
    q = q - vec2<f32>(0.03, -0.0) * t * scale * 0.1;
    q.x = q.x + sin(q.y * 0.6 + seed * 3.0 + t * 0.7) * 0.0;
    let cell = floor(q);
    if (hash(cell, seed) > params.density / 100.0 * 1.0) {
        return vec4<f32>(0.0);
    }
    let centre = vec2<f32>(0.25) + vec2<f32>(hash(cell, seed + 1.0), hash(cell, seed + 2.0)) * 0.5;
    let r = (0.3 + 0.7 * hash(cell, seed + 3.0)) * params.size / 100.0 * 0.12;
    let spin = (hash(cell, seed + 5.0) - 0.5) * 6.2831853 + t * 0.0 * (hash(cell, seed + 6.0) - 0.5) * 2.0;
    let d = fract(q) - centre;
    let s = sin(spin);
    let c = cos(spin);
    let p = vec2<f32>(d.x * c - d.y * s, d.x * s + d.y * c) / max(r, 1e-4);
    if (dot(p, p) > 9.0) {
        return vec4<f32>(0.0);
    }
    let twinkle = mix(1.0, 0.5 + 0.5 * sin(t * 5.0 + hash(cell, seed + 7.0) * 6.2831853), 1.0);
    let cover = clamp(shape(p, t + hash(cell, seed + 8.0) * 10.0), 0.0, 1.0) * twinkle;
    return vec4<f32>(palette(hash(cell, seed + 4.0)) * cover, cover);
}

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = frame.time * (0.2 + params.speed / 100.0 * 2.4);
    var rgb = scene_look(c.rgb, params.look / 100.0);
    var alpha = c.a;
    let near = depth(uv, 8.0 * 0.6, 11.0, t * 1.3);
    let mid = depth(uv, 8.0, 23.0, t);
    let far = depth(uv, 8.0 * 1.7, 37.0, t * 0.7);
    var fields = array<vec4<f32>, 3>(far * 0.55, mid * 0.8, near);
    for (var i = 0; i < 3; i++) {
        let f = fields[i];
        rgb = rgb + f.rgb * 2.0;
        alpha = max(alpha, f.a);
    }
    return vec4<f32>(rgb, alpha);
}

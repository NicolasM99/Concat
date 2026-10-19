struct Params { radius: f32 }

const PI: f32 = 3.14159265;

fn inb(uv: vec2<f32>) -> bool {
    return uv.x >= 0.0 && uv.x <= 1.0 && uv.y >= 0.0 && uv.y <= 1.0;
}

// A page curl: the outgoing shot is a sheet lifted from the bottom-right
// corner and rolled over a cylinder that travels to the top-left, its pale
// back laid over what is still flat, the incoming shot beneath.
fn page(q: vec2<f32>) -> bool {
    return inb(q);
}

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let dn = normalize(vec2<f32>(1.0, 1.0));
    let r = max(params.radius / 100.0, 0.01) * 0.25;
    let smax = dot(vec2<f32>(1.0, 1.0), dn);
    let pos = mix(smax + 0.02, -r * PI - 0.02, smoothstep(0.0, 1.0, progress));
    let s = dot(uv, dn);
    let dist = s - pos;
    let paper = vec3<f32>(0.85, 0.84, 0.8);
    if (dist < 0.0) {
        // Flat: the back of the turned page may lie over it.
        let sb = 2.0 * pos + PI * r - s;
        let qb = uv + dn * (sb - s);
        if (page(qb) && sb > pos) {
            let c = from_at(qb);
            return vec4<f32>(mix(c.rgb, paper, 0.75) * 0.95, 1.0);
        }
        return from_at(uv);
    }
    if (dist <= r) {
        let a = asin(clamp(dist / r, 0.0, 1.0));
        let sb = pos + (PI - a) * r;
        let qb = uv + dn * (sb - s);
        if (page(qb)) {
            let c = from_at(qb);
            return vec4<f32>(mix(c.rgb, paper, 0.75) * mix(0.75, 1.0, cos(a)), 1.0);
        }
        let sf = pos + a * r;
        let qf = uv + dn * (sf - s);
        if (page(qf)) {
            let c = from_at(qf);
            return vec4<f32>(c.rgb * mix(1.0, 0.55, a / (PI * 0.5)), c.a);
        }
    }
    // Uncovered: the incoming shot, shadowed close to the roll.
    let shadow = 1.0 - 0.5 * exp(-max(dist - r, 0.0) / (r * 0.8));
    let b = to_at(uv);
    let lifted = step(r, dist);
    return vec4<f32>(b.rgb * mix(1.0, shadow, lifted), b.a);
}

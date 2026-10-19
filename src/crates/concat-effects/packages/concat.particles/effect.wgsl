struct Params { size: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let px = max(params.size, 2.0);
    let cells = frame.size / px;
    let drift = vec2<f32>(0.25, -0.15);
    var colour = to_at(uv);
    // A speck leaves its cell when the sweep reaches it and drifts off,
    // fading; look back along the drift for the specks passing here.
    for (var k = 0; k < 5; k++) {
        let back = uv - drift * f32(k) * 0.04;
        let cell = floor(back * cells);
        let centre = (cell + vec2<f32>(0.5)) / cells;
        let leave = centre.x * 0.6 + hash(cell, 5.0) * 0.3;
        let age = progress * 1.1 - leave;
        if (age > 0.0 && age < 0.4) {
            let at = centre + drift * age;
            let d = length((uv - at) * cells);
            let a = smoothstep(0.5, 0.2, d) * (1.0 - age / 0.4);
            let c = from_at(centre);
            colour = vec4<f32>(mix(colour.rgb, c.rgb * 1.6 + vec3<f32>(0.2), a), colour.a);
        }
    }
    let cell = floor(uv * cells);
    let centre = (cell + vec2<f32>(0.5)) / cells;
    let leave = centre.x * 0.6 + hash(cell, 5.0) * 0.3;
    if (progress * 1.1 < leave) {
        return from_at(uv);
    }
    return colour;
}

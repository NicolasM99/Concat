// SPDX-License-Identifier: AGPL-3.0-or-later
// SPDX-FileCopyrightText: 2026 Jareer and Concat contributors

//! Animations: how a clip comes in, goes out, or moves through its time -
//! CapCut's In, Out and Combo, and a title's Loop.
//!
//! An animation is a package like any other, a folder whose `effect.toml`
//! has `kind = "animation"` and an `[animation]` table instead of a shader.
//! The table says which slot it fills, how long it lasts by default, and
//! the motion as expressions of `t`, how far through it the clip is:
//!
//! ```toml
//! [animation]
//! slot = "in"            # in, out, combo or loop
//! duration = 0.5         # seconds, the default; a clip may set its own
//! text = false           # true: it is offered to titles, not pictures
//! scale = "0.6 + 0.4 * t"
//! x = "-(1 - t)"         # frame widths, added to the clip's own
//! y = "0"                # frame heights
//! rotation = "0"         # degrees, clockwise
//! opacity = "t"          # a factor on the clip's own
//! sx = "1"               # a factor on its width alone: a flip, a squeeze
//! sy = "1"               # a factor on its height alone
//!
//! [animation.effect]     # a look ridden over the same window, optional
//! id = "concat.gaussian-blur"
//! params = { radius = "40 * (1 - t)" }
//! ```
//!
//! `t` runs 0..1: from the clip's first frame to the end of its In, from the
//! start of its Out to its last frame, across the whole clip for a Combo,
//! and round each cycle of a Loop. `pi` is π. An In ends where nothing is
//! changed and an Out starts there, so the clip between them is the clip as
//! it was placed: outside its windows an animation adds nothing at all.
//!
//! The motion rides on top of the clip's placement and its keys - a scale
//! is a factor, an offset an addition - so the same animation means the same
//! thing on any clip. The document stores only `{ id, duration }` per slot.
//!
//! A title's animation may move its letters apart instead, with a
//! `[animation.glyphs]` table: each glyph's pose as expressions of `t` and of
//! which glyph it is, and the whole block's - words and plate together:
//!
//! ```toml
//! [animation.glyphs]
//! # per glyph: i (0..n-1, spaces and line breaks counted), n, line, lines,
//! # word, words, li and ln (its place on its line, and the line's length),
//! # u (how far across the block it is, 0..1), gx and gy (its centre from
//! # the block's, ems right and down), ws and we (when its word is spoken,
//! # seconds into the animation), d (the animation's seconds), and w and h,
//! # the block's size in ems
//! dx = "0"               # ems right
//! dy = "0"               # ems down
//! sx = "window(t, i / n, i / n + 0.5)"
//! sy = "1"
//! rotation = "0"         # degrees clockwise, about the glyph's centre
//! opacity = "1"
//! blur = "0"             # ems
//! # the block: n, lines, words, w and h as above
//! block_dx = "0"
//! block_dy = "0"
//! block_scale = "1"
//! block_opacity = "1"
//! block_blur = "0"
//! clip_top = 0           # 1: nothing shows above the block's resting top
//! ```
//!
//! `bezier(x, x1, y1, x2, y2)` eases as After Effects does and
//! `window(t, a, b)` is how far `t` is through `a..b`: the two CapCut's own
//! keyframe tables are written in.

use std::collections::BTreeMap;

use serde::Deserialize;

use crate::expr::{Expr, Value};

/// Which of a clip's animations a package is.
#[derive(Deserialize, Clone, Copy, PartialEq, Eq, Hash, Debug)]
#[serde(rename_all = "lowercase")]
pub enum Slot {
    /// How the clip arrives, over its first seconds.
    In,
    /// How the clip leaves, over its last seconds.
    Out,
    /// A motion over the whole clip, in place of an In and an Out.
    Combo,
    /// A motion that repeats for as long as the clip lasts: a title's.
    Loop,
}

impl Slot {
    /// Every slot, in the order a panel lists them.
    pub const ALL: [Slot; 4] = [Slot::In, Slot::Out, Slot::Combo, Slot::Loop];

    /// The name the manifest and the document spell it with.
    pub fn name(self) -> &'static str {
        match self {
            Slot::In => "in",
            Slot::Out => "out",
            Slot::Combo => "combo",
            Slot::Loop => "loop",
        }
    }
}

fn half() -> f64 {
    0.5
}

/// The `[animation]` table.
#[derive(Deserialize, Clone, PartialEq, Debug)]
#[serde(deny_unknown_fields)]
pub struct AnimationSpec {
    /// The slot the animation fills.
    pub slot: Slot,
    /// How long it lasts when a clip does not say, in seconds; a Loop's
    /// cycle.
    #[serde(default = "half")]
    pub duration: f64,
    /// Whether it is a title's animation: offered to text clips rather
    /// than to pictures. Either kind still runs on any clip it is set on.
    #[serde(default)]
    pub text: bool,
    /// The factor on the clip's scale.
    #[serde(default)]
    pub scale: Option<String>,
    /// Frame widths added to the clip's horizontal offset.
    #[serde(default)]
    pub x: Option<String>,
    /// Frame heights added to the clip's vertical offset.
    #[serde(default)]
    pub y: Option<String>,
    /// Degrees added to the clip's rotation, clockwise.
    #[serde(default)]
    pub rotation: Option<String>,
    /// The factor on the clip's opacity.
    #[serde(default)]
    pub opacity: Option<String>,
    /// The factor on the clip's width alone.
    #[serde(default)]
    pub sx: Option<String>,
    /// The factor on the clip's height alone.
    #[serde(default)]
    pub sy: Option<String>,
    /// A look ridden over the same window.
    #[serde(default)]
    pub effect: Option<LookSpec>,
    /// A title's letters moved apart: see the module docs.
    #[serde(default)]
    pub glyphs: Option<GlyphsSpec>,
}

/// The `[animation.glyphs]` table: each glyph's pose and the block's, as
/// expressions.
#[derive(Deserialize, Clone, PartialEq, Debug, Default)]
#[serde(deny_unknown_fields)]
pub struct GlyphsSpec {
    /// Ems the glyph moves right.
    #[serde(default)]
    pub dx: Option<String>,
    /// Ems it moves down.
    #[serde(default)]
    pub dy: Option<String>,
    /// A factor on its width.
    #[serde(default)]
    pub sx: Option<String>,
    /// A factor on its height.
    #[serde(default)]
    pub sy: Option<String>,
    /// Degrees it turns clockwise.
    #[serde(default)]
    pub rotation: Option<String>,
    /// A factor on its opacity.
    #[serde(default)]
    pub opacity: Option<String>,
    /// Its blur's radius in ems.
    #[serde(default)]
    pub blur: Option<String>,
    /// Ems the block moves right.
    #[serde(default)]
    pub block_dx: Option<String>,
    /// Ems the block moves down.
    #[serde(default)]
    pub block_dy: Option<String>,
    /// A factor on the block's size, about its centre.
    #[serde(default)]
    pub block_scale: Option<String>,
    /// A factor on the block's opacity.
    #[serde(default)]
    pub block_opacity: Option<String>,
    /// The block's blur's radius in ems.
    #[serde(default)]
    pub block_blur: Option<String>,
    /// Whether nothing shows above the block's resting top edge.
    #[serde(default)]
    pub clip_top: bool,
}

/// One glyph's pose on one frame; see [`GlyphsSpec`].
#[derive(Clone, Copy, PartialEq, Debug)]
pub struct GlyphMotion {
    /// Ems right.
    pub dx: f64,
    /// Ems down.
    pub dy: f64,
    /// A factor on its width.
    pub sx: f64,
    /// A factor on its height.
    pub sy: f64,
    /// Degrees clockwise.
    pub rotation: f64,
    /// A factor on its opacity.
    pub opacity: f64,
    /// Its blur's radius in ems.
    pub blur: f64,
}

impl GlyphMotion {
    /// Where the layout put it.
    pub const REST: GlyphMotion = GlyphMotion {
        dx: 0.0,
        dy: 0.0,
        sx: 1.0,
        sy: 1.0,
        rotation: 0.0,
        opacity: 1.0,
        blur: 0.0,
    };
}

/// The block's pose on one frame; see [`GlyphsSpec`].
#[derive(Clone, Copy, PartialEq, Debug)]
pub struct BlockMotion {
    /// Ems right.
    pub dx: f64,
    /// Ems down.
    pub dy: f64,
    /// A factor on its size, about its centre.
    pub scale: f64,
    /// A factor on its opacity.
    pub opacity: f64,
    /// Its blur's radius in ems.
    pub blur: f64,
    /// Whether nothing shows above its resting top edge.
    pub clip_top: bool,
}

impl BlockMotion {
    /// Where the layout put it.
    pub const REST: BlockMotion = BlockMotion {
        dx: 0.0,
        dy: 0.0,
        scale: 1.0,
        opacity: 1.0,
        blur: 0.0,
        clip_top: false,
    };
}

/// Which glyph a pose is asked for, and the block it is in.
#[derive(Clone, Copy, PartialEq, Debug)]
pub struct GlyphPlace {
    /// Its character's index, spaces and line breaks counted.
    pub index: usize,
    /// How many characters there are.
    pub count: usize,
    /// The laid-out line it is on.
    pub line: usize,
    /// How many lines there are.
    pub lines: usize,
    /// The word it is in.
    pub word: usize,
    /// How many words there are.
    pub words: usize,
    /// The block's width in ems.
    pub width: f64,
    /// The block's height in ems.
    pub height: f64,
    /// Its place on its line, from 0.
    pub in_line: usize,
    /// How many glyphs its line holds.
    pub line_glyphs: usize,
    /// How far across the block its centre is, 0..1.
    pub across: f64,
    /// Its centre from the block's centre in ems, right and down.
    pub from_centre: (f64, f64),
    /// When its word is spoken, seconds into the animation: start and end.
    pub word_time: (f64, f64),
    /// How long the animation runs, in seconds.
    pub duration: f64,
}

/// The names a glyph's expressions read, and the block's.
const GLYPH_NAMES: [&str; 18] = [
    "t", "pi", "i", "n", "line", "lines", "word", "words", "w", "h", "li", "ln", "u", "gx", "gy",
    "ws", "we", "d",
];
const BLOCK_NAMES: [&str; 7] = ["t", "pi", "n", "lines", "words", "w", "h"];

/// The `[animation.effect]` table: an effect package and its knobs as
/// expressions of `t`.
#[derive(Deserialize, Clone, PartialEq, Debug)]
#[serde(deny_unknown_fields)]
pub struct LookSpec {
    /// The effect package's id.
    pub id: String,
    /// Its knobs, each an expression of `t`; a knob left out keeps its
    /// default.
    #[serde(default)]
    pub params: BTreeMap<String, String>,
}

/// The longest an animation may last by default, in seconds.
pub const MAX_DURATION: f64 = 60.0;

/// What a clip's animations do to it at one instant, on top of what it
/// already is.
#[derive(Clone, Copy, PartialEq, Debug)]
pub struct Motion {
    /// A factor on the scale.
    pub scale: f64,
    /// Frame widths added to the horizontal offset.
    pub x: f64,
    /// Frame heights added to the vertical offset.
    pub y: f64,
    /// Degrees added to the rotation.
    pub rotation: f64,
    /// A factor on the opacity.
    pub opacity: f64,
    /// A factor on the width alone.
    pub sx: f64,
    /// A factor on the height alone.
    pub sy: f64,
}

impl Motion {
    /// Nothing changed.
    pub const NONE: Motion = Motion {
        scale: 1.0,
        x: 0.0,
        y: 0.0,
        rotation: 0.0,
        opacity: 1.0,
        sx: 1.0,
        sy: 1.0,
    };

    /// `self` then `other`, both riding on the clip.
    pub fn then(self, other: Motion) -> Motion {
        Motion {
            scale: self.scale * other.scale,
            x: self.x + other.x,
            y: self.y + other.y,
            rotation: self.rotation + other.rotation,
            opacity: self.opacity * other.opacity,
            sx: self.sx * other.sx,
            sy: self.sy * other.sy,
        }
    }

    /// Whether it changes nothing, to within a hair.
    pub fn is_none(self) -> bool {
        (self.scale - 1.0).abs() < 1e-9
            && self.x.abs() < 1e-9
            && self.y.abs() < 1e-9
            && self.rotation.abs() < 1e-9
            && (self.opacity - 1.0).abs() < 1e-9
            && (self.sx - 1.0).abs() < 1e-9
            && (self.sy - 1.0).abs() < 1e-9
    }
}

impl Default for Motion {
    fn default() -> Self {
        Motion::NONE
    }
}

/// An animation's table, its expressions parsed once at load.
#[derive(Clone, Debug)]
pub struct Animation {
    spec: AnimationSpec,
    motion: [Option<Expr>; 7],
    look: Option<(String, Vec<(String, Expr)>)>,
    /// The glyphs' seven expressions and the block's five, parsed.
    glyphs: Option<Choreography>,
}

/// A glyphs table parsed: each glyph's seven expressions, the block's five.
type Choreography = ([Option<Expr>; 7], [Option<Expr>; 5]);

/// The names an animation's expressions may read.
const NAMES: [&str; 2] = ["t", "pi"];

fn parse(what: &str, source: &str) -> Result<Expr, String> {
    parse_reading(what, source, &NAMES)
}

fn parse_reading(what: &str, source: &str, known: &[&str]) -> Result<Expr, String> {
    let expr = Expr::parse(source).map_err(|error| format!("{what} = {source:?}: {}", error.0))?;
    let mut names = Vec::new();
    expr.names(&mut names);
    if let Some(name) = names.iter().find(|name| !known.contains(&name.as_str())) {
        return Err(format!(
            "{what} = {source:?}: `{name}` is not known; it reads {}",
            known.join(", ")
        ));
    }
    Ok(expr)
}

impl Animation {
    /// The table checked and its expressions parsed: what a load refuses a
    /// package over.
    pub fn new(spec: AnimationSpec) -> Result<Animation, String> {
        if !(spec.duration.is_finite() && spec.duration > 0.0 && spec.duration <= MAX_DURATION) {
            return Err(format!(
                "[animation] duration {} is outside 0..{MAX_DURATION} seconds",
                spec.duration
            ));
        }
        let fields = [
            ("scale", &spec.scale),
            ("x", &spec.x),
            ("y", &spec.y),
            ("rotation", &spec.rotation),
            ("opacity", &spec.opacity),
            ("sx", &spec.sx),
            ("sy", &spec.sy),
        ];
        let mut motion: [Option<Expr>; 7] = Default::default();
        for (slot, (what, source)) in motion.iter_mut().zip(fields) {
            if let Some(source) = source {
                *slot = Some(parse(what, source)?);
            }
        }
        let look = match &spec.effect {
            Some(look) => {
                let mut knobs = Vec::new();
                for (key, source) in &look.params {
                    knobs.push((key.clone(), parse(&format!("effect {key}"), source)?));
                }
                Some((look.id.clone(), knobs))
            }
            None => None,
        };
        let glyphs = match &spec.glyphs {
            Some(table) => {
                let mut glyph: [Option<Expr>; 7] = Default::default();
                let fields = [
                    ("dx", &table.dx),
                    ("dy", &table.dy),
                    ("sx", &table.sx),
                    ("sy", &table.sy),
                    ("rotation", &table.rotation),
                    ("opacity", &table.opacity),
                    ("blur", &table.blur),
                ];
                for (slot, (what, source)) in glyph.iter_mut().zip(fields) {
                    if let Some(source) = source {
                        *slot = Some(parse_reading(what, source, &GLYPH_NAMES)?);
                    }
                }
                let mut block: [Option<Expr>; 5] = Default::default();
                let fields = [
                    ("block_dx", &table.block_dx),
                    ("block_dy", &table.block_dy),
                    ("block_scale", &table.block_scale),
                    ("block_opacity", &table.block_opacity),
                    ("block_blur", &table.block_blur),
                ];
                for (slot, (what, source)) in block.iter_mut().zip(fields) {
                    if let Some(source) = source {
                        *slot = Some(parse_reading(what, source, &BLOCK_NAMES)?);
                    }
                }
                Some((glyph, block))
            }
            None => None,
        };
        let animation = Animation {
            spec,
            motion,
            look,
            glyphs,
        };
        // An expression that cannot be evaluated - text where a number is
        // wanted - is a fault of the package, found here rather than on a
        // frame.
        for t in [0.0, 0.5, 1.0] {
            animation.try_motion_at(t)?;
            if animation.glyphs.is_some() {
                let place = GlyphPlace {
                    index: 1,
                    count: 4,
                    line: 0,
                    lines: 1,
                    word: 0,
                    words: 2,
                    width: 6.0,
                    height: 1.3,
                    in_line: 1,
                    line_glyphs: 4,
                    across: 0.4,
                    from_centre: (-0.5, 0.0),
                    word_time: (0.1, 0.3),
                    duration: 0.5,
                };
                animation.try_glyph_at(t, &place)?;
                animation.try_block_at(t, &place)?;
            }
        }
        Ok(animation)
    }

    /// The slot it fills.
    pub fn slot(&self) -> Slot {
        self.spec.slot
    }

    /// Its default length in seconds.
    pub fn duration(&self) -> f64 {
        self.spec.duration
    }

    /// Whether it is offered to titles.
    pub fn for_text(&self) -> bool {
        self.spec.text
    }

    /// The id of the effect it rides over its window, if any.
    pub fn look_id(&self) -> Option<&str> {
        self.look.as_ref().map(|(id, _)| id.as_str())
    }

    fn env(t: f64) -> BTreeMap<String, Value> {
        BTreeMap::from([
            ("t".to_owned(), Value::Float(t)),
            ("pi".to_owned(), Value::Float(std::f64::consts::PI)),
        ])
    }

    fn try_motion_at(&self, t: f64) -> Result<Motion, String> {
        let env = Self::env(t);
        let read = |expr: &Option<Expr>, or: f64| -> Result<f64, String> {
            match expr {
                Some(expr) => match expr.eval(&env).map_err(|error| error.0)? {
                    Value::Int(n) => Ok(n as f64),
                    Value::Float(x) => Ok(x),
                    Value::Text(_) => Err("an animation's expression must be a number".to_owned()),
                },
                None => Ok(or),
            }
        };
        let [scale, x, y, rotation, opacity, sx, sy] = &self.motion;
        Ok(Motion {
            scale: read(scale, 1.0)?,
            x: read(x, 0.0)?,
            y: read(y, 0.0)?,
            rotation: read(rotation, 0.0)?,
            opacity: read(opacity, 1.0)?.clamp(0.0, 1.0),
            sx: read(sx, 1.0)?,
            sy: read(sy, 1.0)?,
        })
    }

    /// The motion `t` of the way through. Anything that does not come out
    /// a finite number is taken as no change.
    pub fn motion_at(&self, t: f64) -> Motion {
        match self.try_motion_at(t.clamp(0.0, 1.0)) {
            Ok(motion)
                if [
                    motion.scale,
                    motion.x,
                    motion.y,
                    motion.rotation,
                    motion.opacity,
                    motion.sx,
                    motion.sy,
                ]
                .iter()
                .all(|v| v.is_finite()) =>
            {
                Motion {
                    scale: motion.scale.max(0.0),
                    sx: motion.sx.max(0.0),
                    sy: motion.sy.max(0.0),
                    ..motion
                }
            }
            _ => Motion::NONE,
        }
    }

    /// Whether it moves a title's letters apart rather than the clip.
    pub fn moves_glyphs(&self) -> bool {
        self.glyphs.is_some()
    }

    fn glyph_env(t: f64, place: &GlyphPlace) -> BTreeMap<String, Value> {
        let mut env = Self::env(t);
        for (name, value) in [
            ("i", place.index),
            ("n", place.count),
            ("line", place.line),
            ("lines", place.lines),
            ("word", place.word),
            ("words", place.words),
            ("li", place.in_line),
            ("ln", place.line_glyphs),
        ] {
            env.insert(name.to_owned(), Value::Int(value as i64));
        }
        env.insert("w".to_owned(), Value::Float(place.width));
        env.insert("h".to_owned(), Value::Float(place.height));
        env.insert("u".to_owned(), Value::Float(place.across));
        env.insert("gx".to_owned(), Value::Float(place.from_centre.0));
        env.insert("gy".to_owned(), Value::Float(place.from_centre.1));
        env.insert("ws".to_owned(), Value::Float(place.word_time.0));
        env.insert("we".to_owned(), Value::Float(place.word_time.1));
        env.insert("d".to_owned(), Value::Float(place.duration));
        env
    }

    fn read_into(
        expr: &Option<Expr>,
        env: &BTreeMap<String, Value>,
        or: f64,
    ) -> Result<f64, String> {
        match expr {
            Some(expr) => match expr.eval(env).map_err(|error| error.0)? {
                Value::Int(n) => Ok(n as f64),
                Value::Float(x) => Ok(x),
                Value::Text(_) => Err("an animation's expression must be a number".to_owned()),
            },
            None => Ok(or),
        }
    }

    fn try_glyph_at(&self, t: f64, place: &GlyphPlace) -> Result<GlyphMotion, String> {
        let Some((glyph, _)) = &self.glyphs else {
            return Ok(GlyphMotion::REST);
        };
        let env = Self::glyph_env(t, place);
        let [dx, dy, sx, sy, rotation, opacity, blur] = glyph;
        Ok(GlyphMotion {
            dx: Self::read_into(dx, &env, 0.0)?,
            dy: Self::read_into(dy, &env, 0.0)?,
            sx: Self::read_into(sx, &env, 1.0)?,
            sy: Self::read_into(sy, &env, 1.0)?,
            rotation: Self::read_into(rotation, &env, 0.0)?,
            opacity: Self::read_into(opacity, &env, 1.0)?.clamp(0.0, 1.0),
            blur: Self::read_into(blur, &env, 0.0)?.max(0.0),
        })
    }

    fn try_block_at(&self, t: f64, place: &GlyphPlace) -> Result<BlockMotion, String> {
        let Some((_, block)) = &self.glyphs else {
            return Ok(BlockMotion::REST);
        };
        let env = Self::glyph_env(t, place);
        let [dx, dy, scale, opacity, blur] = block;
        Ok(BlockMotion {
            dx: Self::read_into(dx, &env, 0.0)?,
            dy: Self::read_into(dy, &env, 0.0)?,
            scale: Self::read_into(scale, &env, 1.0)?.max(0.0),
            opacity: Self::read_into(opacity, &env, 1.0)?.clamp(0.0, 1.0),
            blur: Self::read_into(blur, &env, 0.0)?.max(0.0),
            clip_top: self.spec.glyphs.as_ref().is_some_and(|g| g.clip_top),
        })
    }

    /// One glyph's pose `t` of the way through; one whose expressions fail
    /// or come out other than finite is left where the layout put it.
    pub fn glyph_at(&self, t: f64, place: &GlyphPlace) -> GlyphMotion {
        match self.try_glyph_at(t.clamp(0.0, 1.0), place) {
            Ok(pose)
                if [
                    pose.dx,
                    pose.dy,
                    pose.sx,
                    pose.sy,
                    pose.rotation,
                    pose.opacity,
                    pose.blur,
                ]
                .iter()
                .all(|v| v.is_finite()) =>
            {
                pose
            }
            _ => GlyphMotion::REST,
        }
    }

    /// The block's pose `t` of the way through, on the same terms.
    pub fn block_at(&self, t: f64, place: &GlyphPlace) -> BlockMotion {
        match self.try_block_at(t.clamp(0.0, 1.0), place) {
            Ok(pose)
                if [pose.dx, pose.dy, pose.scale, pose.opacity, pose.blur]
                    .iter()
                    .all(|v| v.is_finite()) =>
            {
                pose
            }
            _ => BlockMotion::REST,
        }
    }

    /// The look's knobs `t` of the way through, by key; a knob whose
    /// expression fails is left at its default.
    pub fn look_at(&self, t: f64) -> Option<(&str, BTreeMap<String, f64>)> {
        let (id, knobs) = self.look.as_ref()?;
        let env = Self::env(t.clamp(0.0, 1.0));
        let values = knobs
            .iter()
            .filter_map(|(key, expr)| match expr.eval(&env) {
                Ok(Value::Int(n)) => Some((key.clone(), n as f64)),
                Ok(Value::Float(x)) if x.is_finite() => Some((key.clone(), x)),
                _ => None,
            })
            .collect();
        Some((id.as_str(), values))
    }
}

/// How far into its window `slot` is at `at` seconds into a clip `length`
/// long, for an animation lasting `duration`: None outside the window,
/// where it changes nothing. `duration` is what the clip set, already
/// fitted ([`fitted`]).
pub fn progress(slot: Slot, duration: f64, at: f64, length: f64) -> Option<f64> {
    // NaN fails every comparison, so it is taken as no window at all.
    let positive = |x: f64| x.is_finite() && x > 0.0;
    if !positive(length) || !positive(duration) || at < 0.0 || at > length {
        return None;
    }
    match slot {
        Slot::In => (at < duration).then(|| (at / duration).clamp(0.0, 1.0)),
        Slot::Out => {
            let start = length - duration;
            (at >= start).then(|| ((at - start) / duration).clamp(0.0, 1.0))
        }
        Slot::Combo => Some((at / length).clamp(0.0, 1.0)),
        Slot::Loop => Some((at / duration).fract()),
    }
}

/// An In and an Out fitted into a clip `length` long: each kept as it is
/// when both fit, and shrunk in proportion when together they would not.
pub fn fitted(enter: Option<f64>, exit: Option<f64>, length: f64) -> (Option<f64>, Option<f64>) {
    let a = enter.unwrap_or(0.0).max(0.0);
    let b = exit.unwrap_or(0.0).max(0.0);
    let total = a + b;
    if total <= length || total <= 0.0 {
        return (enter, exit);
    }
    let k = length.max(0.0) / total;
    (enter.map(|d| d * k), exit.map(|d| d * k))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn spec(slot: Slot) -> AnimationSpec {
        AnimationSpec {
            slot,
            duration: 0.5,
            text: false,
            scale: Some("0.5 + 0.5 * t".to_owned()),
            x: Some("-(1 - t)".to_owned()),
            y: None,
            rotation: None,
            opacity: Some("t".to_owned()),
            sx: None,
            sy: None,
            effect: None,
            glyphs: None,
        }
    }

    #[test]
    fn an_in_starts_moved_and_ends_where_the_clip_is() {
        let animation = Animation::new(spec(Slot::In)).expect("loads");
        let start = animation.motion_at(0.0);
        assert_eq!(start.scale, 0.5);
        assert_eq!(start.x, -1.0);
        assert_eq!(start.opacity, 0.0);
        assert!(animation.motion_at(1.0).is_none());
    }

    #[test]
    fn windows_open_and_close_where_their_slots_say() {
        assert_eq!(progress(Slot::In, 1.0, 0.5, 4.0), Some(0.5));
        assert_eq!(progress(Slot::In, 1.0, 1.5, 4.0), None);
        assert_eq!(progress(Slot::Out, 1.0, 3.5, 4.0), Some(0.5));
        assert_eq!(progress(Slot::Out, 1.0, 2.5, 4.0), None);
        assert_eq!(progress(Slot::Combo, 1.0, 1.0, 4.0), Some(0.25));
        assert_eq!(progress(Slot::Loop, 1.0, 2.25, 4.0), Some(0.25));
    }

    #[test]
    fn an_in_and_an_out_that_overlap_are_shrunk_to_fit() {
        assert_eq!(fitted(Some(1.0), Some(1.0), 4.0), (Some(1.0), Some(1.0)));
        assert_eq!(fitted(Some(3.0), Some(1.0), 2.0), (Some(1.5), Some(0.5)));
    }

    #[test]
    fn an_unknown_name_is_refused() {
        let mut bad = spec(Slot::In);
        bad.x = Some("speed * t".to_owned());
        assert!(Animation::new(bad).is_err());
    }

    #[test]
    fn motions_compose_as_factors_and_sums() {
        let a = Motion {
            scale: 2.0,
            x: 0.1,
            ..Motion::NONE
        };
        let b = Motion {
            scale: 0.5,
            x: 0.2,
            opacity: 0.5,
            ..Motion::NONE
        };
        let c = a.then(b);
        assert_eq!(c.scale, 1.0);
        assert!((c.x - 0.3).abs() < 1e-12);
        assert_eq!(c.opacity, 0.5);
    }
}

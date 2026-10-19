// SPDX-License-Identifier: AGPL-3.0-or-later
// SPDX-FileCopyrightText: 2026 Jareer and Concat contributors

//! Titles whose letters move apart.
//!
//! An animation with an `[animation.glyphs]` table poses each glyph on its
//! own - CapCut's letter-by-letter Ins and Outs - which a still and a clip
//! transform cannot do. Over the animation's window such a title is painted
//! once a frame, every glyph where the table says, and each painting stands
//! in for the title for that frame; between the windows the still does, as
//! for any title. The paintings are keyed like the still, by everything
//! that changes their pixels, so a title that has not changed is not
//! painted again.

use std::path::{Path, PathBuf};

use concat_effects::Catalogue;
use concat_effects::animation::{Animation, GlyphPlace};
use concat_export::{ExportClip, ExportKey};
use concat_project::model::{Clip, ClipAnimation};
use concat_text::{BlockPose, Choreography, Fonts, GlyphPose, GlyphSlot, TitleStyle};

/// The animation a slot holds, when it moves a title's letters apart.
fn moving<'a>(catalogue: &'a Catalogue, slot: &Option<ClipAnimation>) -> Option<&'a Animation> {
    slot.as_ref()
        .and_then(|chosen| catalogue.get(&chosen.id))
        .and_then(|package| package.animation())
        .filter(|animation| animation.moves_glyphs())
}

/// One frame of an animation, as the painter asks for it.
struct Dance<'a> {
    animation: &'a Animation,
    t: f64,
    count: usize,
    words: usize,
    lines: usize,
    /// The animation's length in seconds, and when it starts in the clip.
    duration: f64,
    from: f64,
    /// Each word's spoken span in clip seconds, or empty to spread the
    /// words evenly over the animation.
    word_times: &'a [[f64; 2]],
}

impl Dance<'_> {
    /// When word `word` is spoken, in seconds into the animation.
    fn word_time(&self, word: usize) -> (f64, f64) {
        match self.word_times.get(word) {
            Some([start, end]) => (start - self.from, end - self.from),
            None => {
                let share = self.duration / self.words.max(1) as f64;
                (share * word as f64, share * (word + 1) as f64)
            }
        }
    }
}

impl Choreography for Dance<'_> {
    fn block(&self, width: f32, height: f32) -> BlockPose {
        let pose = self.animation.block_at(
            self.t,
            &GlyphPlace {
                index: 0,
                count: self.count,
                line: 0,
                lines: self.lines,
                word: 0,
                words: self.words,
                width: f64::from(width),
                height: f64::from(height),
                in_line: 0,
                line_glyphs: 0,
                across: 0.5,
                from_centre: (0.0, 0.0),
                word_time: (0.0, self.duration),
                duration: self.duration,
            },
        );
        BlockPose {
            dx: pose.dx as f32,
            dy: pose.dy as f32,
            scale: pose.scale as f32,
            opacity: pose.opacity as f32,
            blur: pose.blur as f32,
            clip_top: pose.clip_top,
        }
    }

    fn glyph(&self, slot: &GlyphSlot) -> GlyphPose {
        let pose = self.animation.glyph_at(
            self.t,
            &GlyphPlace {
                index: slot.index,
                count: slot.count,
                line: slot.line,
                lines: slot.lines,
                word: slot.word,
                words: slot.words,
                width: 0.0,
                height: 0.0,
                in_line: slot.in_line,
                line_glyphs: slot.line_glyphs,
                across: f64::from(slot.across),
                from_centre: (f64::from(slot.from_centre.0), f64::from(slot.from_centre.1)),
                word_time: self.word_time(slot.word),
                duration: self.duration,
            },
        );
        GlyphPose {
            dx: pose.dx as f32,
            dy: pose.dy as f32,
            sx: pose.sx as f32,
            sy: pose.sy as f32,
            rotation: pose.rotation as f32,
            opacity: pose.opacity as f32,
            blur: pose.blur as f32,
        }
    }
}

/// What painting one title's frames needs.
pub(crate) struct Stage<'a> {
    pub fonts: &'a Fonts,
    pub dir: &'a Path,
    /// The still's key: everything its pixels depend on.
    pub key: u64,
    pub width: u32,
    pub height: u32,
    /// The project's frame rate.
    pub rate: f64,
}

/// The pieces that stand in for a title clip whose In or Out moves its
/// letters: a painting a frame over those windows and the still between
/// them, each the still's clip cut to its span. Empty when neither slot
/// moves letters, and the still stands in alone.
pub(crate) fn pieces(
    stage: &Stage<'_>,
    clip: &Clip,
    title: &TitleStyle,
    word_times: &[[f64; 2]],
    still: &ExportClip,
) -> Result<Vec<ExportClip>, String> {
    let catalogue = Catalogue::builtin();
    let Some(chosen) = &clip.animations else {
        return Ok(Vec::new());
    };
    let enter = moving(catalogue, &chosen.enter);
    let exit = moving(catalogue, &chosen.exit);
    if (enter.is_none() && exit.is_none()) || clip.duration <= 0.0 || stage.rate <= 0.0 {
        return Ok(Vec::new());
    }
    let (fit_in, fit_out) = concat_effects::animation::fitted(
        chosen.enter.as_ref().map(|a| a.duration),
        chosen.exit.as_ref().map(|a| a.duration),
        clip.duration,
    );
    let length = clip.duration;
    let din = enter.and(fit_in).unwrap_or(0.0).clamp(0.0, length);
    let dout = exit.and(fit_out).unwrap_or(0.0).clamp(0.0, length - din);
    let frame = 1.0 / stage.rate;
    let count = title.content.chars().count();
    let words = title.content.split_whitespace().count().max(1);
    let lines = title.content.lines().count().max(1);
    let mut out = Vec::new();
    let window = |out: &mut Vec<ExportClip>,
                  animation: &Animation,
                  from: f64,
                  span: f64,
                  which: &str|
     -> Result<(), String> {
        let frames = (span * stage.rate - 1e-6).ceil().max(0.0) as usize;
        for k in 0..frames {
            let a = from + k as f64 * frame;
            let b = (from + (k + 1) as f64 * frame).min(from + span);
            let t = ((a - from) / span).clamp(0.0, 1.0);
            let dance = Dance {
                animation,
                t,
                count,
                words,
                lines,
                duration: span,
                from,
                word_times,
            };
            let path = paint(stage, title, &dance, which, k)?;
            let mut piece = cut(still, a, b, length);
            piece.path = path.to_string_lossy().into_owned();
            piece.animations = None;
            piece.reveal_map = None;
            out.push(piece);
        }
        Ok(())
    };
    if let Some(animation) = enter {
        window(&mut out, animation, 0.0, din, "in")?;
    }
    if length - din - dout > 1e-6 {
        let mut rest = cut(still, din, length - dout, length);
        if let Some(kept) = &mut rest.animations {
            if enter.is_some() {
                kept.enter = None;
            }
            if exit.is_some() {
                kept.exit = None;
            }
        }
        out.push(rest);
    }
    if let Some(animation) = exit {
        window(&mut out, animation, length - dout, dout, "out")?;
    }
    Ok(out)
}

/// One frame of the title, painted to a PNG under the titles' folder unless
/// it is there already.
fn paint(
    stage: &Stage<'_>,
    title: &TitleStyle,
    dance: &Dance<'_>,
    which: &str,
    frame: usize,
) -> Result<PathBuf, String> {
    let mut bytes = stage.key.to_le_bytes().to_vec();
    bytes.extend_from_slice(which.as_bytes());
    bytes.extend_from_slice(&dance.t.to_bits().to_le_bytes());
    bytes.extend_from_slice(&(dance.animation as *const Animation as usize).to_le_bytes());
    let key = fnv(&bytes);
    let path = stage
        .dir
        .join(format!("{:016x}-{which}-{frame:03}.png", key));
    if path.is_file() {
        return Ok(path);
    }
    let rendered =
        concat_text::render_frame_posed(stage.fonts, title, stage.width, stage.height, dance)
            .map_err(|error| error.to_string())?;
    std::fs::create_dir_all(stage.dir).map_err(|error| error.to_string())?;
    let part = path.with_extension("png.part");
    let file = std::fs::File::create(&part).map_err(|error| error.to_string())?;
    let mut encoder = png::Encoder::new(
        std::io::BufWriter::new(file),
        rendered.width,
        rendered.height,
    );
    encoder.set_color(png::ColorType::Rgba);
    encoder.set_depth(png::BitDepth::Eight);
    let mut writer = encoder.write_header().map_err(|error| error.to_string())?;
    writer
        .write_image_data(&rendered.rgba)
        .map_err(|error| error.to_string())?;
    writer.finish().map_err(|error| error.to_string())?;
    std::fs::rename(&part, &path).map_err(|error| error.to_string())?;
    Ok(path)
}

/// FNV-1a, as the titles' other files are keyed.
fn fnv(bytes: &[u8]) -> u64 {
    let mut hash = 0xcbf2_9ce4_8422_2325_u64;
    for byte in bytes {
        hash ^= u64::from(*byte);
        hash = hash.wrapping_mul(0x0000_0100_0000_01b3);
    }
    hash
}

/// The still's clip over `a..b` seconds of its `length`: its timing moved
/// there and its keys cut to the span, each property's value at either end
/// held as a key so the piece moves as that stretch of the clip did.
fn cut(still: &ExportClip, a: f64, b: f64, length: f64) -> ExportClip {
    let mut piece = still.clone();
    piece.start = still.start + a;
    piece.duration = (b - a).max(1e-6);
    let (from, to) = (a / length, b / length);
    piece.animation = cut_keys(&still.animation, from, to);
    piece
}

fn cut_keys(keys: &[ExportKey], from: f64, to: f64) -> Vec<ExportKey> {
    let span = (to - from).max(1e-9);
    let mut properties: Vec<&str> = keys.iter().map(|key| key.property.as_str()).collect();
    properties.dedup();
    let mut out = Vec::new();
    for property in properties {
        let mut own: Vec<&ExportKey> = keys.iter().filter(|key| key.property == property).collect();
        own.sort_by(|x, y| x.at.total_cmp(&y.at));
        let value_at = |at: f64| -> f64 {
            match own.iter().position(|key| key.at >= at) {
                None => own.last().map_or(0.0, |key| key.value),
                Some(0) => own[0].value,
                Some(i) => {
                    let (l, r) = (own[i - 1], own[i]);
                    let gap = (r.at - l.at).max(1e-9);
                    l.value + (r.value - l.value) * ((at - l.at) / gap)
                }
            }
        };
        let template = own[0];
        out.push(ExportKey {
            at: 0.0,
            value: value_at(from),
            ..template.clone()
        });
        for key in &own {
            if key.at > from && key.at < to {
                out.push(ExportKey {
                    at: (key.at - from) / span,
                    ..(*key).clone()
                });
            }
        }
        out.push(ExportKey {
            at: 1.0,
            value: value_at(to),
            ..template.clone()
        });
    }
    out
}

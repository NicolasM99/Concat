// SPDX-License-Identifier: AGPL-3.0-or-later
// SPDX-FileCopyrightText: 2026 Jareer and Concat contributors

//! Opening a CapCut project.
//!
//! A CapCut project is a folder holding `draft_content.json` (CapCut for
//! desktop; `draft_info.json` in some builds and in JianYing): its canvas,
//! a list of materials - files, words, transitions, effects, animations,
//! speeds - and tracks of segments that place them, every time in
//! microseconds. The import reads it into a new Concat project beside it:
//!
//! - the files, as bin media, found where CapCut keeps them (the draft's own
//!   `materials` folder through its `##_draftpath_placeholder_…_##`, or a
//!   path on disk);
//! - every segment as a clip: its span, in-point, speed or speed curve,
//!   volume, fades, placement, flips, opacity, keys, mask and background;
//! - titles with their words, face, size, colour, stroke, shadow, box and
//!   alignment;
//! - transitions on the cut after the segment that carries them, as the
//!   incoming clip's;
//! - In, Out, Combo and Loop animations, effects and filters as the
//!   packages that stand in for them, and an effect or a filter track as a
//!   layer over what is beneath it; colour adjustments as Concat's Adjust.
//!
//! CapCut names an item in the language its interface was in, so an item is
//! found by its id first ([`ids`], generated from VectCutAPI's catalogue and
//! from real drafts), then by the words of its name ([`names`]), and last by
//! the plainest stand-in of its kind. Everything that is approximated or
//! left out is said in the import's notes.
//!
//! Recent CapCut releases can write the draft encrypted; such a draft is
//! refused with a word on what to do, rather than read as garbage.

mod ids;
mod names;

use std::collections::{BTreeMap, HashMap};
use std::path::{Path, PathBuf};
use std::sync::Arc;

use concat_project::commands::NewMedia;
use concat_project::model::Animations;
use concat_project::model::{
    AppliedFilter, Background, Clip, ClipAnimation, ClipKey, ClipKind, ClipMask, CustomFont,
    KeyEase, KeyProperty, MaskShape, MediaItem, MediaKind, Project, SpeedPoint, TextAlign,
    TextStyle, Timeline, Track, Transition, VideoSettings,
};
use serde_json::Value;

use names::{Slot, Want};

/// The file in an imported project that keeps the import's notes.
pub const REPORT: &str = "capcut-import.txt";

/// What an import made, and what it had to say about it.
#[derive(Debug)]
pub struct Imported {
    /// The new project.
    pub info: crate::projects::ProjectInfo,
    /// Lines for the person: what was approximated, missing or left out.
    pub notes: Vec<String>,
}

/// A converted draft, before it is written anywhere.
#[derive(Debug)]
pub struct Converted {
    /// The project's name, CapCut's own.
    pub name: String,
    /// The edit.
    pub project: Project,
    /// What was approximated, missing or left out.
    pub notes: Vec<String>,
}

/// Footage the import took from CapCut's cache - a flash transition's -
/// copied into the project's own folder and the bin pointed there: CapCut
/// clears its cache, and the project should not lose its flashes when it
/// does. A file that will not copy stays where it is.
fn keep_cached_footage(project: &mut Project, folder: &Path) {
    let into = folder.join("capcut");
    for media in &mut project.media {
        let path = Path::new(&media.path);
        let cached = media.path.replace('\\', "/").contains("/Cache/effect/");
        if !cached || !path.is_file() {
            continue;
        }
        let Some(name) = path.file_name() else {
            continue;
        };
        // The package's id names the folder, so two packages' frames of
        // the same name do not meet.
        let package = path
            .ancestors()
            .find(|dir| dir.parent().and_then(Path::file_name) == Some("effect".as_ref()))
            .and_then(Path::file_name)
            .map(|id| id.to_string_lossy().into_owned())
            .unwrap_or_default();
        let target = into.join(package).join(name);
        if std::fs::create_dir_all(target.parent().unwrap_or(&into)).is_ok()
            && (target.is_file() || std::fs::copy(path, &target).is_ok())
        {
            media.path = target.to_string_lossy().into_owned();
        }
    }
}

/// The draft file in `path`: the folder's `draft_content.json` or
/// `draft_info.json`, or `path` itself when it names one.
pub fn draft_file(path: &Path) -> Option<PathBuf> {
    if path.is_file() {
        let name = path.file_name()?.to_str()?;
        return matches!(name, "draft_content.json" | "draft_info.json").then(|| path.to_owned());
    }
    ["draft_content.json", "draft_info.json"]
        .iter()
        .map(|name| path.join(name))
        .find(|candidate| candidate.is_file())
}

/// Whether `path` is a CapCut project: a folder with a draft in it, or the
/// draft itself.
pub fn is_capcut(path: &Path) -> bool {
    draft_file(path).is_some()
}

/// Reads the CapCut project at `draft` into a new Concat project created
/// under `location`.
pub fn import(draft: &Path, location: &str) -> Result<Imported, String> {
    let file = draft_file(draft).ok_or_else(|| {
        format!(
            "{} is not a CapCut project: it holds no draft_content.json",
            draft.display()
        )
    })?;
    let folder = file.parent().unwrap_or(Path::new(".")).to_owned();
    let bytes = std::fs::read(&file)
        .map_err(|error| format!("could not read {}: {error}", file.display()))?;
    let document = parse(&bytes, &file)?;
    let probe = |path: &str| {
        crate::media::probe(path)
            .ok()
            .map(|summary| summary.to_new_media())
    };
    let mut converted = convert_with(&document, &folder, &probe, true);
    let video = converted.project.timelines[0].video;
    // A second import of the same draft is a project of its own beside the
    // first: the first free name of "Name", "Name 2", "Name 3"...
    let name = (1..)
        .map(|n| {
            if n == 1 {
                converted.name.clone()
            } else {
                format!("{} {n}", converted.name)
            }
        })
        .find(|name| {
            !Path::new(location)
                .join(crate::projects::folder_name(name))
                .exists()
        })
        .unwrap_or_else(|| converted.name.clone());
    converted.name = name;
    let info = crate::projects::create(
        location,
        &converted.name,
        video.width,
        video.height,
        video.rate_num,
        video.rate_den,
    )?;
    keep_cached_footage(&mut converted.project, Path::new(&info.path));
    let settings = concat_project::doc::DocumentSettings {
        name: converted.name.clone(),
        width: video.width,
        height: video.height,
        rate_num: video.rate_num,
        rate_den: video.rate_den,
    };
    let document = concat_project::doc::to_document(&settings, &converted.project);
    crate::projects::save(&info.path, &document)?;
    converted.notes.sort();
    converted.notes.dedup();
    // What the import had to say, kept beside the project for a look later.
    if !converted.notes.is_empty() {
        let report = format!(
            "Imported from the CapCut project {}

{}
",
            folder.display(),
            converted.notes.join(
                "
"
            )
        );
        let _ = std::fs::write(Path::new(&info.path).join(REPORT), report);
    }
    Ok(Imported {
        info,
        notes: converted.notes,
    })
}

/// The draft's JSON, or why it is not readable.
fn parse(bytes: &[u8], file: &Path) -> Result<Value, String> {
    let text = String::from_utf8_lossy(bytes);
    if !text.trim_start().starts_with('{') {
        return Err(format!(
            "{} is encrypted, as recent CapCut releases write it, and cannot be read. \
             In CapCut, export the project as a template or duplicate it with an earlier \
             CapCut release to get a readable draft.",
            file.display()
        ));
    }
    serde_json::from_str(&text)
        .map_err(|error| format!("{} is not a CapCut draft: {error}", file.display()))
}

/// Microseconds as seconds.
fn seconds(value: &Value) -> f64 {
    value.as_f64().unwrap_or(0.0) / 1_000_000.0
}

fn number(value: &Value, or: f64) -> f64 {
    value.as_f64().filter(|v| v.is_finite()).unwrap_or(or)
}

fn text<'a>(value: &'a Value, key: &str) -> &'a str {
    value.get(key).and_then(Value::as_str).unwrap_or("")
}

/// The frame rate CapCut's `fps` means, as an exact fraction.
fn rate(fps: f64) -> (i64, i64) {
    for (nominal, num, den) in [
        (23.976, 24000, 1001),
        (29.97, 30000, 1001),
        (59.94, 60000, 1001),
    ] {
        if (fps - nominal).abs() < 0.01 {
            return (num, den);
        }
    }
    let whole = fps.round().clamp(1.0, 240.0) as i64;
    (whole, 1)
}

/// The file a CapCut material path names: the draft's own folder for its
/// placeholder, a path as it is otherwise.
fn resolve(path: &str, folder: &Path) -> Option<PathBuf> {
    if path.is_empty() {
        return None;
    }
    if let Some(rest) = path.strip_prefix("##_draftpath_placeholder_") {
        let tail = rest.split_once("_##").map(|(_, tail)| tail)?;
        let tail = tail.trim_start_matches(['/', '\\']);
        return Some(folder.join(tail));
    }
    Some(PathBuf::from(path))
}

/// `#rrggbb` from CapCut's `[r, g, b]` in `0..1`.
fn hex_of(rgb: &[Value]) -> Option<String> {
    let channel = |index: usize| {
        let value = rgb.get(index)?.as_f64()?;
        Some((value.clamp(0.0, 1.0) * 255.0).round() as u8)
    };
    Some(format!(
        "#{:02x}{:02x}{:02x}",
        channel(0)?,
        channel(1)?,
        channel(2)?
    ))
}

/// A CapCut `#rrggbb` (or `#aarrggbb`), lower-cased, or None.
fn hex(colour: &str) -> Option<String> {
    let digits = colour.strip_prefix('#')?;
    match digits.len() {
        6 if digits.chars().all(|c| c.is_ascii_hexdigit()) => {
            Some(format!("#{}", digits.to_lowercase()))
        }
        8 if digits.chars().all(|c| c.is_ascii_hexdigit()) => {
            Some(format!("#{}", digits[2..].to_lowercase()))
        }
        _ => None,
    }
}

/// What an item of the draft stands for in Concat: a package id and the
/// knobs it is set to, from the id table, the item's name, or the plainest
/// stand-in, saying which in `notes`.
fn stand_in(
    want: Want,
    item: &Value,
    notes: &mut Vec<String>,
) -> Option<(String, BTreeMap<String, f64>)> {
    let name = text(item, "name");
    let known = ["resource_id", "effect_id", "id", "third_resource_id"]
        .iter()
        .filter_map(|key| item.get(*key))
        .filter_map(|value| match value {
            Value::String(s) => Some(s.clone()),
            Value::Number(n) => Some(n.to_string()),
            _ => None,
        })
        .find_map(|id| {
            ids::IDS
                .binary_search_by(|(key, _, _)| key.cmp(&id.as_str()))
                .ok()
                .map(|index| ids::IDS[index])
        });
    let (id, knobs) = match known {
        Some((_, id, knobs)) => (id, knobs),
        None => match names::guess(want, name) {
            Some(found) => {
                notes.push(format!(
                    "\u{201c}{name}\u{201d} is approximated as {}",
                    label(found.0)
                ));
                found
            }
            None => match names::fallback(want) {
                Some(id) => {
                    notes.push(format!(
                        "\u{201c}{name}\u{201d} has no counterpart; it plays as {}",
                        label(id)
                    ));
                    (id, "")
                }
                None => {
                    notes.push(format!(
                        "\u{201c}{name}\u{201d} has no counterpart and is left out"
                    ));
                    return None;
                }
            },
        },
    };
    let mut params = BTreeMap::new();
    for pair in knobs.split(',').filter(|pair| !pair.is_empty()) {
        if let Some((key, value)) = pair.split_once('=')
            && let Ok(value) = value.parse::<f64>()
        {
            params.insert(key.to_owned(), value);
        }
    }
    Some((id.to_owned(), params))
}

/// A package's name, for a note.
fn label(id: &str) -> String {
    concat_effects::Catalogue::builtin()
        .get(id)
        .map(|package| package.manifest.effect.name.clone())
        .unwrap_or_else(|| id.to_owned())
}

/// Ids, minted the way the editor mints them.
struct Mint {
    counts: HashMap<&'static str, u32>,
}

impl Mint {
    fn next(&mut self, prefix: &'static str) -> String {
        let n = self.counts.entry(prefix).or_insert(0);
        *n += 1;
        format!("{prefix}{n}")
    }
}

/// A CapCut track's kind, as the import treats it.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
enum Lane {
    Picture,
    Audio,
    Text,
    Sticker,
    Effect,
    Filter,
    /// Something this import does not read.
    Other,
}

fn lane_of(kind: &str) -> Lane {
    match kind {
        "video" => Lane::Picture,
        "audio" => Lane::Audio,
        "text" => Lane::Text,
        "sticker" => Lane::Sticker,
        "effect" => Lane::Effect,
        "filter" | "adjust" => Lane::Filter,
        _ => Lane::Other,
    }
}

/// Every material of the draft by its id, with the list it came from.
fn materials(document: &Value) -> HashMap<String, (String, Value)> {
    let mut by_id = HashMap::new();
    if let Some(lists) = document.get("materials").and_then(Value::as_object) {
        for (list, items) in lists {
            for item in items.as_array().into_iter().flatten() {
                if let Some(id) = item.get("id").and_then(Value::as_str) {
                    by_id.insert(id.to_owned(), (list.clone(), item.clone()));
                }
            }
        }
    }
    by_id
}

/// Where a draft's segments land: the outermost draft as it is, a compound
/// clip's own draft shifted to where the compound sits, cut to its span and
/// moved as it is moved.
#[derive(Clone, Copy, Debug)]
struct Place {
    /// Seconds added to a segment's time.
    shift: f64,
    /// The span of the outer timeline the segments may show in.
    window: (f64, f64),
    /// The compound's placement, composed onto each clip.
    scale: f64,
    offset: (f64, f64),
    rotation: f64,
    opacity: f64,
    /// How many compounds deep.
    depth: u32,
}

impl Place {
    const ROOT: Place = Place {
        shift: 0.0,
        window: (f64::NEG_INFINITY, f64::INFINITY),
        scale: 1.0,
        offset: (0.0, 0.0),
        rotation: 0.0,
        opacity: 1.0,
        depth: 0,
    };
}

/// The deepest compound clips are opened: past it a draft is taken to loop.
const MAX_DEPTH: u32 = 8;

/// What a conversion builds as it goes.
struct Builder<'a> {
    folder: &'a Path,
    probe: &'a dyn Fn(&str) -> Option<NewMedia>,
    project: Project,
    mint: Mint,
    media_of: HashMap<String, String>,
    by_path: HashMap<String, String>,
    lanes: Vec<Track>,
    /// The lanes made for compound clips' contents, by the lane they sit
    /// over, so one compound's tracks reuse those a neighbour's left free.
    nested: HashMap<String, Vec<String>>,
    clips: Vec<Clip>,
    fonts: Vec<CustomFont>,
    notes: Vec<String>,
    pending: Vec<(String, f64, Transition)>,
    skipped: BTreeMap<String, usize>,
    /// Whether a clip of a file that is not on disk is left out, as an
    /// import leaves it so the project exports; the file's name by its
    /// material, for the note that says where its clips were.
    drop_missing: bool,
    gone: HashMap<String, String>,
    /// CapCut's flash transitions' footage, to lay over their cuts: where
    /// the cut is, how long the transition, which flash, and its package.
    flashes: Vec<(f64, f64, Flash, PathBuf)>,
}

/// The two CapCut transitions whose flash is footage in their package.
#[derive(Clone, Copy, PartialEq, Debug)]
enum Flash {
    /// Destello II: 70 frames, `clipname_000.png` on.
    Frames,
    /// Flash de ola de calor: `light3.mp4`, 45 frames at 30.
    Video,
}

impl Flash {
    fn of(resource_id: &str) -> Option<Flash> {
        match resource_id {
            "6952697917563998722" => Some(Flash::Frames),
            "7564617241841437953" => Some(Flash::Video),
            _ => None,
        }
    }
}

/// Every file under `dir` whose name `wanted` takes, sorted by name.
fn files_under(dir: &Path, wanted: &dyn Fn(&str) -> bool) -> Vec<PathBuf> {
    let mut found = Vec::new();
    let mut stack = vec![dir.to_owned()];
    while let Some(at) = stack.pop() {
        let Ok(entries) = std::fs::read_dir(&at) else {
            continue;
        };
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_dir() {
                stack.push(path);
            } else if path
                .file_name()
                .and_then(|n| n.to_str())
                .is_some_and(wanted)
            {
                found.push(path);
            }
        }
    }
    found.sort();
    found
}

/// The draft as a Concat project. `probe` describes a file on disk, or
/// gives None for one it cannot read; a missing file still comes in, so the
/// project can be relinked.
pub fn convert(
    document: &Value,
    folder: &Path,
    probe: &dyn Fn(&str) -> Option<NewMedia>,
) -> Converted {
    convert_with(document, folder, probe, false)
}

/// [`convert`], leaving out the clips of files that are not on disk when
/// `drop_missing` says to: a project with a clip of a file that is gone does
/// not export, and the most common such file is a sound CapCut kept in its
/// cache and has since cleared.
fn convert_with(
    document: &Value,
    folder: &Path,
    probe: &dyn Fn(&str) -> Option<NewMedia>,
    drop_missing: bool,
) -> Converted {
    let canvas = &document["canvas_config"];
    let width = number(&canvas["width"], 1920.0).max(2.0) as u32;
    let height = number(&canvas["height"], 1080.0).max(2.0) as u32;
    let (rate_num, rate_den) = rate(number(&document["fps"], 30.0));
    let video = VideoSettings {
        width: width & !1,
        height: height & !1,
        rate_num,
        rate_den,
        ..VideoSettings::default()
    };
    let name = {
        let own = text(document, "name");
        if own.is_empty() {
            folder
                .file_name()
                .and_then(|name| name.to_str())
                .unwrap_or("CapCut project")
                .to_owned()
        } else {
            own.to_owned()
        }
    };
    let mut builder = Builder {
        folder,
        probe,
        project: Project::with_video(video),
        mint: Mint {
            counts: HashMap::new(),
        },
        media_of: HashMap::new(),
        by_path: HashMap::new(),
        lanes: Vec::new(),
        nested: HashMap::new(),
        clips: Vec::new(),
        fonts: Vec::new(),
        notes: Vec::new(),
        pending: Vec::new(),
        skipped: BTreeMap::new(),
        drop_missing,
        gone: HashMap::new(),
        flashes: Vec::new(),
    };
    builder.draft(document, Place::ROOT, None);
    builder.finish(name, video)
}

impl Builder<'_> {
    /// The project, once every draft is read.
    fn finish(mut self, name: String, video: VideoSettings) -> Converted {
        // Each transition onto the clip that starts where its carrier ends.
        for (track_id, at, transition) in std::mem::take(&mut self.pending) {
            if let Some(clip) = self
                .clips
                .iter_mut()
                .find(|clip| clip.track_id == track_id && (clip.start - at).abs() < 0.02)
            {
                clip.transition_in = Some(transition);
            }
        }
        self.lay_flashes(video);
        for (what, count) in std::mem::take(&mut self.skipped) {
            self.notes.push(format!(
                "{count} {what} item(s) left out: Concat has no counterpart yet"
            ));
        }
        let tracks = if self.lanes.is_empty() {
            self.project.timelines[0].tracks.clone()
        } else {
            self.lanes
        };
        // The lanes stay in CapCut's order: the first is the bottom of the
        // stack, in Concat as in CapCut.
        let timeline = Timeline {
            id: "TL1".to_owned(),
            name: name.clone(),
            video,
            background: Background::None,
            tracks,
            clips: self.clips.into_iter().map(Arc::new).collect(),
            extra: Default::default(),
        };
        self.project.timelines = vec![Arc::new(timeline)];
        self.project.active_timeline_id = "TL1".to_owned();
        self.project.fonts = self.fonts;
        Converted {
            name,
            project: self.project,
            notes: self.notes,
        }
    }

    /// Each flash transition's footage over its cut, on a lane of its own
    /// at the top, in Screen - as CapCut draws it over the picture - and
    /// filling the frame.
    fn lay_flashes(&mut self, video: VideoSettings) {
        let flashes = std::mem::take(&mut self.flashes);
        if flashes.is_empty() {
            return;
        }
        let lane = format!("T{}", self.lanes.len() + 1);
        self.lanes.push(Track {
            id: lane.clone(),
            ..Track::default()
        });
        let rate = video.rate().max(1.0);
        let (canvas_w, canvas_h) = (f64::from(video.width), f64::from(video.height));
        // Concat fits a picture inside the frame; CapCut's flash covers it.
        let cover = |w: f64, h: f64| {
            let (fit, fill) = (
                (canvas_w / w).min(canvas_h / h),
                (canvas_w / w).max(canvas_h / h),
            );
            fill / fit
        };
        for (cut, length, flash, dir) in flashes {
            let from = (cut - length / 2.0).max(0.0);
            match flash {
                Flash::Frames => {
                    let frames = files_under(&dir, &|name| {
                        name.starts_with("clipname_") && name.ends_with(".png")
                    });
                    if frames.len() < 70 {
                        self.notes.push(format!(
                            "the Flash II frames in {} are incomplete",
                            dir.display()
                        ));
                        continue;
                    }
                    let shown = (length * rate).ceil() as usize;
                    for k in 0..shown {
                        let p = k as f64 / (length * rate);
                        let index = ((p * 70.0).floor() as usize + 1).min(69);
                        let start = from + k as f64 / rate;
                        let span = (from + length - start).min(1.0 / rate);
                        let media_id = self.still(&frames[index], "Flash II");
                        let id = self.mint.next("c");
                        let mut clip = Clip::blank(
                            &id,
                            &lane,
                            ClipKind::Image,
                            "Flash II".to_owned(),
                            start,
                            span,
                        );
                        clip.media_id = media_id;
                        clip.blend = "screen".to_owned();
                        clip.scale = cover(720.0, 405.0);
                        self.clips.push(clip);
                    }
                }
                Flash::Video => {
                    let Some(file) = files_under(&dir, &|name| name == "light3.mp4")
                        .into_iter()
                        .next()
                    else {
                        self.notes.push(format!(
                            "the Heat Wave Flash video is not in {}",
                            dir.display()
                        ));
                        continue;
                    };
                    let media_id = self.footage(&file, "Heat Wave Flash");
                    let id = self.mint.next("c");
                    let mut clip = Clip::blank(
                        &id,
                        &lane,
                        ClipKind::Video,
                        "Heat Wave Flash".to_owned(),
                        from,
                        length,
                    );
                    clip.media_id = media_id;
                    clip.blend = "screen".to_owned();
                    clip.scale = cover(2160.0, 2160.0);
                    // Its 44 frames span the transition, each held from
                    // half a frame early, as CapCut rounds to them.
                    clip.speed = ((44.0 / 30.0) / length).clamp(0.0625, 16.0);
                    clip.source_start = 0.5 / 30.0;
                    clip.volume = 0.0;
                    self.clips.push(clip);
                }
            }
        }
    }

    /// A video file in the bin, once, as probed.
    fn footage(&mut self, path: &Path, name: &str) -> String {
        let path_text = path.to_string_lossy().into_owned();
        if let Some(id) = self.by_path.get(&path_text) {
            return id.clone();
        }
        let media_id = self.mint.next("m");
        let found = (self.probe)(&path_text);
        self.project.media.push(MediaItem {
            id: media_id.clone(),
            path: path_text.clone(),
            name: name.to_owned(),
            duration: found.as_ref().and_then(|f| f.duration),
            kind: MediaKind::Video,
            width: found.as_ref().and_then(|f| f.width),
            height: found.as_ref().and_then(|f| f.height),
            frame_rate: found.as_ref().and_then(|f| f.frame_rate),
            frame_rate_fraction: found.as_ref().and_then(|f| f.frame_rate_fraction.clone()),
            video_codec: found.as_ref().and_then(|f| f.video_codec.clone()),
            audio_codec: None,
            has_audio: false,
            audio_tracks: Vec::new(),
            placeholder: false,
            color_range: None,
            color_space: found.as_ref().map(|f| f.color_space).unwrap_or_default(),
            origin: None,
            extra: Default::default(),
        });
        self.by_path.insert(path_text, media_id.clone());
        media_id
    }

    /// The bin entries for a draft's files, once each.
    fn bin(&mut self, by_id: &HashMap<String, (String, Value)>) {
        for (material_id, (list, item)) in by_id {
            if list != "videos" && list != "audios" {
                continue;
            }
            let Some(path) = resolve(text(item, "path"), self.folder) else {
                continue;
            };
            let path_text = path.to_string_lossy().into_owned();
            if let Some(existing) = self.by_path.get(&path_text) {
                self.media_of.insert(material_id.clone(), existing.clone());
                continue;
            }
            let kind = match (list.as_str(), text(item, "type")) {
                ("videos", "photo") => MediaKind::Image,
                ("videos", _) => MediaKind::Video,
                _ => MediaKind::Audio,
            };
            let probed = path.is_file().then(|| (self.probe)(&path_text)).flatten();
            if !path.is_file() {
                if self.drop_missing {
                    let name = path
                        .file_name()
                        .map(|n| n.to_string_lossy().into_owned())
                        .unwrap_or_else(|| path_text.clone());
                    self.notes.push(format!(
                        "{} is not on this machine; its clips are left out",
                        path.display()
                    ));
                    self.gone.insert(material_id.clone(), name);
                    continue;
                }
                self.notes.push(format!(
                    "{} is missing; relink it in the bin",
                    path.display()
                ));
            }
            let id = self.mint.next("m");
            let display = {
                let own = text(item, "material_name");
                let own = if own.is_empty() {
                    text(item, "name")
                } else {
                    own
                };
                if own.is_empty() {
                    path.file_name()
                        .map(|n| n.to_string_lossy().into_owned())
                        .unwrap_or_default()
                } else {
                    own.to_owned()
                }
            };
            let media = match probed {
                Some(found) => MediaItem {
                    id: id.clone(),
                    path: found.path,
                    name: display,
                    duration: found.duration,
                    kind: found.kind,
                    width: found.width,
                    height: found.height,
                    frame_rate: found.frame_rate,
                    frame_rate_fraction: found.frame_rate_fraction,
                    video_codec: found.video_codec,
                    audio_codec: found.audio_codec,
                    has_audio: found.has_audio,
                    audio_tracks: found.audio_tracks,
                    placeholder: false,
                    color_range: None,
                    color_space: found.color_space,
                    origin: found.origin,
                    extra: Default::default(),
                },
                None => MediaItem {
                    id: id.clone(),
                    path: path_text.clone(),
                    name: display,
                    duration: Some(seconds(&item["duration"])).filter(|d| *d > 0.0),
                    kind,
                    width: item["width"].as_u64().map(|w| w as u32),
                    height: item["height"].as_u64().map(|h| h as u32),
                    frame_rate: None,
                    frame_rate_fraction: None,
                    video_codec: None,
                    audio_codec: None,
                    has_audio: item["has_audio"]
                        .as_bool()
                        .unwrap_or(kind == MediaKind::Audio),
                    audio_tracks: Vec::new(),
                    placeholder: false,
                    color_range: None,
                    color_space: Default::default(),
                    origin: None,
                    extra: Default::default(),
                },
            };
            self.by_path.insert(path_text, id.clone());
            self.media_of.insert(material_id.clone(), id);
            self.project.media.push(media);
        }
    }

    /// A lane for a draft's track: a new one for the outermost draft's,
    /// and for a compound's the lowest of those over `over` that is free
    /// for the compound's span, a new one above them when none is.
    fn lane_for(&mut self, track: &Value, place: Place, over: Option<&str>) -> String {
        let flag = track["attribute"].as_i64().unwrap_or(0);
        let fresh = |id: String| Track {
            id,
            // CapCut's attribute: 1 is a muted lane. A hidden clip says so
            // on itself (`visible`), not on its lane.
            muted: flag & 1 != 0,
            ..Track::default()
        };
        let Some(over) = over else {
            let id = format!("T{}", self.lanes.len() + 1);
            self.lanes.push(fresh(id.clone()));
            return id;
        };
        let (from, to) = place.window;
        let taken = |lane: &str, clips: &[Clip]| {
            clips.iter().any(|clip| {
                clip.track_id == lane
                    && clip.start < to - 1e-6
                    && clip.start + clip.duration > from + 1e-6
            })
        };
        let pool = self.nested.get(over).cloned().unwrap_or_default();
        if let Some(free) = pool.iter().find(|lane| !taken(lane, &self.clips)) {
            return free.clone();
        }
        let id = format!("T{}", self.lanes.len() + 1);
        // Above the lane it sits over and the ones already made for it.
        let anchor = pool.last().map(String::as_str).unwrap_or(over);
        let at = self
            .lanes
            .iter()
            .position(|lane| lane.id == anchor)
            .map_or(self.lanes.len(), |index| index + 1);
        self.lanes.insert(at, fresh(id.clone()));
        self.nested
            .entry(over.to_owned())
            .or_default()
            .push(id.clone());
        id
    }

    /// One draft's tracks, placed as `place` says. `over` is the lane a
    /// compound clip sits on, for its contents to be stacked over.
    fn draft(&mut self, document: &Value, place: Place, over: Option<&str>) {
        let by_id = materials(document);
        self.bin(&by_id);
        let tracks: Vec<&Value> = document["tracks"]
            .as_array()
            .map(|t| t.iter().collect())
            .unwrap_or_default();
        // Sound on lanes above the pictures, which keeps CapCut's stack of
        // pictures as it was.
        let mut ordered: Vec<&Value> = tracks
            .iter()
            .copied()
            .filter(|t| lane_of(text(t, "type")) != Lane::Audio)
            .collect();
        ordered.extend(
            tracks
                .iter()
                .copied()
                .filter(|t| lane_of(text(t, "type")) == Lane::Audio),
        );
        for track in ordered {
            let lane = lane_of(text(track, "type"));
            if lane == Lane::Other {
                *self
                    .skipped
                    .entry(format!("{} track", text(track, "type")))
                    .or_default() += 1;
                continue;
            }
            let track_id = self.lane_for(track, place, over);
            for segment in track["segments"].as_array().into_iter().flatten() {
                self.segment(segment, lane, &track_id, &by_id, place);
            }
        }
    }

    /// One segment as a clip on `track_id`, or a compound's contents over it.
    fn segment(
        &mut self,
        segment: &Value,
        lane: Lane,
        track_id: &str,
        by_id: &HashMap<String, (String, Value)>,
        place: Place,
    ) {
        let own_start = seconds(&segment["target_timerange"]["start"]);
        let own_duration = seconds(&segment["target_timerange"]["duration"]);
        if own_duration <= 0.0 {
            return;
        }
        // Within a compound: shifted to where it sits, and cut to its span.
        let shifted = own_start + place.shift;
        let start = shifted.max(place.window.0);
        let end = (shifted + own_duration).min(place.window.1);
        if end - start <= 1e-6 {
            return;
        }
        let head = start - shifted;
        let duration = end - start;
        let material_id = text(segment, "material_id");
        if let Some(name) = self.gone.get(material_id) {
            self.notes.push(format!(
                "the clip of {name} at {start:.2}s is left out: its file is gone"
            ));
            return;
        }
        let Some((list, material)) = by_id.get(material_id) else {
            return;
        };
        let extras: Vec<(&String, &Value)> = segment["extra_material_refs"]
            .as_array()
            .into_iter()
            .flatten()
            .filter_map(Value::as_str)
            .filter_map(|id| by_id.get(id))
            .map(|(list, item)| (list, item))
            .collect();

        // A compound clip: its own draft, opened in its place.
        if list == "videos"
            && text(material, "path").is_empty()
            && let Some((_, combination)) =
                extras.iter().find(|(list, _)| list.as_str() == "drafts")
        {
            self.compound(
                segment,
                combination,
                track_id,
                place,
                (start, end),
                own_start,
            );
            return;
        }

        let id = self.mint.next("c");
        let mut clip = match (lane, list.as_str()) {
            (Lane::Picture | Lane::Audio, "videos" | "audios") => {
                let Some(media_id) = self.media_of.get(material_id).cloned() else {
                    return;
                };
                let media = self.project.media_by_id(&media_id);

                let kind = match media.map(|m| m.kind) {
                    Some(MediaKind::Image) => ClipKind::Image,
                    Some(MediaKind::Audio) => ClipKind::Audio,
                    _ => ClipKind::Video,
                };
                let name = media.map(|m| m.name.clone()).unwrap_or_default();
                let mut clip = Clip::blank(&id, track_id, kind, name, start, duration);
                clip.media_id = media_id;
                clip.source_start = seconds(&segment["source_timerange"]["start"]);
                clip
            }
            (Lane::Text, "texts") => {
                let video = self.project.active().video;
                let canvas = (f64::from(video.width), f64::from(video.height));
                let style = text_style(material, canvas, &mut self.fonts, &mut self.notes);
                let name = style.content.lines().next().unwrap_or("").to_owned();
                let mut clip = Clip::blank(&id, track_id, ClipKind::Text, name, start, duration);
                clip.text = Some(style);
                clip
            }
            (Lane::Effect, "video_effects" | "effects") => {
                let Some((package, params)) = stand_in(Want::Effect, material, &mut self.notes)
                else {
                    return;
                };
                let mut clip = Clip::blank(
                    &id,
                    track_id,
                    ClipKind::Layer,
                    label(&package),
                    start,
                    duration,
                );
                clip.video_effects = vec![applied(package, params, material)];
                clip
            }
            (Lane::Filter, _) => {
                let Some(entry) = look_of(material, &mut self.notes) else {
                    return;
                };
                let mut clip = Clip::blank(
                    &id,
                    track_id,
                    ClipKind::Layer,
                    label(&entry.id),
                    start,
                    duration,
                );
                clip.video_effects = vec![entry];
                clip
            }
            (Lane::Sticker, _) => {
                let Some(path) =
                    resolve(text(material, "path"), self.folder).filter(|p| p.is_file())
                else {
                    *self.skipped.entry("sticker".to_owned()).or_default() += 1;
                    return;
                };
                let media_id = self.still(&path, text(material, "name"));
                let mut clip =
                    Clip::blank(&id, track_id, ClipKind::Image, "Sticker", start, duration);
                clip.media_id = media_id;
                clip
            }
            _ => return,
        };

        // The segment's own settings.
        clip.volume = number(&segment["volume"], 1.0).max(0.0);
        if segment["visible"].as_bool() == Some(false) {
            clip.opacity = 0.0;
        }
        placement(&mut clip, segment);
        // A caption's size is its style's alone: CapCut sets a subtitle at
        // its font size whatever scale the segment carries (measured
        // against CapCut's own export, a 0.97 scale draws the words and
        // their plate at full size).
        if list == "texts" && text(material, "type") == "subtitle" {
            clip.scale = 1.0;
            clip.stretch_y = 1.0;
        }
        // A compound's placement rides over its contents'.
        if place.depth > 0 {
            clip.offset_x = place.offset.0 + clip.offset_x * place.scale;
            clip.offset_y = place.offset.1 + clip.offset_y * place.scale;
            clip.scale *= place.scale;
            clip.rotation += place.rotation;
            clip.opacity *= place.opacity;
        }
        clip.keys = keys(segment, own_duration);
        for (list, item) in &extras {
            self.extra(&mut clip, list, item, track_id, start + duration);
        }
        // Cut short at its head by a compound's span: the in-point moves on
        // by as much of the source as the cut covers.
        if head > 0.0 {
            clip.source_start += head * clip.speed;
        }
        if segment["reverse"].as_bool() == Some(true) {
            self.notes.push(format!(
                "\u{201c}{}\u{201d} plays reversed in CapCut; reverse it again in Concat",
                clip.name
            ));
        }
        self.clips.push(clip);
    }

    /// A still for a sticker, in the bin once.
    fn still(&mut self, path: &Path, name: &str) -> String {
        let path_text = path.to_string_lossy().into_owned();
        if let Some(id) = self.by_path.get(&path_text) {
            return id.clone();
        }
        let media_id = self.mint.next("m");
        let found = (self.probe)(&path_text);
        self.project.media.push(MediaItem {
            id: media_id.clone(),
            path: path_text.clone(),
            name: name.to_owned(),
            duration: None,
            kind: MediaKind::Image,
            width: found.as_ref().and_then(|f| f.width),
            height: found.as_ref().and_then(|f| f.height),
            frame_rate: None,
            frame_rate_fraction: None,
            video_codec: None,
            audio_codec: None,
            has_audio: false,
            audio_tracks: Vec::new(),
            placeholder: false,
            color_range: None,
            color_space: Default::default(),
            origin: None,
            extra: Default::default(),
        });
        self.by_path.insert(path_text, media_id.clone());
        media_id
    }

    /// What one of a segment's extra materials does to its clip.
    fn extra(&mut self, clip: &mut Clip, list: &str, item: &Value, track_id: &str, end: f64) {
        match list {
            "speeds" => speed(clip, item, &mut self.notes),
            "canvases" => {
                if let Some(background) = background(item, self.folder) {
                    clip.background = Some(background);
                }
            }
            "audio_fades" => {
                clip.fade_in = seconds(&item["fade_in_duration"]);
                clip.fade_out = seconds(&item["fade_out_duration"]);
            }
            "transitions" => {
                if let Some((package, _)) = stand_in(Want::Transition, item, &mut self.notes) {
                    let length = seconds(&item["duration"]).max(0.1);
                    if let Some(flash) = Flash::of(text(item, "resource_id")) {
                        match resolve(text(item, "path"), self.folder).filter(|dir| dir.is_dir()) {
                            Some(dir) => self.flashes.push((end, length, flash, dir)),
                            None => self.notes.push(format!(
                                "the flash of the {} transition at {end:.2}s is not on this \
                                 machine; open the project in CapCut once to fetch it",
                                text(item, "name")
                            )),
                        }
                    }
                    self.pending.push((
                        track_id.to_owned(),
                        end,
                        Transition {
                            id: package,
                            duration: length,
                        },
                    ));
                }
            }
            "material_animations" => animations(clip, item, &mut self.notes),
            "video_effects" => {
                if let Some((package, params)) = stand_in(Want::Effect, item, &mut self.notes) {
                    clip.video_effects.push(applied(package, params, item));
                }
            }
            "effects" => {
                if let Some(entry) = look_of(item, &mut self.notes) {
                    merge_adjust(&mut clip.video_effects, entry);
                }
            }
            "masks" | "common_mask" => {
                if let Some(mask) = mask(item) {
                    clip.mask = Some(mask);
                }
            }
            "realtime_denoises" => {
                if item["is_denoise"].as_bool().unwrap_or(false) {
                    clip.filters.push(AppliedFilter::new("concat.denoise"));
                }
            }
            "vocal_beautifys" => {
                if item["enable"].as_bool().unwrap_or(false)
                    || item["is_enable"].as_bool().unwrap_or(false)
                {
                    clip.filters
                        .push(AppliedFilter::new("concat.enhance-voice"));
                }
            }
            "audio_effects" => match audio_stand_in(item) {
                Some((package, _)) => clip.filters.push(AppliedFilter::new(package)),
                None => self.notes.push(format!(
                    "the voice effect \u{201c}{}\u{201d} has no counterpart and is left out",
                    text(item, "name")
                )),
            },
            _ => {}
        }
    }

    /// A compound clip's own draft, laid over the lane it sits on: its
    /// segments shifted to where the compound starts, cut to its span, and
    /// placed as it is placed.
    fn compound(
        &mut self,
        segment: &Value,
        combination: &Value,
        track_id: &str,
        place: Place,
        (start, end): (f64, f64),
        own_start: f64,
    ) {
        if place.depth >= MAX_DEPTH {
            self.notes
                .push("a compound clip nested past eight deep is left out".to_owned());
            return;
        }
        let inner = match &combination["draft"] {
            Value::Object(_) => combination["draft"].clone(),
            _ => {
                let file = resolve(text(combination, "draft_file_path"), self.folder);
                match file
                    .and_then(|file| std::fs::read(file).ok())
                    .and_then(|bytes| serde_json::from_slice::<Value>(&bytes).ok())
                {
                    Some(inner) => inner,
                    None => {
                        self.notes.push(
                            "a compound clip's own draft could not be read and is left out"
                                .to_owned(),
                        );
                        return;
                    }
                }
            }
        };
        let mut moved = Clip::blank("", track_id, ClipKind::Video, "", 0.0, 1.0);
        placement(&mut moved, segment);
        let hidden = segment["visible"].as_bool() == Some(false);
        let inner_place = Place {
            // The compound's in-point is where its own draft is read from.
            shift: place.shift + own_start - seconds(&segment["source_timerange"]["start"]),
            window: (start, end),
            scale: place.scale * moved.scale,
            offset: (
                place.offset.0 + moved.offset_x * place.scale,
                place.offset.1 + moved.offset_y * place.scale,
            ),
            rotation: place.rotation + moved.rotation,
            opacity: place.opacity * moved.opacity * if hidden { 0.0 } else { 1.0 },
            depth: place.depth + 1,
        };
        self.draft(&inner, inner_place, Some(track_id));
    }
}

/// A package link as a clip stores it, its knobs from the id table and,
/// where CapCut's adjust parameters name a knob the package has, from
/// those.
fn applied(package: String, mut params: BTreeMap<String, f64>, item: &Value) -> AppliedFilter {
    let catalogue = concat_effects::Catalogue::builtin();
    if let Some(found) = catalogue.get(&package) {
        for adjust in item["adjust_params"].as_array().into_iter().flatten() {
            let key = text(adjust, "name").trim_start_matches("effects_adjust_");
            let key = match key {
                "range" => "range",
                "intensity" => "strength",
                "luminance" => "luminance",
                other => other,
            };
            if let Some(param) = found.manifest.params.iter().find(|param| param.key == key) {
                let value = number(&adjust["value"], 0.5);
                // CapCut's knobs run 0..1 across what the package spans.
                params
                    .entry(param.key.clone())
                    .or_insert(param.min + (param.max - param.min) * value);
            }
        }
    }
    let mut entry = AppliedFilter::new(package);
    entry.params = params;
    entry
}

/// A CapCut colour material - a filter with its strength, or one of the
/// adjustments - as a link in the clip's chain.
fn look_of(item: &Value, notes: &mut Vec<String>) -> Option<AppliedFilter> {
    let kind = text(item, "type");
    let value = number(&item["value"], 0.0);
    let adjust = |key: &str, scaled: f64| {
        let mut entry = AppliedFilter::new("concat.adjust");
        entry.params.insert(key.to_owned(), scaled);
        Some(entry)
    };
    match kind {
        "brightness" => adjust("brightness", value * 100.0),
        "contrast" => adjust("contrast", value * 100.0),
        "saturation" => adjust("saturation", value * 100.0),
        "highlight" => adjust("highlights", value * 100.0),
        "shadow" => adjust("shadows", value * 100.0),
        "light_sensation" => adjust("exposure", value * 1.5),
        "temperature" => adjust("temperature", 6500.0 + value * 3000.0),
        "tone" => adjust("tint", value * 100.0),
        "sharpen" => adjust("sharpen", value.abs() * 100.0),
        "fade" => adjust("fade", value.abs() * 100.0),
        "vignetting" => adjust("vignette", value.abs() * 100.0),
        "filter" => {
            let mut entry = filter_stand_in(item, notes)?;
            entry
                .params
                .insert("intensity".to_owned(), (value * 100.0).clamp(0.0, 100.0));
            Some(entry)
        }
        "video_effect" => {
            stand_in(Want::Effect, item, notes).map(|(id, params)| applied(id, params, item))
        }
        _ => {
            if !kind.is_empty() && value.abs() > 1e-6 {
                notes.push(format!("the adjustment \u{201c}{kind}\u{201d} is left out"));
            }
            None
        }
    }
}

/// Folds an Adjust into one already on the chain, so a clip's several
/// CapCut adjustments become one Adjust with all of them set.
fn merge_adjust(chain: &mut Vec<AppliedFilter>, entry: AppliedFilter) {
    if entry.id == "concat.adjust"
        && let Some(existing) = chain.iter_mut().find(|link| link.id == "concat.adjust")
    {
        existing.params.extend(entry.params);
        return;
    }
    chain.push(entry);
}

/// A CapCut filter's stand-in among Concat's looks, by the words of its
/// name; a filter Concat has no look like is left out.
fn filter_stand_in(item: &Value, notes: &mut Vec<String>) -> Option<AppliedFilter> {
    let name = text(item, "name").to_lowercase();
    const LOOKS: &[(&[&str], &str)] = &[
        (
            &[
                "b&w",
                "blanco y negro",
                "mono",
                "noir",
                "preto",
                "gris",
                "grey",
                "gray",
            ],
            "concat.mono",
        ),
        (&["retro", "vintage", "antig", "70"], "concat.retro-70s"),
        (
            &["film", "película", "pelicula", "cine", "cinema"],
            "concat.film",
        ),
        (
            &[
                "warm",
                "cálid",
                "calid",
                "quente",
                "chaud",
                "sunset",
                "atardecer",
                "golden",
                "dorad",
            ],
            "concat.warm",
        ),
        (
            &["cool", "frí", "fri", "frio", "froid", "blue", "azul"],
            "concat.cool",
        ),
        (
            &["vivid", "vivo", "intens", "mejor", "enhance", "pop"],
            "concat.vivid",
        ),
        (&["fresh", "fresc"], "concat.fresh"),
        (&["food", "comida", "delici"], "concat.delicious"),
        (&["night", "noche", "noite", "nuit"], "concat.night"),
        (&["dream", "sueñ", "suen", "sonho", "rêve"], "concat.dreamy"),
        (&["natural"], "concat.natural"),
        (
            &[
                "travel",
                "viaje",
                "viagem",
                "voyage",
                "landscape",
                "paisaje",
            ],
            "concat.landscape-pop",
        ),
        (&["portrait", "retrato", "piel", "skin"], "concat.fair"),
    ];
    match LOOKS
        .iter()
        .find(|(words, _)| words.iter().any(|w| name.contains(w)))
    {
        Some((_, id)) => {
            notes.push(format!(
                "the filter \u{201c}{}\u{201d} is approximated as {}",
                text(item, "name"),
                label(id)
            ));
            Some(AppliedFilter::new(*id))
        }
        None => {
            notes.push(format!(
                "the filter \u{201c}{}\u{201d} has no counterpart and is left out",
                text(item, "name")
            ));
            None
        }
    }
}

/// A CapCut voice effect's stand-in, by the words of its name.
fn audio_stand_in(item: &Value) -> Option<(&'static str, ())> {
    let name = text(item, "name").to_lowercase();
    const VOICES: &[(&[&str], &str)] = &[
        (
            &["chipmunk", "ardilla", "squirrel", "esquilo"],
            "concat.chipmunk",
        ),
        (&["robot", "robô"], "concat.robot"),
        (&["echo", "eco"], "concat.echo"),
        (&["megaphone", "megáfono", "megafono"], "concat.megaphone"),
        (&["vinyl", "vinilo", "vinil"], "concat.vinyl"),
        (&["lo-fi", "lofi"], "concat.lofi"),
        (&["deep", "grave", "profund"], "concat.deep"),
        (&["sweet", "dulce", "doce"], "concat.sweet"),
        (&["distort"], "concat.distorted"),
        (&["santa", "papá noel", "noel"], "concat.santa"),
        (&["elf", "duende"], "concat.elf"),
        (&["tremble", "tembl"], "concat.tremble"),
        (&["electronic", "electrón", "electron"], "concat.electronic"),
        (&["synth", "sintet"], "concat.synth"),
        (&["house", "casa", "hall", "salón"], "concat.big-house"),
        (&["battery", "batería", "bateria"], "concat.low-battery"),
        (&["high", "agud", "alto"], "concat.high"),
        (&["low", "bajo", "baixo"], "concat.low"),
    ];
    VOICES
        .iter()
        .find(|(words, _)| words.iter().any(|w| name.contains(w)))
        .map(|(_, id)| (*id, ()))
}

/// The segment's placement: CapCut's position is in halves of the canvas
/// from its centre, y up; Concat's in whole widths and heights, y down.
fn placement(clip: &mut Clip, segment: &Value) {
    let place = &segment["clip"];
    if place.is_null() {
        return;
    }
    let sx = number(&place["scale"]["x"], 1.0);
    let sy = number(&place["scale"]["y"], sx);
    clip.scale = sx.abs().max(0.01);
    if (sy - sx).abs() > 1e-6 && sx.abs() > 1e-6 {
        clip.stretch_y = (sy / sx).abs();
    }
    clip.offset_x = number(&place["transform"]["x"], 0.0) / 2.0;
    clip.offset_y = -number(&place["transform"]["y"], 0.0) / 2.0;
    clip.rotation = number(&place["rotation"], 0.0);
    clip.opacity *= number(&place["alpha"], 1.0).clamp(0.0, 1.0);
    clip.flip_h = place["flip"]["horizontal"].as_bool().unwrap_or(false);
    clip.flip_v = place["flip"]["vertical"].as_bool().unwrap_or(false);
}

/// CapCut's keyframes on the segment as Concat's keys.
fn keys(segment: &Value, duration: f64) -> Vec<ClipKey> {
    let mut out = Vec::new();
    // A key's time is in the source's time in current drafts - the first
    // sits at the segment's source start, the last at most its source end -
    // and from the segment's own start in older ones. Read either way, onto
    // the segment's timeline time.
    let source_start = seconds(&segment["source_timerange"]["start"]);
    let source_length = seconds(&segment["source_timerange"]["duration"]).max(1e-6);
    let rate = source_length / duration.max(1e-6);
    let offsets: Vec<f64> = segment["common_keyframes"]
        .as_array()
        .into_iter()
        .flatten()
        .flat_map(|track| track["keyframe_list"].as_array().into_iter().flatten())
        .map(|key| seconds(&key["time_offset"]))
        .collect();
    let in_source = source_start > 1e-3
        && offsets
            .iter()
            .all(|&at| at >= source_start - 1e-3 && at <= source_start + source_length + 1e-3);
    let (origin, rate) = if in_source {
        (source_start, rate)
    } else {
        (0.0, 1.0)
    };
    for track in segment["common_keyframes"].as_array().into_iter().flatten() {
        let (property, scale, shift): (KeyProperty, f64, f64) = match text(track, "property_type") {
            "KFTypePositionX" => (KeyProperty::OffsetX, 0.5, 0.0),
            "KFTypePositionY" => (KeyProperty::OffsetY, -0.5, 0.0),
            "KFTypeScaleX" | "KFTypeUniformScale" => (KeyProperty::Scale, 1.0, 0.0),
            "KFTypeRotation" => (KeyProperty::Rotation, 1.0, 0.0),
            "KFTypeAlpha" | "KFTypeGlobalAlpha" => (KeyProperty::Opacity, 1.0, 0.0),
            "KFTypeVolume" => (KeyProperty::Volume, 1.0, 0.0),
            _ => continue,
        };
        for key in track["keyframe_list"].as_array().into_iter().flatten() {
            let at = ((seconds(&key["time_offset"]) - origin) / rate / duration.max(1e-6))
                .clamp(0.0, 1.0);
            let value = key["values"].get(0).and_then(Value::as_f64).unwrap_or(0.0) * scale + shift;
            let ease = match text(key, "curveType") {
                "" | "Line" => KeyEase::LINEAR,
                _ => KeyEase::IN_OUT,
            };
            out.push(ClipKey {
                property,
                at,
                value,
                ease,
            });
        }
    }
    out
}

/// A speed material: a constant rate, or a curve of `(at, rate)` points.
fn speed(clip: &mut Clip, item: &Value, notes: &mut Vec<String>) {
    let constant = number(&item["speed"], 1.0);
    clip.speed = constant.clamp(0.0625, 16.0);
    if item["mode"].as_i64() == Some(1)
        && let Some(points) = item["curve_speed"]["speed_points"].as_array()
    {
        let curve: Vec<SpeedPoint> = points
            .iter()
            .map(|point| SpeedPoint {
                at: number(&point["x"], 0.0).clamp(0.0, 1.0),
                speed: (number(&point["y"], 1.0) * constant).clamp(0.0625, 16.0),
            })
            .collect();
        if curve.len() >= 2 {
            clip.speed_curve = Some(curve);
        } else {
            notes.push(format!(
                "the speed curve on \u{201c}{}\u{201d} is read as a constant rate",
                clip.name
            ));
        }
    }
}

/// A canvas material as the clip's own background.
fn background(item: &Value, folder: &Path) -> Option<Background> {
    match text(item, "type") {
        "canvas_blur" => Some(Background::Blur {
            amount: number(&item["blur"], 0.375).clamp(0.0, 1.0),
        }),
        "canvas_color" => hex(text(item, "color")).map(|color| Background::Color { color }),
        // A picture behind the clip is the bin's in Concat; the import
        // softens the clip itself behind it instead.
        "canvas_image" => resolve(text(item, "image"), folder)
            .filter(|path| path.is_file())
            .map(|_| Background::Blur { amount: 0.375 }),
        _ => None,
    }
}

/// The animations a segment carries, by their slots.
fn animations(clip: &mut Clip, item: &Value, notes: &mut Vec<String>) {
    let title = clip.kind == ClipKind::Text;
    let mut set: Animations = clip.animations.clone().unwrap_or_default();
    for animation in item["animations"].as_array().into_iter().flatten() {
        let slot = match text(animation, "type") {
            "in" => Slot::In,
            "out" => Slot::Out,
            "group" | "combo" => Slot::Combo,
            "loop" => Slot::Loop,
            // A caption's word-by-word motion plays as the title's way in.
            "caption" => Slot::In,
            _ => continue,
        };
        let Some((id, _)) = stand_in(Want::Animation { slot, text: title }, animation, notes)
        else {
            continue;
        };
        let applied = Some(ClipAnimation {
            id,
            duration: seconds(&animation["duration"]).max(0.1),
        });
        match slot {
            Slot::In => set.enter = applied,
            Slot::Out => set.exit = applied,
            Slot::Combo => set.combo = applied,
            Slot::Loop => set.looping = applied,
        }
    }
    clip.animations = (!set.is_empty()).then_some(set);
}

/// When each of `content`'s words is spoken: the caption's recognised
/// words, in milliseconds from the caption's start, matched in order onto
/// the content's. They come with the spaces between them, and often with
/// more words than this caption shows, since CapCut splits a sentence over
/// several. Empty when they do not line up.
fn word_times(content: &str, item: &Value) -> Vec<[f64; 2]> {
    let words = &item["words"];
    let (Some(said), Some(starts), Some(ends)) = (
        words["text"].as_array(),
        words["start_time"].as_array(),
        words["end_time"].as_array(),
    ) else {
        return Vec::new();
    };
    let plain = |word: &str| -> String {
        word.chars()
            .filter(|c| c.is_alphanumeric())
            .flat_map(char::to_lowercase)
            .collect()
    };
    let spoken: Vec<(String, f64, f64)> = said
        .iter()
        .zip(starts.iter().zip(ends))
        .filter_map(|(word, (start, end))| {
            let word = plain(word.as_str()?);
            (!word.is_empty()).then(|| {
                (
                    word,
                    start.as_f64().unwrap_or(0.0) / 1000.0,
                    end.as_f64().unwrap_or(0.0) / 1000.0,
                )
            })
        })
        .collect();
    let shown: Vec<String> = content.split_whitespace().map(plain).collect();
    if shown.is_empty() {
        return Vec::new();
    }
    for at in 0..spoken.len() {
        if spoken.len() - at < shown.len() {
            break;
        }
        if shown
            .iter()
            .zip(&spoken[at..])
            .all(|(word, (heard, _, _))| word == heard)
        {
            return spoken[at..at + shown.len()]
                .iter()
                .map(|(_, start, end)| [*start, *end])
                .collect();
        }
    }
    Vec::new()
}

/// A CapCut mask as the clip's.
fn mask(item: &Value) -> Option<ClipMask> {
    let config = &item["config"];
    let shape = match text(item, "resource_type") {
        "line" => MaskShape::Linear,
        "mirror" => MaskShape::Mirror,
        "circle" => MaskShape::Circle,
        "rectangle" => MaskShape::Rectangle,
        "heart" => MaskShape::Heart,
        "geometric_shape" | "star" => MaskShape::Star,
        _ => return None,
    };
    let mut mask = ClipMask::of(shape);
    mask.x = 0.5 + number(&config["centerX"], 0.0) / 2.0;
    mask.y = 0.5 - number(&config["centerY"], 0.0) / 2.0;
    mask.width = number(&config["width"], mask.width).abs();
    mask.height = number(&config["height"], mask.height).abs();
    mask.rotation = number(&config["rotation"], 0.0);
    mask.feather = number(&config["feather"], 0.0).clamp(0.0, 1.0);
    mask.roundness = number(&config["roundCorner"], 0.0).clamp(0.0, 1.0);
    mask.invert = config["invert"].as_bool().unwrap_or(false);
    Some(mask)
}

/// The weight a font file's name gives, when it names one.
fn weight_in(path: &str) -> Option<f64> {
    let name = Path::new(path).file_stem()?.to_str()?.to_lowercase();
    [
        ("extrablack", 950.0),
        ("black", 900.0),
        ("heavy", 900.0),
        ("extrabold", 800.0),
        ("ultrabold", 800.0),
        ("semibold", 600.0),
        ("demibold", 600.0),
        ("bold", 700.0),
        ("medium", 500.0),
        ("extralight", 200.0),
        ("light", 300.0),
        ("thin", 100.0),
        ("regular", 400.0),
    ]
    .iter()
    .find(|(word, _)| name.contains(word))
    .map(|(_, weight)| *weight)
}

/// A text material as a title's style.
/// CapCut's text size unit, in pixels of em on a canvas whose shorter side
/// is 1080: measured by fitting Concat's painting of the same words over
/// CapCut's export (size 8 is a 50.25 px em, size 10 a 62.9 px one).
const EM_PER_SIZE: f64 = 6.285;

fn text_style(
    item: &Value,
    (canvas_w, canvas_h): (f64, f64),
    fonts: &mut Vec<CustomFont>,
    notes: &mut Vec<String>,
) -> TextStyle {
    let mut style = TextStyle::default();
    let content: Value = serde_json::from_str(text(item, "content")).unwrap_or(Value::Null);
    let words = content
        .get("text")
        .and_then(Value::as_str)
        .map(str::to_owned)
        .unwrap_or_else(|| text(item, "recognize_text").to_owned());
    style.content = words;
    let first = content["styles"].get(0).cloned().unwrap_or(Value::Null);
    let size = first["size"]
        .as_f64()
        .or_else(|| item["font_size"].as_f64())
        .unwrap_or(15.0);
    // The em in pixels, then as Concat's fraction of the frame's height.
    let em = size * EM_PER_SIZE * canvas_w.min(canvas_h) / 1080.0;
    style.font_size = (em / canvas_h).clamp(0.003, 0.5);
    if let Some(colour) = first["fill"]["content"]["solid"]["color"]
        .as_array()
        .and_then(|c| hex_of(c))
    {
        style.color = colour;
    } else if let Some(colour) = hex(text(item, "text_color")) {
        style.color = colour;
    }
    style.opacity = number(&item["text_alpha"], 1.0).clamp(0.0, 1.0);
    style.font_weight =
        if first["bold"].as_bool().unwrap_or(false) || number(&item["bold_width"], 0.0) > 0.0 {
            800.0
        } else {
            600.0
        };
    style.italic =
        first["italic"].as_bool().unwrap_or(false) || number(&item["italic_degree"], 0.0) != 0.0;
    style.align = match item["alignment"].as_i64() {
        Some(0) => TextAlign::Left,
        Some(2) => TextAlign::Right,
        _ => TextAlign::Center,
    };
    // CapCut sets lines in the face's typographic box, a plate behind each
    // line; see `concat_text::TitleStyle::snug_lines`.
    style.snug_lines = true;
    style.line_height = 1.0 + number(&item["line_spacing"], 0.02);
    style.tracking = number(&item["letter_spacing"], 0.0) * 0.05 * style.font_size;
    // The stroke is the style's own: the material's border colour is only
    // what the panel would offer next. Its width is a fraction of the em,
    // the outline reaching that far past the glyph's edge.
    let stroke = first["strokes"].get(0).cloned().unwrap_or(Value::Null);
    if let Some(colour) = stroke["content"]["solid"]["color"]
        .as_array()
        .and_then(|c| hex_of(c))
    {
        style.stroke_color = colour;
        style.stroke_width = number(&stroke["width"], 0.08) * em / canvas_h;
    }
    style.shadow = item["has_shadow"].as_bool().unwrap_or(false)
        || first["shadows"].as_array().is_some_and(|s| !s.is_empty());
    // The plate: CapCut's width and height dials are air in ems either
    // side of each line, its roundness a fraction of half an em.
    if let Some(colour) = hex(text(item, "background_color"))
        && number(&item["background_alpha"], 1.0) > 0.0
        && item["background_style"].as_i64().unwrap_or(0) != 0
    {
        let alpha = number(&item["background_alpha"], 1.0).clamp(0.0, 1.0);
        style.background = if alpha < 1.0 {
            format!("{colour}{:02x}", (alpha * 255.0).round() as u8)
        } else {
            colour
        };
        style.background_lines = true;
        style.background_padding_x = number(&item["background_width"], 0.14) * em / canvas_h;
        style.background_padding_y = number(&item["background_height"], 0.14) * em / canvas_h;
        style.background_radius =
            number(&item["background_round_radius"], 0.0) * em * 0.5 / canvas_h;
    }
    style.word_times = word_times(&style.content, item);
    // CapCut's line width wraps the words; the plate still hugs them.
    let width = number(&item["line_max_width"], 0.0);
    if width > 0.0 && width < 1.0 {
        style.wrap_width = width;
    }
    // The face: a file CapCut points at, registered on the project once.
    let path = first["font"]["path"]
        .as_str()
        .filter(|p| !p.is_empty())
        .or_else(|| item["font_path"].as_str());
    if let Some(path) = path {
        let file = Path::new(path);
        if file.is_file() {
            match concat_text::families_in(file).into_iter().next() {
                Some(family) => {
                    if !fonts.iter().any(|font| font.path == path) {
                        fonts.push(CustomFont {
                            family: family.clone(),
                            path: path.to_owned(),
                        });
                    }
                    style.font_family = format!("\"{family}\"");
                    // A face that is one weight of a family says which in
                    // its file's name: SSTHeavy, Roboto-Bold, Inter Light.
                    if let Some(weight) = weight_in(path) {
                        style.font_weight = weight;
                    }
                }
                None => notes.push(format!(
                    "the font {path} could not be read; the title uses Concat's"
                )),
            }
        } else {
            notes.push(format!(
                "the font {path} is not on this machine; the title uses Concat's"
            ));
        }
    }
    style
}

#[cfg(test)]
mod tests {
    use super::*;

    fn draft() -> Value {
        serde_json::json!({
            "name": "Test",
            "fps": 30.0,
            "canvas_config": {"width": 1080, "height": 1920},
            "materials": {
                "videos": [
                    {"id": "V1", "type": "video", "path": "##_draftpath_placeholder_X_##/materials/video/a.mp4",
                     "duration": 8000000, "width": 1080, "height": 1920, "material_name": "a.mp4"},
                    {"id": "V2", "type": "photo", "path": "C:/nowhere/b.png", "duration": 5000000}
                ],
                "audios": [{"id": "A1", "type": "extract_music", "path": "C:/nowhere/c.mp3", "duration": 9000000, "name": "c.mp3"}],
                "texts": [{"id": "X1", "content": "{\"text\":\"HELLO\",\"styles\":[{\"fill\":{\"content\":{\"solid\":{\"color\":[1,0,0]}}},\"size\":12}]}", "alignment": 1}],
                "speeds": [{"id": "S1", "type": "speed", "mode": 0, "speed": 2.0}],
                "transitions": [{"id": "TR1", "type": "transition", "name": "Destello II", "resource_id": "6952697917563998722", "duration": 466666}],
                "material_animations": [{"id": "AN1", "type": "sticker_animation", "animations": [
                    {"type": "in", "name": "Zoom 1", "resource_id": "6740868384637850120", "duration": 500000},
                    {"type": "out", "name": "Desaparición progresiva", "resource_id": "0", "duration": 400000}]}],
                "audio_fades": [{"id": "F1", "fade_in_duration": 1000000, "fade_out_duration": 500000}],
                "video_effects": [{"id": "E1", "type": "video_effect", "name": "Lentes de zoom", "resource_id": "7399465441057328389",
                    "adjust_params": [{"name": "effects_adjust_range", "value": 0.5}]}]
            },
            "tracks": [
                {"type": "video", "attribute": 0, "segments": [
                    {"material_id": "V1", "target_timerange": {"start": 0, "duration": 2000000},
                     "source_timerange": {"start": 1000000, "duration": 4000000},
                     "extra_material_refs": ["S1", "TR1", "AN1"],
                     "clip": {"scale": {"x": 1.5, "y": 1.5}, "transform": {"x": 0.5, "y": -0.5}, "rotation": 10.0, "alpha": 1.0,
                              "flip": {"horizontal": true, "vertical": false}},
                     "common_keyframes": [{"property_type": "KFTypePositionX", "keyframe_list": [
                        {"time_offset": 0, "values": [0.0], "curveType": "Line"},
                        {"time_offset": 1000000, "values": [1.0], "curveType": "Line"}]}]},
                    {"material_id": "V2", "target_timerange": {"start": 2000000, "duration": 3000000},
                     "source_timerange": {"start": 0, "duration": 3000000}, "extra_material_refs": []}
                ]},
                {"type": "effect", "segments": [
                    {"material_id": "E1", "target_timerange": {"start": 0, "duration": 1000000}}]},
                {"type": "text", "segments": [
                    {"material_id": "X1", "target_timerange": {"start": 500000, "duration": 1500000},
                     "extra_material_refs": [], "clip": {"scale": {"x": 1.0, "y": 1.0}, "transform": {"x": 0.0, "y": 0.6}}}]},
                {"type": "audio", "segments": [
                    {"material_id": "A1", "target_timerange": {"start": 0, "duration": 5000000},
                     "source_timerange": {"start": 0, "duration": 5000000}, "volume": 0.5, "extra_material_refs": ["F1"]}]}
            ]
        })
    }

    #[test]
    fn a_draft_becomes_a_project_with_its_clips_where_capcut_put_them() {
        let converted = convert(&draft(), Path::new("D:/drafts/Test"), &|_| None);
        let project = &converted.project;
        assert_eq!(project.media.len(), 3, "{:?}", project.media);
        assert!(
            project.media[0].path.ends_with("materials/video/a.mp4")
                || project.media.iter().any(|m| m.path.ends_with("a.mp4"))
        );
        let timeline = &project.timelines[0];
        assert_eq!((timeline.video.width, timeline.video.height), (1080, 1920));
        assert_eq!(timeline.tracks.len(), 4);
        let clips: Vec<&Clip> = timeline.clips.iter().map(Arc::as_ref).collect();
        assert_eq!(clips.len(), 5);

        let first = clips
            .iter()
            .find(|clip| clip.kind == ClipKind::Video)
            .expect("the video");
        assert_eq!(
            (first.start, first.duration, first.source_start),
            (0.0, 2.0, 1.0)
        );
        assert_eq!(first.speed, 2.0);
        assert_eq!(
            (first.scale, first.offset_x, first.offset_y, first.rotation),
            (1.5, 0.25, 0.25, 10.0)
        );
        assert!(first.flip_h);
        assert_eq!(first.keys.len(), 2);
        assert_eq!((first.keys[1].at, first.keys[1].value), (0.5, 0.5));
        let animations = first.animations.as_ref().expect("animations");
        assert_eq!(
            animations.enter.as_ref().map(|a| a.id.as_str()),
            Some("concat.in-zoom-1")
        );
        assert_eq!(
            animations.exit.as_ref().map(|a| a.id.as_str()),
            Some("concat.out-fade-out")
        );

        let still = clips
            .iter()
            .find(|clip| clip.kind == ClipKind::Image)
            .expect("the still");
        assert_eq!(
            still.transition_in.as_ref().map(|t| t.id.as_str()),
            Some("concat.flash-cut"),
            "the transition rides into the next clip"
        );

        let layer = clips
            .iter()
            .find(|clip| clip.kind == ClipKind::Layer)
            .expect("the effect");
        assert_eq!(layer.video_effects[0].id, "concat.zoom-lens");
        assert_eq!(layer.video_effects[0].params.get("range"), Some(&50.0));

        let title = clips
            .iter()
            .find(|clip| clip.kind == ClipKind::Text)
            .expect("the title");
        let style = title.text.as_ref().expect("a style");
        assert_eq!(style.content, "HELLO");
        assert_eq!(style.color, "#ff0000");
        assert!((title.offset_y + 0.3).abs() < 1e-9);

        let sound = clips
            .iter()
            .find(|clip| clip.kind == ClipKind::Audio)
            .expect("the sound");
        assert_eq!(
            (sound.volume, sound.fade_in, sound.fade_out),
            (0.5, 1.0, 0.5)
        );
        assert!(converted.notes.iter().any(|note| note.contains("missing")));
    }

    /// An import writes a project Concat opens as it opens its own, every
    /// clip there, and its flattened timeline ready to draw.
    #[test]
    fn an_import_is_a_project_concat_opens() {
        let dir = std::env::temp_dir().join(format!("concat-capcut-{}", std::process::id()));
        let draft_dir = dir.join("draft");
        std::fs::create_dir_all(&draft_dir).expect("a scratch folder");
        std::fs::write(draft_dir.join("draft_content.json"), draft().to_string())
            .expect("the draft");
        let location = dir.join("projects");
        std::fs::create_dir_all(&location).expect("a location");
        let imported = import(&draft_dir, &location.to_string_lossy()).expect("imports");
        let again = import(&draft_dir, &location.to_string_lossy()).expect("imports twice");
        assert_ne!(
            imported.info.path, again.info.path,
            "a second import is a project of its own"
        );
        let session = crate::session::Session::open_info(&imported.info).expect("opens");
        // The draft's files are nowhere on this machine, so their clips are
        // left out and the title and the effect come in.
        let clips = &session.project().active().clips;
        assert_eq!(clips.len(), 2);
        assert!(clips.iter().all(|clip| clip.media_id.is_empty()));
        assert!(imported.notes.iter().any(|note| note.contains("left out")));
        assert!(Path::new(&imported.info.path).join(REPORT).is_file());
        assert!(!session.flattened_clips().is_empty());
        let _ = std::fs::remove_dir_all(&dir);
    }

    /// A compound clip opens as its own draft's clips, where it sits on
    /// the timeline, cut to its span and moved as it is moved.
    #[test]
    fn a_compound_clip_opens_as_its_contents_in_its_place() {
        let inner = serde_json::json!({
            "materials": {"videos": [{"id": "IV", "type": "video", "path": "C:/x/inner.mp4", "duration": 9000000}]},
            "tracks": [{"type": "video", "segments": [
                {"material_id": "IV", "target_timerange": {"start": 0, "duration": 3000000},
                 "source_timerange": {"start": 500000, "duration": 3000000}, "extra_material_refs": [],
                 "clip": {"scale": {"x": 1.0, "y": 1.0}, "transform": {"x": 0.2, "y": 0.0}}}]}]
        });
        let outer = serde_json::json!({
            "canvas_config": {"width": 1920, "height": 1080}, "fps": 30.0,
            "materials": {
                "videos": [{"id": "CV", "type": "video", "path": "", "duration": 3000000}],
                "drafts": [{"id": "D1", "type": "combination", "draft": inner}]
            },
            "tracks": [{"type": "video", "segments": [
                {"material_id": "CV", "target_timerange": {"start": 10000000, "duration": 2000000},
                 "source_timerange": {"start": 1000000, "duration": 2000000}, "extra_material_refs": ["D1"],
                 "clip": {"scale": {"x": 0.5, "y": 0.5}, "transform": {"x": 0.0, "y": 0.0}}}]}]
        });
        let converted = convert(&outer, Path::new("D:/drafts/C"), &|_| None);
        let clips = &converted.project.timelines[0].clips;
        assert_eq!(clips.len(), 1, "the compound is its contents");
        let clip = &clips[0];
        // The inner clip ran 0..3 in its draft; read from 1 s, placed at 10 s
        // and two long, it shows 1..3 of itself at 10..12.
        assert!(
            (clip.start - 10.0).abs() < 1e-9 && (clip.duration - 2.0).abs() < 1e-9,
            "{} {}",
            clip.start,
            clip.duration
        );
        assert!(
            (clip.source_start - 1.5).abs() < 1e-9,
            "{}",
            clip.source_start
        );
        assert!((clip.scale - 0.5).abs() < 1e-9);
        assert!((clip.offset_x - 0.05).abs() < 1e-9, "{}", clip.offset_x);
        assert_eq!(
            converted.project.timelines[0].tracks.len(),
            2,
            "its contents ride a lane over its own"
        );
    }

    #[test]
    fn the_id_table_is_sorted_and_names_only_installed_packages() {
        let catalogue = concat_effects::Catalogue::builtin();
        assert!(
            ids::IDS.windows(2).all(|pair| pair[0].0 < pair[1].0),
            "sorted for the search"
        );
        let missing: Vec<&str> = ids::IDS
            .iter()
            .map(|(_, id, _)| *id)
            .filter(|id| catalogue.get(id).is_none())
            .collect();
        assert!(missing.is_empty(), "{missing:?}");
    }

    #[test]
    fn an_encrypted_draft_is_refused_with_a_reason() {
        let error =
            parse(b"\x8f\x01garbage", Path::new("draft_content.json")).expect_err("refused");
        assert!(error.contains("encrypted"));
    }

    /// Every CapCut project on this machine converts without a panic, and
    /// says what it could not bring. Skipped where CapCut keeps none.
    #[test]
    fn the_capcut_projects_on_this_machine_convert() {
        let Some(local) = std::env::var_os("LOCALAPPDATA") else {
            return;
        };
        let root = Path::new(&local).join("CapCut/User Data/Projects/com.lveditor.draft");
        let Ok(entries) = std::fs::read_dir(&root) else {
            return;
        };
        for entry in entries.flatten() {
            let Some(file) = draft_file(&entry.path()) else {
                continue;
            };
            let Ok(bytes) = std::fs::read(&file) else {
                continue;
            };
            let Ok(document) = parse(&bytes, &file) else {
                continue;
            };
            let converted = convert(&document, &entry.path(), &|_| None);
            let clips = converted.project.timelines[0].clips.len();
            let mut notes = converted.notes.clone();
            notes.sort();
            notes.dedup();
            eprintln!(
                "{:40} {clips:4} clips, {:3} notes",
                entry.file_name().to_string_lossy(),
                notes.len()
            );
            for note in notes {
                eprintln!("    {note}");
            }
        }
    }
}

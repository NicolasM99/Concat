// SPDX-License-Identifier: AGPL-3.0-or-later
// SPDX-FileCopyrightText: 2026 Jareer and Concat contributors

//! A clip's animations, resolved against the catalogue: the motion the
//! engine asks for each frame ([`ClipMotion`]) and the looks they ride over
//! their windows, which join the clip's shader passes.
//!
//! The windows are measured on the clip as the person placed it. A
//! transition's overlap lengthens a clip before its start or past its end
//! ([`crate::ExportClip::animation_head`]); the In still begins at the cut
//! and the Out still ends at the clip's own last frame.

use std::collections::BTreeMap;
use std::sync::Arc;

use concat_core::RevealMap;
use concat_core::ShaderPass;
use concat_core::animate::{ClipMotion, Motion};
use concat_effects::Catalogue;
use concat_effects::animation::{self, Animation, Slot};

use crate::ExportClip;

/// One filled slot: its animation and how long it runs.
#[derive(Debug)]
struct Window {
    slot: Slot,
    duration: f64,
    animation: &'static Animation,
}

/// A clip's animations, ready to answer for any instant.
#[derive(Debug)]
pub(crate) struct ClipAnimations {
    windows: Vec<Window>,
    /// Seconds of the engine's clip before the clip's own first frame.
    head: f64,
    /// The clip's own length, without the overlap either side.
    length: f64,
}

impl ClipAnimations {
    /// The animations `clip` has that the catalogue knows, or None when
    /// it has none: an unknown id is skipped, as an unknown effect is.
    pub(crate) fn of(clip: &ExportClip) -> Option<ClipAnimations> {
        let set = clip.animations.as_ref()?;
        let length = (clip.duration - clip.animation_head - clip.animation_tail).max(0.0);
        if length <= 0.0 {
            return None;
        }
        let catalogue = Catalogue::builtin();
        let find = |slot: Slot, applied: &Option<concat_project::model::ClipAnimation>| {
            let applied = applied.as_ref()?;
            let animation = catalogue.get(&applied.id)?.animation()?;
            // A package for one slot set in another runs as the slot it
            // was set in: the document's slot is what the person chose.
            Some((slot, applied.duration.max(0.0), animation))
        };
        let enter = find(Slot::In, &set.enter);
        let exit = find(Slot::Out, &set.exit);
        let (enter_len, exit_len) = animation::fitted(
            enter.as_ref().map(|(_, d, _)| *d),
            exit.as_ref().map(|(_, d, _)| *d),
            length,
        );
        let mut windows = Vec::new();
        for (found, fitted) in [(enter, enter_len), (exit, exit_len)] {
            if let (Some((slot, _, animation)), Some(duration)) = (found, fitted) {
                windows.push(Window {
                    slot,
                    duration,
                    animation,
                });
            }
        }
        for found in [
            find(Slot::Combo, &set.combo),
            find(Slot::Loop, &set.looping),
        ]
        .into_iter()
        .flatten()
        {
            let (slot, duration, animation) = found;
            windows.push(Window {
                slot,
                duration,
                animation,
            });
        }
        (!windows.is_empty()).then_some(ClipAnimations {
            windows,
            head: clip.animation_head.max(0.0),
            length,
        })
    }

    /// Each window open at `seconds` after the engine's clip begins, with
    /// how far through it the clip is.
    fn open(&self, seconds: f64) -> impl Iterator<Item = (&Window, f64)> {
        let at = seconds - self.head;
        self.windows.iter().filter_map(move |window| {
            animation::progress(window.slot, window.duration, at, self.length).map(|t| (window, t))
        })
    }

    /// The looks the open windows ride, as shader passes, at `seconds`
    /// after the engine's clip begins.
    pub(crate) fn passes_at(
        &self,
        seconds: f64,
        reveal_map: Option<Arc<RevealMap>>,
    ) -> Vec<ShaderPass> {
        let catalogue = Catalogue::builtin();
        self.open(seconds)
            .filter_map(|(window, t)| {
                let (id, values): (&str, BTreeMap<String, f64>) = window.animation.look_at(t)?;
                catalogue.get(id)?.pass(&values, reveal_map.clone())
            })
            .collect()
    }
}

impl ClipMotion for ClipAnimations {
    fn passes_at(&self, seconds: f64, reveal_map: Option<Arc<RevealMap>>) -> Vec<ShaderPass> {
        ClipAnimations::passes_at(self, seconds, reveal_map)
    }

    fn motion_at(&self, seconds: f64) -> Motion {
        self.open(seconds)
            .map(|(window, t)| window.animation.motion_at(t))
            .fold(Motion::NONE, |acc, m| Motion {
                scale: acc.scale * m.scale,
                offset_x: acc.offset_x + m.x,
                offset_y: acc.offset_y + m.y,
                rotation: acc.rotation + m.rotation,
                opacity: acc.opacity * m.opacity,
                stretch_x: acc.stretch_x * m.sx,
                stretch_y: acc.stretch_y * m.sy,
            })
    }
}

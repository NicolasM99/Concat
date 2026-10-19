// SPDX-License-Identifier: AGPL-3.0-or-later
// SPDX-FileCopyrightText: 2026 Jareer and Concat contributors

//! Paints one title to a PNG, for measuring a style against a reference
//! frame.
//!
//! usage: title_probe <font file> <text> <font size> <stroke width>
//!        <colour> <stroke colour> <plate colour|-> <pad x> <pad y>
//!        <radius> <line height> <width> <height> <out.png>
//!
//! Sizes are the style's own fractions of the frame height.

use concat_text::{Align, Fonts, TitleStyle};

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let [
        font,
        text,
        size,
        stroke,
        colour,
        stroke_colour,
        plate,
        pad_x,
        pad_y,
        radius,
        line_height,
        width,
        height,
        out,
    ] = args.as_slice()
    else {
        eprintln!("title_probe: wrong number of arguments; see the source");
        std::process::exit(2);
    };
    let number = |text: &str| text.parse::<f64>().expect("a number");
    let mut fonts = Fonts::new();
    fonts.add_file(std::path::Path::new(font));
    let family = concat_text::families_in(std::path::Path::new(font))
        .into_iter()
        .next()
        .expect("a font file");
    let style = TitleStyle {
        content: text.replace("\\n", "\n"),
        font_family: format!("\"{family}\""),
        font_size: number(size),
        font_weight: 700.0,
        italic: false,
        color: colour.clone(),
        align: Align::Center,
        stroke_width: number(stroke),
        stroke_color: stroke_colour.clone(),
        shadow: false,
        background: if plate == "-" {
            String::new()
        } else {
            plate.clone()
        },
        background_radius: number(radius),
        background_padding_x: number(pad_x),
        background_padding_y: number(pad_y),
        line_height: number(line_height),
        tracking: 0.0,
        max_width: 0.0,
        max_height: 0.0,
        wrap_width: 0.0,
        background_lines: true,
        snug_lines: true,
    };
    let rendered = concat_text::render(
        &fonts,
        &style,
        width.parse().expect("a width"),
        height.parse().expect("a height"),
    )
    .expect("the title paints");
    std::fs::write(out, rendered.png).expect("the file writes");
}

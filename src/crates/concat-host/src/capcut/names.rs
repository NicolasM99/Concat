// SPDX-License-Identifier: AGPL-3.0-or-later
// SPDX-FileCopyrightText: 2026 Jareer and Concat contributors

//! A stand-in for a CapCut item the id table does not know, found from the
//! words of its name. CapCut writes the name in the language of the
//! interface it was picked in, so the words are listed in the languages
//! CapCut's users most often edit in: English, Spanish, Portuguese, French,
//! German and Italian. The first rule whose word the name contains wins,
//! so the more particular rules come first.

/// What the importer is looking for a stand-in for.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub(super) enum Want {
    Transition,
    Effect,
    /// An animation in a slot, on a title or on a picture.
    Animation {
        slot: Slot,
        text: bool,
    },
}

/// A clip's animation slot.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub(super) enum Slot {
    In,
    Out,
    Combo,
    Loop,
}

const LEFT: &[&str] = &[
    "left",
    "izquierda",
    "esquerda",
    "gauche",
    "links",
    "sinistra",
];
const RIGHT: &[&str] = &["right", "derecha", "direita", "droite", "rechts", "destra"];
const UP: &[&str] = &[
    "up", "arriba", "subir", "cima", "haut", "oben", "alto", "sube",
];
const DOWN: &[&str] = &[
    "down", "abajo", "bajar", "baixo", "bas", "unten", "basso", "caída", "caida", "fall",
];

/// The direction knob's value a name implies, 0 left, 1 right, 2 up and
/// 3 down, for a package that takes one.
fn direction(name: &str) -> Option<&'static str> {
    let has = |words: &[&str]| words.iter().any(|word| contains_word(name, word));
    if has(LEFT) {
        Some("direction=0")
    } else if has(RIGHT) {
        Some("direction=1")
    } else if has(UP) {
        Some("direction=2")
    } else if has(DOWN) {
        Some("direction=3")
    } else {
        None
    }
}

/// Whether `word` is in `name` as a word or the start of one: "flash" in
/// "Flash II", "desliz" in "Deslizar", not "up" in "superior".
fn contains_word(name: &str, word: &str) -> bool {
    name.split(|c: char| !c.is_alphanumeric())
        .any(|part| part.starts_with(word))
}

fn any(name: &str, words: &[&str]) -> bool {
    words.iter().any(|word| contains_word(name, word))
}

type Rule = (&'static [&'static str], &'static str);

const TRANSITIONS: &[Rule] = &[
    (
        &["alejamiento con velocidad", "speed zoom", "radial"],
        "concat.zoom-blur-transition",
    ),
    (
        &[
            "alej", "zoom out", "afast", "éloign", "dézoom", "rauszoom", "allontan",
        ],
        "concat.zoom-transition|direction=1",
    ),
    (
        &["zoom", "acerc", "aproxim", "rapproch", "avvicin", "pull"],
        "concat.zoom-transition",
    ),
    (
        &[
            "swirl",
            "remolino",
            "redemoinho",
            "tourbillon",
            "wirbel",
            "vortice",
            "whirl",
        ],
        "concat.swirl",
    ),
    (
        &["spin", "gir", "rot", "tourn", "dreh", "ruota"],
        "concat.spin",
    ),
    (
        &[
            "flash", "destell", "brillo", "clarão", "clarao", "éclair", "blitz", "lampo", "strobe",
        ],
        "concat.flash-transition",
    ),
    (
        &[
            "glitch", "error", "falla", "fallo", "falha", "panne", "störung", "errore",
        ],
        "concat.glitch-transition",
    ),
    (
        &[
            "blur",
            "desenfo",
            "borros",
            "desfoc",
            "flou",
            "unschärf",
            "sfoc",
        ],
        "concat.blur-dissolve",
    ),
    (
        &["black", "negro", "preto", "noir", "schwarz", "nero"],
        "concat.fade-black",
    ),
    (
        &[
            "white", "blanco", "branco", "blanc", "weiß", "weiss", "bianco",
        ],
        "concat.fade-white",
    ),
    (
        &[
            "smoke", "humo", "fumaça", "fumaca", "fumée", "rauch", "fumo",
        ],
        "concat.black-smoke",
    ),
    (
        &["cloud", "nube", "nuvem", "nuage", "wolke", "nuvola"],
        "concat.cloud",
    ),
    (
        &[
            "fire", "flame", "burn", "fuego", "llama", "quem", "fogo", "feu", "feuer", "fuoco",
        ],
        "concat.flame",
    ),
    (
        &["ink", "tinta", "encre", "tinte", "inchiostro"],
        "concat.white-ink",
    ),
    (
        &[
            "heart",
            "corazón",
            "corazon",
            "coração",
            "coeur",
            "herz",
            "cuore",
            "like",
        ],
        "concat.super-like-transition",
    ),
    (
        &["wave", "ola", "onda", "vague", "welle"],
        "concat.wave-right",
    ),
    (
        &["mosaic", "mosaico", "mosaïque", "pixel"],
        "concat.mosaic-transition",
    ),
    (&["cube", "cubo", "würfel"], "concat.cube"),
    (
        &["page", "página", "pagina", "seite"],
        "concat.page-turning",
    ),
    (
        &[
            "shutter",
            "blind",
            "persiana",
            "store",
            "jalousie",
            "veneziana",
        ],
        "concat.shutter",
    ),
    (
        &["clock", "reloj", "relógio", "horloge", "uhr", "orologio"],
        "concat.clock-wipe",
    ),
    (
        &[
            "circle", "círculo", "circulo", "cercle", "kreis", "cerchio", "iris",
        ],
        "concat.iris",
    ),
    (
        &[
            "light", "leak", "luz", "lumière", "licht", "luce", "bubble", "burbuja", "bolha",
            "bulle", "blase", "bolla",
        ],
        "concat.light-leak-transition",
    ),
    (
        &["split", "divid", "dividir", "partag", "teil"],
        "concat.split",
    ),
    (
        &["push", "empuj", "pousse", "schieb", "spingi"],
        "concat.push",
    ),
    (
        &["slide", "desliz", "desliza", "glisse", "gleit", "scorr"],
        "concat.slide",
    ),
    (
        &["wipe", "barrido", "cortin", "limpar", "balay", "wisch"],
        "concat.linear-wipe",
    ),
    (
        &["stretch", "estir", "estic", "étir", "dehn", "allung"],
        "concat.stretch",
    ),
    (
        &["shake", "sacud", "tembl", "trem", "secou", "wackel", "agit"],
        "concat.shake-transition",
    ),
    (
        &[
            "dissolve", "disolv", "mix", "mezcl", "fund", "dissol", "mischen", "mescol",
        ],
        "concat.dissolve",
    ),
];

const EFFECTS: &[Rule] = &[
    (
        &[
            "zoom",
            "lente",
            "lens",
            "acerc",
            "objectif",
            "objektiv",
            "obiettivo",
        ],
        "concat.zoom-lens",
    ),
    (
        &[
            "glitch",
            "error",
            "falla",
            "fallo",
            "falha",
            "panne",
            "störung",
            "cyberpunk",
        ],
        "concat.glitch",
    ),
    (
        &[
            "shake", "sacud", "tembl", "trem", "secou", "wackel", "vibr", "jitter",
        ],
        "concat.shake",
    ),
    (
        &[
            "blur",
            "desenfo",
            "borros",
            "desfoc",
            "flou",
            "unschärf",
            "sfoc",
        ],
        "concat.blur",
    ),
    (
        &["flash", "destell", "clarão", "éclair", "blitz", "strobe"],
        "concat.flash",
    ),
    (&["rgb", "cromát", "cromat", "chromat"], "concat.chromatic"),
    (
        &["vhs", "retro", "vintage", "antig", "ancien", "alt"],
        "concat.seventies",
    ),
    (
        &["film", "película", "pelicula", "filme", "pellicola"],
        "concat.retro-film",
    ),
    (&["neon", "neón"], "concat.neon-outline"),
    (
        &[
            "glow",
            "brillo",
            "resplandor",
            "brilho",
            "lueur",
            "leucht",
            "bagliore",
        ],
        "concat.glowburst",
    ),
    (
        &["snow", "nieve", "neve", "neige", "schnee"],
        "concat.snowfall",
    ),
    (
        &["rain", "lluvia", "chuva", "pluie", "regen", "pioggia"],
        "concat.rainfall",
    ),
    (
        &[
            "heart",
            "corazón",
            "corazon",
            "coração",
            "coeur",
            "herz",
            "cuore",
            "love",
            "amor",
        ],
        "concat.pink-hearts",
    ),
    (
        &["star", "estrella", "estrela", "étoile", "stern", "stella"],
        "concat.starry",
    ),
    (
        &[
            "spark",
            "chispa",
            "faísca",
            "étincelle",
            "funke",
            "scintill",
        ],
        "concat.spark",
    ),
    (
        &[
            "fire", "flame", "fuego", "llama", "fogo", "feu", "feuer", "fuoco",
        ],
        "concat.fire",
    ),
    (
        &[
            "particle",
            "partícula",
            "particula",
            "particule",
            "partikel",
            "particella",
            "dust",
            "polvo",
        ],
        "concat.gold-dust",
    ),
    (
        &[
            "mirror", "espejo", "espelho", "miroir", "spiegel", "specchio",
        ],
        "concat.mirror-fx",
    ),
    (
        &[
            "split",
            "pantalla dividida",
            "screens",
            "pantallas",
            "telas",
            "écrans",
        ],
        "concat.dual-screens",
    ),
    (&["ripple", "ondas", "ondul", "welle"], "concat.ripple"),
    (
        &["distort", "distors", "distorç", "verzerr"],
        "concat.distort",
    ),
    (
        &["vignet", "viñeta", "vinheta", "vignett"],
        "concat.vignette",
    ),
    (
        &["negative", "negativo", "négatif", "negativ"],
        "concat.color-negative",
    ),
    (
        &["fisheye", "ojo de pez", "olho de peixe", "fish"],
        "concat.fisheye-2",
    ),
    (&["mosaic", "mosaico", "pixel"], "concat.mosaic"),
    (
        &[
            "dark", "oscur", "escur", "sombre", "dunkel", "scur", "noche", "night",
        ],
        "concat.dark-night",
    ),
    (
        &[
            "spooky", "espeluzn", "terror", "horror", "assust", "effray", "gruse",
        ],
        "concat.spooky-camera",
    ),
    (
        &[
            "camera",
            "cámara",
            "câmera",
            "caméra",
            "kamera",
            "telecam",
            "camcorder",
        ],
        "concat.camcorder",
    ),
    (
        &["light", "luz", "lumière", "licht", "luce", "leak"],
        "concat.leak-1",
    ),
    (
        &[
            "static",
            "estátic",
            "estatic",
            "statique",
            "statisch",
            "statico",
            "transform",
        ],
        "concat.jitter",
    ),
];

/// A rule for an animation: its word, and the package for a picture and
/// for a title.
type AnimRule = (&'static [&'static str], &'static str, &'static str);

const ANIM_IN: &[AnimRule] = &[
    (
        &[
            "typewriter",
            "máquina",
            "maquina",
            "escrib",
            "escrev",
            "machine à écrire",
            "schreibmaschine",
            "macchina",
            "type",
            "tipo",
            "revel",
            "secuen",
        ],
        "concat.text-in-typewriter",
        "concat.text-in-typewriter",
    ),
    (
        &[
            "bounce", "rebot", "salt", "rebond", "spring", "rimbalz", "viaje",
        ],
        "concat.text-in-bounce-in",
        "concat.text-in-bounce-in",
    ),
    (
        &["pop", "negrita", "bold", "gras", "fett", "grassetto"],
        "concat.text-in-pop-up",
        "concat.text-in-pop-up",
    ),
    (
        &[
            "flip",
            "volte",
            "volt",
            "retourn",
            "dreh",
            "capovol",
            "despliegue",
            "unfold",
        ],
        "concat.in-flip",
        "concat.text-in-flipping",
    ),
    (
        &["wave", "ondul", "onda", "vague", "welle"],
        "concat.text-in-wave-in",
        "concat.text-in-wave-in",
    ),
    (
        &[
            "whirl",
            "remolino",
            "espiral",
            "spiral",
            "tourbillon",
            "wirbel",
        ],
        "concat.in-whirl",
        "concat.text-in-spiral",
    ),
    (
        &["spin", "rot", "gir", "tourn", "ruot"],
        "concat.in-rotate",
        "concat.text-in-spin-in-1",
    ),
    (
        &["shake", "sacud", "tembl", "trem", "secou", "wackel", "vibr"],
        "concat.in-shake-1",
        "concat.text-in-random-bounce",
    ),
    (
        &[
            "blur",
            "desenfo",
            "borros",
            "desfoc",
            "flou",
            "unschärf",
            "sfoc",
            "concentr",
        ],
        "concat.in-blur",
        "concat.text-in-blur",
    ),
    (
        &["wipe", "barrido", "cortin", "balay", "wisch"],
        "concat.in-screen-wipe",
        "concat.text-in-wipe-right",
    ),
    (
        &[
            "alej", "zoom out", "afast", "éloign", "rauszoom", "allontan",
        ],
        "concat.in-zoom-out",
        "concat.text-in-zoom-out",
    ),
    (
        &["germin", "crec", "grow", "cresc", "pouss", "wachs"],
        "concat.in-zoom-1",
        "concat.text-in-grow",
    ),
    (
        &[
            "zoom",
            "acerc",
            "ampli",
            "agrand",
            "aproxim",
            "rapproch",
            "vergröß",
            "ingrand",
        ],
        "concat.in-zoom-1",
        "concat.text-in-zoom-in",
    ),
    (
        &[
            "slide",
            "desliz",
            "glisse",
            "gleit",
            "scorr",
            "aparición",
            "aparicion",
            "lateral",
            "showing",
        ],
        "",
        "",
    ),
    (
        &[
            "fade", "fund", "desvanec", "esvaec", "fondu", "einblend", "dissolv", "básica",
            "basica", "basic",
        ],
        "concat.in-fade-in",
        "concat.text-in-fade-in",
    ),
];

const ANIM_OUT: &[AnimRule] = &[
    (
        &["typewriter", "máquina", "maquina", "escrib", "type", "tipo"],
        "concat.text-out-typewriter",
        "concat.text-out-typewriter",
    ),
    (
        &["bounce", "rebot", "salt", "rebond", "rimbalz"],
        "concat.text-out-bounce-out",
        "concat.text-out-bounce-out",
    ),
    (
        &["flip", "volte", "volt", "retourn", "capovol"],
        "concat.out-flip",
        "concat.text-out-flipping",
    ),
    (
        &[
            "whirl",
            "remolino",
            "espiral",
            "spiral",
            "tourbillon",
            "wirbel",
        ],
        "concat.out-whirl",
        "concat.text-out-spin-out-1",
    ),
    (
        &["spin", "rot", "gir", "tourn", "ruot"],
        "concat.out-rotate",
        "concat.text-out-spin-out-1",
    ),
    (
        &[
            "blur",
            "desenfo",
            "borros",
            "desfoc",
            "flou",
            "unschärf",
            "sfoc",
        ],
        "concat.out-blur",
        "concat.text-out-blur",
    ),
    (
        &["wipe", "barrido", "cortin", "balay", "wisch"],
        "concat.out-screen-wipe",
        "concat.text-out-wipe-right",
    ),
    (
        &[
            "alej", "zoom out", "afast", "éloign", "allontan", "shrink", "reduc",
        ],
        "concat.out-zoom-out",
        "concat.text-out-zoom-out",
    ),
    (
        &["zoom", "acerc", "ampli", "agrand"],
        "concat.out-zoom-in",
        "concat.text-out-zoom-in",
    ),
    (
        &["slide", "desliz", "glisse", "gleit", "scorr", "lateral"],
        "",
        "",
    ),
    (
        &[
            "fade", "fund", "desvanec", "desapar", "esvaec", "fondu", "ausblend", "dissolv",
        ],
        "concat.out-fade-out",
        "concat.text-out-fade-out",
    ),
];

const ANIM_LOOP: &[AnimRule] = &[
    (
        &["wave", "ondul", "onda", "vague", "welle"],
        "concat.text-loop-wave",
        "concat.text-loop-wave",
    ),
    (
        &["shake", "sacud", "tembl", "trem", "secou", "wackel"],
        "concat.text-loop-shake",
        "concat.text-loop-shake",
    ),
    (
        &["swing", "balanc", "column", "schaukel", "oscill"],
        "concat.text-loop-swing",
        "concat.text-loop-swing",
    ),
    (
        &["rot", "gir", "spin", "tourn"],
        "concat.text-loop-rotate",
        "concat.text-loop-rotate",
    ),
    (
        &["jump", "salt", "saut", "sprung", "bounce", "rebot"],
        "concat.text-loop-jump",
        "concat.text-loop-jump",
    ),
    (
        &["flash", "parpad", "pisca", "clignot", "blink"],
        "concat.text-loop-flash",
        "concat.text-loop-flash",
    ),
    (
        &["scroll", "desplaz", "rolar", "défil"],
        "concat.text-loop-scrolling",
        "concat.text-loop-scrolling",
    ),
];

/// The slide In or Out a name means, by the way it says it moves.
fn slide(slot: Slot, text: bool, name: &str) -> (&'static str, &'static str) {
    let dir = direction(name).unwrap_or("direction=1");
    let pick = |left, right, up, down| match dir {
        "direction=0" => left,
        "direction=2" => up,
        "direction=3" => down,
        _ => right,
    };
    let id = match (slot, text) {
        (Slot::In, false) => pick(
            "concat.in-slide-left",
            "concat.in-slide-right",
            "concat.in-slide-up",
            "concat.in-slide-down",
        ),
        (Slot::In, true) => pick(
            "concat.text-in-slide-left",
            "concat.text-in-slide-right",
            "concat.text-in-slide-up",
            "concat.text-in-slide-down",
        ),
        (_, false) => pick(
            "concat.out-slide-left",
            "concat.out-slide-right",
            "concat.out-slide-up",
            "concat.out-slide-down",
        ),
        (_, true) => pick(
            "concat.text-out-slide-left",
            "concat.text-out-slide-right",
            "concat.text-out-slide-up",
            "concat.text-out-slide-down",
        ),
    };
    (id, "")
}

/// The package and knobs that stand in for an item called `name`, or None
/// when no rule's word is in it.
pub(super) fn guess(want: Want, name: &str) -> Option<(&'static str, &'static str)> {
    let name = name.to_lowercase();
    match want {
        Want::Transition => {
            let (_, target) = TRANSITIONS.iter().find(|(words, _)| any(&name, words))?;
            let (id, knobs) = target.split_once('|').unwrap_or((target, ""));
            // A move that names its way takes it.
            let knobs = if knobs.is_empty()
                && matches!(id, "concat.slide" | "concat.push" | "concat.linear-wipe")
            {
                direction(&name).unwrap_or("")
            } else {
                knobs
            };
            Some((id, knobs))
        }
        Want::Effect => {
            let (_, id) = EFFECTS.iter().find(|(words, _)| any(&name, words))?;
            Some((id, ""))
        }
        Want::Animation { slot, text } => {
            let rules = match slot {
                Slot::In => ANIM_IN,
                Slot::Out => ANIM_OUT,
                Slot::Loop => ANIM_LOOP,
                Slot::Combo => return None,
            };
            let (_, picture, title) = rules.iter().find(|(words, _, _)| any(&name, words))?;
            if picture.is_empty() {
                return Some(slide(slot, text, &name));
            }
            Some((if text { title } else { picture }, ""))
        }
    }
}

/// What stands in when nothing matched: the plainest thing of its kind,
/// so the edit keeps its shape.
pub(super) fn fallback(want: Want) -> Option<&'static str> {
    match want {
        Want::Transition => Some("concat.dissolve"),
        Want::Effect => None,
        Want::Animation { slot, text } => Some(match (slot, text) {
            (Slot::In, false) => "concat.in-fade-in",
            (Slot::In, true) => "concat.text-in-fade-in",
            (Slot::Out, false) => "concat.out-fade-out",
            (Slot::Out, true) => "concat.text-out-fade-out",
            (Slot::Combo, _) => "concat.combo-zoom-1",
            (Slot::Loop, _) => "concat.text-loop-pulse",
        }),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn names_in_other_languages_find_their_stand_ins() {
        assert_eq!(
            guess(Want::Transition, "Deslizar hacia la izquierda"),
            Some(("concat.slide", "direction=0"))
        );
        assert_eq!(
            guess(Want::Transition, "Destello II"),
            Some(("concat.flash-transition", ""))
        );
        assert_eq!(
            guess(Want::Transition, "Alejar"),
            Some(("concat.zoom-transition", "direction=1"))
        );
        assert_eq!(
            guess(
                Want::Animation {
                    slot: Slot::In,
                    text: true
                },
                "Aparición hacia abajo"
            ),
            Some(("concat.text-in-slide-down", ""))
        );
        assert_eq!(
            guess(
                Want::Animation {
                    slot: Slot::Out,
                    text: false
                },
                "Desaparición progresiva"
            ),
            Some(("concat.out-fade-out", ""))
        );
        assert_eq!(
            guess(Want::Effect, "Lentes de zoom"),
            Some(("concat.zoom-lens", ""))
        );
        assert_eq!(guess(Want::Effect, "Something new"), None);
    }

    #[test]
    fn every_stand_in_is_a_package() {
        let catalogue = concat_effects::Catalogue::builtin();
        let mut ids: Vec<&str> = TRANSITIONS
            .iter()
            .map(|(_, target)| target.split('|').next().unwrap_or(target))
            .chain(EFFECTS.iter().map(|(_, id)| *id))
            .collect();
        for rules in [ANIM_IN, ANIM_OUT, ANIM_LOOP] {
            ids.extend(
                rules
                    .iter()
                    .flat_map(|(_, a, b)| [*a, *b])
                    .filter(|id| !id.is_empty()),
            );
        }
        for slot in [Slot::In, Slot::Out] {
            for text in [false, true] {
                for name in ["left", "right", "up", "down"] {
                    ids.push(slide(slot, text, name).0);
                }
            }
        }
        for want in [
            Want::Transition,
            Want::Animation {
                slot: Slot::In,
                text: false,
            },
            Want::Animation {
                slot: Slot::Loop,
                text: true,
            },
            Want::Animation {
                slot: Slot::Combo,
                text: false,
            },
        ] {
            ids.extend(fallback(want));
        }
        let missing: Vec<&&str> = ids
            .iter()
            .filter(|id| catalogue.get(id).is_none())
            .collect();
        assert!(missing.is_empty(), "{missing:?}");
    }
}

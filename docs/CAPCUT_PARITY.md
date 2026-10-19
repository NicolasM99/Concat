# CapCut parity

What of CapCut's catalogue this build of Concat carries, and the package that carries it.
The list is CapCut's own, as VectCutAPI's `pyJianYingDraft` metadata records it (`capcut_*_meta.py`).
Everything here is drawn by Concat's own GPU shaders and FFmpeg chains: no CapCut asset is copied.

## Summary

| Catalogue | Covered | CapCut |
|---|---|---|
| Transitions | 101 | 101 |
| Video effects | 253 | 253 |
| Body effects | 81 | 92 |
| Animations: In | 43 | 43 |
| Animations: Out | 23 | 23 |
| Animations: Combo | 108 | 108 |
| Animations: Text In | 76 | 76 |
| Animations: Text Out | 68 | 68 |
| Animations: Text Loop | 53 | 53 |
| Voice effects | 28 | 29 |
| Masks | 6 | 9 |

CapCut's filter library (its colour looks) is not in VectCutAPI's CapCut metadata, so it is not
listed here; Concat ships its own looks on the Filters page.

## How it is built

- Transitions and effects are packages under `src/crates/concat-effects/packages`, a folder each:
  `effect.toml`, an `effect.wgsl` shader and `fixtures.toml` probes pinned on a GPU.
- Animations are a new package kind, `animation`: an `[animation]` table whose motion is
  expressions of `t` and whose optional look is another package's knobs. See
  `src/crates/concat-effects/src/animation.rs`. A clip stores `{ id, duration }` per slot in
  `animations` (`in`, `out`, `combo`, `loop`), set from the library's Animations page or the API's
  `updateClip`.
- The packages were generated from the specs in `scripts/capcut-parity/`; see its README.

## Transitions

| CapCut | Concat package | Note |
|---|---|---|
| Montage Snippets | `concat.montage-snippets` |  |
| Mix | `concat.dissolve` |  |
| Black Fade | `concat.fade-black` |  |
| Then and Now | `concat.then-and-now` |  |
| White Flash | `concat.fade-white` |  |
| Dissolve | `concat.dissolve` |  |
| Gradient Wipe | `concat.gradient-wipe` |  |
| Dissolve II | `concat.dissolve-ii` |  |
| Dissolve III | `concat.dissolve-iii` |  |
| Black smoke | `concat.black-smoke` |  |
| White smoke | `concat.white-smoke` |  |
| B&W Flash | `concat.bw-flash` |  |
| Rainbow Warp | `concat.rainbow-warp` |  |
| RGB Glitch | `concat.rgb-glitch` |  |
| Rainbow Filter | `concat.rainbow-filter` |  |
| Urban Glitch | `concat.urban-glitch` |  |
| Camera Glow | `concat.camera-glow` |  |
| Light Sweep II | `concat.light-sweep` |  |
| Flash | `concat.flash-transition` |  |
| Light Beam | `concat.light-beam` |  |
| Burn | `concat.film-burn` |  |
| Blanch | `concat.blanch` |  |
| Fold Over | `concat.fold-over` |  |
| Bottom Left II | `concat.bottom-left` |  |
| Vertical Blur II | `concat.vertical-blur-ii` |  |
| Inhale | `concat.inhale` |  |
| Shake 3 | `concat.shake-transition` |  |
| Rotate CW II | `concat.rotate-cw-ii` |  |
| Rotate CCW II | `concat.rotate-ccw-ii` |  |
| Pull in | `concat.zoom-transition` |  |
| Pull Out | `concat.zoom-transition` |  |
| CW Swirl | `concat.swirl` |  |
| Right | `concat.push` |  |
| Anti-CW Swirl | `concat.anti-cw-swirl` |  |
| Transform Shimmer | `concat.transform-shimmer` |  |
| Twinkle Zoom | `concat.twinkle-zoom` |  |
| Horizontal Blur | `concat.horizontal-blur` |  |
| Radial Blur | `concat.zoom-blur-transition` |  |
| Blurred Highlight | `concat.blurred-highlight` |  |
| Vertical Blur | `concat.vertical-blur-transition` |  |
| Blur | `concat.blur-dissolve` |  |
| Woosh | `concat.whip-pan` |  |
| Particles | `concat.particles` |  |
| Mosaic | `concat.mosaic-transition` |  |
| Blink | `concat.blink-transition` |  |
| Flip II | `concat.flip-ii` |  |
| Flip | `concat.flip` |  |
| Left | `concat.push` |  |
| Up | `concat.push` |  |
| Wipe Right | `concat.linear-wipe` |  |
| Open Horizontally | `concat.open-horizontally` |  |
| Slide | `concat.slide` |  |
| Wipe Up | `concat.linear-wipe` |  |
| Wipe Left | `concat.linear-wipe` |  |
| Open Vertically | `concat.open-vertically` |  |
| Curling Wave | `concat.curling-wave` |  |
| Flame | `concat.flame` |  |
| Cartoon Swirl | `concat.cartoon-swirl` |  |
| Blue Lines | `concat.blue-lines` |  |
| Recorder | `concat.recorder` |  |
| Like | `concat.like-transition` |  |
| Little Devil | `concat.little-devil` |  |
| Super Like | `concat.super-like-transition` |  |
| Lightning | `concat.lightning-transition` |  |
| Snow | `concat.snow-transition` |  |
| White Ink | `concat.white-ink` |  |
| Cloud | `concat.cloud` |  |
| Wave Right | `concat.wave-right` |  |
| Wave Left | `concat.wave-left` |  |
| Dots Right | `concat.dots-right` |  |
| Circular Slices II | `concat.circular-slices-ii` |  |
| Split III | `concat.split-iii` |  |
| Horizontal Slice | `concat.horizontal-slice` |  |
| Diagonal Slices | `concat.diagonal-slices` |  |
| Split | `concat.split` |  |
| Vertical Slices | `concat.vertical-slices` |  |
| Split IV | `concat.split-iv` |  |
| Vintage Screening | `concat.vintage-screening` |  |
| Cube | `concat.cube` |  |
| Switch | `concat.switch` |  |
| Open | `concat.open` |  |
| Page Turning | `concat.page-turning` |  |
| Clock wipe | `concat.clock-wipe` |  |
| Windmill | `concat.windmill` |  |
| Color Glitch | `concat.color-glitch` |  |
| Strobe | `concat.strobe-transition` |  |
| Blocks | `concat.blocks` |  |
| Glitch | `concat.glitch-transition` |  |
| Horizontal Lines | `concat.horizontal-lines` |  |
| Cutout Flip | `concat.cutout-flip` |  |
| Color Swirl | `concat.color-swirl` |  |
| Shutter II | `concat.shutter-ii` |  |
| Stretch ll | `concat.stretch-ii` |  |
| Stretch | `concat.stretch` |  |
| Shutter | `concat.shutter` |  |
| Whirlpool | `concat.whirlpool` |  |
| Distortion | `concat.distortion` |  |
| Axis Rotation | `concat.axis-rotation` |  |
| Stretch Right | `concat.stretch-right` |  |
| Stretch Left | `concat.stretch-left` |  |
| Squeeze | `concat.squeeze` |  |

## Video effects

| CapCut | Concat package | Note |
|---|---|---|
| Blur | `concat.blur` |  |
| Fade In | `concat.fade-in` |  |
| Heart Kisses | `concat.heart-kisses` |  |
| Explosion | `concat.explosion` |  |
| Fireworks 2 | `concat.fireworks-2` |  |
| Fade Out | `concat.fade-out` |  |
| The End | `concat.the-end` |  |
| Zoom Lens | `concat.zoom-lens` |  |
| Meteor | `concat.meteor` |  |
| Horizontal Open | `concat.horizontal-open` |  |
| Spectrum Scan | `concat.spectrum-scan` |  |
| By the Fireplace | `concat.by-the-fireplace` |  |
| Rolling Film | `concat.rolling-film` |  |
| Landscape Close | `concat.landscape-close` |  |
| Flipped | `concat.flipped` |  |
| Horizontal Close | `concat.horizontal-close` |  |
| Astral | `concat.astral` |  |
| Edge Glow | `concat.edge-glow` |  |
| Shake | `concat.shake` |  |
| Camera Focus | `concat.camera-focus` |  |
| Collision Sparks | `concat.collision-sparks` |  |
| Diamond Zoom | `concat.diamond-zoom` |  |
| Disco Ball 1 | `concat.disco-ball` |  |
| Mini Zoom | `concat.mini-zoom` |  |
| Blu-ray Scanning | `concat.blu-ray-scanning` |  |
| Portrait Open | `concat.portrait-open` |  |
| Girl's Secrets | `concat.girls-secrets` |  |
| Color Phosphor | `concat.color-phosphor` |  |
| Rebound Swing | `concat.rebound-swing` |  |
| Camera Shake | `concat.camera-shake` |  |
| Pulse | `concat.pulse` |  |
| Vertical Open | `concat.vertical-open` |  |
| Star | `concat.star` |  |
| Heart Disco | `concat.heart-disco` |  |
| Butterfly Dream | `concat.butterfly-dream` |  |
| Camcorder | `concat.camcorder` |  |
| TV On | `concat.tv-on` |  |
| Vignette | `concat.vignette` |  |
| Heartbeat | `concat.heartbeat` |  |
| Blurry Focus | `concat.blurry-focus` |  |
| Noise 2 | `concat.noise-2` |  |
| Leak 1 | `concat.leak-1` |  |
| Black Noise | `concat.black-noise` |  |
| Old TV 2 | `concat.old-tv-2` |  |
| Fuzzy | `concat.fuzzy` |  |
| Soft | `concat.soft` |  |
| TV Off | `concat.tv-off` |  |
| Lightning Crack | `concat.lightning-crack` |  |
| Shake 3 | `concat.shake-3` |  |
| Gleam | `concat.gleam` |  |
| Butterflies | `concat.butterflies` |  |
| Ripple | `concat.ripple` |  |
| Electro Border | `concat.electro-border` |  |
| Tri-layer Mirror | `concat.tri-layer-mirror` |  |
| Radiating Love | `concat.radiating-love` |  |
| White Flash | `concat.white-flash` |  |
| Lightning | `concat.lightning-fx` |  |
| Motion Blur | `concat.motion-blur` |  |
| Spooky Camera | `concat.spooky-camera` |  |
| Frosted Quality | `concat.frosted-quality` |  |
| Leak 2 | `concat.leak-2` |  |
| Vertical Close | `concat.vertical-close` |  |
| Rainbow Neon | `concat.rainbow-neon` |  |
| Sharpen Edges | `concat.sharpen-edges` |  |
| Chromatic | `concat.chromatic` |  |
| Dizzy | `concat.dizzy` |  |
| Swing | `concat.swing` |  |
| Halo 2 | `concat.halo-2` |  |
| Vertical Blur | `concat.vertical-blur` |  |
| Black Flash | `concat.black-flash` |  |
| Wipe Board | `concat.wipe-board` |  |
| Butterfly Color | `concat.butterfly-color` |  |
| Camera Focus 2 | `concat.camera-focus-2` |  |
| To Color | `concat.to-color` |  |
| Flicker | `concat.flicker` |  |
| Pixel Blur | `concat.pixel-blur` |  |
| TV Colored Lines | `concat.tv-colored-lines` |  |
| Shake 2 | `concat.shake-2` |  |
| Wobbly Black | `concat.wobbly-black` |  |
| Strobe | `concat.strobe` |  |
| Low Exposure | `concat.low-exposure` |  |
| White Out | `concat.white-out` |  |
| Shockwave | `concat.shockwave` |  |
| Black Flash 2 | `concat.black-flash-2` |  |
| Throb | `concat.throb` |  |
| Colorful | `concat.colorful` |  |
| Club Mood | `concat.club-mood` |  |
| Neon Outline | `concat.neon-outline` |  |
| RGB Border | `concat.rgb-border` |  |
| Disco | `concat.disco` |  |
| Delay | `concat.delay` |  |
| Neon Swing | `concat.neon-swing` |  |
| Shadow | `concat.shadow-ghost` |  |
| Color Flame | `concat.color-flame` |  |
| Rainbow Haze | `concat.rainbow-haze` |  |
| Unreal | `concat.unreal` |  |
| Flashing Frame | `concat.flashing-frame` |  |
| Trippy | `concat.trippy` |  |
| Orange Negative | `concat.orange-negative` |  |
| White Border | `concat.white-border` |  |
| Color Negative | `concat.color-negative` |  |
| Stuck Frame | `concat.stuck-frame` |  |
| Magnifying Glass | `concat.magnifying-glass` |  |
| Wide Angle | `concat.wide-angle` |  |
| Heart Magnifier | `concat.heart-magnifier` |  |
| Chrome Blur | `concat.chrome-blur` |  |
| Fisheye 4 | `concat.fisheye-4` |  |
| Cinema | `concat.cinema` |  |
| Rotary Focus | `concat.rotary-focus` |  |
| Blink | `concat.blink` |  |
| Chromatic Quirk | `concat.chromatic-quirk` |  |
| Backlit Focus | `concat.backlit-focus` |  |
| Hazy | `concat.hazy` |  |
| Blackout | `concat.blackout` |  |
| Mirror | `concat.mirror-fx` |  |
| Fisheye | `concat.fisheye` |  |
| Fisheye 2 | `concat.fisheye-2` |  |
| VX1000 | `concat.vx1000` |  |
| Binoculars | `concat.binoculars` |  |
| Tree Shade | `concat.tree-shade` |  |
| Angel | `concat.angel` |  |
| Sunset 4 | `concat.sunset-4` |  |
| Spark | `concat.spark` |  |
| Spark 2 | `concat.spark-2` |  |
| Pool Reflection | `concat.pool-reflection` |  |
| Magic | `concat.magic` |  |
| Blinds 2 | `concat.blinds-2` |  |
| Negative Strobe | `concat.negative-strobe` |  |
| Halo | `concat.halo` |  |
| Rainbow Sparkle | `concat.rainbow-sparkle` |  |
| Tree Shade 2 | `concat.tree-shade-2` |  |
| Light leak | `concat.light-leak-overlay` |  |
| Window | `concat.window-shade` |  |
| Flash | `concat.flash` |  |
| Blinds | `concat.blinds-shade` |  |
| Flame Frame | `concat.flame-frame` |  |
| Cold Lab | `concat.cold-lab` |  |
| Glowburst | `concat.glowburst` |  |
| Electro Heart | `concat.electro-heart` |  |
| Develop | `concat.develop` |  |
| Train Window | `concat.train-window` |  |
| Film Frame | `concat.film-frame` |  |
| Dark Night | `concat.dark-night` |  |
| Noise 1 | `concat.noise-1` |  |
| Retro Film | `concat.retro-film` |  |
| Film Frame 2 | `concat.film-frame-2` |  |
| 1998 | `concat.nineteen-98` |  |
| Reversal Film | `concat.reversal-film` |  |
| Film 2 | `concat.film-2` |  |
| Glitch | `concat.glitch` |  |
| Level Glitch 2 | `concat.level-glitch-2` |  |
| Color Glitch | `concat.color-glitch-fx` |  |
| Chromo-zoom | `concat.chromo-zoom` |  |
| X-Signal | `concat.x-signal` |  |
| 70's | `concat.seventies` |  |
| Distort | `concat.distort` |  |
| Invisible Person | `concat.invisible-person` |  |
| Color Glitch 2 | `concat.color-glitch-2` |  |
| Bad TV | `concat.bad-tv` |  |
| Snow Glitch | `concat.snow-glitch` |  |
| Ethereal | `concat.ethereal` |  |
| Level Glitch | `concat.level-glitch` |  |
| Edgy | `concat.edgy` |  |
| Ripples | `concat.ripples` |  |
| Screen Pulse | `concat.screen-pulse` |  |
| Spinning Space | `concat.spinning-space` |  |
| Distorted | `concat.distorted-mirror` |  |
| Gentle Ripples | `concat.gentle-ripples` |  |
| Jittered Ripples 3 | `concat.jittered-ripples-3` |  |
| White Diffusion | `concat.white-diffusion` |  |
| Rippling | `concat.rippling` |  |
| Jittered Ripples | `concat.jittered-ripples` |  |
| Jittered Ripples 2 | `concat.jittered-ripples-2` |  |
| Vortex Setting | `concat.vortex` |  |
| Firefly | `concat.firefly` |  |
| Sun | `concat.sun` |  |
| Cherry Blossom | `concat.cherry-blossom` |  |
| Rain | `concat.rainfall` |  |
| Mist | `concat.mist` |  |
| Soft Rose | `concat.soft-rose` |  |
| Purple Mist | `concat.purple-mist` |  |
| Feathers | `concat.feathers` |  |
| Starry | `concat.starry` |  |
| Pink Hearts | `concat.pink-hearts` |  |
| Luminance | `concat.luminance-fx` |  |
| Fire | `concat.fire` |  |
| Camcorder 3 | `concat.camcorder-3` |  |
| Camcorder 2 | `concat.camcorder-2` |  |
| B&W VHS | `concat.bw-vhs` |  |
| Frame 1 | `concat.frame-1` |  |
| Photo Frame | `concat.photo-frame` |  |
| TV Lines | `concat.tv-lines` |  |
| Retro Cam | `concat.retro-cam` |  |
| Graphic 3 | `concat.graphic-3` |  |
| Noise | `concat.noise-fx` |  |
| White Sprockets | `concat.white-sprockets` |  |
| Insta | `concat.insta` |  |
| Jitter | `concat.jitter` |  |
| Constellation | `concat.constellation` |  |
| Mini stars II | `concat.mini-stars-ii` |  |
| Mini Stars | `concat.mini-stars` |  |
| Star Rain | `concat.star-rain` |  |
| Daily | `concat.daily` |  |
| Star Rain 2 | `concat.star-rain-2` |  |
| Color Diamond | `concat.color-diamond` |  |
| Daily 2 | `concat.daily-2` |  |
| Daily 4 | `concat.daily-4` |  |
| Polychromatic | `concat.polychromatic` |  |
| Milky Way 2 | `concat.milky-way-2` |  |
| Iridescent | `concat.iridescent` |  |
| Torn Frames | `concat.torn-frames` |  |
| Folds 4 | `concat.folds-4` |  |
| Blue Mosaic | `concat.blue-mosaic` |  |
| Dot Silkscreen | `concat.dot-silkscreen` |  |
| Folds 5 | `concat.folds-5` |  |
| Paper Tear | `concat.paper-tear` |  |
| Painting | `concat.painting` |  |
| Striped Glass | `concat.striped-glass` |  |
| Folds 2 | `concat.folds-2` |  |
| Grain | `concat.grain` |  |
| Old | `concat.old` |  |
| Folds | `concat.folds` |  |
| Energy | `concat.energy` |  |
| Neon | `concat.neon-frame` |  |
| Fire Edges | `concat.fire-edges` |  |
| Warning | `concat.warning` |  |
| B&W Sketch | `concat.bw-sketch` |  |
| Quick Math | `concat.quick-math` |  |
| Flames | `concat.flames` |  |
| Question Marks | `concat.question-marks` |  |
| Splice | `concat.splice` |  |
| Mosaic | `concat.mosaic` |  |
| Cartoon Border | `concat.cartoon-border` |  |
| Flames 2 | `concat.flames-2` |  |
| Super Like | `concat.super-like` |  |
| Oh My God | `concat.oh-my-god` |  |
| Dual Screens | `concat.dual-screens` |  |
| Four Screens | `concat.four-screens` |  |
| Three Screens | `concat.three-screens` |  |
| Split Screen | `concat.split-screen` |  |
| Six Screens | `concat.six-screens` |  |
| Circuit | `concat.circuit` |  |
| Nine Screens | `concat.nine-screens` |  |
| Alt. B&W | `concat.alt-bw` |  |
| Snowflakes | `concat.snowflakes` |  |
| Gold Sparkles | `concat.gold-sparkles` |  |
| Xmas Stars | `concat.xmas-stars` |  |
| Snowfall | `concat.snowfall` |  |
| Gold Sequins | `concat.gold-sequins` |  |
| Confetti II | `concat.confetti-ii` |  |
| Sparkle Spiral | `concat.sparkle-spiral` |  |
| Gold Dust | `concat.gold-dust` |  |
| Wonderland | `concat.wonderland` |  |

## Body effects

| CapCut | Concat package | Note |
|---|---|---|
| Woman 4 | - | an AI face or gender transform |
| Face Mosaic | `concat.face-mosaic` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Flipped | `concat.flipped` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Embarrassed Face | `concat.embarrassed-face` | approximated: drawn around the picture's outlines or a point placed on the subject |
| In My Heart | `concat.in-my-heart` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Lightning Eyes | `concat.lightning-eyes` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Sad | `concat.sad` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Totem Flames | `concat.totem-flames` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Like | `concat.like-burst` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Big Head | `concat.big-head` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Electric Storm | `concat.electric-storm` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Heart Flames | `concat.heart-flames` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Electro Border | `concat.electro-border` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Club Hearts | `concat.club-hearts` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Electric Shock | `concat.electric-shock` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Musical Notes 2 | `concat.musical-notes-2` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Hurricane | `concat.hurricane` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Woman 3 | - | an AI face or gender transform |
| Cool | `concat.cool-shades` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Lovestruck | `concat.lovestruck` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Heart Background | `concat.heart-background` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Star Trails | `concat.star-trails` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Cutout Poster | `concat.cutout-poster` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Gorilla Face | - | an AR face mask |
| Big Mouth | `concat.big-mouth` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Tyndall Effect | `concat.tyndall-effect` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Musical Notes | `concat.musical-notes` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Crackling | `concat.crackling` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Man 4 | - | an AI face or gender transform |
| Shape Trails 2 | `concat.shape-trails-2` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Revolving Text | - | needs text set on the effect |
| Streamer Stroke | `concat.streamer-stroke` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Hellfire | `concat.hellfire` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Man 3 | - | an AI face or gender transform |
| Struck | `concat.struck` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Halo 2 | `concat.halo-2` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Chroma Diffusion | `concat.chroma-diffusion` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Aura | `concat.aura` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Bright Idea | `concat.bright-idea` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Thermal Aura | `concat.thermal-aura` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Radiate Bolts | `concat.radiate-bolts` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Mechanical | `concat.mechanical` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Dopelgangers | `concat.dopelgangers` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Phantom | `concat.phantom` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Lightning Bound | `concat.lightning-bound` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Dot Shadow | `concat.dot-shadow` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Butterfly Wings | `concat.butterfly-wings` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Gas Flow | `concat.gas-flow` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Distorted Whirl | `concat.distorted-whirl` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Eye Reflection | `concat.eye-reflection` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Color Fringe | `concat.color-fringe` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Flame Eyes | `concat.flame-eyes` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Fluoro Flash | `concat.fluoro-flash` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Scan | `concat.scan` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Ghost | `concat.ghost` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Apparate 1 | `concat.apparate` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Phantom Face | `concat.phantom-face` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Pop-Out | - | needs the subject cut out of the frame |
| Starlight | `concat.starlight` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Bubbles 2 | `concat.bubbles` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Flame Wings 1 | `concat.flame-wings-1` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Revolving Flames | `concat.revolving-flames` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Flame Trails | `concat.flame-trails` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Technology 2 | `concat.technology-2` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Firework | `concat.firework-burst` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Halo | `concat.halo` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Gas Waves | `concat.gas-waves` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Sound Wave | `concat.sound-wave` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Geometric Lasers | `concat.geometric-lasers` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Shape Trails | `concat.shape-trails` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Flame Wings 2 | `concat.flame-wings-2` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Consciousness | `concat.consciousness` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Looping Arrows | `concat.looping-arrows` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Scan 2 | `concat.scan-2` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Flame Outline | `concat.flame-outline` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Thermal Aura 2 | `concat.thermal-aura-2` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Frame Scatter 2 | `concat.frame-scatter-2` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Frame Scatter | `concat.frame-scatter` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Sinking | `concat.sinking` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Axis Rotation | `concat.axis-rotation-fx` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Light Trails | `concat.light-trails` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Speed Streaks | `concat.speed-streaks` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Face Glitch | `concat.face-glitch` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Lightning | `concat.lightning-fx` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Neon Doodle | `concat.neon-doodle` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Heart Lenses | `concat.heart-lenses` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Loving Gaze | `concat.loving-gaze` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Neon Variation | `concat.neon-variation` | approximated: drawn around the picture's outlines or a point placed on the subject |
| Woman 2 | - | an AI face or gender transform |
| Woman | - | an AI face or gender transform |
| Man | - | an AI face or gender transform |
| Man 2 | - | an AI face or gender transform |

## Animations: In

| CapCut | Concat package | Note |
|---|---|---|
| Fade In | `concat.in-fade-in` |  |
| Zoom 1 | `concat.in-zoom-1` |  |
| Rock Vertically | `concat.in-rock-vertically` |  |
| Slide Down | `concat.in-slide-down` |  |
| Slide Up | `concat.in-slide-up` |  |
| Slide Right | `concat.in-slide-right` |  |
| Slide Left | `concat.in-slide-left` |  |
| Rotate | `concat.in-rotate` |  |
| Flame Risen | `concat.in-flame-risen` |  |
| Rotation Opening | `concat.in-rotation-opening` |  |
| Retro Fadein 2 | `concat.in-retro-fadein-2` |  |
| Retro Fadein | `concat.in-retro-fadein` |  |
| Screen Wipe | `concat.in-screen-wipe` |  |
| RGB Scanlines | `concat.in-rgb-scanlines` |  |
| Zoom 2 | `concat.in-zoom-2` |  |
| Zoom Out | `concat.in-zoom-out` |  |
| Zoom In | `concat.in-zoom-in` |  |
| Shake 3 | `concat.in-shake-3` |  |
| CRT Bands | `concat.in-crt-bands` |  |
| Vibrating Panels | `concat.in-vibrating-panels` |  |
| Swing Top Right | `concat.in-swing-top-right` |  |
| Anime Frame | `concat.in-anime-frame` |  |
| Rock Horizontally | `concat.in-rock-horizontally` |  |
| Gray Mask | `concat.in-gray-mask` |  |
| Shake 1 | `concat.in-shake-1` |  |
| Spin Up 2 | `concat.in-spin-up-2` |  |
| Whirl | `concat.in-whirl` |  |
| Mini Zoom | `concat.in-mini-zoom` |  |
| Spin Up 1 | `concat.in-spin-up-1` |  |
| Swing Bottom | `concat.in-swing-bottom` |  |
| Swing Right | `concat.in-swing-right` |  |
| Swing Bottom Left | `concat.in-swing-bottom-left` |  |
| Flip | `concat.in-flip` |  |
| Shake 2 | `concat.in-shake-2` |  |
| Blinds | `concat.in-blinds` |  |
| Swing Bottom Right | `concat.in-swing-bottom-right` |  |
| Puzzle | `concat.in-puzzle` |  |
| Swing Top Left | `concat.in-swing-top-left` |  |
| Shake Down | `concat.in-shake-down` |  |
| Swing | `concat.in-swing` |  |
| Wiper | `concat.in-wiper` |  |
| Roll Right | `concat.in-roll-right` |  |
| Spin Left | `concat.in-spin-left` |  |

## Animations: Out

| CapCut | Concat package | Note |
|---|---|---|
| Fade Out | `concat.out-fade-out` |  |
| RGB Scanlines | `concat.out-rgb-scanlines` |  |
| Blurred Fadein | `concat.out-blurred-fadein` |  |
| Slide Down | `concat.out-slide-down` |  |
| Slide Up | `concat.out-slide-up` |  |
| Slide Right | `concat.out-slide-right` |  |
| Slide Left | `concat.out-slide-left` |  |
| Blurred Fadein 1 | `concat.out-blurred-fadein-1` |  |
| Zoom In | `concat.out-zoom-in` |  |
| CRT Bands | `concat.out-crt-bands` |  |
| Flame Risen | `concat.out-flame-risen` |  |
| Screen Wipe | `concat.out-screen-wipe` |  |
| Rotation Closing | `concat.out-rotation-closing` |  |
| Rotate | `concat.out-rotate` |  |
| Anime Frame | `concat.out-anime-frame` |  |
| Zoom Out | `concat.out-zoom-out` |  |
| Rotate Out 1 | `concat.out-rotate-out-1` |  |
| Mini Zoom | `concat.out-mini-zoom` |  |
| Gray Mask | `concat.out-gray-mask` |  |
| Whirl | `concat.out-whirl` |  |
| Vibrating Panels | `concat.out-vibrating-panels` |  |
| Rotate Out 2 | `concat.out-rotate-out-2` |  |
| Flip | `concat.out-flip` |  |

## Animations: Combo

| CapCut | Concat package | Note |
|---|---|---|
| Zoom 1 | `concat.combo-zoom-1` |  |
| Stretch and distort | `concat.combo-stretch-and-distort` |  |
| Bounce 1 | `concat.combo-bounce-1` |  |
| Sway Out | `concat.combo-sway-out` |  |
| 3D card 2 | `concat.combo-3d-card-2` |  |
| Slide and wave | `concat.combo-slide-and-wave` |  |
| Pendulum 1 | `concat.combo-pendulum-1` |  |
| Wobble | `concat.combo-wobble` |  |
| Wave and slide | `concat.combo-wave-and-slide` |  |
| Enlarge and bounce | `concat.combo-enlarge-and-bounce` |  |
| Distort and stretch | `concat.combo-distort-and-stretch` |  |
| Pendulum 2 | `concat.combo-pendulum-2` |  |
| Zoom 2 | `concat.combo-zoom-2` |  |
| Sway In | `concat.combo-sway-in` |  |
| BendZoom | `concat.combo-bendzoom` |  |
| Bounce 2 | `concat.combo-bounce-2` |  |
| Spin Rise | `concat.combo-spin-rise` |  |
| Train 2 | `concat.combo-train-2` |  |
| Spin | `concat.combo-spin` |  |
| Shrink and bounce | `concat.combo-shrink-and-bounce` |  |
| Smartphone 1 | `concat.combo-smartphone-1` |  |
| Distort Right | `concat.combo-distort-right` |  |
| Trisect 2 | `concat.combo-trisect-2` |  |
| Train 4 | `concat.combo-train-4` |  |
| Fall Spin | `concat.combo-fall-spin` |  |
| 3D card 1 | `concat.combo-3d-card-1` |  |
| Spinning top 2 | `concat.combo-spinning-top-2` |  |
| Fall Right | `concat.combo-fall-right` |  |
| Pan Right | `concat.combo-pan-right` |  |
| Distort Left | `concat.combo-distort-left` |  |
| Slip and slide 2 | `concat.combo-slip-and-slide-2` |  |
| Slip and slide 1 | `concat.combo-slip-and-slide-1` |  |
| Roll InOut 2 | `concat.combo-roll-inout-2` |  |
| Right Zoom | `concat.combo-right-zoom` |  |
| Slice  Rotate 2 | `concat.combo-slice-rotate-2` |  |
| Cube 3 | `concat.combo-cube-3` |  |
| Pirate ship 1 | `concat.combo-pirate-ship-1` |  |
| Bisect 2 | `concat.combo-bisect-2` |  |
| Pan Left | `concat.combo-pan-left` |  |
| Train 3 | `concat.combo-train-3` |  |
| Train 1 | `concat.combo-train-1` |  |
| Magic Cube 2 | `concat.combo-magic-cube-2` |  |
| Yoyo 2 | `concat.combo-yoyo-2` |  |
| 3D card 5 | `concat.combo-3d-card-5` |  |
| Fall Bottom Right | `concat.combo-fall-bottom-right` |  |
| 3D card 3 | `concat.combo-3d-card-3` |  |
| Funhouse mirror 1 | `concat.combo-funhouse-mirror-1` |  |
| Revolving Checker 2 | `concat.combo-revolving-checker-2` |  |
| Roll InOut 1 | `concat.combo-roll-inout-1` |  |
| Left Zoom | `concat.combo-left-zoom` |  |
| Fall Left | `concat.combo-fall-left` |  |
| Checker Slide 2 | `concat.combo-checker-slide-2` |  |
| Waltzer 2 | `concat.combo-waltzer-2` |  |
| Smartphone 3 | `concat.combo-smartphone-3` |  |
| Spinning top 1 | `concat.combo-spinning-top-1` |  |
| Smaller | `concat.combo-smaller` |  |
| Zoom Spin | `concat.combo-zoom-spin` |  |
| Spin In | `concat.combo-spin-in` |  |
| Fall Bottom Left | `concat.combo-fall-bottom-left` |  |
| Yoyo 1 | `concat.combo-yoyo-1` |  |
| Flip 6 | `concat.combo-flip-6` |  |
| Funhouse mirror 2 | `concat.combo-funhouse-mirror-2` |  |
| ZoomRoll | `concat.combo-zoomroll` |  |
| 3D card 4 | `concat.combo-3d-card-4` |  |
| Spin Fall | `concat.combo-spin-fall` |  |
| Cube | `concat.combo-cube` |  |
| Fan Out | `concat.combo-fan-out` |  |
| Triplets 1 | `concat.combo-triplets-1` |  |
| Magic Cube 1 | `concat.combo-magic-cube-1` |  |
| 3D card 6 | `concat.combo-3d-card-6` |  |
| Quarter 2 | `concat.combo-quarter-2` |  |
| Spin Out | `concat.combo-spin-out` |  |
| Pirate ship 2 | `concat.combo-pirate-ship-2` |  |
| Bisect Domino 2 | `concat.combo-bisect-domino-2` |  |
| Waltzer 4 | `concat.combo-waltzer-4` |  |
| Rise Spin | `concat.combo-rise-spin` |  |
| Puzzle | `concat.combo-puzzle` |  |
| Bisect 1 | `concat.combo-bisect-1` |  |
| Pirate ship 3 | `concat.combo-pirate-ship-3` |  |
| Pirate ship 4 | `concat.combo-pirate-ship-4` |  |
| Checker Slide 1 | `concat.combo-checker-slide-1` |  |
| Waltzer 1 | `concat.combo-waltzer-1` |  |
| Smartphone 2 | `concat.combo-smartphone-2` |  |
| Sliding Doors 1 | `concat.combo-sliding-doors-1` |  |
| Split up  down 2 | `concat.combo-split-up-down-2` |  |
| Cube 2 | `concat.combo-cube-2` |  |
| Crystal 1 | `concat.combo-crystal-1` |  |
| Angle 1 | `concat.combo-angle-1` |  |
| Trisect 1 | `concat.combo-trisect-1` |  |
| Flip 2 | `concat.combo-flip-2` |  |
| Waltzer 3 | `concat.combo-waltzer-3` |  |
| Blinds | `concat.combo-blinds` |  |
| Crystal 2 | `concat.combo-crystal-2` |  |
| Triplets 2 | `concat.combo-triplets-2` |  |
| Angle 2 | `concat.combo-angle-2` |  |
| Cube 3 II | `concat.combo-cube-3-1` |  |
| Cube 2 II | `concat.combo-cube-2-1` |  |
| Slice  Rotate 1 | `concat.combo-slice-rotate-1` |  |
| Quarter 1 | `concat.combo-quarter-1` |  |
| Revolving Checker 1 | `concat.combo-revolving-checker-1` |  |
| Flip II | `concat.combo-flip-ii` |  |
| Flip 3 | `concat.combo-flip-3` |  |
| Flip 4 | `concat.combo-flip-4` |  |
| Rollercoaster 1 | `concat.combo-rollercoaster-1` |  |
| Rollercoaster 2 | `concat.combo-rollercoaster-2` |  |
| Split up  down 1 | `concat.combo-split-up-down-1` |  |
| Bisect Domino 1 | `concat.combo-bisect-domino-1` |  |
| Flip 5 | `concat.combo-flip-5` |  |

## Animations: Text In

| CapCut | Concat package | Note |
|---|---|---|
| Throw Out | `concat.text-in-throw-out` |  |
| Typewriter | `concat.text-in-typewriter` |  |
| Concentrate | `concat.text-in-concentrate` |  |
| Fade In | `concat.text-in-fade-in` |  |
| Glitch | `concat.text-in-glitch` |  |
| Spin In 2 | `concat.text-in-spin-in-2` |  |
| Spin In 1 | `concat.text-in-spin-in-1` |  |
| Zoom Out 2 | `concat.text-in-zoom-out-2` |  |
| Wave in | `concat.text-in-wave-in` |  |
| Faulty text | `concat.text-in-faulty-text` |  |
| Dissolve | `concat.text-in-dissolve` |  |
| Pop Up | `concat.text-in-pop-up` |  |
| Random Typewriter | `concat.text-in-random-typewriter` |  |
| Fly In | `concat.text-in-fly-in` |  |
| Chroma Type | `concat.text-in-chroma-type` |  |
| Spiral | `concat.text-in-spiral` |  |
| Blur | `concat.text-in-blur` |  |
| Type 2 | `concat.text-in-type-2` |  |
| Type 1 | `concat.text-in-type-1` |  |
| Float Down | `concat.text-in-float-down` |  |
| Zoom In | `concat.text-in-zoom-in` |  |
| Open | `concat.text-in-open` |  |
| Blur to the Left | `concat.text-in-blur-to-the-left` |  |
| Karaoke | `concat.text-in-karaoke` |  |
| Flicker | `concat.text-in-flicker` |  |
| Flip and jump | `concat.text-in-flip-and-jump` |  |
| Flutter | `concat.text-in-flutter` |  |
| Dissolve Down | `concat.text-in-dissolve-down` |  |
| Wipe Right | `concat.text-in-wipe-right` |  |
| Blur Wipe Right | `concat.text-in-blur-wipe-right` |  |
| Slingshot | `concat.text-in-slingshot` |  |
| Blur to the right | `concat.text-in-blur-to-the-right` |  |
| Jolt Forward | `concat.text-in-jolt-forward` |  |
| Rotation Verbatim | `concat.text-in-rotation-verbatim` |  |
| Elastic Telescopic II | `concat.text-in-elastic-telescopic-ii` |  |
| Flip Verbatim | `concat.text-in-flip-verbatim` |  |
| Zoom Out | `concat.text-in-zoom-out` |  |
| Trail | `concat.text-in-trail` |  |
| Slide Right | `concat.text-in-slide-right` |  |
| Clock wipe | `concat.text-in-clock-wipe` |  |
| Flipping | `concat.text-in-flipping` |  |
| Squeeze | `concat.text-in-squeeze` |  |
| Fold | `concat.text-in-fold` |  |
| Roll In | `concat.text-in-roll-in` |  |
| Judder Up | `concat.text-in-judder-up` |  |
| Type 3 | `concat.text-in-type-3` |  |
| Bounce In | `concat.text-in-bounce-in` |  |
| Slide Up | `concat.text-in-slide-up` |  |
| Blow In | `concat.text-in-blow-in` |  |
| Wobble | `concat.text-in-wobble` |  |
| Bounce from TR | `concat.text-in-bounce-from-tr` |  |
| Showing Right | `concat.text-in-showing-right` |  |
| Showing Up | `concat.text-in-showing-up` |  |
| Mini Zoom | `concat.text-in-mini-zoom` |  |
| Set to the Right | `concat.text-in-set-to-the-right` |  |
| Slide Left | `concat.text-in-slide-left` |  |
| Bounce In TL | `concat.text-in-bounce-in-tl` |  |
| Wipe Up | `concat.text-in-wipe-up` |  |
| Random Bounce | `concat.text-in-random-bounce` |  |
| Blur Wipe Left | `concat.text-in-blur-wipe-left` |  |
| Sunrise | `concat.text-in-sunrise` |  |
| Wipe Down | `concat.text-in-wipe-down` |  |
| Wipe In LR | `concat.text-in-wipe-in-lr` |  |
| Wipe Left | `concat.text-in-wipe-left` |  |
| Slide Left 1 | `concat.text-in-slide-left-1` |  |
| Slide Down | `concat.text-in-slide-down` |  |
| Slide Up 1 | `concat.text-in-slide-up-1` |  |
| Showing Left | `concat.text-in-showing-left` |  |
| Slide Down 1 | `concat.text-in-slide-down-1` |  |
| Boing | `concat.text-in-boing` |  |
| Spring | `concat.text-in-spring` |  |
| Ease In Right | `concat.text-in-ease-in-right` |  |
| Turn Horizontal | `concat.text-in-turn-horizontal` |  |
| Grow | `concat.text-in-grow` |  |
| Showing Down | `concat.text-in-showing-down` |  |
| Flip up | `concat.text-in-flip-up` |  |

## Animations: Text Out

| CapCut | Concat package | Note |
|---|---|---|
| Fade Out | `concat.text-out-fade-out` |  |
| Blur | `concat.text-out-blur` |  |
| Zoom In | `concat.text-out-zoom-in` |  |
| Typewriter | `concat.text-out-typewriter` |  |
| Zoom In 2 | `concat.text-out-zoom-in-2` |  |
| Dissolve Up | `concat.text-out-dissolve-up` |  |
| Slide Down | `concat.text-out-slide-down` |  |
| Dissolve | `concat.text-out-dissolve` |  |
| Slide Up | `concat.text-out-slide-up` |  |
| Flicker | `concat.text-out-flicker` |  |
| Blur to the Left | `concat.text-out-blur-to-the-left` |  |
| Zoom Out | `concat.text-out-zoom-out` |  |
| Slide Down 1 | `concat.text-out-slide-down-1` |  |
| Mini Zoom | `concat.text-out-mini-zoom` |  |
| Bounce Out | `concat.text-out-bounce-out` |  |
| Wipe Left | `concat.text-out-wipe-left` |  |
| Expand | `concat.text-out-expand` |  |
| Throw Back | `concat.text-out-throw-back` |  |
| Slide Left | `concat.text-out-slide-left` |  |
| Slide Up 1 | `concat.text-out-slide-up-1` |  |
| Type 1 | `concat.text-out-type-1` |  |
| Dilute | `concat.text-out-dilute` |  |
| Type 2 | `concat.text-out-type-2` |  |
| Horizontal Close | `concat.text-out-horizontal-close` |  |
| Slide Right | `concat.text-out-slide-right` |  |
| Disband to the Left | `concat.text-out-disband-to-the-left` |  |
| Random Typewriter | `concat.text-out-random-typewriter` |  |
| Flutter | `concat.text-out-flutter` |  |
| Fold | `concat.text-out-fold` |  |
| Trail | `concat.text-out-trail` |  |
| Chromatic Aberration Tailing | `concat.text-out-chromatic-aberration-tailing` |  |
| Roll Out | `concat.text-out-roll-out` |  |
| Pop Down | `concat.text-out-pop-down` |  |
| Slingshot | `concat.text-out-slingshot` |  |
| Faulty text | `concat.text-out-faulty-text` |  |
| Sunset | `concat.text-out-sunset` |  |
| Ink Print | `concat.text-out-ink-print` |  |
| Wipe Right | `concat.text-out-wipe-right` |  |
| Bounce Out TR | `concat.text-out-bounce-out-tr` |  |
| Glitch | `concat.text-out-glitch` |  |
| Stroke Fill | `concat.text-out-stroke-fill` |  |
| Wipe Down | `concat.text-out-wipe-down` |  |
| Flip Down | `concat.text-out-flip-down` |  |
| Blur Erase Right | `concat.text-out-blur-erase-right` |  |
| Turn Horizontal | `concat.text-out-turn-horizontal` |  |
| Flipping | `concat.text-out-flipping` |  |
| Grow | `concat.text-out-grow` |  |
| Ease Out Right | `concat.text-out-ease-out-right` |  |
| Spring | `concat.text-out-spring` |  |
| Blur Erase Left | `concat.text-out-blur-erase-left` |  |
| Wipe Up | `concat.text-out-wipe-up` |  |
| Bounce Out TL | `concat.text-out-bounce-out-tl` |  |
| Vrille | `concat.text-out-vrille` |  |
| Blow Away | `concat.text-out-blow-away` |  |
| Type 3 | `concat.text-out-type-3` |  |
| Rotation Verbatim | `concat.text-out-rotation-verbatim` |  |
| Fly Out | `concat.text-out-fly-out` |  |
| Float Up | `concat.text-out-float-up` |  |
| Spin Out 1 | `concat.text-out-spin-out-1` |  |
| Spin Out 2 | `concat.text-out-spin-out-2` |  |
| Slide Down 2 | `concat.text-out-slide-down-2` |  |
| Flip Verbatim | `concat.text-out-flip-verbatim` |  |
| Boing | `concat.text-out-boing` |  |
| Random Bounce | `concat.text-out-random-bounce` |  |
| Wave out | `concat.text-out-wave-out` |  |
| Elastic Telescopic II | `concat.text-out-elastic-telescopic-ii` |  |
| Clock wipe | `concat.text-out-clock-wipe` |  |
| Jump and flip | `concat.text-out-jump-and-flip` |  |

## Animations: Text Loop

| CapCut | Concat package | Note |
|---|---|---|
| Flare | `concat.text-loop-flare` |  |
| Wobble 2 | `concat.text-loop-wobble-2` |  |
| Wave | `concat.text-loop-wave` |  |
| Color Glitch | `concat.text-loop-color-glitch` |  |
| Enlarge Letters | `concat.text-loop-enlarge-letters` |  |
| Converge | `concat.text-loop-converge` |  |
| Scroll Up | `concat.text-loop-scroll-up` |  |
| Flash | `concat.text-loop-flash` |  |
| Jiggly | `concat.text-loop-jiggly` |  |
| Gushing | `concat.text-loop-gushing` |  |
| Wobbly Projector 1 | `concat.text-loop-wobbly-projector-1` |  |
| Wave 3 | `concat.text-loop-wave-3` |  |
| Ink Print | `concat.text-loop-ink-print` |  |
| Donut | `concat.text-loop-donut` |  |
| Shout Out | `concat.text-loop-shout-out` |  |
| Pulse | `concat.text-loop-pulse` |  |
| Tremble | `concat.text-loop-tremble` |  |
| Super Wavy 2 | `concat.text-loop-super-wavy-2` |  |
| Font Reel | `concat.text-loop-font-reel` |  |
| VHS | `concat.text-loop-vhs` |  |
| Space Type | `concat.text-loop-space-type` |  |
| Wobble 3 | `concat.text-loop-wobble-3` |  |
| Top Arch | `concat.text-loop-top-arch` |  |
| Rotate | `concat.text-loop-rotate` |  |
| Random Bounce | `concat.text-loop-random-bounce` |  |
| Jump | `concat.text-loop-jump` |  |
| Shake | `concat.text-loop-shake` |  |
| Wave 2 | `concat.text-loop-wave-2` |  |
| Scrolling | `concat.text-loop-scrolling` |  |
| Strong Tremble 1 | `concat.text-loop-strong-tremble-1` |  |
| Jiggle | `concat.text-loop-jiggle` |  |
| Rotate 1 | `concat.text-loop-rotate-1` |  |
| Dance | `concat.text-loop-dance` |  |
| Super Wavy | `concat.text-loop-super-wavy` |  |
| Emotional Loading | `concat.text-loop-emotional-loading` |  |
| Retro BW | `concat.text-loop-retro-bw` |  |
| Wobble | `concat.text-loop-wobble` |  |
| Pixel Bounce | `concat.text-loop-pixel-bounce` |  |
| Swing | `concat.text-loop-swing` |  |
| Fold | `concat.text-loop-fold` |  |
| Trailing Beating | `concat.text-loop-trailing-beating` |  |
| Pressing | `concat.text-loop-pressing` |  |
| Page Turning I | `concat.text-loop-page-turning-i` |  |
| Bullet Screen | `concat.text-loop-bullet-screen` |  |
| Wiper | `concat.text-loop-wiper` |  |
| Shake 1 | `concat.text-loop-shake-1` |  |
| Blocks | `concat.text-loop-blocks` |  |
| Scream | `concat.text-loop-scream` |  |
| Strong Tremble 2 | `concat.text-loop-strong-tremble-2` |  |
| Flip | `concat.text-loop-flip` |  |
| Wobbly Projector 2 | `concat.text-loop-wobbly-projector-2` |  |
| Wobbly Projector 3 | `concat.text-loop-wobbly-projector-3` |  |
| Jump Pieces | `concat.text-loop-jump-pieces` |  |

## Voice effects

| CapCut | Concat package | Note |
|---|---|---|
| Big House | `concat.big-house` |  |
| Low | `concat.low` |  |
| Energetic | `concat.energetic` |  |
| High | `concat.high` |  |
| Low Battery | `concat.low-battery` |  |
| Tremble | `concat.tremble` |  |
| Electronic | `concat.electronic` |  |
| Sweet | `concat.sweet` |  |
| Vinyl | `concat.vinyl` |  |
| Mic Hog | `concat.mic-hog` |  |
| Lo-Fi | `concat.lofi` |  |
| Megaphone | `concat.megaphone` |  |
| Echo | `concat.echo` |  |
| Synth | `concat.synth` |  |
| Deep | `concat.deep` |  |
| Fussy male | `concat.fussy-male` |  |
| Bestie | `concat.bestie` |  |
| Queen | `concat.queen` |  |
| Squirrel | `concat.squirrel` |  |
| Distorted | `concat.distorted` |  |
| Chipmunk | `concat.chipmunk` |  |
| Trickster | `concat.trickster` |  |
| Elf | `concat.elf` |  |
| Elfy | `concat.elfy` |  |
| Santa | `concat.santa` |  |
| Jessie | `concat.jessie` |  |
| Good Guy | `concat.good-guy` |  |
| Robot | `concat.robot` |  |
| Folk | - | speech-to-song needs a singing model |

## Masks

Concat's clip mask (`ClipMask`) predates this work.

| CapCut | Concat | Note |
|---|---|---|
| Split | mask: Linear |  |
| Filmstrip | mask: Mirror |  |
| Circle | mask: Circle |  |
| Rectangle | mask: Rectangle |  |
| Stars | mask: Star |  |
| Heart | mask: Heart |  |
| Text | - | not yet: a mask shaped by text or drawn freehand |
| Brush | - | not yet: a mask shaped by text or drawn freehand |
| Pen | - | not yet: a mask shaped by text or drawn freehand |

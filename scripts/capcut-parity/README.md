# CapCut parity packages

The specs the CapCut-parity packages under `src/crates/concat-effects/packages`
were generated from. The packages are ordinary folders and the source of truth;
these scripts are how they were written, kept so a family of them can be changed
in one place. See [docs/CAPCUT_PARITY.md](../../docs/CAPCUT_PARITY.md) for what
covers what.

- `tr_*.py` - transitions; `fx_*.py` - effects (`fx_body*.py` are CapCut's body
  effects, approximated around the picture's outlines or a placed point);
  `fx_reveal.py` - the reveal effects animations ride; `anim_clip.py`,
  `anim_text.py` - the clips' and titles' animations; `audio.py` - voice effects.
- `lib_wgsl.py`, `anim_lib.py` - the shared WGSL snippets and expression helpers.
- `generated.txt` - the slugs these scripts own; `gen.py` refuses to overwrite a
  package folder not on it.

Regenerate every package, from the repository root:

```sh
cd scripts/capcut-parity
python gen.py ../../src/crates/concat-effects/packages tr_light.py tr_motion.py tr_shape.py \
  fx_particles.py fx_camera.py fx_lens.py fx_glitch.py fx_light.py fx_color.py fx_frame.py \
  fx_texture.py fx_body.py fx_body2.py fx_reveal.py anim_clip.py anim_text.py
python audio.py ../../src/crates/concat-effects/packages
```

`gen.py` keeps a package's `fixtures.toml` once it exists. A new or changed
shader's probes are pinned from what a GPU renders:

```sh
cd src
CONCAT_REQUIRE_GPU=1 cargo test -p concat-render --features gpu -- every_package_probe_holds > probes.log 2>&1
python ../scripts/capcut-parity/bless.py crates/concat-effects/packages probes.log
```

`bless.py` only touches packages listed in `generated.txt`. Look at the cards
(`CONCAT_CARDS_DIR=... cargo test -p concat-host every_card_draws`) before
pinning: a probe pins what the shader does, not whether that is right.

`dump.py <VectCutAPI checkout> catalog.json` writes CapCut's catalogue from
VectCutAPI's `pyJianYingDraft` metadata, and `parity_doc.py catalog.json
<packages> docs/CAPCUT_PARITY.md` rewrites the parity table from it.

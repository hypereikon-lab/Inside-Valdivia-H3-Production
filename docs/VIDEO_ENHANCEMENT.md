# H3-native temporal expansion and spatial enhancement

Inside Valdivia uses MiniMax H3 itself for both guided temporal expansion and
spatial regeneration. No auxiliary interpolation, restoration, or learned
upscaler model is part of the locked production surface.

## Materialization targets

| Function | Topology | Initial state | Evidence |
| --- | --- | --- | --- |
| guided duration expansion | `generate.with_guides@dense-anchor-temporal-expansion` | every retained decoded source frame becomes an official target-time AddGuide | 2x and 3x execute with positive operator review; 4x executes and awaits review |
| native token dilation | `densify.temporal@token-inpaint` | packed H3 visual tokens dilated onto a longer time lattice | rejected across same-duration and duration-expansion tests |
| fast spatial candidate | `regenerate.spatial@latent-second-pass` | bicubic resized native H3 visual latent | shape/masks unit-validated; visuals pending |
| VAE-manifold candidate | `regenerate.spatial@pixel-vae-second-pass` | decoded resize re-encoded by H3 VAE | visual graft unit-validated; visuals pending |
| VRAM-bounded candidate | `regenerate.spatial@tiled-pixel-vae` | overlapping H3-VAE tiles with one global prior | offline design only |

All paths reuse the locked H3 model, text encoder, and H3 video VAE already
present on the laboratory machine.

## Guided temporal expansion

The supported H3-native slow-motion path is a composition of decoded frame
selection and the official `MiniMaxH3AddGuide` conditioning primitive. For
factor `f`, retained source frame `i` is placed at target frame `i * f`. The
frames between those observations remain generative:

```text
source:    S0  S1  S2  S3 ...
2x target: S0  __  S1  __  S2  __  S3 ...
3x target: S0  __  __  S1  __  __  S2 ...
4x target: S0  __  __  __  S1  __  __  __ ...
```

The delivery clock always remains 24 fps. The live five-second ladder is:

| Factor | Source prefix | Official guides | H3 target | Delivery |
| ---: | ---: | ---: | ---: | ---: |
| 2x | 60 frames | 60 at stride 2 | 124 | 119 frames / 4.958 s |
| 3x | 40 frames | 40 at stride 3 | 124 | 118 frames / 4.917 s |
| 4x | 30 frames | 30 at stride 4 | 124 | 117 frames / 4.875 s |

This is guided temporal expansion, not optical-flow interpolation and not a
change to video playback metadata. H3 receives explicit target-time visual
observations and synthesizes a new coherent trajectory through them. The 2x
and 3x results received positive operator review; 4x has execution evidence but
still needs full-motion review. See the exact graphs and arithmetic in
`experiments/workflows/temporal-expansion-2026-08-31/`.

The experiment runs at 896×512 because 60 independent guide encodes approached
the measured system-RAM limit. Resolution regeneration remains a separate pass;
do not silently combine it with temporal characterization.

### Rejected native-token route

Packed-token dilation is not a supported slow-motion workflow. It executed at
2x in the earlier same-duration test and at 2x/3x in the present duration-
expansion test, but visual review rejected the motion. The transformed initial
state does not constrain H3 as a sequence of exact target-time observations;
the model is free to reinterpret it as a new trajectory. Exact decoded-anchor
restoration also failed because it exposed an alternating cadence discontinuity.

The low-level CAUCE lattice nodes remain valid for state inspection and other
experiments, but the repository must not advertise their composition as
temporal interpolation or slow motion.

## Spatial regeneration baselines

The first target increases `[768,1344]` to `[1024,1792]`, preserving 124 frames
at 24 fps.

Both full-frame variants use one fixed seed and the same denoise ladder:

```text
0.15, 0.25, 0.35, 0.50, 0.65
```

The latent variant spatially resizes only the H3 visual stream. The pixel/VAE
variant decodes source frames, applies deterministic Lanczos resize, re-encodes
with the H3 video VAE, and grafts that visual state onto the source packed AV
carrier. Both rebuild official H3 conditioning at target geometry and keep
structural-audio denoise at zero.

Compare every result to:

```text
source decode
deterministic resize only
H3 latent second pass
H3 pixel/VAE second pass
```

A useful result needs detail gain beyond the resize control without objectionable
flicker, texture boil, geometry drift, identity drift, or changed gesture timing.

## Tiled research path

The tiled path is not a shortcut to acceptance. It exists for targets that do
not fit the measured 32 GB VRAM envelope. The first offline profile uses
768×768 tiles, 128-pixel overlap, complete temporal context per tile, a shared
global upscale prior, and smootherstep overlap fusion.

Do not materialize it by inventing node contracts. Capture current
`/object_info`, select available vanilla crop/composite mechanisms, and prove
that overlap seams are lower than the full-frame baseline. If a full-frame
target fits, prefer the simpler graph.

## Ordering

Only after guided temporal expansion and spatial regeneration pass
independently, compare:

```text
generate.with_guides@dense-anchor-temporal-expansion -> regenerate.spatial
regenerate.spatial -> generate.with_guides@dense-anchor-temporal-expansion
```

The former lets the spatial pass see final dense motion but processes more
frames. The latter gives temporal inpainting higher-resolution anchors but may
amplify spatial-pass drift. Runtime, VRAM, detail stability, anchor drift, and
motion quality decide.

## LoRA boundary

Training is separate from CAUCE inference nodes. The repository retains two
schema-validated DiffSynth-Studio-derived designs:

- spatial regeneration LoRA from degraded/lower-resolution context to a
  higher-quality target;
- temporal completion LoRA trained on the same missing-token distributions
  produced by native CAUCE dilation.

The official H3 repository publishes model weights for further development but
does not ship a local training stack. DiffSynth-Studio documents H3 full and
LoRA training; its current NF4 examples use rank 32 over `qkv_proj`, `out_proj`,
`mlp.fc1`, and `mlp.fc2`. The spatial Ref2VA recipe is `lab-gated`; the
temporal recipe is `requires-task-adapter` because upstream does not publish a
Retake training recipe. A 32 GB RTX 5090 may support a bounded LoRA experiment,
but neither is executable until its stated gate passes. Full 33B fine-tuning is
outside the current hardware target. See [Training](TRAINING.md).

## Live sequence

1. Re-run dense AddGuide 2x/3x once on a second source and seed.
2. Review the completed 4x output for anchor fidelity, cadence and motion.
3. Promote no factor until its acceptance repeat count and visual checks pass.
4. Materialize latent and pixel/VAE spatial graphs; run the denoise ladder.
5. Compare temporal-first and spatial-first only after independent acceptance.
6. Record exact runtime, peak VRAM/RAM, disk delta, artifacts, native states,
   receipts, and explicit visual assessments.
7. Stop on unknown queue outcome, missing model/node, low disk reserve, or
   ambiguous active workflow identity.

The dense-guide ladder is live-characterized but not yet production-promoted.

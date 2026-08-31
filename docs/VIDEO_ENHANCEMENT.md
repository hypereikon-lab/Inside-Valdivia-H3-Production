# H3-native temporal and spatial enhancement

Inside Valdivia uses MiniMax H3 itself for both temporal densification and
spatial regeneration. No auxiliary interpolation, restoration, or learned
upscaler model is part of the locked production surface.

## Materialization targets

| Function | Topology | Initial state | Evidence |
| --- | --- | --- | --- |
| more motion samples | `densify.temporal@token-inpaint` | native H3 visual tokens dilated onto a longer time lattice | geometry/masks unit-validated; H3 execution and visuals pending |
| fast spatial candidate | `regenerate.spatial@latent-second-pass` | bicubic resized native H3 visual latent | shape/masks unit-validated; visuals pending |
| VAE-manifold candidate | `regenerate.spatial@pixel-vae-second-pass` | decoded resize re-encoded by H3 VAE | visual graft unit-validated; visuals pending |
| VRAM-bounded candidate | `regenerate.spatial@tiled-pixel-vae` | overlapping H3-VAE tiles with one global prior | offline design only |

All four reuse the locked H3 model, text encoder, and H3 video VAE already
present on the laboratory machine.

## Temporal densification baseline

The first experiment uses a retained 124-frame packed H3 AV state:

```text
source frames               124 at 24 fps
source visual tokens         37
factor                         2
delivery frames             247 at 48 fps
legal H3 target             260 at model-time 24 fps
target visual tokens          77
decoded tail crop             13
```

CAUCE copies every source visual token to a monotone target-token anchor. The
remaining target tokens start empty and carry denoise 1. Source anchors carry
denoise 0. The ordinary H3 sampler therefore receives native known state on
both temporal sides of each missing interval.

Initial fixed values:

```text
factor             2
anchor_denoise     0
gap_denoise        1
feather_tokens     1, then 2 and 3 as controlled variants
curve              smootherstep
audio_denoise      1
```

The model target remains inside H3's documented 124–362-frame training range.
Factors 3 and 4 are deferred until 2x produces genuine additional motion and
acceptable anchor drift. Longer sources must be processed through overlapping
native windows, not one out-of-range target.

Prompt comparison is part of the experiment: minimal continuity text, the
source-generation prompt, and an explicit continuous-motion prompt at fixed
seed. H3 structural audio is discarded after inference; the fixed production
soundtrack remains external.

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

Only after temporal and spatial operations pass independently, compare:

```text
densify.temporal -> regenerate.spatial
regenerate.spatial -> densify.temporal
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

1. Update CAUCE to locked commit `9172c30b37fc43272473409e6f42eaacc0a10e60`.
2. Restart only the ComfyUI process and capture one fresh full runtime manifest.
3. Confirm the three new CAUCE node types and existing H3 model files.
4. Materialize temporal 2x and execute one 124-frame fixed-seed baseline.
5. Materialize latent and pixel/VAE spatial graphs; run the denoise ladder.
6. Record exact runtime, peak VRAM/RAM, disk delta, artifacts, native states,
   receipts, and explicit visual assessments.
7. Stop on unknown queue outcome, missing model/node, low disk reserve, or
   ambiguous active workflow identity.

The current repository state is offline-ready, not production-accepted.

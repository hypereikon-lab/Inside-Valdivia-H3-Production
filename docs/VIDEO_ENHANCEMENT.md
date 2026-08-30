# Video enhancement pipelines

The production system treats temporal sample-rate conversion, creative H3
retiming, and spatial-temporal restoration as separate capabilities.

## Available offline plans

| Function | Operation / variant | Owner | Present state |
| --- | --- | --- | --- |
| 24 to 48 fps default | `interpolate.frames@rife-2x` | native ComfyUI RIFE + CAUCE clock plan | offline-ready; model/runtime unconfirmed |
| 24 to 48 fps large-motion comparison | `interpolate.frames@film-2x` | native ComfyUI FILM + same CAUCE clock plan | offline-ready; model/runtime unconfirmed |
| spatial-temporal restoration | `restore.video@seedvr2-3b-nvfp4` | official native ComfyUI SeedVR2 graph | offline-ready; model/runtime unconfirmed |
| creative duration change | `generate.with_guides@multi-anchor` + `CaucePlanH3GuideRetime` preflight | official H3 AddGuide | existing topology; retime experiment planned |

No item above is yet a retained executable UI/API workflow or a visual success.

## Exact temporal interpolation

For `N` source frames at `f` fps and multiplier `m`:

```text
target_frame_count = (N - 1) * m + 1
target_fps         = f * m
source frame i     = output frame i * m
```

`CaucePlanFrameInterpolation` records those values before inference. Runtime
materialization must derive `N` from the actual decoded batch rather than a
hand-entered guess. The output count and all source-anchor positions are
technical acceptance checks.

RIFE 2x is the first default. FILM 2x is a controlled comparison for shots with
large displacement or occlusion failure. They are alternatives, not sequential
passes. ComfyUI 0.34.0 supplies one native loader and one native interpolator
for both models; no interpolation custom-node repository is required.

## Why the alternating H3 mask is not shipped

H3 does not expose one independently maskable token per decoded frame. The
official VAE temporally compresses by four and the DiT's visual-token coverage
repeats `(1, 4, 4, 4, 4)` over each seventeen decoded frames. Animated mask
projection takes the temporal maximum in each token span.

At 2x, most four-frame tokens contain both an original frame and a requested
empty frame. The whole token is therefore regenerated. For a 124-frame source,
the exact interpolated target is 247 frames but the next legal H3 target is 260
frames with 77 video tokens. `CauceInspectH3InterleaveProjection` exposes the
mixed-token count. This construction remains a diagnostic of an invalid
pixel-preservation assumption, not a production workflow.

## Creative H3 retime

`CaucePlanH3GuideRetime` selects source frames at a declared stride and maps
them across a legal endpoint-aligned `17k+5` H3 target. The official
`generate.with_guides@multi-anchor` graph then performs inference.

The output remains 24 fps. It can invent and reorganize motion between guides,
so it is useful as a generative revision rather than as FPS conversion. The
planned guide-stride experiment compares 12, 24, and 48 source frames while
holding model, prompt, seed, sampler, and duration scale fixed.

## SeedVR2 restoration

The spatial pipeline follows the official native ComfyUI video template:

```text
VIDEO -> components -> resize -> SeedVR2 preprocess
  -> tiled VAE encode -> temporal chunk -> conditioning
  -> one-step sample -> temporal merge -> tiled decode -> postprocess
```

Initial laboratory target:

```text
GPU                 RTX 5090, 32 GB VRAM
model               seedvr2_3b_nvfp4.safetensors, 1,996,687,726 bytes
VAE                 ema_vae_fp16.safetensors, 501,324,814 bytes
first scale         1.5x characterization only
steps / cfg         1 / 1.0
sampler / schedule  euler / simple
denoise             1.0
chunking            auto first
color correction    lab first
```

The model payload fits the disk envelope, but weight size does not prove that
activation memory fits. Automatic chunk behavior, overlap, peak VRAM, runtime,
and boundary quality must be measured on the real tower. Frame count and fps
must remain unchanged.

## Combined production candidate

The primary candidate order is:

```text
accepted H3 output at 24 fps
  -> SeedVR2 restoration at 24 fps
  -> RIFE 2x at restored resolution
  -> final 48 fps video
```

This keeps the expensive SeedVR2 pass on the smaller original frame batch.
The `enhancement-order` experiment includes the reverse order as a bounded
control, not as a second default. A four-output characterization set is
required: source, RIFE-only, SeedVR2-only, and SeedVR2 to RIFE.

## Live sequence

1. capture a fresh runtime manifest and confirm storage reserve;
2. confirm the native `FrameInterpolationModelLoader` and `FrameInterpolate`
   schemas and download only the two content-addressed model files if absent;
3. materialize the shared native interpolation archetype and run exact count
   smokes for RIFE and FILM on a short accepted source;
4. confirm native SeedVR2 node schemas and exact model filenames;
5. download only the 3B NVFP4 model and VAE after the storage gate;
6. materialize the SeedVR2 topology and characterize 1.25x, 1.5x, and 2x;
7. compare the accepted SeedVR2 setting alone, RIFE alone, and both orders;
8. retain paired UI/API graphs only from the exact visually assessed active
   graph and runtime manifest.

No CUDA, PyTorch, driver, or unrelated package update belongs to this sequence.

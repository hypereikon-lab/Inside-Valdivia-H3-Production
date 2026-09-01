# Live H3 operation batch — 2026-08-31

This document records one live characterization batch against the authenticated
laboratory ComfyUI runtime. It separates successful execution from useful visual
behavior. Every row resolves to an immutable run receipt, the exact executed API
graph, a ComfyUI prompt id, a saved MP4 and (except where noted by history) a
retained native H3 AV checkpoint.

## Fixed runtime and inputs

- Runtime manifest: `e97aa6c8e6f449e0f3d0f51fd3921e66c51f763de6d64de3ed9f2474019ba9c9`
- GPU: RTX 5090, 34,190,458,880 bytes VRAM
- System RAM: 67,768,381,440 bytes
- FL2VA: `minimax_h3_fl2va_pruned_fp8_scaled.safetensors`
- Ref2VA: `minimax_h3_ref2va_pruned_fp8_scaled.safetensors`
- Text encoder: `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`
- Video VAE: `minimax_h3_video_vae_fp16.safetensors`
- Baseline geometry: 1344×768, 124 frames, 24 fps
- Sampler / scheduler / steps: `res_multistep` / `simple` / 20
- Frame A SHA-256: `c1e448e2a28dd259d31e78f59fb4bd4778229424b678410af1b7c6bab37ec07e`
- Frame B SHA-256: `dc34fc48c6ea7b5df5924dd2a856b573ab1f2f2058d9bbb4e943daf342eab767`

The batch did not update CUDA, PyTorch, ComfyUI, models, custom-node source,
Windows, Cloudflare or the tunnel. It did not restart ComfyUI. Jobs ran strictly
serially. H3 structural audio remained a model-internal stream; every delivered
artifact is a silent video.

## Results

| # | Operation / variant | Time | Evidence state | Measured result |
| --- | --- | ---: | --- | --- |
| 01 | `generate.keyframed@first-frame` | 326.014 s | `executes` | Reconstructs A at the start and produces a coherent new forward trajectory. One run is not enough for promotion. |
| 02 | `generate.keyframed@last-frame` | 317.370 s | `executes` | Reaches B at the final endpoint. The supplied image is an endpoint, not a semantic reference. |
| 03 | `generate.keyframed@first-last` | 342.865 s | `executes` | Reaches both endpoints over one 124-frame shot and supplies the native source state for the derived tests. |
| 04 | `generate.from_references@image-reference-match` | 346.862 s | `executes` | Uses A and B as ordered spatial/material references without treating either as an endpoint. The trajectory is distinct from 01–03. |
| 05 | `complete.native_av@two-source-connection` | 303.015 s | `executes` | Preserves 39 left frames and 34 right frames, regenerating only the 51-frame middle with 8-frame `smootherstep` fades. Left/right preserved-context MAD is 1.97/2.38 levels per RGB channel after independent MP4 encoding. Boundary frame differences rise to 4.76 and 5.42 versus roughly 2–3 locally, so this is promising but not visually promoted. |
| 06 | `densify.temporal@token-inpaint` | 1016.671 s | `rejected` | Correct delivery geometry: 247 frames at 48 fps, 5.145833 s, with non-duplicate intermediate frames. It is not faithful slow motion: sampled anchor drift is 11–16/255 and endpoint drift is 6.30/7.32. Cadence is uneven. Treat this as temporal regeneration/retiming, not accepted interpolation. |
| 07 | `regenerate.spatial@latent-second-pass` | 745.164 s | `executes` | Fits and completes at 1792×1024 on the 5090. At video denoise 0.35, sampled edge energy rises from 9.63 to 12.36 (~28%), but composition MAD reaches 17.61/255 and texture is visibly more aggressive. It needs a lower-strength ladder before use. |
| 08 | `generate.with_guides@single-anchor` | 332.338 s | `rejected` | B is reconstructed at frame 61, but frame 60→61 jumps by 46.17/255 versus ~2–5 around it. A single still guide is an exact anchor, not a smooth-motion constraint. Use a temporal guide clip when approach/departure continuity matters. |
| 09 | `continue.native_av@masked-overlap` | 376.077 s | `executes` | Produces 243 frames / 10.125 s from a 22-frame native overlap plus 119 new frames. The decoded prefix matches the source exactly (MAD 0). The only new boundary, 123→124, measures 3.52/255 versus ~1.2–1.9 locally. Promising; repeat before promotion. |
| 10 | `refine.video@full-frame` | 342.556 s | `executes` | At video strength 0.20, sampled edge energy rises from 10.76 to 13.41 (~25%) with composition MAD 7.21/255. Adjacent-frame MAD changes from 2.16 to 2.43. This is a better fidelity/detail tradeoff than spatial 0.35, but still needs a fixed-source ladder. |
| 11 | `rollback.native_av@branch-suffix` | 16.644 s | `executes` | Split at frame 90 and reappend reconstructs 124/124 decoded frames with mean MAD 0, maximum MAD 0 and zero non-identical frames at the controlled comparison resolution. MP4 byte hashes differ because the artifact was re-encoded. The graph did not persist prefix and suffix as independent checkpoints, so it does not yet satisfy the full acceptance profile. |
| 12 | `densify.temporal@token-inpaint` exact decoded-anchor delivery | 45.5 s | `rejected` | Restores all 124 source frames exactly before encoding and retains 123 H3-generated gaps, yielding 247 frames at 48 fps. Source-versus-even-anchor PSNR improves from 25.20 to 34.85 dB after independent MP4 encoding, but mean adjacent luma difference rises from 5.65 to 10.65. The generated gaps alternate with a different decoded trajectory, so exact anchors expose rather than solve the cadence discontinuity. |
| 13 | native-token duration expansion 2x | 303.337 s | `rejected` | Retains 56 source frames, dilates their packed visual tokens and delivers 111 frames at 24 fps / 4.625 s. The graph executes, but operator review rejects the motion as useful slow motion. |
| 14 | native-token duration expansion 3x | 296.933 s | `rejected` | Retains 39 source frames, dilates their packed visual tokens and delivers 115 frames at 24 fps / 4.792 s. The graph executes, but operator review again rejects the motion. No 4x run is justified. |
| 15 | `generate.with_guides@dense-anchor-temporal-expansion` 2x | 393.625 s | `executes` | Decodes 60 contiguous source frames, places them as 60 official AddGuides at indices 0,2,…,118 and delivers 119 frames at 24 fps / 4.958 s. Operator review reports that the AddGuide method works. Formal promotion still needs repeat evidence. |
| 16 | `generate.with_guides@dense-anchor-temporal-expansion` 3x | 272.572 s | `executes` | Places 40 official guides at indices 0,3,…,117 and lets H3 generate two frames per interval. Delivery is 118 frames at 24 fps / 4.917 s. Operator review reports that the AddGuide method works. |
| 17 | `generate.with_guides@dense-anchor-temporal-expansion` 4x | 206.198 s | `executes` | Places 30 official guides at indices 0,4,…,116 and lets H3 generate three frames per interval. Delivery is 117 frames at 24 fps / 4.875 s. Execution is verified; visual review is pending. |
| 18 | direct-MP4 dense AddGuide 4x, frames 0–29 | 635.985 s | `executes` | Loads a 960×960 MP4 through native Comfy video nodes, places 30 guides and delivers 117 frames / 4.875 s. Visual review pending. |
| 19 | direct-MP4 dense AddGuide 4x, frames 38–67 | 635.887 s | `executes` | Same fixed graph and seed with only the source start changed. Delivers 117 frames / 4.875 s. Visual review pending. |
| 20 | direct-MP4 dense AddGuide 4x, frames 77–106 | 635.985 s | `executes` | Same fixed graph and seed with only the source start changed. Delivers 117 frames / 4.875 s. Visual review pending. |
| 21 | direct-MP4 dense AddGuide 4x, frames 115–144 | 634.851 s | `executes` | Reaches the final frame of the 145-frame source and delivers 117 frames / 4.875 s. Visual review pending. |

MAD values are mean absolute RGB-channel differences on controlled, same-size
canvas samples. They are diagnostics, not perceptual quality scores. The exact
sampling code is not a substitute for human full-motion review; generative
variants remain below promotion until the acceptance catalog's minimum run count
and explicit visual review are satisfied.

## Evidence layout

- Executed API graphs: `workflows/executed/2026-08-31/*.api.json` and
  `experiments/workflows/temporal-expansion-2026-08-31/*.api.json`
- Project invocations: `invocations/2026-08-31-*.json`
- Immutable local receipts: `runtime/receipts/2026-08-31/*.json` (intentionally
  ignored by repository policy; tracked invocations retain their references and
  executed graphs retain matching content hashes)
- Native checkpoints on the lab runtime: `output/cauce/latents/2026-08-31/*.safetensors`
- Videos on the lab runtime: `output/video/2026-08-31/*.mp4`

The browser URL for an artifact is derived from its receipt, for example:

```text
/view?filename=09_native_forward_continuation_00001_.mp4&subfolder=video%5C2026-08-31&type=output
```

## Decisions from this batch

1. Keep first, last, first/last and Ref2VA as separate official conditioning
   baselines. They solve different constraints.
2. Retain native two-sided completion and native forward continuation as the
   strongest CAUCE candidates, but require a second run and full-motion review.
3. Do not call the current 2× token-dilation graph a production temporal
   upscaler. Its exact clock is correct; its source preservation is not.
4. Do not use an isolated still `AddGuide` as a continuity mechanism. Test a
   legal-length guide clip instead.
5. Characterize refinement at 0.10, 0.15, 0.20 and 0.25 before selecting a
   baseline. Characterize spatial regeneration below 0.35.
6. Retain rollback round-trip as deterministic native state management. It
   does not require H3 sampling, but a promotion run must persist and
   content-address the prefix and suffix independently.
7. Do not treat decoded anchor restoration as a fix for the rejected factor-two
   token-inpaint result. It proves exact source placement, but H3's four-frame
   temporal VAE groups cannot encode an independent alternating decoded-frame
   preserve/generate mask.
8. Reject native-token duration expansion as slow motion. Correct execution and
   legal H3 shapes are insufficient when H3 reinterprets the transformed state.
9. Retain dense official AddGuide expansion as the supported hypothesis. It
   places every retained source frame at an explicit target time and received
   positive operator review at 2x and 3x. The 4x result still needs review, and
   no factor is promoted until repeat-count requirements pass.
10. Direct-MP4 input is sufficient. A source does not need to originate in H3
    or retain packed native state before dense AddGuide expansion; native Comfy
    video decoding can supply the exact ordered frame observations.

## Immediate next characterization set

- repeat native continuation with the same source and a second seed;
- repeat two-source completion and inspect both boundaries in real time;
- run the fixed-source refinement ladder at 0.10/0.15/0.20/0.25;
- run the spatial ladder at 0.10/0.20/0.30;
- replace the rejected still anchor with a 5- or 22-frame guide clip;
- repeat dense AddGuide 2x/3x on a second source and seed, review the completed
  4x result, and characterize maximum guide count at production resolution;
- keep native token dilation paused unless a new H3-native conditioning path
  can constrain decoded cadence.

# Hydra to H3 Fun Control causal comparison

This experiment tests Hydra only as a deterministic `IMAGE`-sequence transform
upstream of the official MiniMax H3 Fun Control input. It does not alter H3
latents or patch the sampler.

## Fixed basis

- source: frames `[0, 73)` of `Gen-4_5.gen-4_5 (5).mp4`;
- Canny thresholds: `0.2`, `0.5`;
- H3: FL2VA pruned INT8 trunk plus pruned INT8 Fun Control patch;
- generation: 768 x 768, 73 frames, 24 fps;
- profile: quality 20, `simple`, `res_multistep`, denoise 1;
- seed: `20260902`;
- first frame and prompt match the retained direct-Canny baseline.

## Variants

1. `hydra-canny-passthrough-quality20` inserts `src(s0)` between Canny and Fun
   Control. Its direct and post-Hydra carrier videos determine whether the
   raster handoff is sufficiently transparent.
2. `hydra-canny-affine-quality20` applies a visible time-varying scale and
   rotation to that same Canny sequence. It tests whether H3 responds to a
   procedural carrier transformation without a latent warp.

The pass-through is a technical gate. The affine variant is an experimental
control hypothesis. Neither becomes a production workflow merely by executing.
Human review must compare carrier motion, generated camera/geometry response,
artifacts, and prompt/first-frame preservation against the direct-Canny
baseline.

## Execution evidence

Both graphs completed on the laboratory RTX 5090 against runtime manifest
`43a0568eecf4966c751d8209b4533eda05eb2cd998ddfdd2b88b4e0166c1a843`.

| Variant | Prompt id | Runtime | Carrier vs direct Canny | Generated vs retained direct-Canny baseline |
| --- | --- | ---: | --- | --- |
| pass-through | `57ad4cf2-7858-44dd-9f1f-2433da750224` | 87.381 s | PSNR infinity; SSIM 1.000000 | PSNR infinity; SSIM 1.000000 |
| affine | `06f4da4d-c57e-473a-9db9-e9059945e21e` | 66.948 s | PSNR 13.491519; SSIM 0.654497 | PSNR 21.058351; SSIM 0.625558 |

The pass-through establishes exact decoded-video and fixed-seed generative
equivalence for this graph. The affine result establishes a causal change, not
an aesthetic success. Full-motion operator review remains required before a
smaller-amplitude ladder or another transform is justified.

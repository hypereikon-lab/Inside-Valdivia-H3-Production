# H3 adaptation boundary

Training is a separate research surface from CAUCE inference. CAUCE constructs
deterministic H3 state, masks, geometry, and operation contracts inside ComfyUI;
it does not contain an optimizer, a dataset loader, or hidden model weights.

The machine target is one RTX 5090 with 32 GB VRAM, 64 GB host RAM, and at most
120 GB currently free disk. Under that constraint, this repository permits
measured LoRA trials and rejects full 33B fine-tuning. Neither recipe is a
production claim.

## Pinned upstream basis

The recipes are derived from DiffSynth-Studio commit
`102fe9980b9375ecb6436d360297a00327472535`. Its current H3 NF4 examples train a
rank-32 DiT LoRA on:

```text
attn.qkv_proj
attn.out_proj
mlp.fc1
mlp.fc2
```

The upstream smoke-test baseline is 480×832, 124 frames, learning rate `1e-4`,
five epochs, gradient checkpointing, and a quantized H3 base. Those values are
recorded for reproducibility; they are not asserted to be optimal for Inside
Valdivia.

## Spatial regeneration LoRA

[`h3-spatial-regeneration-lora.json`](../training/recipes/h3-spatial-regeneration-lora.json)
uses the upstream-supported Ref2VA LoRA path. Each clean target clip is paired
with a deterministic degraded copy of itself as an ordered video reference.
This is the closest currently trainable open implementation of H3's published
in-context regeneration principle:

```text
HQ target clip
  ├─ deterministic degradation + resize ─> Ref2VA video condition
  └─ unchanged clean clip                 ─> flow-matching target
```

It remains `lab-gated`: first prove that one NF4 forward/backward step fits,
measure host RAM and disk, preserve 25 GB free, and verify that the resulting
adapter can be loaded by the locked ComfyUI H3 runtime. A useful adapter must
beat deterministic resize and unadapted H3 controls on held-out clips without
motion timing, geometry, or identity drift.

## Temporal completion LoRA

[`h3-temporal-completion-lora.json`](../training/recipes/h3-temporal-completion-lora.json)
is deliberately marked `requires-task-adapter`. DiffSynth-Studio exposes H3
Retake inference and H3 LoRA SFT, but does not publish a Retake training recipe.
The missing adapter must derive sparse conditioning from each dense target,
inject `retake_video` plus exact `frame_regions_to_retake` or an equivalent
native mask, and prove that known tokens act as preserved context rather than a
second noisy target.

Its initial distributions match operations we can already characterize:

- factor-2 alternating native-token gaps for temporal densification;
- bounded contiguous interior gaps for bidirectional completion;
- one-sided prefix and suffix gaps for rollback/continuation.

This is a small training-code extension, not a new inference model, but it is
still real work. Until the adapter passes a two-sample overfit fixture with no
anchor drift, calling the recipe executable would be false.

## Dataset invariants

Both recipes require:

- 24 fps source media and legal H3 `17n+5` frame counts;
- scene-level train/validation split before creating degradations or masks;
- immutable source, transform, prompt, seed, and mask manifests;
- no production audio objective—the fixed soundtrack stays external;
- held-out controls, runtime/VRAM/RAM/disk receipts, and visual acceptance.

The audio branch may receive controlled silence only when an upstream joint-AV
loader structurally requires it. Generated audio is discarded and is not part
of project evaluation.

## What is not claimed

- The unpublished local H3-Regenerate-2K system has not been reproduced.
- A spatial LoRA has not yet been trained or accepted.
- The temporal-completion task adapter does not yet exist.
- Full 33B fine-tuning does not fit the current single-machine operating target.
- A training result is not promoted merely because its loss decreases.

The catalog and validator preserve those distinctions mechanically.

# AddGuide temporal expansion — 2026-08-31 / 2026-09-01

This characterization turns a short prefix of one 24 fps H3 source into a new
timeline close to five seconds. It does not alter container playback speed.
Every retained source frame is decoded, attached with the official
`MiniMaxH3AddGuide` node at `target_index = source_index * factor`, and H3
generates the intervening target frames.

```text
delivery_frames = (source_frames - 1) * factor + 1
delivery_fps    = 24
model_frames    = next legal H3 length >= delivery_frames
```

The live ladder used one 124-frame FL2VA native source, a legal 124-frame H3
target and a deterministic delivery crop:

| Factor | Source frames | Guide indices | Generated gaps | Delivery | Runtime | Evidence |
| ---: | ---: | --- | ---: | --- | ---: | --- |
| 2x | 60 | 0, 2, …, 118 | 59 | 119 frames / 4.958 s | 393.625 s | executes; positive operator review |
| 3x | 40 | 0, 3, …, 117 | 78 | 118 frames / 4.917 s | 272.572 s | executes; positive operator review |
| 4x | 30 | 0, 4, …, 116 | 87 | 117 frames / 4.875 s | 206.198 s | executes; visual review pending |

The 2x and 3x results were explicitly reported as working by the operator. That
is strong experiment feedback, but it does not by itself satisfy the repository
promotion profile's repeat count and full visual checklist. The 4x result has
only execution evidence so far.

A same-size diagnostic compared each decoded source frame with its generated
frame at the corresponding guide index after independent MP4 encoding. Mean
PSNR was 28.05 dB at 2x, 27.98 dB at 3x and 27.91 dB at 4x. The close values
show that guide reconstruction fidelity does not collapse as the tested factor
increases. PSNR does not evaluate the inter-guide motion and is not a visual
acceptance substitute.

All three accepted experiment graphs use 896×512 to keep dozens of independent
VAE-encoded guide conditions inside the measured 64 GB RAM / 32 GB VRAM
envelope. They retain native H3 checkpoints and silent MP4 deliveries.

## Direct-MP4 4x windows

The same operation also executes without a pre-existing H3 native checkpoint.
`LoadVideo` and `GetVideoComponents` decode an uploaded MP4, after which exact
decoded ranges feed the ordinary dense AddGuide chain. A 145-frame, 24 fps,
960×960 source was sampled at four evenly distributed 30-frame windows:

| Window | Source frames | Approximate source time | Delivery | Runtime |
| --- | --- | --- | --- | ---: |
| 1 | 0–29 | 0.00–1.21 s | 117 frames / 4.875 s | 635.985 s |
| 2 | 38–67 | 1.58–2.79 s | 117 frames / 4.875 s | 635.887 s |
| 3 | 77–106 | 3.21–4.42 s | 117 frames / 4.875 s | 635.985 s |
| 4 | 115–144 | 4.79–6.00 s | 117 frames / 4.875 s | 634.851 s |

All four graphs validated live with zero issues and completed serially. They
used identical model, prompt, seed, sampler, scheduler, steps and geometry; only
the source start frame changed. Their visual verdict remains pending.

## Sparse-anchor 4x characterization

The builder also supports sparse source-anchor strides while preserving target
time. For a source offset `i`, the official AddGuide remains at
`target_index = i * factor`; reducing guide count therefore creates genuinely
larger intervals for H3 to synthesize rather than compressing the surviving
guides toward the start of the target.

The retained comparison uses the first 30 decoded frames of the same direct
MP4, a 124-frame target, a deterministic 117-frame delivery crop, seed 310944,
and 672×672 geometry. Both runs use the same generalized prompt and differ only
in source stride:

| Source stride | Source offsets | Target guide indices | Guides | Runtime | Technical result |
| ---: | --- | --- | ---: | ---: | --- |
| 8 | 0, 8, 16, 24, 29 | 0, 32, 64, 96, 116 | 5 | 102.109 s | executes; sampled trajectory remains visually coherent; operator review pending |
| 16 | 0, 16, 29 | 0, 64, 116 | 3 | 95.649 s | rejected by technical visual inspection: large unguided spans collapse to white frames and pseudo-text |

Both deliveries are exactly 672×672, 117 frames, 24 fps and 4.875 seconds.
Stride 16 therefore saves only 6.460 seconds relative to stride 8 on this
cached run while losing the scene between anchors. It is retained as a boundary
result, not a recommended workflow. Stride 8 is the only sparse candidate that
continues to visual review.

The prompt is deliberately content-independent:

```text
Generate a single continuous slow-motion trajectory through the supplied
temporally ordered visual anchors. Preserve the subjects, scene geometry,
camera path, lighting, exposure, textures, motion direction and causal
continuity. Generate coherent motion only between the anchors. No cuts,
resets, duplicated gestures, temporal echoes, morphing, new objects, text
or generated audio.
```

The default builder now emits only stride 8 and stride 16. Arbitrary positive
strides remain available for explicit characterization, but intermediate
stride-2/4 graphs are not retained in the repository.

## Sparse stride-8 2x pass

The first 60 decoded frames of the direct MP4 were also expanded 2x with source
offsets `[0, 8, 16, 24, 32, 40, 48, 56, 59]` at target indices
`[0, 16, 32, 48, 64, 80, 96, 112, 118]`. The graph uses the same generalized
prompt, 672×672 geometry, seed and sampler as the 4x sparse comparison. It
completed in 118.598 seconds and delivered exactly 119 frames at 24 fps
(4.958 seconds). Sampled technical inspection is coherent; full-motion operator
review remains pending.

The remaining source was then covered without artificial padding:

| Window | Source range | Source frames | Guides | H3 target | Delivery | Runtime |
| ---: | --- | ---: | ---: | ---: | --- | ---: |
| 1 | 0–59 | 60 | 9 | 124 | 119 frames / 4.958 s | 118.598 s |
| 2 | 59–118 | 60 | 9 | 124 | 119 frames / 4.958 s | 119.064 s |
| 3 | 118–144 | 27 | 5 | 56 | 53 frames / 2.208 s | 46.033 s |

Adjacent windows share exactly one source boundary frame. Assembly must remove
the first decoded frame of windows 2 and 3 so the shared boundary is represented
once. The final window demonstrates that the operation can select the next
legal H3 target and crop to the exact delivery length instead of padding the
source or extending beyond its final frame.

## Rejected native-token hypothesis

The `rejected/` directory preserves the exact 2x and 3x graphs that dilated
packed H3 visual tokens and asked H3 to inpaint the gaps. Both graphs execute,
but operator review rejected their motion. They are evidence, not supported
workflows, and the builder deliberately cannot regenerate them.

The practical distinction is causal: token dilation supplies a transformed
initial state that H3 may reinterpret, while dense AddGuide supplies explicit
target-time observations. For guided slow motion, only the latter remains on
the supported path.

## Rejected Qwen timed-reference replacement

The sparse 2x / stride-8 window was repeated with the same decoded source
frames, target times, seed, sampler, steps, 672×672 geometry and 119-frame
delivery, replacing the nine official AddGuides with nine
`MiniMaxH3AddTimedImageReference` nodes. This necessarily uses Ref2VA because
the community nodes patch its Qwen tokenizer path. The references are
semantic-only: they are not H3 VAE states at the requested target indices.

The graph executed in 120.763 seconds, effectively the same as the 118.598
second AddGuide baseline. It failed the intended operation. Instead of
reconstructing one full-frame state at each target time, the model composed
three repeated circular views in a horizontal band on a pale canvas. Across
the nine nominal anchor times, same-size source correspondence measured only
2.58 dB PSNR / 0.054 SSIM, versus 25.99 dB / 0.695 for AddGuide. These metrics
only characterize anchor preservation, but the order-of-magnitude collapse is
also visually unambiguous.

Timed semantic references therefore are not a drop-in implementation of sparse
guided temporal expansion. They remain suitable for testing when an appearance,
object or event should become semantically relevant near a time. AddGuide is
the retained primitive when a decoded frame must act as a target-aligned visual
state. Any future timed-reference-plus-AddGuide study belongs in research and
must begin from a new hypothesis rather than a retained production workflow.

# Dense-AddGuide temporal expansion — 2026-08-31

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

## Rejected native-token hypothesis

The `rejected/` directory preserves the exact 2x and 3x graphs that dilated
packed H3 visual tokens and asked H3 to inpaint the gaps. Both graphs execute,
but operator review rejected their motion. They are evidence, not supported
workflows, and the builder deliberately cannot regenerate them.

The practical distinction is causal: token dilation supplies a transformed
initial state that H3 may reinterpret, while dense AddGuide supplies explicit
target-time observations. For guided slow motion, only the latter remains on
the supported path.

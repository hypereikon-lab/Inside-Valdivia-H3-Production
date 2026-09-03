# H3 prompting as an experimental control surface

Prompting is currently the least characterized part of the production system.
The repository has exact prompts in executed graphs, but those prompts were
mostly held fixed while conditioning, masks, guides, acceleration and control
were varied. They are evidence for those mechanisms, not evidence that the
wording is optimal.

The project therefore treats a prompt as one model input with a measurable
response surface. It is not metadata, a magic phrase, an inferred description
of the media, or a hidden creative ontology.

## What is known from the released implementation

The following is source evidence rather than a project inference:

- H3-Base uses Qwen3-VL-32B hidden states from layer 50 as conditioning for the
  H3 Omni Transformer.
- In official ComfyUI FL2VA, `MiniMaxH3ImageToVideo` tokenizes the prompt with
  the supplied first and/or last images. The same images are also encoded by
  the visual VAE and attached as keyframes that are re-injected during
  sampling.
- In official ComfyUI Ref2VA, reference images, videos and audio are presented
  to the tokenizer in a defined order and are also supplied as reference
  blocks to the diffusion model. Prompt labels such as `<Picture 1>` and
  `<Video 1>` therefore have an actual input-order contract.
- H3-Base is CFG-distilled and the canonical local ComfyUI graph uses
  `BasicGuider`. There is no independent negative-prompt branch. Any
  prohibition is ordinary positive-language conditioning and must earn its
  place empirically.
- Local ComfyUI uses H3-Base directly. It does not silently invoke the
  proprietary H3-Context-IR service. The public prompt grammar is the closest
  released specification of its expected input, not a local reproduction of
  the private Context-IR transformation.

The prompt-writing source is pinned in `prompting/catalog.json` to MiniMax-H3
commit `d21241f0a4b3acbb34c97dae47fa417b7065e438`, including hashes for the
skill, base-mode guide and Ref2VA guide. Recheck the pin when upstream changes;
do not let a moving web guide alter an experiment after it has been declared.

## Project scope

Media remains opaque. No prompt tool captions an image, assigns objects,
invents actions, or stores a scene ontology. A human supplies the intended
movement or transformation; the prompt only expresses that intent to H3.

The soundtrack is fixed outside generation. The prompt matrices use:

```text
overall_soundscape: N/A
non_diegetic_music: N/A
```

This prevents audio invention from becoming an experimental variable. It does
not turn the released joint AV architecture into a video-only model or prove a
runtime saving.

Prompts are written in English because that is the language required by the
published guides. No local LLM prompt rewriter is a runtime dependency. A
rewriter can be compared later only after the direct prompt response is known.

## Separate the conditioning modes

The same prose should not be copied blindly across all H3 tasks.

### I2VA

The first image fixes the opening. The prompt owns the departure:

```text
first-frame anchor -> onset -> continuous development -> resulting state
```

The main unknown is how much causal and timed path detail improves motion
before it begins to overconstrain a five-second sample.

### FL2VA

The two images fix the endpoints. The prompt should spend most of its useful
information on the path between them:

```text
opening state -> observable intermediate change -> progressive convergence
-> final-frame landing
```

Repeating two static image descriptions wastes the part of the signal that can
disambiguate motion. The first experiments therefore leave image content
undescribed and vary only prompt form, camera semantics and temporal profile.

### L2VA

The last image fixes the arrival. The prompt must propose a compatible earlier
state and a convergence path. It is not equivalent to reversing I2VA: causal
events, occlusions and camera dynamics may not be time reversible. L2VA gets a
dedicated matrix after the I2VA/FL2VA vocabulary is characterized.

### Ref2VA

Ref2VA is a role-binding problem as well as a prose problem. A reference image
can supply visible identity or style; a reference video can supply whole-video
camera movement, cuts, rhythm or temporal structure; either can instead be a
concrete keyframe role. Those relationships must not be collapsed into one
generic "reference" instruction.

The public format contains six sections:

```text
subject_definitions
summary
retention_analysis
detailed_description
overall_soundscape
non_diegetic_music
```

The first project comparison asks a deliberately narrow question: does this
formal role/retention structure improve transfer of one reference video's
camera motion relative to short label-aware prose? It does not assume that
longer is better.

### AddGuide

AddGuide already supplies target-time visual state through the H3 VAE path.
Prompt text cannot make a badly placed guide exact, but it may change what the
model believes the unobserved gaps are for. The retained comparison varies:

1. neutral continuity;
2. explicit generation only between ordered guide states;
3. explicit duration expansion / slow-motion synthesis.

This isolates language from guide density and placement. Guide indices,
source frames, seed and graph remain identical.

### Fun Control

Structural control should not be introduced while the textual baseline is
still ambiguous. Once one prompt form is retained, the first control-language
matrix keeps the carrier and strength fixed and compares:

1. text-neutral;
2. text congruent with the carrier;
3. text deliberately conflicting with the carrier.

The result maps control authority. It does not attempt to optimize the carrier,
strength and prompt simultaneously.

## Prompt dimensions worth characterizing

### 1. Kinematic operator

Use physically distinct language when physically distinct results are wanted:

| Language | Intended distinction |
| --- | --- |
| zoom in / out | focal length changes; camera body remains stationary |
| push in / pull out | camera translates forward / backward |
| pan | stationary camera pivots horizontally |
| truck | camera translates horizontally |
| tilt | stationary camera pivots vertically |
| pedestal | camera translates vertically |
| arc | camera travels around a subject or center |
| tracking | camera follows a moving locus |
| roll | camera rotates around the optical axis |

The published guide adds amplitude and speed only when meaningful. `Fast
zoom`, `fast push` and `fast recursive traverse` are not stylistic synonyms;
the FL2VA matrix tests whether H3's output respects their geometric difference.

### 2. Observable path

Prefer consequences that can appear in frames:

- foreground regions pass the camera;
- parallax changes continuously;
- occlusions open or close;
- scale changes monotonically;
- newly revealed regions become the next visible space;
- remaining differences narrow toward the last frame.

Words such as `cinematic`, `beautiful`, `dynamic` or `seamless` cannot by
themselves specify a trajectory. They may describe a preference, but they are
weak experimental variables unless paired with observable behavior.

### 3. Temporal profile

Separate motion type from its time law:

- uniform velocity;
- monotonic acceleration;
- monotonic deceleration;
- accelerate, then decelerate into the endpoint;
- explicit phase boundaries at exact seconds.

The output can then be measured as an optical-flow magnitude curve instead of
judged only from a global impression.

### 4. Endpoint policy

For FL2VA, distinguish these outcomes:

- land on the final image only at the final moment;
- land early and hold;
- approach but miss;
- dissolve or reset into the endpoint;
- preserve endpoint pixels but break motion immediately before them.

Pixel fidelity at the final frame and temporal quality in the preceding window
are separate measurements.

### 5. Instruction load

One primary gesture is the default for short characterization clips. Add
secondary subject motion, environmental motion, lighting change or multiple
camera operations only as later one-variable tests. A long prompt can be more
precise, but it can also contain competing trajectories and impossible timing.

### 6. Reference authority

For Ref2VA, test explicit roles rather than adding more assets at once:

- visible content or appearance;
- camera trajectory;
- local action or gesture;
- editing source;
- continuation source;
- timing or cut structure;
- weak style reference.

The official `fully_preserved`, `partially_preserved`, `attribute_transfer` and
`weak_reference` markers are candidates for a later fixed-input authority
matrix. Their presence in the guide is evidence that the syntax is expected;
their degree of behavioral control in the local quantized model is not yet
known.

### 7. Prompt embeddings

Official ComfyUI supports `embedding:` tokens for MiniMax H3, and the official
template points to ten downloadable style embeddings. These are learned
conditioning additions, not ordinary wording. They belong in a separate style
experiment after plain-text motion is stable, with one embedding and one fixed
prompt at a time. They are not required for movement control.

## Community observations: hypotheses, not facts

Recent community projects repeatedly propose three useful ideas:

- describe continuous physical logic rather than a succession of desired
  stills;
- turn vague relative timing into countable ratios or explicit phases;
- motivate transitions through visible occlusion, parallax or an action that
  causally reveals the next state.

Some reports also advocate hundreds of lines of locks and prohibitions. Those
examples are not controlled comparisons, and a successful public clip does not
establish that prompt length or a named phrase caused the result. The project
keeps the causal ideas as hypotheses but does not adopt large prompt directors,
automatic captioners or negative-constraint walls as dependencies.

## Evaluation protocol

Each matrix in `prompting/catalog.json` changes the exact prompt and nothing
else. Every invocation must retain:

- ordered source hashes;
- H3 family and exact model files;
- acceleration profile;
- canvas, frame count and 24 fps clock;
- seed, sampler, scheduler, steps and shifts;
- exact API graph hash and exact prompt bytes;
- prompt id, runtime manifest, artifact and receipt;
- a human visual verdict.

### Screening

Use one seed and the same eight-step FL2VA profile for every variant in a
matrix. This is a cost-efficient sensitivity screen, not final quality
evidence. If the outputs are pixel-identical or perceptually indistinguishable,
first verify that the prompt field reached `MiniMaxH3ImageToVideo`; do not infer
that wording never matters.

### Confirmation

For the best two variants, use the `quality-20` profile and at least three
seeds. A technique is retained only if its intended effect repeats and does not
trade away endpoint fidelity or temporal coherence beyond the accepted bound.
Acceleration-specific behavior is recorded as such.

### Measurements

Machine diagnostics:

- output count, geometry, duration and file integrity;
- first/last anchor PSNR, SSIM and perceptual difference;
- optical-flow direction and magnitude over time;
- velocity and jerk curves;
- cut/reset/near-static-hold candidates;
- pairwise fixed-seed differences between prompt variants;
- runtime and peak shared-host resources.

Human review:

- whether the requested physical movement is actually present;
- continuity of path and occlusion;
- endpoint arrival quality, not just endpoint pixels;
- unwanted morphing, dissolves, duplicated gestures or frozen intervals;
- whether extra language made the result more controllable or merely busier.

No numeric metric is a substitute for visual acceptance.

## Execution order

`prompting/catalog.json` contains exact English prompts in three stages.

### Stage 1 — FL2VA response surface

1. terse phrase vs concise official path vs timed official path;
2. optical zoom vs physical push vs recursive spatial traverse;
3. uniform vs accelerating vs accelerate-then-land timing.

These nine screening runs answer the most immediate production question: what
language gives a useful and repeatable path between two fixed frames?

### Stage 2 — adjacent native conditioning

1. I2VA single clause vs causal path vs timed path;
2. Ref2VA flat role instruction vs official six-section role binding;
3. AddGuide neutral continuity vs gap generation vs duration expansion.

### Stage 3 — text/control authority

Run neutral, congruent and conflicting text against one fixed, already useful
Fun Control carrier. Control strength, interval and preprocessing remain fixed.

Only after these stages should the project optimize prompt embeddings, style
language, multiple simultaneous motions, reference count, control strength or
automatic rewriting.

## What remains genuinely open

- Whether the full public Context-IR-like structure is better than concise
  natural language at five seconds.
- Whether the local quantized Qwen encoder follows exact timing strongly enough
  to shape velocity rather than only scene order.
- Whether `zoom` and `push` produce a stable geometric distinction across
  seeds.
- Whether FL2VA endpoint alignment benefits from exact effective duration
  (`frames / 24`) or a rounded editorial duration in ComfyUI.
- Whether Ref2VA retention markers change authority or mainly help prompt
  organization.
- Whether AddGuide gap language changes generated motion once guide states are
  already exact.
- Whether aligned text strengthens Fun Control or merely duplicates it.
- Whether style embeddings preserve or interfere with movement and endpoint
  fidelity.

These are experiment questions, not missing node features.

## Sources

- [MiniMax H3 official repository](https://github.com/MiniMax-AI/MiniMax-H3)
- [Official H3 prompt-writing skill](https://github.com/MiniMax-AI/MiniMax-H3/tree/main/.agents/skills/h3-prompt-writing)
- [Official base-mode prompt guide](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/.agents/skills/h3-prompt-writing/references/base-en.txt)
- [Official Ref2VA prompt guide](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/.agents/skills/h3-prompt-writing/references/ref-en.txt)
- [Official ComfyUI H3 nodes](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_minimax_h3.py)
- [Official ComfyUI H3 workflow templates](https://github.com/Comfy-Org/workflow_templates/tree/main/templates)
- [H3 prompt journal, inspected only for community hypotheses](https://github.com/LoveRain1997/h3-prompt-journal)
- [Community H3 Guide nodepack, inspected only as design reference](https://github.com/ethanfel/ComfyUI-MiniMax-H3-Guide)
- [Community H3 Prompt Writer, inspected only as design reference](https://github.com/duckyshell/ComfyUI-MiniMaxH3-Prompt-Writer)


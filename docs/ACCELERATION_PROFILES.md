# H3 acceleration profiles

Checked on 2026-09-01. Acceleration is an execution profile applied to an
existing operation. It is not a new CAUCE operation, sampler implementation or
workflow family.

## Current state versus chosen target

The 2026-08-31 capture proves these trunks are present:

```text
minimax_h3_fl2va_pruned_fp8_scaled.safetensors
minimax_h3_ref2va_pruned_fp8_scaled.safetensors
```

Those files are incidental installation state, not an architectural decision.
The host already runs an RTX 5090, PyTorch `2.13.0+cu130` and
`comfy-kitchen 0.2.31`. Comfy-Org explicitly recommends `int8_convrot` when the
CUDA 13 path is available and reserves `fp8_scaled` as a fallback. The selected
target trunks are therefore:

```text
minimax_h3_fl2va_pruned_int8_convrot.safetensors   20,970,379,616 bytes
minimax_h3_ref2va_pruned_int8_convrot.safetensors  20,970,379,616 bytes
```

They replace rather than supplement the two 20,958,205,608-byte FP8-scaled
files after one-at-a-time verification. Net steady-state storage growth is only
about 24 MB across both trunks. The existing Qwen3-VL NVFP4 encoder and H3
video/audio VAEs remain appropriate.

`pruned` is intentional: the approximately 21 GB trunks fit the 32 GB device
and retain the required FL2VA/Ref2VA surfaces. Full dense trunks are not needed
for this production runtime. Experimental W4A8/GGUF alternatives may save more
memory but add loaders and uncertainty without solving a current constraint.

Current project graphs use `simple`, 20 steps and `res_multistep`. The target
`int8_convrot` 20-step graph becomes the quality baseline before any fast LoRA
is accepted.

The same semantic operation may select one execution profile:

```text
operation + inputs + seed + geometry
  -> quality-20
  -> turbo-fl2va-8
  -> turbo-fl2va-4
  -> turbo-ref2va-4
  -> pdd-fl2va-8
  -> pdd-ref2va-8
```

Changing profile must be visible in the invocation and receipt. A fast result
cannot silently overwrite or masquerade as a quality-baseline artifact.

## Tier 1: LightX2V Turbo

Turbo is the lowest-risk acceleration route for the target host:

- it uses the ordinary ComfyUI LoRA loader;
- the official ComfyUI templates demonstrate Turbo LoRAs with the selected
  pruned `int8_convrot` H3 strategy;
- it requires no custom sampler or nodepack;
- FL2VA and Ref2VA have separate compatible weights;
- model strength must remain an explicit graph parameter.

Observed Comfy-Org model revision:

```text
repository  Comfy-Org/MiniMax-H3
revision    4cc1d817b6184899b41293954329f576cb5ae86b
```

| Profile | File | Size | Intended use |
| --- | --- | ---: | --- |
| `turbo-fl2va-8` | `minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors` | 1,956,193,000 bytes | default fast FL2VA iteration with a better quality/speed compromise |
| `turbo-fl2va-4` | `minimax_h3_fl2v_turbo_4step_v1.0_768p_comfyui_bf16.safetensors` | 1,956,192,992 bytes | fastest FL2VA scouting at the native 768-class training geometry |
| `turbo-ref2va-4` | `minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors` | 1,956,193,000 bytes | fast reference-driven scouting |

The FL2VA Turbo files must not be applied to the Ref2VA trunk, or vice versa.
The nominal step count is part of the profile and should match the selected
weight in the first accepted baseline. Alternative step counts are research
variants, not production defaults.

### Recommended Turbo use

```text
idea search / broad ladders       turbo-4
ordinary workflow iteration       turbo-8 when available
reference-composition iteration   turbo-ref2va-4
acceptance candidate              quality-20 comparison
final or uncertain material       quality-20
```

The approximate speed gain cannot be inferred from step count alone because
text encoding, VAE work, model loading, control preprocessing and saving are
fixed costs. Sampler work should nevertheless fall substantially from 20 to 8
or 4 evaluations.

## Tier 2: official PDD acceleration LoRAs

Alibaba PAI's Parallel Decoding Distillation weights combine a rank-64 trunk
LoRA with a bank of 32 interval-specific output heads. ComfyUI support was
merged in commit:

```text
2504e68d4d9dedb514e172692f13436623f25aed
```

The laboratory capture predates that commit, so PDD is not currently available
even if a weight is copied to disk. Core must be updated and baseline-smoked
first.

The original Alibaba files use Diffusers layout. Current stock ComfyUI expects
a converted Comfy-format file containing both the trunk LoRA and head bank.
The observed public conversion source is:

```text
repository  Kijai/MiniMax-H3-experimental
revision    f4cac997f880e93cf6940af61ee8d58ef31ff7f3
```

| Profile | File for selected pruned trunks | Size |
| --- | --- | ---: |
| `pdd-fl2va-8` | `MiniMax-H3-FL2VA-Acc-8Step_pruned_comfy.safetensors` | 1,725,921,392 bytes |
| `pdd-ref2va-8` | `MiniMax-H3-Ref2VA-Acc-8Step_pruned_comfy.safetensors` | 1,725,921,392 bytes |

The unpruned PDD conversions are not correct choices for the selected
`*_pruned_int8_convrot` trunks. Upstream testing specifically reported the
pruned conversions working on pruned `int8_convrot`, `fp8_scaled` and `nvfp4`
layouts on an RTX 5090.

### PDD invariants

The first profile is deliberately narrow:

```text
steps          8
scheduler      simple
sampler        euler or res_multistep, tested separately
LoRA strength  1.0
family         FL2VA weight on FL2VA trunk; Ref2VA weight on Ref2VA trunk
```

The output-head bank was trained for 8-step interval coverage. Lower LoRA
strength can partially populate the resized heads and produce artifacts;
off-grid schedules or other step counts are not accepted defaults. PDD must
not be combined with Turbo or an internal KJ H3 model patch in its first test.

Upstream testing on an RTX 5090 reported PDD functioning with pruned
`int8_convrot`, `fp8_scaled` and `nvfp4` trunks, but that is compatibility
evidence, not proof for this exact portable runtime. A live paired smoke remains
mandatory.

## Tier 3: memory and kernel optimizations

These mechanisms are not synonymous with faster sampling:

- `MiniMaxChunkFeedForward` lowers peak memory but adds calls and can be slower;
- `MiniMaxLowVRAMAttention` trades memory for overhead;
- SageAttention/VSA paths depend on current CUDA, PyTorch and Blackwell kernels
  and have unresolved compatibility reports;
- replacing `fp8_scaled` with the official preferred `int8_convrot` path is a
  baseline migration, not an accelerator to mix into a LoRA A/B.

Do not combine these with Turbo/PDD during initial characterization. Otherwise
the cause of a speed, quality or stability difference becomes ambiguous.

## Paired evaluation design

Every candidate uses the same:

- semantic operation and topology;
- input hashes;
- seed;
- legal frame count and native pixel geometry;
- prompt and references/guides;
- output codec settings.

Record:

- end-to-end wall time;
- sampler-only time if available;
- peak VRAM and RAM;
- first-run versus hot-model time;
- motion continuity;
- prompt/reference/guide adherence;
- texture and fine structure;
- terminal-frame stability;
- any audio-state or masked-edit regression even when audio is not delivered.

The initial ladder is:

```text
quality-20 / simple / res_multistep
turbo matching family / nominal steps / simple / res_multistep
pdd matching pruned family / 8 / simple / res_multistep
```

For FL2VA, test Turbo 8 before Turbo 4. For Ref2VA, the available official
Turbo candidate is 4-step. PDD enters only after the updated core reproduces
the unchanged quality baseline.

## Installation order

1. reconcile clean queue, free disk and current model list;
2. update core alone to a pinned commit containing PDD and current H3 fixes;
3. restart and reproduce the unchanged FP8 20-step baselines;
4. stage one FL2VA `pruned_int8_convrot` trunk while retaining its FP8 fallback;
5. run the unchanged 20-step graph and record quality/time/memory;
6. only after success retire the old FL2VA FP8 file;
7. repeat the same isolated replacement for Ref2VA;
8. add one Turbo LoRA only; no simultaneous code mutation;
9. restart/reload model inventory and run the paired FL2VA smoke;
10. add the matching Ref2VA Turbo file only after FL2VA evidence;
11. run the unchanged 20-step baseline before adding any PDD weight;
12. add one pruned PDD conversion and run exactly 8-step `simple`;
13. retain only profiles whose measured time savings justify their visual cost.

Downloading all three Turbo files consumes about 5.87 GB. Both pruned PDD
files add about 3.45 GB. Start with one file per active conditioning family and
preserve the host's disk reserve.

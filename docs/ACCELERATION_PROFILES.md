# H3 acceleration profiles

Live-checked on 2026-09-02. Acceleration is an execution profile applied to an
existing H3 operation. It is not a new CAUCE operation, sampler, or workflow
family.

## Current runtime

The production trunks are now the pruned CUDA-13 `int8_convrot` variants:

```text
minimax_h3_fl2va_pruned_int8_convrot.safetensors   20,970,379,616 bytes
minimax_h3_ref2va_pruned_int8_convrot.safetensors  20,970,379,616 bytes
```

The former FP8-scaled trunks were retired only after one-at-a-time download,
digest verification, model refresh, and H3 sampling. They are no longer on the
host. The Qwen3-VL NVFP4 encoder and H3 video/audio VAEs remain unchanged.

`pruned` is intentional: the approximately 21 GB trunks fit the RTX 5090's
34.19 GB reported VRAM while retaining the FL2VA and Ref2VA surfaces. The live
runtime is ComfyUI `0.34.0`, frontend `1.51.9`, PyTorch `2.13.0+cu130`, and
`comfy-kitchen 0.2.31`.

The same semantic operation may select exactly one profile:

```text
operation + inputs + seed + geometry
  -> quality-20
  -> turbo-fl2va-8
  -> turbo-fl2va-4
  -> turbo-ref2va-4
  -> pdd-fl2va-8
  -> pdd-ref2va-8
```

The selected profile must be explicit in the invocation, output prefix, and
receipt. A fast result must never masquerade as a 20-step quality result.

## Installed artifacts

All files below were independently downloaded and SHA-256 verified by Model
Control. Turbo and PDD are family-specific and must never be stacked.

| Profile | Artifact | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `quality-20` FL2VA | `minimax_h3_fl2va_pruned_int8_convrot.safetensors` | 20,970,379,616 | `e889202c41dafb67b10d67b97f0d8541508036a6090af23425a5c2615d03c47a` |
| `quality-20` Ref2VA | `minimax_h3_ref2va_pruned_int8_convrot.safetensors` | 20,970,379,616 | `9255f52b6677845ad238f20dfaafa94727053694127ab7f255c048f0f9365779` |
| `turbo-fl2va-8` | `minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors` | 1,956,193,000 | `2339acdf19bfe123f46b971ea35d367a84adb85de43627e1eceafa5a5b2b111e` |
| `turbo-fl2va-4` | `minimax_h3_fl2v_turbo_4step_v1.0_768p_comfyui_bf16.safetensors` | 1,956,192,992 | `c396a9a06f58399e9df9754b18299818d84a2ddd371724ba48fe4a41221437dc` |
| `turbo-ref2va-4` | `minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors` | 1,956,193,000 | `5b9ab5ade15d0775676d01a907268a69a1468dc6033b3b0d3ded5502f3ebb84c` |
| `pdd-fl2va-8` | `MiniMax-H3-FL2VA-Acc-8Step_pruned_comfy.safetensors` | 1,725,921,392 | `e97b813a6f857b9dab310f31ec30a8334f63a3e7dcb5d07c0c91933d3447a897` |
| `pdd-ref2va-8` | `MiniMax-H3-Ref2VA-Acc-8Step_pruned_comfy.safetensors` | 1,725,921,392 | `6f18e1c2eccb14b37322607730f26b16bf1169b56cd098ea006cffaec43d1e39` |

The trunks and Turbo files use Comfy-Org revision
`4cc1d817b6184899b41293954329f576cb5ae86b`. The pruned PDD conversions
use Kijai revision `f4cac997f880e93cf6940af61ee8d58ef31ff7f3`.

## Profile topology

### `quality-20`

```text
selected INT8 trunk
  -> official H3 conditioning
  -> BasicScheduler(simple, 20, denoise=1)
  -> KSamplerSelect(res_multistep)
  -> SamplerCustomAdvanced
```

This is the comparison baseline for final or uncertain material. A successful
Ref2VA INT8 smoke was retained as prompt
`c5c08436-f19f-43f0-8f3b-caaef8d9e3bb`; the 22-frame 512×288 technical run
took approximately 17.7 seconds end to end.

### Turbo

Turbo uses ordinary `LoraLoaderModelOnly` at strength `1.0`, the matching
family trunk, `simple`, the nominal 8 or 4 steps, and `res_multistep`.

```text
FL2VA INT8 -> FL2VA Turbo 8 or 4
Ref2VA INT8 -> Ref2VA Turbo 4
```

Never apply an FL2VA Turbo file to Ref2VA or the reverse. Alternative step
counts and strengths are experiments, not defaults.

Recommended use:

```text
broad scouting                   turbo-fl2va-4
ordinary FL2VA iteration         turbo-fl2va-8
reference-driven iteration       turbo-ref2va-4
acceptance/final comparison      quality-20
```

### PDD

The PDD files combine a trunk LoRA with interval-specific output heads. The
accepted technical profile is deliberately narrow:

```text
steps          8
scheduler      simple
sampler        res_multistep
strength       1.0
family         matching pruned FL2VA or Ref2VA trunk
```

Do not lower strength, use off-grid schedules, or stack PDD with Turbo or a KJ
model patch. Those changes confound the output-head behavior.

## Live technical smoke matrix

All rows used one 512×288, 22-frame graph at 24 fps, seed `20260902`, the
matching INT8 trunk, `simple`, and `res_multistep`. Times include model/cache
effects and are not a controlled benchmark.

| Profile | Prompt id | Result | Approx. end-to-end |
| --- | --- | --- | ---: |
| `turbo-fl2va-8` | `5e6d4384-c5f4-48a5-9ff9-8864f654929e` | success | 20 s cold |
| `turbo-fl2va-4` | `94c99dad-ba3e-4f60-a7da-8be0b0208537` | success | 3.4 s hot |
| `turbo-ref2va-4` | `efcaf613-0427-46c4-84cc-ab666c11aa21` | success | 13 s |
| `pdd-fl2va-8` | `3f292788-5c4f-4528-a5c5-c2d9b20ed180` | success | 13.6 s |
| `pdd-ref2va-8` | `926ea996-8eeb-458e-ad37-2da187427c83` | success | 13.4 s |

`success` means the exact graph loaded, sampled, decoded, and saved without an
exception. It does not mean the image quality, motion, identity, or prompt
adherence has passed human review. No fast profile is promoted over
`quality-20` until a fixed-input visual ladder is judged.

Exact executable smoke graphs are retained under
`workflows/smoke/2026-09-02/` and the runtime evidence is in
`runtime/smokes/2026-09-02-h3-runtime.json`.

## Controlled 1344×768 characterization

The first fixed-input visual ladder ran on 2026-09-02 with a fresh runtime
manifest, the same input, prompt, seed, 73-frame geometry, scheduler, sampler,
and codec path. Quality 20 took 133.186 seconds; Turbo 8 took 56.658 seconds
(2.35× faster); PDD 8 took 54.629 seconds (2.44× faster).

Turbo and PDD remain unpromoted. Their SSIM against quality 20 was 0.669033 and
0.641949 respectively, while their pairwise SSIM was 0.579774. These values
show that acceleration changes the generative trajectory; they do not rank
aesthetic quality. Exact graphs, prompt ids, hashes, structural-control results,
and the pending human-review gate are recorded in
`docs/LIVE_CHARACTERIZATION_2026-09-02.md` and
`runtime/characterizations/2026-09-02-h3-visual-ladder.json`.

## Evaluation protocol

Every comparison holds constant:

- semantic operation and graph topology;
- input hashes and ordering;
- seed, legal frame count, and native pixel geometry;
- prompt, references, endpoints, and guides;
- output fps and codec settings.

Record end-to-end and sampler-only time when available, first-run versus hot
state, peak VRAM/RAM, motion continuity, conditioning adherence, texture,
fine structure, and terminal-frame stability. A useful production comparison
must include the same `quality-20` output.

## Memory and kernel patches

KJNodes is installed for generic utilities and diagnostics, but its H3 memory
patches are not acceleration defaults:

- `MiniMaxChunkFeedForward` may lower peak memory while adding calls;
- `MiniMaxLowVRAMAttention` trades memory for overhead;
- SageAttention/VSA paths remain coupled to Blackwell/CUDA/PyTorch kernels.

Activate one only after a measured OOM or peak-memory problem, then compare it
against the unchanged graph. The current trunks fit; no resource failure
justifies speculative kernel mutation.

## Storage and rollback

The three Turbo files consume approximately 5.87 GB and the two PDD files about
3.45 GB. Model Control provides exact inventory, digest verification, and
bounded deletion for every listed file. Generated media and temporary assets
still share the host's limited storage, so preserve the declared reserve.

Rollback is a profile selection, not a CUDA/PyTorch rollback:

1. select `quality-20` and remove the LoRA edge from the graph;
2. verify the queue is idle;
3. delete an unused accelerator only through Model Control;
4. never reinstall the retired FP8 trunks unless a measured INT8 regression
   requires an explicit A/B.

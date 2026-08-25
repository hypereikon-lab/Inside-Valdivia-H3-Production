# Laboratory runtime audit — 2026-08-25

Read-only capture through the authenticated ComfyUI origin.

## Runtime

```text
ComfyUI                 0.33.0
required frontend       1.49.6
Python                  3.12.10 embedded, Windows
PyTorch                 2.13.0+cu130
GPU                     NVIDIA GeForce RTX 5090
GPU memory              34,190,458,880 bytes reported by runtime
RAM                     67,768,381,440 bytes reported by runtime
registered node types   913
frontend extensions     53
queue                    empty
Manager queue            idle
```

The physical GPU/RAM envelope matches the expected 32 GiB-class RTX 5090 and
64 GiB system-memory workstation. This capture does not measure free disk.

## H3 capabilities present

Official node schemas are present for:

- `EmptyMiniMaxH3LatentAV`
- `MiniMaxH3ImageToVideo`
- `MiniMaxH3ReferenceToVideo`
- `MiniMaxH3AddGuide`
- `MiniMaxH3SigmaShift`

The three external native-continuation nodes are absent.

The required local H3 model families are already visible through `/models`:

```text
diffusion_models/minimax_h3_fl2va_pruned_fp8_scaled.safetensors
diffusion_models/minimax_h3_ref2va_pruned_fp8_scaled.safetensors
text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors
vae/minimax_h3_video_vae_fp16.safetensors
vae/minimax_h3_audio_vae_fp32.safetensors
```

No additional model download is part of the planned custom-node deployment.

## Installed CAUCE state

Manager reports `hypereikon-lab/ComfyUI-Cauce` enabled at commit
`6c604413572cec8f7119a823eb15d108e50adb6a`. The live registry still exposes 26
pre-cleanup node types, including rejected sampler/latent experiments. Neither
`CaucePrepareH3TwoSidedGuideWindow` nor
`CauceAssembleH3TwoSidedGuideWindow` is present.

CAUCE 2.1 commit `dc1eb19c7c131c82e0768a16a430485d049bc3b0` is now the public repository's
default-branch head but has not yet been deployed to the laboratory.

## Workspace layer

The current frontend exposes the required public surfaces:

- `app.extensionManager.workflow`
- `app.extensionManager.command`
- `app.loadGraphData`
- `app.loadApiJson`
- `app.graphToPrompt`
- core command `Workspace.CloseWorkflow`

`GET /workspace-control/capabilities` returns 404 because the new extension is
not installed yet.

## Evidence state

```text
tunnel/runtime reachability                    observed
official H3 schema availability                schema-validated
CAUCE 2.1 local deterministic layer            unit-validated
CAUCE 2.1 live node availability               pending deployment
Workspace Control live availability            pending deployment
native continuation live availability          pending deployment
W1-W7 concrete graph execution                 not claimed by this audit
```

Manager reports three saved workflows and none references a `Cauce*` node.
Replacing the old CAUCE registry therefore has no detected saved-workflow
dependency. The currently open unsaved browser workflow remains user-owned and
must not be closed automatically.

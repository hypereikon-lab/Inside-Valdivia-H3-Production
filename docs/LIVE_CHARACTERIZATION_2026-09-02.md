# H3 live characterization — 2026-09-02

This batch closes the first fixed-input visual ladder on the current INT8
runtime. It deliberately does not promote a workflow: all graphs executed, but
motion quality and artistic usefulness remain a human review decision.

## Runtime gate

The fresh content-addressed manifest is
`runtime/manifests/2026-09-02-live.json`, hash
`a3cc30305d3a82b78142aaa149d54e804b2a5841dd150c84637d03212ed3f392`.
It captures 1,185 live node schemas plus `/features`, `/system_stats`,
`/extensions`, `/models`, and an idle `/queue`. Core, full, and experimental
control requirements all pass against this exact manifest.

The compatibility lock previously carried an accidental future timestamp. It
now uses the actual commit time of the lock (`2026-09-02T00:56:24-04:00`), so a
newer runtime capture is no longer classified as stale.

## FL2VA quality ladder

Held constant: the same 2560×1440 input PNG and hash, 1344×768 generation,
73 frames, 24 fps, seed `20260902`, prompt, `simple`, `res_multistep`, and
`denoise=1`. Only the sampling profile changed.

| Profile | Steps | Remote execution | Speedup | Mean adjacent luma delta | SSIM vs 20-step |
| --- | ---: | ---: | ---: | ---: | ---: |
| quality | 20 | 133.186 s | 1.00× | 2.048734 | 1.000000 |
| Turbo FL2VA | 8 | 56.658 s | 2.35× | 2.102687 | 0.669033 |
| PDD FL2VA | 8 | 54.629 s | 2.44× | 1.978352 | 0.641949 |

Turbo and PDD have pairwise SSIM `0.579774`; they are materially different
generation trajectories. SSIM is not a quality score here. It only prevents us
from pretending the two acceleration families are equivalent.

The exact graphs live under `workflows/evaluations/2026-09-02/`. The local
comparison video is ordered left-to-right: quality 20, Turbo 8, PDD 8.

## Fun Control structural carriers

The first 73 frames of the existing 960×960 domemaster clip were used at
768×768. The first decoded frame, prompt, seed, 20-step sampler, Fun Control
patch, strength, and activation interval were held constant.

| Carrier | Remote execution | Mean adjacent luma delta | Ratio vs source | SSIM vs decoded source |
| --- | ---: | ---: | ---: | ---: |
| source window | — | 12.094216 | 1.000 | 1.000000 |
| Canny | 72.495 s | 9.871510 | 0.816 | 0.616813 |
| DA3 depth | 70.052 s | 9.198796 | 0.761 | 0.578479 |

Both preserve the circular domemaster boundary and execute without OOM. On
this source, Canny retains more of the decoded trajectory and change magnitude;
DA3 depth is more reconstructive. That makes Canny the first candidate for
human review when exact camera path/projection matters. Depth remains useful
for experiments where geometric organization matters more than pixel/path
fidelity.

The local control comparison is ordered left-to-right: decoded source, Canny,
DA3 depth.

## Closeout

ComfyUI ended with an empty queue. The run briefly left H3, Fun Control, and
DA3 cached simultaneously, reducing reported free RAM and VRAM. The ordinary
`/free` route unloaded models and released memory without a restart or file
mutation; final free memory was approximately 54.66 GB RAM and 32.26 GB VRAM.

The machine-readable evidence, prompt ids, output hashes, and metrics are in
`runtime/characterizations/2026-09-02-h3-visual-ladder.json`. The next gate is
human review of the two comparison videos. Until then the characterization
status is `executed-pending-human-review`, not `visually-accepted`.

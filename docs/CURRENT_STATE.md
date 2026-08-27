# Current state

This is the authority for present capability claims.

## Source state

```text
CAUCE
  commit   dcb48570b362cbbdcb9d5b739c6b1c0ca278fa40
  version  5.2.0
  nodes    20
  operations / topology dossiers  10 / 28
  local tests  40 passing

Runtime Control
  commit   980e0100e3ef763426ac467763a7f8889cff8409
  version  0.4.0
  local tests  20 passing

Workspace Control
  commit   56c1687df1454da849f095973635d2b745083b3a
  version  0.3.0
  local tests  7 passing

Production data
  exact CAUCE commit/catalog/contract lock
  28 offline materialization plans
  12 controlled experiment definitions
  1 offline rolling-chain plan
  2 runtime requirements profiles
  10 acceptance profiles covering all 28 variants
  0 visual assessment records until live artifacts exist
  1 six-phase live materialization gate
  1 fail-closed storage policy
  local tests  23 passing
```

All 40 CAUCE tests pass under the bundled local Python runtime with NumPy. A
reduced interpreter without NumPy is not release evidence. Across the four
active repositories the complete offline suites currently contain 90 passing
checks.

The local source repositories are complete and content-addressed. On 2026-08-26
the authenticated laboratory runtime was updated through Manager to the exact
CAUCE commit above, restarted at process level, and re-probed through the same
Cloudflare tunnel.

## Live runtime verification

```text
ComfyUI       0.33.0
frontend      1.49.6
PyTorch       2.13.0+cu130
device        NVIDIA GeForce RTX 5090
total VRAM    34,190,458,880 bytes
total RAM     67,768,381,440 bytes
CAUCE commit  dcb48570b362cbbdcb9d5b739c6b1c0ca278fa40
CAUCE nodes   20 present / 0 missing / 0 legacy motion nodes
queue         idle after restart and deterministic smokes
```

The process restart produced transient 502 responses and recovered through the
unchanged tunnel after 8.8 seconds. No ComfyUI core, CUDA, PyTorch, driver,
model, Manager, or unrelated custom-node update was requested.

Two non-generative prompt-id smokes executed successfully on the live process:

- `CauceH3ExpandAVCanvas`: 22-frame 64x64 native state placed at `(32,32)` in
  a 128x128 canvas, with exact source and target latent shapes reported;
- `CauceH3ApplyVideoDenoiseMask`: one static 0.5 mask projected over all seven
  native visual tokens, reporting result minimum and maximum both equal to 0.5.

The reports are tiny JSON artifacts under `output/cauce/live_smoke`. These
smokes prove the deterministic node paths load and execute; they do not prove
H3 sampling quality, useful outpaint, masked-edit locality, or refinement.

## What is implemented

CAUCE provides deterministic primitives for:

- exact half-open decoded-frame ranges;
- H3 24 fps visual-token and 40 Hz structural-audio layout arithmetic;
- packed AV window allocation, span extraction and absolute placement;
- independent continuous video/audio denoise masks with linear, smoothstep,
  and smootherstep ramps;
- static and per-frame continuous video-mask projection onto native H3 tokens;
- exact 32-pixel-aligned native canvas expansion for outpainting;
- exact native AV interval replacement;
- native span guides, synchronized append, split/rollback, save, and load;
- H3 target/reference/guide preflight and conditioning inspection.

Official ComfyUI owns H3 first/last frames, Ref2VA references, arbitrary-frame
AddGuide conditioning, model loading, prompting, sampling, and decoding. CAUCE
composes those official mechanisms; it does not replace the model or sampler.

The ten operations are grouped as H3 conditioning grammar, native H3 AV state
algebra, and decoded media algebra. They are orthogonal functions, not workflow
stages. See [Project model](PROJECT_MODEL.md).

Runtime Control implements guarded materialization plus `comfy.run-series/1`:
all concrete graphs are validated against one fresh `/object_info`, each prompt
id is persisted atomically immediately after submission, exact submitted jobs
are resumed rather than duplicated, and every completed step receives an
immutable receipt. It intentionally neither interprets H3 nor binds one step's
outputs into the next graph.

Runtime Control 0.4 also evaluates project requirements against one full
content-addressed manifest. A manifest can come from direct HTTP access or from
bounded endpoint JSON captured inside an authenticated browser; browser cookies
are never extracted. Workspace Control 0.3 adds a browser-local diagnostic that
must pass before tab or graph automation begins.

## Operation evidence

| Operation | Current implementation evidence | Live/visual evidence |
| --- | --- | --- |
| `generate.keyframed` | official H3 contract + checked variants | not materialized at current lock |
| `generate.from_references` | official H3 contract + checked variants | not materialized at current lock |
| `generate.with_guides` | official H3/AddGuide contract + checked variants | not materialized at current lock |
| `continue.native_av` | CAUCE layout/span/mask paths unit-validated | older keyframe mechanism executed synthetically; current variants uncharacterized |
| `complete.native_av` | placement/mask/replacement layer unit-validated | not yet sampled live |
| `edit.masked_video` | static/animated mask projection and composition unit-validated | static mask primitive executes live; H3 result unassessed |
| `refine.video` | bounded native-state denoise contract unit-validated | useful strength range uncharacterized |
| `reframe.outpaint_video` | aligned allocation, exact copy, and new-region mask unit-validated | expansion primitive executes live; H3 result unassessed |
| `rollback.native_av` | synchronized split/branch layer unit-validated | not yet exercised in production |
| `frames.assemble` | deterministic range layer unit-validated | no inference claim |

`implemented`, `materialized`, `executes`, and `visually accepted` are separate
states. No current-lock topology yet has a retained paired UI/API graph. The
repository therefore makes no claim that any of the 28 variants is presently
production-ready or visually accepted.

## Offline-ready assets

The 28 materialization plans cover the entire CAUCE topology catalog. Their
static operation hashes, variants, model filenames, geometry, frame arithmetic,
input cardinality, mask semantics, and output slots are checked. Live-owned
values remain null: actual media ids, sampler, scheduler, steps, flow shifts,
seed, graph node ids, `/object_info` manifest, and paired graph hashes.

Stable catalog priority no longer doubles as empirical execution order. The
six phases in `materialization/live-gate.json` cover every topology once and
put core FL2VA controls before full Ref2VA/AddGuide and native-state mechanisms.
The runtime core and full profiles verify expected H3/CAUCE nodes, models,
hardware, and queue; free storage and physical recovery remain explicit manual
checks.

The rolling chain is also offline-ready. It specifies strict dependencies,
native-state identities, exact source commits, per-step checkpoints, and a
new-plan-from-checkpoint branch policy. It is not an executable Runtime Control
series until its selected materialization plans have concrete prebound API
graphs and operation-reference files.

## Next live gate

With the tunnel and CAUCE 5.2 now available:

1. persist the full content-addressed runtime manifest and verify free storage;
2. install and validate Workspace Control before any automated tab or graph
   mutation; it is not present in the currently loaded browser page;
3. materialize one graph at a time from the checked plans, beginning with a
   small operational core;
4. run exact prompt-id technical smokes, retain receipts and native state, then
   perform visual acceptance separately;
5. compile the accepted, explicitly prebound graphs into a Runtime Control
   serial plan and test interruption/resume before long unattended production.

Every graph must persist a resolvable video artifact through the current core
`CreateVideo -> SaveVideo` path. `VAEDecode` alone is not sufficient evidence
of a durable production result.

An HTTP 504 establishes only that the Cloudflare path could not reach a healthy
origin at that moment. It does not diagnose the tower, tunnel service, or
ComfyUI process, and it does not invalidate offline source work.

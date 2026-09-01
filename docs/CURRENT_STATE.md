# Current state

This is the authority for present capability claims.

## Source state

```text
CAUCE
  commit   5a3d3a23b79712ed07349079b8312da4cd3fe4de
  version  5.7.0
  nodes    24
  operations / topology dossiers / graph archetypes  12 / 32 / 29
  local release tests  47 passing, zero skips

Runtime Control
  commit   6751b8fd90b02ef871bc046f228b83b004871d3a
  version  0.6.0
  local tests  25 passing

Workspace Control
  commit   65d6612d1cbeae3e35c664873a2aa1088ac3e7d2
  version  0.4.2
  local tests  10 passing

Repository Control
  commit   49d50644173c62d74b799099fee2a2eddbfdf642
  version  1.0.1
  local tests  5 passing

Production data
  exact component commit/tree/version/metadata locks
  exact CAUCE operation and graph-archetype locks
  32 offline binding/materialization profiles over 29 graph archetypes
  1 retained paired UI/API graph validated against the captured live schema
  16 controlled experiment definitions
  2 schema-validated, explicitly gated H3 LoRA research recipes
  1 offline rolling-chain plan
  2 runtime requirements profiles
  12 acceptance profiles covering all 32 variants
  15 executed live project invocations, 17 API graphs and immutable run receipts
  3 explicit rejected visual assessment records
  1 eight-phase live materialization gate
  1 fail-closed storage policy
  local tests  27 passing
```

All 47 CAUCE tests pass under the bundled local Python runtime with NumPy. A
reduced interpreter without NumPy is not release evidence. Across the four
control repositories plus this production repository, the complete offline
suites currently contain 114 passing
checks.

The local source repositories are complete, public, pushed, and
content-addressed. CAUCE and Workspace Control are Registry-prepared but not
published; publishing still requires the `hypereikon-lab` Registry publisher
and its release secret. Runtime Control remains a separate source package;
Repository Control is a bounded public-Git extension.

## Live runtime state

The authenticated laboratory runtime was captured on 2026-08-31 as
`runtime/manifests/2026-08-31-live.json`, manifest SHA-256
`e97aa6c8e6f449e0f3d0f51fd3921e66c51f763de6d64de3ed9f2474019ba9c9`.
Its six endpoint payloads are retained separately under
`runtime/captures/2026-08-31/`. The capture reports ComfyUI 0.33.0, frontend
1.49.6, Python 3.12.10, PyTorch 2.13.0+cu130, 64 GB system RAM, an RTX 5090
with 34,190,458,880 bytes of VRAM, 914 node types, 27 model entries, and an
idle queue.

Both `h3-core` and `h3-full` requirements evaluate ready against that exact
manifest. This is stronger evidence than a guessed minimum version: the live
0.33.0 schema already exposes the AddGuide and continuous per-token mask
surface needed by the full profile, so no ComfyUI update is presently required.
Workspace Control 0.4.2 also reports `readiness.ready = true`; the saved
canonical text-only graph is clean and persisted. Manager/repository inventory
shows clean CAUCE, Workspace Control, and Repository Control checkouts at the
locked public commits. Runtime Control 0.6.0 documents the separate first-install, repository
fast-forward and process-restart planes; it is an external source package and
is not imported by the laboratory Comfy process.

After one guarded Comfy-only restart, the origin returned in 12 seconds with
the GPU queue idle, all 24 required CAUCE node types imported from
`custom_nodes.ComfyUI-Cauce`, and CAUCE, Workspace Control and Repository
Control still clean at their locked revisions. The bounded receipt is retained
at `runtime/verifications/2026-08-31-post-restart.json`. No CUDA, PyTorch,
driver, model, ComfyUI core, frontend, Windows or Cloudflare mutation occurred.

The first characterization batch is retained in
[`LIVE_BATCH_2026-08-31.md`](LIVE_BATCH_2026-08-31.md). All seventeen submitted
graphs completed and wrote resolvable `SaveVideo` artifacts plus native-state
paths where declared. The remaining platform checks are physical: free disk on
the actual model/output volume, Windows sleep policy, host/tunnel recovery, and
exact `LoadVideo` frame ordering for imported production clips.

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
- H3 target/reference/guide preflight and conditioning inspection;
- native H3 temporal-token dilation with exact delivery clocks, retained as a
  low-level primitive but rejected as a slow-motion composition;
- native H3 spatial latent resize and H3-VAE visual-stream graft;
- dense official-AddGuide temporal expansion at factor-spaced target indices.

Official ComfyUI owns H3 first/last frames, Ref2VA references, arbitrary-frame
AddGuide conditioning, model loading, prompting, sampling, and decoding. CAUCE
composes those official mechanisms; it does not replace the model or sampler.
The current official template and the characterized laboratory FL2VA graph use
the direct model-to-guider/scheduler path. `MiniMaxH3SigmaShift` remains a
native opt-in experiment, not a canonical dependency.

The twelve operations are grouped as H3 conditioning grammar, native H3 AV
state algebra, and decoded media algebra. They are
orthogonal functions, not workflow stages. See [Project model](PROJECT_MODEL.md).

Runtime Control implements guarded materialization plus `comfy.run-series/1`:
all concrete graphs are validated against one fresh `/object_info`, each prompt
id is persisted atomically immediately after submission, exact submitted jobs
are resumed rather than duplicated, and every completed step receives an
immutable receipt. It intentionally neither interprets H3 nor binds one step's
outputs into the next graph.

Runtime Control 0.5 also evaluates project requirements against one full
content-addressed manifest. A manifest can come from direct HTTP access or from
bounded endpoint JSON captured inside an authenticated browser; browser cookies
are never extracted. First installs now persist a mutation journal before the
Manager request and require reconciliation after an unknown transport outcome.
Workspace Control 0.4 adds browser-local dry-run plans for exact open/close
targets, whole-set close validation, and provenance-rich paired exports. Its
diagnostic must pass before tab or graph automation begins.

## Operation evidence

| Operation | Current implementation evidence | Live/visual evidence |
| --- | --- | --- |
| `generate.keyframed` | official H3 contract + checked variants | first-frame, last-frame and first/last execute at 1344×768 × 124; one run each, not promoted |
| `generate.from_references` | official H3 contract + checked variants | ordered two-image `match` binding executes; one run, not promoted |
| `generate.with_guides` | official H3/AddGuide contract + checked variants | single interior still is rejected; dense 2x/3x target-time guide ladders execute with positive operator review, while 4x executes and awaits review |
| `continue.native_av` | CAUCE layout/span/mask paths unit-validated | masked-overlap executes to 243 frames with exact decoded prefix preservation; promising, not promoted |
| `complete.native_av` | placement/mask/replacement layer unit-validated | two-source connection executes with preserved left/right contexts; measurable boundary rise remains |
| `edit.masked_video` | static/animated mask projection and composition unit-validated | static mask primitive executes live; H3 result unassessed |
| `refine.video` | bounded native-state denoise contract unit-validated | full-frame 0.20 executes with useful detail signal and moderate drift; ladder still required |
| `reframe.outpaint_video` | aligned allocation, exact copy, and new-region mask unit-validated | expansion primitive executes live; H3 result unassessed |
| `rollback.native_av` | synchronized split/branch layer unit-validated | split/reappend executes and matches all 124 decoded comparison frames; promotion still needs independently persisted prefix/suffix checkpoints |
| `frames.assemble` | deterministic range layer unit-validated | no inference claim |
| `densify.temporal` | native token-lattice geometry, masks, exact decoded-anchor restoration, tail crop, and delivery clock unit-validated | rejected as slow motion in same-duration 2x and duration-expansion 2x/3x tests; generated gaps follow a reinterpreted trajectory rather than the source cadence |
| `regenerate.spatial` | latent resize and H3-VAE visual-stream graft unit-validated; three offline topologies | 1792×1024 latent second pass fits the 5090 and executes; 0.35 gains detail but drifts too far for a baseline |

`implemented`, `materialized`, `executes`, and `visually accepted` are separate
states. Seventeen exact API graphs now have prompt-id receipts and saved artifacts;
the native temporal-dilation path is explicitly rejected. No generative variant has yet met its
minimum repeat count and visual promotion rule, so none is called
production-ready.

## Materialization assets

The 32 materialization plans cover the entire CAUCE topology catalog and map
through the locked archetype catalog to 29 distinct node/edge structures. Their
static operation hashes, variants, model filenames, geometry, frame arithmetic,
input cardinality, mask semantics, and output slots are checked. Live-owned
values remain null until pairing. The text-only control is the first
exception: its paired graph, sampler, scheduler, steps, seed, runtime manifest,
parameterization and content hashes are retained under `workflows/`. Its
creative prompt remains an invocation-time value.

Stable catalog priority no longer doubles as empirical execution order. The
eight phases in `materialization/live-gate.json` cover every topology once and
put core FL2VA controls before full Ref2VA/AddGuide and native-state mechanisms.
The runtime core/full profiles verify the relevant
nodes, models, hardware, and queue; free storage and physical recovery remain
explicit manual checks.

The rolling chain is also offline-ready. It specifies strict dependencies,
native-state identities, exact source commits, per-step checkpoints, and a
new-plan-from-checkpoint branch policy. It is not an executable Runtime Control
series until its selected materialization plans have concrete prebound API
graphs and operation-reference files.

## Next live gate

With the laboratory origin healthy, both automated runtime profiles passing and
the first live batch complete:

1. verify free storage, Windows sleep policy, and the agreed host/tunnel
   recovery path without changing the GPU stack;
2. repeat native continuation and two-source completion with a second seed and
   perform full-motion human review;
3. run fixed-source denoise ladders for refinement and spatial regeneration;
4. replace the rejected isolated still anchor with a legal guide clip;
5. redesign source preservation before repeating the rejected temporal 2× run;
6. persist rollback prefix and suffix independently, then repeat its deterministic
   round-trip acceptance check;
7. pair accepted API graphs with their UI graphs and compile only those accepted,
   explicitly prebound graphs into a Runtime Control serial plan.

Every graph must persist a resolvable video artifact through the current core
`CreateVideo -> SaveVideo` path. `VAEDecode` alone is not sufficient evidence
of a durable production result.

An HTTP 504 establishes only that the Cloudflare path could not reach a healthy
origin at that moment. It does not diagnose the tower, tunnel service, or
ComfyUI process, and it does not invalidate offline source work.

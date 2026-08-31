# Current state

This is the authority for present capability claims.

## Source state

```text
CAUCE
  commit   9172c30b37fc43272473409e6f42eaacc0a10e60
  version  5.6.0
  nodes    24
  operations / topology dossiers / graph archetypes  12 / 32 / 29
  local release tests  47 passing, zero skips

Runtime Control
  commit   6e1f6817d46d02282279c24cb84338e568ae9aea
  version  0.5.2
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
  31 offline binding/materialization profiles over 29 graph archetypes
  1 retained paired UI/API graph validated against the captured live schema
  16 controlled experiment definitions
  2 schema-validated, explicitly gated H3 LoRA research recipes
  1 offline rolling-chain plan
  2 runtime requirements profiles
  12 acceptance profiles covering all 32 variants
  0 visual assessment records until live artifacts exist
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
locked public commits. Runtime Control 0.5.2 documents the separate first-install, repository
fast-forward and process-restart planes; it is an external source package and
is not imported by the laboratory Comfy process.

After one guarded Comfy-only restart, the origin returned in 12 seconds with
the GPU queue idle, all 24 required CAUCE node types imported from
`custom_nodes.ComfyUI-Cauce`, and CAUCE, Workspace Control and Repository
Control still clean at their locked revisions. The bounded receipt is retained
at `runtime/verifications/2026-08-31-post-restart.json`. No CUDA, PyTorch,
driver, model, ComfyUI core, frontend, Windows or Cloudflare mutation occurred.

The remaining live checks are physical or artifact-level: free disk on the
actual model/output volume, Windows sleep policy, host/tunnel recovery, exact
`LoadVideo` frame ordering, and one resolvable `SaveVideo` artifact.

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
- native H3 temporal-token dilation with exact delivery clocks;
- native H3 spatial latent resize and H3-VAE visual-stream graft;
- sparse-guide H3 retime planning.

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
| `generate.keyframed` | official H3 contract + checked variants | text-only paired and schema-validated; not executed or visually assessed |
| `generate.from_references` | official H3 contract + checked variants | not materialized at current lock |
| `generate.with_guides` | official H3/AddGuide contract + checked variants | not materialized at current lock |
| `continue.native_av` | CAUCE layout/span/mask paths unit-validated | older keyframe mechanism executed synthetically; current variants uncharacterized |
| `complete.native_av` | placement/mask/replacement layer unit-validated | not yet sampled live |
| `edit.masked_video` | static/animated mask projection and composition unit-validated | static mask primitive executes live; H3 result unassessed |
| `refine.video` | bounded native-state denoise contract unit-validated | useful strength range uncharacterized |
| `reframe.outpaint_video` | aligned allocation, exact copy, and new-region mask unit-validated | expansion primitive executes live; H3 result unassessed |
| `rollback.native_av` | synchronized split/branch layer unit-validated | not yet exercised in production |
| `frames.assemble` | deterministic range layer unit-validated | no inference claim |
| `densify.temporal` | native token-lattice geometry, masks, tail crop, and delivery clock unit-validated | official H3 sampling and visuals unassessed |
| `regenerate.spatial` | latent resize and H3-VAE visual-stream graft unit-validated; three offline topologies | denoise range, VRAM, tiles, and visuals unassessed |

`implemented`, `materialized`, `executes`, and `visually accepted` are separate
states. One current-lock topology has a retained paired UI/API graph and zero
schema issues. It has not been queued. The repository therefore makes no claim
that any of the 32 variants is presently production-ready or visually
accepted.

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

With the laboratory origin healthy and both automated runtime profiles passing:

1. verify free storage, Windows sleep policy, and the agreed host/tunnel
   recovery path without changing the GPU stack;
2. bind a real text-only prompt, run its exact prompt-id technical smoke,
   retain the receipt and native state, then perform visual acceptance;
3. materialize the first-frame archetype and continue one graph at a time;
4. for accepted graphs, retain receipts and native state, then
   perform visual acceptance separately;
5. compile the accepted, explicitly prebound graphs into a Runtime Control
   serial plan and test interruption/resume before long unattended production.

Every graph must persist a resolvable video artifact through the current core
`CreateVideo -> SaveVideo` path. `VAEDecode` alone is not sufficient evidence
of a durable production result.

An HTTP 504 establishes only that the Cloudflare path could not reach a healthy
origin at that moment. It does not diagnose the tower, tunnel service, or
ComfyUI process, and it does not invalidate offline source work.

# Controlled H3 experiments

`experiments/catalog.json` contains nine planned, one-variable comparisons:
endpoint mode, reference-image sizing, reference duration, guide length, guide
placement, continuation prompt relation, native mask boundary, overlap
transport, and future guide.

Every run records source hashes/order, operation and materialized graph hashes,
model files, geometry, frame count, exact prompt/seed, sampler/scheduler/steps,
video/audio shifts, runtime manifest, prompt id, artifacts, the sole changed
variable, and a visual verdict.

Native masks are tested as the official H3 sampler consumes them: continuous
per-token video and structural-audio strengths. Comparisons isolate curve,
fade, boundary, or transport; they do not mix several changes and call the
result causal.

Metrics such as pixel difference, optical-flow magnitude, or queue completion
are diagnostic only. They cannot establish useful motion correspondence,
identity preservation, temporal boundary quality, or visual acceptance.

The scope excludes generative audio, soundtrack encoding, training, LoRA,
acceleration, streaming, and arbitrary sampler patches. The fixed soundtrack
is used only when assigning accepted outputs to the edit.

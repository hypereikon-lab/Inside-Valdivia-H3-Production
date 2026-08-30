# Technical and visual acceptance

`acceptance/catalog.json` defines one fail-closed profile for every locked
operation and covers all 31 materialization variants exactly once.

## Two independent judgments

Technical acceptance asks whether the declared data operation actually
occurred:

- graph matched the captured schema;
- prompt completed under one exact id;
- frame/token ranges and masks matched the plan;
- known state was preserved where required;
- outputs and checkpoints are resolvable from history;
- hashes and lineage are complete.

Visual acceptance asks whether the output is useful for its requested purpose:

- endpoint or reference correspondence;
- motion continuity;
- guide arrival and departure;
- absence of objectionable jumps, freezes, duplication, ghosting, tiling, or
  decode artifacts;
- acceptable preservation outside a regenerated interval.

Neither judgment substitutes for the other. A visually attractive untracked
result is not reproducible. A technically exact but visually poor result is
`rejected`, not a capability.

## Promotion rule

Generative operations require at least two technically successful inspected
runs before a variant can be treated as a production baseline. Deterministic
assembly and rollback round trips require one. Every profile requires:

```text
all technical checks = pass
explicit visual verdict = present
minimum successful run count = met
```

The profile describes what must be reviewed. Actual assessments belong to
project evidence and must reference exact invocation, receipt, artifact, graph,
runtime manifest, and reviewer. Acceptance is never written into the immutable
Runtime Control receipt after the fact.

`assessments/catalog.json` indexes these records under
`assessments/records/`. It is intentionally empty until a real artifact has
been inspected. The validator requires every recorded technical and visual
check to match its operation profile exactly, forbids an accepted verdict when
any check fails, and requires a rejected verdict to name at least one failed
visual check.

## Controlled comparisons

When an experiment changes one declared variable, reuse all possible immutable
inputs and record the value for every run. Pixel difference, optical flow, or
runtime can aid diagnosis, but the measure must still address the requested
property. Merely changing pixels does not demonstrate useful control.

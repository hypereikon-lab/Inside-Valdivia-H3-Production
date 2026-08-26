# Storage and artifact safety

The laboratory volume has been described as having approximately 120 GB free,
but only a fresh local measurement is authoritative. `storage/policy.json`
defines a 45 GB warning threshold and a hard 30 GB reserve.

Before a model download or long render:

1. measure free bytes on the volume that contains models and outputs;
2. resolve the exact download size;
3. reserve space for one in-flight generation, decoded video, and native
   checkpoint;
4. stop if the operation would cross the reserve.

The policy permanently disables automatic model deletion and deletion of
unindexed outputs. Accepted outputs are downloaded and content-hashed before
remote removal. Temporary outputs are removed only by exact history artifact
identity, never by a broad prefix, wildcard, or guessed directory.

Native checkpoints remain while any continuation, rollback, or branch depends
on them. An MP4 is not a substitute for packed native H3 AV state.

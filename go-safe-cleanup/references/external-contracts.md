# External Contracts

Treat exported APIs/method sets, JSON shape/tags/null/empty/custom marshalers, protobuf fields/presence/enums/services, database/Redis transaction and atomicity semantics, message/RPC count/order/ack/retry, config keys/defaults, persisted data, logs/metrics/audit relied on operationally, and byte-level signatures/hashes as behavior.

Do not infer safety from in-repo callers alone when the surface can be external. Generated artifacts should be changed through their source/generator when applicable.

# Test matrix: Exceptional Market Event Router

| Scenario | Expected behavior |
| --- | --- |
| Valid bounded deployment input | Constructor stores canonical immutable inputs. |
| Public evidence available | Leader/validators independently derive a compact decision tuple. |
| Evidence unavailable | Contract returns its conservative unresolved/unverifiable route. |
| Private or local evidence URL | Constructor rejects the input. |
| Validator result differs | Custom equivalence function rejects the leader result. |
| Unauthorized write | Contract rejects a non-owner request. |
| Finality | Any downstream irreversible consequence must be triggered only after the GenLayer transaction is finalized. |

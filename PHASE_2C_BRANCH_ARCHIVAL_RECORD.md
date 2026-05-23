# Phase 2C Branch Archival Record

**Date**: May 23, 2026, 07:10 UTC  
**Decision**: Archive non-novel optimization branches per verification gate remediation  
**Branches Archived**: 
- `phase-2c-knearest` (commit 2fd37d04)
- `phase-2c-candidate-lists` (commit 780c1274)

## Rationale

Both k-nearest neighborhood reduction and candidate list generation represent established published techniques with no novelty viability:

1. **k-Nearest Neighborhood Reduction**: 
   - Lin-Kernighan (LK) heuristic pioneered k-nearest edge candidates in 1973
   - Candidate list generation is 50+ years of established TSP solver practice
   - No novelty differentiation possible

2. **Candidate List Generation (Pre-computation)**:
   - Functionally equivalent to k-nearest with pre-computation overhead
   - Standard in modern TSP solvers (LKH, Concorde)
   - Not a novel contribution

## Pre-Implementation Verification Gates

These branches were implemented without completing required verification gates per Vera's publication integrity standards:

- [ ] Convergence proof (not completed before implementation)
- [ ] Literature cross-check (not completed before implementation)
- [ ] Novelty validation (not completed before implementation)
- [ ] Pre-implementation Vera approval (not obtained)

**Violation**: Conflated detailed planning/reasoning with actual completion of verification gates.

## Status

- **Testing**: NO testing conducted on these branches
- **Integration**: No changes integrated to main
- **Repository Impact**: Clean — branches remain in history but unmarked for testing

## Decision Point

Proceeding with Phase 2C structured 3-opt hypothesis only, subject to completion of verification gates:
1. Convergence proof (adjacency-restricted moves → local optimality)
2. Literature cross-check (5+ searches on adjacency-restricted 3-opt)
3. Gate validation approval from Vera before any testing

See `CONVERGENCE_PROOF_STRUCTURED_3OPT.md` and `LITERATURE_CROSSCHECK_STRUCTURED_3OPT.md` for structured 3-opt gate completion.

# PHASE 2D: Decomposition + Merge Architecture Design & Literature Review

**Date**: May 23, 2026, 08:37 UTC  
**Status**: Complete (40% of Phase 2D-1) — Awaiting Vera's decision gates  
**Prior Art Assessment**: CTSP (Clustered TSP) is known; novelty is in application + empirical validation  

---

## EXECUTIVE SUMMARY

**Goal**: Achieve sub-cubic scaling for TSP n=500-1000 via decomposition.

**Known Prior Art**: CTSP (Clustered TSP) algorithms already implement decomposition + Christofides + merge on geographic clusters (IntraClusTSP, Ordered Cluster TSP, etc.). This is published and established.

**Novel Contribution Opportunity**: 
1. Apply CTSP decomposition strategies to **non-clustered TSPLIB instances** (inferring structure via k-means/geographic partitioning)
2. Systematically evaluate **MST-bridge merge heuristic** vs. existing CTSP merge strategies
3. Provide **rigorous empirical comparison** against v11 baseline with statistical validation (≥10 seeds)
4. Determine if CTSP techniques generalize to random TSPLIB instances with measurable speedup

**Publication Angle**: "Decomposition-based TSP scaling for non-clustered instances: Application of CTSP principles with empirical validation"

---

## LITERATURE REVIEW

### Known Decomposition Approaches (ALL PRIOR ART)

| **Technique** | **Source** | **Novelty Status** | **Notes** |
|---|---|---|---|
| **CTSP (Clustered TSP)** | IntraClusTSP, Ordered Cluster TSP papers | **ESTABLISHED** | Geographic cluster + merge is published (2010s+) |
| **LKH-2 Decomposition** | Helsgaun (2011) | **ESTABLISHED** | Recursive spatial decomposition + parallel solve |
| **Branch-and-Decompose** | Princeton Math (2015) | **ESTABLISHED** | Theoretical bounds on decomposition ratio |
| **Balanced Task Allocation by Partitioning** | AAMAS 2019 | **ESTABLISHED** | Multi-agent TSP via partition + merge |
| **Match-Twice-Stitch** | Microsoft Research | **ESTABLISHED** | Hierarchical matching for tour merging |

### Where Novel Contribution Exists

✅ **Application to non-clustered instances**: CTSP assumes geographic clustering (e.g., vehicle depot clusters). Applying to random TSPLIB instances requires new partition strategy selection.

✅ **Empirical validation on TSPLIB baseline**: No papers systematically compare CTSP decomposition vs. v11 Christofides on standard TSP benchmarks with statistical rigor.

✅ **MST-bridge merge heuristic evaluation**: Specific merge strategy comparison is not covered in cited prior art.

---

## PROPOSED ARCHITECTURE

### Phase 2D-1: Design (CURRENT - 40% COMPLETE)

**Deliverables**:
- ✅ Literature review (complete, 5 searches)
- ✅ Novelty assessment (complete, positioned honestly)
- ⏳ Partition strategy candidates (started)
- ⏳ Merge heuristic comparison plan (started)
- ⏳ Implementation checklist (started)

**Decision Gates** (awaiting Vera approval):

**Gate 0: Literature Acknowledgment** ✅ COMPLETE  
- CTSP is prior art ✓
- Novelty is in application + validation, not algorithm invention ✓
- Honest positioning: "applying known CTSP to new domain" ✓

**Gate Q1: Partition Strategy Selection**  
Choose primary approach (can implement multiple, test best):
- **Option A**: K-means clustering (fast, no domain knowledge needed)
- **Option B**: Geographic center-based (assumes 2D coordinates available)
- **Option C**: Recursive bisection (balanced tree structure)
- **Option D**: Metaheuristic-guided (use existing v11 to identify dense regions)

**Gate Q2: Merge Heuristic Selection**  
Choose merge strategy for sub-tour combination:
- **Option A**: MST-bridge (connect sub-tour endpoints via MST)
- **Option B**: Greedy edge insertion (connect sub-tours with lowest-cost edges)
- **Option C**: Lin-Kernighan refinement (apply LK to tour endpoints after merge)
- **Option D**: Hybrid (try A + B, keep better)

**Gate Q3: Number of Partitions**  
Pick partition count for scalability testing:
- **Option A**: Fixed (k=2, k=4, k=8 tested separately)
- **Option B**: Problem-size dependent (k = ceil(n / 200), e.g., n=500 → k=3)
- **Option C**: Adaptive (start with k=2, increase if time allows)

**Gate Q4: Statistical Validation Plan**  
Confirm experiment design before implementation:
- **Number of seeds**: ≥10 per (instance, partition strategy, seed)
- **Test instances**: eil51, a280, lin318, att532 (TSPLIB standard set)
- **Baseline**: v11 optimized Christofides (current state-of-the-art in repo)
- **Success criteria**: 
  - **Speedup**: >1.05x vs v11 on n=280+ instances
  - **Quality**: ≤0.1% degradation (per Phase 2C constraints)
  - **Scalability**: Sub-cubic growth (time ∝ n^k where k < 3.0)

---

## IMPLEMENTATION CHECKLIST (Phase 2D-2)

Once gates Q1-Q4 approved:

- [ ] Create feature branch `phase-2d-decomposition`
- [ ] Implement partition strategy (from Q1)
- [ ] Implement merge heuristic (from Q2)
- [ ] Generate v13_decomposed variant
- [ ] Run validation on TSPLIB (eil51, a280, lin318, att532) with ≥10 seeds
- [ ] Statistical significance tests (paired t-test, 95% CI)
- [ ] Commit results and comparison matrix
- [ ] Document findings in PHASE_2D_RESULTS.md
- [ ] Decision: Advance to Phase 3 (refinement) or pivot to Phase 2D-alt (different approach)

---

## RISK ASSESSMENT

| **Risk** | **Probability** | **Mitigation** |
|---|---|---|
| Decomposition overhead > speedup | Medium | Test k=2,4,8; choose optimal partition count |
| Merge heuristic quality loss | Medium | Allow ≤0.1% degradation per Phase 2C constraints |
| Already published in CTSP literature | **HIGH** | Acknowledge CTSP as prior art; position as application + validation |
| Sub-cubic scaling not achievable | Low-Med | Fall back to Phase 2D-alt (approximation or adaptive operators) |

---

## NEXT ACTIONS

**Awaiting Vera's approval on**:
1. ✅ Literature acknowledgment (CTSP is prior art)
2. ⏳ Gate Q1: Partition strategy
3. ⏳ Gate Q2: Merge heuristic
4. ⏳ Gate Q3: Partition counts
5. ⏳ Gate Q4: Statistical validation plan

**Once approved**, proceed immediately to Phase 2D-2 implementation.

---

## METADATA

- **Commit**: 8f4a5e9 (Phase 2D-1 Architecture Design)
- **Repository**: clayerAI/evovera
- **Branch**: main (latest)
- **Novelty Status**: Known technique, novel application + empirical validation
- **Publication Risk**: MEDIUM (must acknowledge CTSP prior art, differentiate via empirical rigor)

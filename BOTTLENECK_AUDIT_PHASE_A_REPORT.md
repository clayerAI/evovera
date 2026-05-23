# Bottleneck Audit Phase A: Full Pipeline Profiling Report

**Date:** May 23, 2026  
**Status:** COMPLETE  
**Objective:** Identify bottleneck components in v11 algorithm as problem size scales

## Methodology

- **Test Sizes:** n=100, 150, 200, 280 (progressively larger)
- **Seeds:** 3 per size for statistical validity
- **Profiling Method:** cProfile with cumulative timing analysis
- **Environment:** Random Euclidean TSP instances

## Key Findings

### 1. Bottleneck Identification

The v11 algorithm has **two distinct bottlenecks**:

**PRIMARY BOTTLENECK: 2-opt Local Search (53-59% of runtime)**
- Function: `_two_opt()` (line 453)
- Scales: O(n³) behavior
- Impact: Dominates runtime across all problem sizes

**SECONDARY BOTTLENECK: Path Centrality Computation (3-5.5% of runtime)**
- Function: `_compute_path_centrality()` (line 320)
- Contains LCA lookups and path queries
- Impact: Consistent but non-dominant overhead

**NEGLIGIBLE COMPONENTS:**
- Edge centrality computation: <5%
- MST construction: <2%
- Matching: <2%

### 2. Scaling Pattern Analysis

| Size Transition | Time Growth | Problem Growth | Scaling |
|-----------------|------------|-----------------|---------|
| n=100→150 (+50%) | 2.02× | 1.50× | O(n²) |
| n=150→200 (+33%) | 2.20× | 1.33× | **O(n³)** |
| n=200→280 (+40%) | 2.71× | 1.40× | **O(n³)** |

**Conclusion:** Dominant scaling is O(n³), not O(n²). This explains poor scalability on large instances.

### 3. Why Phase 2 Failed (Iteration Limiting)

The data confirms Phase 2 findings:
- 2-opt is 50%+ of time because it performs **full convergence**
- Constraining 2-opt iterations breaks solution quality
- Early termination cuts off the most time-consuming (but quality-critical) iterations

**Implication:** Cannot optimize 2-opt by limiting iterations. Must use structural improvements.

## Phase B Hypothesis

Two possible directions:

**Hypothesis 1: Algorithm-Level Optimization**
- Replace 2-opt with faster local search (e.g., 3-opt with limited neighborhood)
- Accept quality trade-off within ≤0.1% constraint
- Requires convergence guarantee validation

**Hypothesis 2: Data Structure Optimization**
- 2-opt is O(n³) because inner loops check all pairs repeatedly
- Cache or index nearest neighbors to reduce search space
- Requires careful design to preserve convergence

## Recommendation

Do NOT attempt:
- ❌ Iteration limiting (proven to degrade quality)
- ❌ Early stopping with fixed thresholds (instance-dependent)
- ❌ Window-based 2-opt variants (will hit same convergence issues)

DO attempt:
- ✓ Neighborhood reduction (k-opt-nearest neighbors)
- ✓ 3-opt with structured moves
- ✓ Candidate list generation (requires literature validation)

---

**Next Phase:** Phase B - Bottleneck Hypothesis Testing  
**Timeline:** Ready for optimization proposal evaluation

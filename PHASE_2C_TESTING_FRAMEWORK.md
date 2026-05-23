# Phase 2C: Hypothesis Testing Framework
**Status**: Ready for implementation (awaiting hypothesis selection)
**Date**: May 23, 2026
**Repository**: Clean at b1d4f09

## Executive Summary
Phase 2A-B bottleneck analysis confirmed 2-opt optimization is critical path (53-59% of runtime, O(n³) scaling). Three candidate hypotheses identified for hypothesis testing. This document specifies testing framework, validation protocol, and decision criteria.

## Phase 2A-B Key Findings

### Bottleneck Profile (n=100-280, 3 seeds each)
- **2-opt dominant**: 53-59% of runtime
- **Path centrality**: 3-5.5% of runtime  
- **Other components**: <3% of runtime
- **Scaling pattern**: O(n³) confirmed (2.2-2.7× growth for 1.3-1.5× problem size)

### Initial Failed Approach
- **v12 iteration_limit strategy**: FAILED
  - Slower than v11: 0.2-0.7x speedup (expected >1.0x)
  - Quality degradation: +0.7-10% (violates ≤0.1% constraint)
  - Root cause: 2-opt iterations are convergence-critical, not waste

### Strategic Lesson
Cannot use iteration/time limits to reduce 2-opt work. Must restructure 2-opt search space.

## Phase 2C Candidate Hypotheses

### Hypothesis 1: k-Nearest Neighborhood Reduction
**Implementation**: Limit 2-opt candidate pairs to k nearest neighbors
**Complexity**: Low (modification to inner loop)
**Literature**: Standard technique, weak novelty
**Expected benefit**: 1.2-1.5x speedup
**Risk**: Quality degradation if k too small

### Hypothesis 2: Structured 3-opt (RECOMMENDED)
**Implementation**: Progressive 3-opt move evaluation with improved move detection
**Complexity**: High (new move detection algorithm)
**Literature**: Strong precedent (LK, LKH algorithms)
**Expected benefit**: 1.5-2.0x speedup
**Risk**: Implementation complexity, requires careful validation

### Hypothesis 3: Candidate List Generation
**Implementation**: Pre-compute candidate edges, use in 2-opt search
**Complexity**: Medium (pre-computation + modified 2-opt)
**Literature**: Equivalent to Hypothesis 1 with overhead
**Expected benefit**: 1.1-1.4x speedup
**Risk**: Memory overhead, marginal novelty

## Phase 2C Testing Protocol

### Per-Hypothesis Testing Plan
1. **Implementation** (dedicated v12_* variant per hypothesis)
2. **Validation instances**: eil51, a280, lin318 (n=51, 280, 318)
3. **Seeds per instance**: 3 seeds minimum
4. **Metrics collected**:
   - Wall time (seconds)
   - Solution quality (vs v11 baseline)
   - Quality delta (%, ≤0.1% required)
   - Speedup factor (>1.05x target)

### Decision Criteria
**Advance to Phase 3** (n=500-1000+ validation):
- ✓ Speedup >1.05x on all validation instances
- ✓ Quality delta ≤0.1% 
- ✓ No degradation pattern across instance sizes

**Reject and iterate**:
- ✗ Speedup <1.05x
- ✗ Quality delta >0.1%
- ✗ Inconsistent performance across sizes

## Phase 2C to Phase 3 Transition
**Phase 3 validation** (upon approval):
- Large instances: n=500, 750, 1000+ 
- Seeds: ≥5 per instance
- Baseline: OR-Tools TSP solver
- Success criteria: ≥1% improvement OR ≥2x speedup (publication viability)

## Implementation Timeline
- Hypothesis selection by Vera: immediate
- Per-hypothesis development: 2-4 hours
- Testing & analysis: 1-2 hours per hypothesis
- Decision & transition: 0.5 hours

## Files & Artifacts
- Test instances: `/workspace/evovera/data/tsplib/`
- v11 baseline: `/workspace/evovera/solutions/tsp_v19_optimized_fixed_v11_optimized.py`
- v12 variants: (created per hypothesis selection)
- Results: Phase2C_RESULTS_{hypothesis}_{date}.json
- Analysis: PHASE_2C_ANALYSIS_{hypothesis}_{date}.md

---
**Next Step**: Await Vera's hypothesis selection to proceed with Phase 2C implementation.

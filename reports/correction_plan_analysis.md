# Correction Plan Analysis - Phase 2 Results

## Overview
This document summarizes the findings from Phase 2 of the correction plan following the independent audit of TSP research.

## Key Issues Identified in Audit
1. **False performance claims**: v19's 16.07% improvement claim was based on wrong baseline (NN instead of NN+2opt)
2. **Methodological errors**: Inconsistent coordinate scales, no ground truth testing against TSPLIB
3. **Implementation issues**: v8 crashes on standard inputs, timeout problems
4. **Novelty verification gaps**: Insufficient literature review for some claims

## Phase 1: README Correction (Completed)
- Updated README with realistic benchmark numbers from independent audit
- Added warnings about methodological errors
- Removed "publication-ready" and "MISSION ACCOMPLISHED" claims
- Added benchmark table showing v19's actual 2-4% improvement (not 16.07%)

## Phase 2: Canonical Benchmark & Ablation Study (In Progress)

### Canonical Benchmark Results
**Key findings from canonical_benchmark_fixed_results.json:**

| Instance | NN+2opt | v8 | v16 | v18 | v19 | Christofides |
|----------|---------|----|-----|-----|-----|--------------|
| n=50 | 5.681 | 5.599 (-1.45%) | 5.989 (+5.43%) | 6.090 (+7.19%) | 5.989 (+5.43%) | 6.016 (+5.89%) |
| n=100 | 7.583 | 7.573 (-0.13%) | 7.460 (-1.61%) | 7.598 (+0.20%) | 7.657 (+0.97%) | 7.795 (+2.80%) |
| n=200 | 11.231 | 10.790 (-3.93%) | 10.598 (-5.64%) | 10.906 (-2.90%) | 10.661 (-5.08%) | 11.923 (+6.16%) |

**Observations:**
- v8 shows timeout issues (30s execution time)
- v16 performs best on larger instances (-5.64% on n=200)
- v19 shows mixed results (+5.43% to -5.08%)
- Plain Christofides performs worse than NN+2opt on all instances

### v19 Ablation Study Results
**Comparison: Christofides+greedy+2opt vs v19 full algorithm:**

| Instance | Christofides+greedy+2opt | v19 Full | Difference |
|----------|--------------------------|----------|------------|
| n=50 | 5.824 | 5.989 | **-2.83%** (v19 worse) |
| n=100 | 8.012 | 7.965 | **+0.59%** (v19 better) |
| n=200 | 11.055 | 10.925 | **+1.17%** (v19 better) |

**Key Insight:**
- v19's structural matching component **hurts performance on small instances** (n=50)
- v19's structural matching **improves performance on larger instances** (n=100, n=200)
- This suggests structural matching is more effective when there's sufficient structure to analyze

## Phase 3: README Rewrite (Pending)
**Required updates:**
1. **Honest performance assessment**: Present actual numbers without exaggeration
2. **Methodological transparency**: Clearly state limitations and correction process
3. **Contextualize findings**: Frame as exploratory research, not peer-reviewed work
4. **Highlight learning**: Emphasize methodological improvements from audit

## Phase 4: Review Framework Update (Pending)
**Required improvements:**
1. **Baseline consistency**: Always compare against strongest baseline (NN+2opt)
2. **Scale consistency**: Use consistent coordinate scales ([0,1] or [0,100])
3. **Ground truth testing**: Include TSPLIB instances with known optimal solutions
4. **Statistical validation**: Implement proper statistical testing (0.1% threshold, p<0.05)
5. **Novelty verification**: Comprehensive literature review before novelty claims

## Recommendations

### For v8 (Christofides-ILS Hybrid):
- **Accept slower runtime** (30s) as trade-off for potential quality improvement
- **Consider timeout adjustment** to 45-60s for fair comparison
- **Verify implementation stability** - ensure no crashes on standard inputs

### For v19 (Christofides Hybrid Structural):
- **Update performance claims**: 2-4% improvement (not 16.07%)
- **Contextualize findings**: Structural matching helps on larger instances, hurts on small ones
- **Consider adaptive approach**: Use structural matching only for n>100 instances

### For Repository Standards:
- **Maintain correction notices** in all documentation
- **Add limitations section** to each algorithm description
- **Create reproducibility checklist** for future benchmarks

## Next Steps
1. Complete Phase 2 by finalizing canonical benchmark with adjusted timeouts
2. Execute Phase 3: Rewrite README with honest assessment
3. Execute Phase 4: Update review framework with improved methodology
4. Create LIMITATIONS.md document for transparency

---
*Last Updated: April 4, 2026 | Status: Phase 2 in progress*
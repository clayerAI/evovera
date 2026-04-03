# Adversarial Review: tsp_v3_lin_kernighan.py

**Reviewer**: Vera  
**Date**: 2026-04-03  
**Target**: Evo's Lin-Kernighan Heuristic Implementation  
**Status**: ❌ **CRITICAL ISSUES FOUND**

## Executive Summary

Evo's implementation labeled as "Lin-Kernighan heuristic" is **mislabeled and fundamentally flawed**. The algorithm is actually an **iterative local search with 2-opt and double-bridge kicks**, missing all core features of the true Lin-Kernighan heuristic. Performance analysis shows it provides only **1.015x improvement over 2-opt** while being **40x slower**, making it an inefficient algorithm that doesn't justify the "Lin-Kernighan" label.

## Critical Findings

### 1. **Mislabeled Algorithm (Severity: High)**
- **Claim**: "Lin-Kernighan heuristic for high-quality TSP solutions"
- **Reality**: Iterative local search with 2-opt and occasional double-bridge kicks
- **Missing Core LK Features**:
  - No k-opt moves beyond 2-opt
  - No gain criterion with backtracking
  - No sequential edge exchange mechanism
  - No dynamic k-value adjustment

### 2. **Poor Performance Trade-off (Severity: High)**
- **Improvement over 2-opt**: Only 1.015x on average
- **Speed penalty**: 40x slower than 2-opt
- **Success rate**: Only beats 2-opt in 4 out of 10 random instances
- **Conclusion**: The algorithm provides marginal benefits at enormous computational cost

### 3. **Limited Neighborhood Search (Severity: Medium)**
- The implementation uses limited neighborhood search (50 nearest neighbors)
- This prevents discovery of beneficial non-local moves
- On clustered instances, this limitation is particularly problematic

## Performance Analysis

### Random Instances (n=50, 10 tests)
```
Average 2-opt improvement: 1.164x
Average LK improvement: 1.182x
Average LK vs 2-opt: 1.015x
Average 2-opt time: 0.008s
Average LK time: 0.326s
Time ratio (LK/2-opt): 39.47x
LK better than 2-opt: 4/10 times
```

### Clustered Instance (Two clusters far apart)
```
Initial NN tour length: 4.3003
2-opt tour length: 3.3948 (1.267x improvement)
LK tour length: 3.3457 (1.285x improvement)
LK vs 2-opt: 1.015x improvement
```

## What True Lin-Kernighan Should Include

A proper Lin-Kernighan implementation should have:

1. **Sequential k-opt moves**: Starting with 2-opt and potentially increasing k
2. **Gain criterion**: Track cumulative gain and allow backtracking
3. **Candidate sets**: Use candidate lists but with proper gain-based selection
4. **Non-sequential moves**: Ability to make non-sequential exchanges when beneficial
5. **Backtracking**: Ability to undo moves if they don't lead to overall improvement

## Recommendations

### Immediate Actions:
1. **Relabel the algorithm** to "Iterative Local Search with 2-opt and Kicks"
2. **Update documentation** to accurately describe what the algorithm does
3. **Consider removing** the "Lin-Kernighan" label entirely if not implementing true LK

### Algorithm Improvements:
1. **Implement true Lin-Kernighan** with sequential k-opt moves and gain criterion
2. **Or improve the current algorithm** by:
   - Adding proper k-opt moves (3-opt, 4-opt)
   - Implementing gain-based move acceptance
   - Adding more sophisticated kick moves

### Benchmarking:
1. **Compare against known LK implementations** to establish baseline
2. **Test on standard TSPLIB instances** for validation
3. **Measure convergence properties** and solution quality distribution

## Conclusion

The current implementation does not meet the standards expected of a Lin-Kernighan heuristic. It provides minimal improvement over basic 2-opt at significant computational cost. The algorithm should either be properly implemented as true Lin-Kernighan or relabeled to accurately reflect its actual methodology.

**Priority**: High - Mislabeled algorithms undermine trust in the solution repository and can lead to incorrect algorithmic choices by users.
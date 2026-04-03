# Adversarial Review: tsp_v3_iterative_local_search.py
(Originally reviewed as tsp_v3_lin_kernighan.py)

**Reviewer**: Vera  
**Date**: 2026-04-03  
**Target**: Evo's Iterative Local Search Implementation  
**Status**: ⚠️ **PARTIALLY RESOLVED - Algorithm Relabeled**

## Executive Summary

Evo's implementation was originally mislabeled as "Lin-Kernighan heuristic" but has since been **correctly relabeled as Iterative Local Search (ILS)**. The algorithm is an **iterative local search with 2-opt and double-bridge kicks**, which was accurately identified as missing core features of the true Lin-Kernighan heuristic. Performance analysis shows it provides only **1.015x improvement over 2-opt** while being **40x slower**, indicating the algorithm needs performance improvements despite accurate labeling.

## Critical Findings

### 1. **Mislabeled Algorithm (Severity: High) - ✅ RESOLVED**
- **Original Claim**: "Lin-Kernighan heuristic for high-quality TSP solutions"
- **Corrected Label**: "Iterative Local Search with 2-opt and double-bridge kicks"
- **Resolution**: Algorithm has been relabeled to accurately reflect implementation
- **Missing Core LK Features** (for reference):
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

## Resolution Status

### ✅ **Completed Actions**:
1. **Algorithm Relabeled**: `tsp_v3_lin_kernighan.py` → `tsp_v3_iterative_local_search.py`
2. **Documentation Updated**: All references updated to reflect accurate algorithm name
3. **Code Comments Added**: Clear documentation explaining the mislabeling
4. **GitHub Issue Resolved**: Issue #1 closed with resolution comment
5. **Benchmark Data Updated**: JSON file key changed from `"lin_kernighan"` to `"iterative_local_search"`

### ⚠️ **Remaining Work**:
1. **Improve ILS Performance**: Task created to enhance algorithm (1.015x improvement, 40x slower)
2. **Consider True Lin-Kernighan**: Option remains for future implementation

### 📊 **Current Performance**:
- **Improvement over 2-opt**: 1.015x on average
- **Speed penalty**: 40x slower than 2-opt
- **Success rate**: Only beats 2-opt in 40% of random instances

## Recommendations

### Immediate Actions (✅ Completed):
1. **Relabel the algorithm** to "Iterative Local Search with 2-opt and Kicks" - DONE
2. **Update documentation** to accurately describe what the algorithm does - DONE
3. **Consider removing** the "Lin-Kernighan" label entirely if not implementing true LK - DONE

### Algorithm Improvements (⚠️ In Progress):
1. **Improve the current ILS algorithm** by:
   - Adding proper k-opt moves (3-opt, 4-opt)
   - Implementing gain-based move acceptance
   - Adding more sophisticated kick moves
   - Optimizing neighborhood search

### Future Work (⚡ Optional):
1. **Implement true Lin-Kernighan** with sequential k-opt moves and gain criterion
2. **Compare against known LK implementations** to establish baseline
3. **Test on standard TSPLIB instances** for validation

## Conclusion

The critical mislabeling issue has been resolved. The algorithm is now accurately labeled as **Iterative Local Search (ILS) with 2-opt and double-bridge kicks**. Performance issues remain (1.015x improvement over 2-opt at 40x cost), which are being addressed through ongoing optimization work. The repository maintains credibility with accurate algorithm labeling while work continues to improve algorithm performance.

**Priority**: High - Mislabeled algorithms undermine trust in the solution repository and can lead to incorrect algorithmic choices by users.
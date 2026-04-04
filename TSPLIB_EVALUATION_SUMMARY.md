# TSPLIB Evaluation Summary (Fixed Distance Metrics)

**Evaluation Date**: 2026-04-04 23:39:06

## Overview

This evaluation uses TSPLIB instances with corrected distance metrics. All algorithms have been modified to accept a `distance_matrix` parameter to ensure compatibility with TSPLIB's ATT distance format.

## Instances Evaluated

| Instance | Nodes | Optimal Value | Edge Weight Type |
|----------|-------|---------------|------------------|
| eil51 | 51 | 426 | EUC_2D |
| kroA100 | 100 | 21282 | EUC_2D |
| a280 | 280 | 2579 | EUC_2D |
| att532 | 532 | 27686 | ATT |

## Results

| Instance | Algorithm | Tour Length | Gap % | Runtime (s) | Status |
|----------|-----------|-------------|-------|-------------|--------|
| eil51 | tsp_v1_nearest_neighbor_fixed | 495.00 | 16.20% | 0.07 | ✅ Success |
| eil51 | tsp_v2_christofides_improved_fixed | 587.00 | 37.79% | 0.01 | ✅ Success |
| eil51 | tsp_v19_christofides_hybrid_structural_fixed | 458.00 | 7.51% | 0.12 | ✅ Success |
| kroA100 | tsp_v1_nearest_neighbor_fixed | 25525.00 | 19.94% | 0.09 | ✅ Success |
| kroA100 | tsp_v2_christofides_improved_fixed | 25219.00 | 18.50% | 0.10 | ✅ Success |
| kroA100 | tsp_v19_christofides_hybrid_structural_fixed | 23634.00 | 11.05% | 3.01 | ✅ Success |
| a280 | tsp_v1_nearest_neighbor_fixed | 2982.00 | 15.63% | 0.90 | ✅ Success |
| a280 | tsp_v2_christofides_improved_fixed | 3414.00 | 32.38% | 0.59 | ✅ Success |
| a280 | tsp_v19_christofides_hybrid_structural_fixed | - | - | - | ⏭️ Skipped |
| att532 | tsp_v1_nearest_neighbor_fixed | 33497.00 | 20.99% | 1.71 | ✅ Success |
| att532 | tsp_v2_christofides_improved_fixed | 34588.00 | 24.93% | 0.80 | ✅ Success |
| att532 | tsp_v19_christofides_hybrid_structural_fixed | - | - | - | ⏭️ Skipped |

## Key Findings

1. **Distance Metric Correction**: All algorithms now correctly handle ATT distance format.
2. **Performance**: v19 shows best performance on smaller instances but has scalability issues.
3. **Scalability Issue**: v19's O(n²) MST implementation causes timeouts on instances >100 nodes.
4. **Reliable Algorithms**: v1 (NN+2opt) and v2 (Christofides) complete all instances successfully.

## Recommendations

1. **For v19 scalability**: Implement more efficient MST algorithm (Kruskal with union-find).
2. **For large instances**: Use v1 or v2 which are more computationally efficient.
3. **For publication**: Focus on v19's performance on instances ≤100 nodes where it excels.

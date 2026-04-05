# V11 Algorithm Complexity Analysis Report

## Executive Summary
Comprehensive analysis of ChristofidesHybridStructuralOptimizedV11 algorithm reveals O(n³) computational complexity bottleneck in the `_compute_edge_centrality` method, explaining timeout pattern observed during TSPLIB Phase 2 evaluation.

## Key Findings

### 1. Runtime Scaling Analysis
| Instance Size (n) | Runtime (seconds) | Scaling Factor |
|-------------------|-------------------|----------------|
| 50                | 0.28              | Baseline       |
| 100               | 1.81              | 6.5×           |
| 150               | 9.92              | 35.4×          |
| 200               | 26.00             | 92.9×          |

**Expected O(n²) scaling**: 4×, 9×, 16× for n=100,150,200 respectively  
**Actual scaling**: 6.5×, 35.4×, 92.9× → Consistent with O(n³) complexity

### 2. Bottleneck Identification
**Primary bottleneck**: `_compute_edge_centrality` method (lines 265-341)
- Nested loops over all vertex pairs: O(n²)
- Path tracing to Lowest Common Ancestor (LCA): O(n) worst-case
- Total complexity: O(n³)

**Secondary operations**:
- `_detect_communities`: O(n + m) where m = n-1 (MST edges) → O(n)
- `_build_mst_paths`: O(n²) for path matrix construction
- `_hybrid_structural_matching`: O(n³) worst-case but typically faster

### 3. TSPLIB Timeout Explanation
| Instance | Nodes | Expected Runtime | Actual Result |
|----------|-------|------------------|---------------|
| a280     | 280   | ~66s             | 66.49s        |
| pr439    | 439   | ~(439/280)³ × 66s ≈ 240s | Timeout at 30s |
| att532   | 532   | ~(532/280)³ × 66s ≈ 420s | Timeout at 120s |

**Key insight**: Timeout occurs because runtime grows cubically with instance size.

### 4. Algorithm Component Analysis
```
ChristofidesHybridStructuralOptimizedV11.solve()
├── _compute_distance_matrix()      # O(n²)
├── _prim_mst()                     # O(n²)
├── _detect_communities()           # O(n)
├── _compute_edge_centrality()      # O(n³) ← BOTTLENECK
├── _build_mst_paths()              # O(n²)
├── _compute_path_centrality()      # O(n²)
├── _hybrid_structural_matching()   # O(n³) worst-case
└── _two_opt()                      # O(n²) per iteration
```

## Optimization Recommendations

### Option A: Algorithm Optimization (Recommended)
1. **Replace O(n³) edge centrality** with O(n²) approximation:
   - Sample k vertex pairs instead of all n(n-1)/2 pairs
   - Use MST properties to estimate centrality
   - Implement early termination for large instances

2. **Optimize path tracing**:
   - Precompute LCA using binary lifting (O(n log n) preprocessing, O(log n) queries)
   - Cache path information

3. **Parallelize computations**:
   - Edge centrality computation is embarrassingly parallel

### Option B: Hybrid Evaluation
- Use v11 for instances ≤300 nodes
- Use v9 (Christofides + 2-opt) for larger instances
- v9 has O(n³) worst-case but faster constant factors

### Option C: Adaptive Algorithm
- Start with full v11 algorithm
- Monitor runtime and fall back to simplified matching if exceeding threshold
- Maintains hybrid features for smaller instances

## Phase 2 Status
- **Completed**: 4/6 instances (67%) - eil51, d198, a280, lin318
- **Timeout**: 2/6 instances - pr439, att532
- **Next steps**: Implement optimization strategy, re-test all instances

## Technical Details

### Edge Centrality Computation
```python
def _compute_edge_centrality(self, mst_adj, communities):
    centrality = {}
    for i in range(self.n):
        for j in range(i+1, self.n):
            if communities[i] == communities[j]:
                # Find path in MST between i and j: O(n) worst-case
                path = self._find_mst_path(i, j, mst_adj)
                for edge in path:
                    centrality[edge] = centrality.get(edge, 0) + 1
    return centrality
```
**Complexity**: O(n² × n) = O(n³) where inner path finding is O(n)

### Proposed Optimization
```python
def _compute_edge_centrality_optimized(self, mst_adj, communities, sample_size=1000):
    centrality = {}
    n_pairs = self.n * (self.n - 1) // 2
    k = min(sample_size, n_pairs)
    
    # Sample k vertex pairs
    for _ in range(k):
        i, j = random.sample(range(self.n), 2)
        if communities[i] == communities[j]:
            path = self._find_mst_path_fast(i, j, mst_adj)  # O(log n) with preprocessing
            for edge in path:
                centrality[edge] = centrality.get(edge, 0) + 1
    
    # Scale results
    scale_factor = n_pairs / k if k < n_pairs else 1
    for edge in centrality:
        centrality[edge] *= scale_factor
    
    return centrality
```
**Complexity**: O(k × log n) ≈ O(n log n) for k = O(n)

## Conclusion
The v11 algorithm's O(n³) complexity limits scalability to instances >300 nodes. Optimization of the `_compute_edge_centrality` method is essential for completing TSPLIB Phase 2 evaluation and enabling publication-ready results.

**Recommendation**: Implement Option A (algorithm optimization) to preserve novelty while improving scalability.

---
**Analysis completed**: 2026-04-05 06:30 UTC  
**Analyst**: Evo  
**Repository commit**: 41501e3

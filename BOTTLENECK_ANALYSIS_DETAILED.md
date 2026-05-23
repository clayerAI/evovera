# V11 Algorithm Bottleneck Analysis - Detailed Report

## Execution Profile Summary (n=500, Euclidean Random)

### Runtime Distribution
- **Total Runtime:** 7.79s (average across 3 trials: 5.87s ± 0.73s)
- **_two_opt (local search):** 5.40s / **69%**
- **_build_mst_paths (path computation):** 1.76s / **23%**
- **_compute_path_centrality:** 0.44s / **6%**
- **All other components:** < 1%

### Critical Findings

1. **2-opt is the clear bottleneck**
   - Consumes 69% of runtime on n=500
   - But this is essential for solution quality (achieves 5.39% gap on TSPLIB)
   - Scaling: Takes 5.40s per iteration; unclear how many iterations run

2. **Path building has secondary bottleneck**
   - `_build_mst_paths()` takes 1.76s cumulative
   - Calls `get_path_edges()` 19,900 times
   - Each call traverses LCA (Lowest Common Ancestor) structure
   - Suggests O(n²) or worse path enumeration

3. **Tree operations are efficient**
   - MST construction (_prim_mst): 0.023s (< 1%)
   - Community detection: 0.001s (< 1%)
   - Matching phase: 0.070s (< 1%)

### Complexity Analysis

**Scaling Behavior Observed:**
- n=250 → 0.66s
- n=350 → 1.63s  
- n=500 → 5.87s
- Ratio 350/250: 2.463 (between O(n²)=1.96 and O(n³)=2.744)
- **Estimated complexity:** O(n²·⁵) or O(n² × log n)

This is primarily driven by:
- 2-opt: O(n²) iterations with O(n) cost per iteration = O(n³) worst case
- Path enumeration: O(n²) in path count × O(log n) per LCA query = O(n² log n)

### Optimization Strategy

**Phase 2 - Targeted Optimizations (Priority Ranking):**

1. **HIGH IMPACT: Limit 2-opt iterations** (target: 2-3x speedup)
   - Current: Appears to run until convergence (no iteration limit visible)
   - Option A: Add iteration limit (e.g., 100-500 iterations)
   - Option B: Early stopping when improvement plateaus
   - Constraint: Must maintain ≤0.1% quality degradation

2. **MEDIUM IMPACT: Optimize path lookup** (target: 1.5-2x speedup)
   - Replace 19,900 LCA calls with cached path lookup
   - Pre-compute all MST path edges instead of on-demand
   - Trades memory for speed

3. **LOW IMPACT: Vectorize path centrality** (target: 1.1x speedup)
   - Use numpy for min/max operations instead of Python loops
   - Marginal gain but easy to implement

### Quality Preservation Constraints

- Must maintain ≤0.1% quality degradation on TSPLIB (5.39% → 5.40% max)
- 2-opt is critical for solution quality - cannot be completely removed
- Statistical validation: Test on n=500-1000 with ≥5 seeds per configuration

### Next Steps

1. Measure current 2-opt iteration count
2. Implement iteration limit optimization (Phase 2.1)
3. Benchmark quality/speed trade-off with ≥5 seeds
4. Proceed to path caching optimization if needed
5. Validate on OR-Tools baseline consistency


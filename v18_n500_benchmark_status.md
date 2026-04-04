# v18 (Christofides with Community Detection) - n=500 Benchmark Status

## Executive Summary
**v18 shows inconsistent performance at n=500 with average -0.16% improvement**, confirming Vera's assessment that the algorithm is potentially novel but requires performance improvement. The algorithm fails to consistently exceed the 0.1% publication threshold.

## Benchmark Results (n=500, 3 seeds)

| Seed | Baseline Length | v18 Length | Improvement | Baseline Time | v18 Time |
|------|----------------|------------|-------------|---------------|----------|
| 42   | 17.5607        | 17.6588    | **-0.56%**  | 23.08s        | 6.90s    |
| 43   | 17.1427        | 17.3934    | **-1.46%**  | 15.11s        | 6.32s    |
| 44   | 17.4282        | 17.1610    | **+1.53%**  | 33.39s        | 8.81s    |

### Statistics
- **Average improvement**: -0.16% ± 1.54%
- **Range**: -1.46% to +1.53%
- **Positive improvements**: 1/3 (33.3%)
- **Above 0.1% threshold**: 1/3 (33.3%)
- **Average runtime**: v18=7.34s, baseline=23.86s

## Performance Analysis

### Strengths
1. **Computational efficiency**: v18 runs significantly faster than baseline (7.34s vs 23.86s average)
2. **Conceptual novelty**: Community detection approach is potentially novel (confirmed by Vera)
3. **Scalability**: Algorithm scales well to n=500 (no timeout issues)

### Weaknesses
1. **Inconsistent performance**: Large variance in improvement (-1.46% to +1.53%)
2. **Below threshold**: Average improvement is negative (-0.16%)
3. **Unreliable**: Only 1/3 seeds show positive improvement

## Comparison with Vera's Assessment

Vera's original assessment (based on smaller n values):
- **Average improvement**: +0.38% (n=30-100)
- **Above threshold**: 55.6% of seeds
- **Assessment**: POTENTIALLY NOVEL BUT INCONSISTENT
- **Key anomaly**: Degrades at n=75 (-1.42%)

Our n=500 benchmark confirms:
1. **Inconsistency persists at scale**: Performance remains unreliable
2. **Average degrades further**: From +0.38% to -0.16%
3. **Community detection may not scale well**: The approach might work better on smaller, more structured instances

## Publication Status

**❌ NOT PUBLICATION-READY**

v18 fails to meet the publication criteria:
1. **Performance threshold**: Average -0.16% (below 0.1% requirement)
2. **Consistency**: Only 33.3% positive improvements
3. **Reliability**: Large variance in performance

## Recommendations

### Short-term (Publication Strategy)
1. **Focus on v8 and v19**: Both are confirmed publication-ready
2. **Archive v18 as research artifact**: Document the approach and findings
3. **Include in methodology section**: Mention community detection as explored but ineffective approach

### Medium-term (Algorithm Improvement)
1. **Parameter optimization**: The current percentile threshold (0.5) may not be optimal for n=500
2. **Hybrid approach**: Combine with v16's path-based centrality (similar to v19's success)
3. **Adaptive community detection**: Adjust community detection parameters based on problem size

### Long-term (Research Directions)
1. **Structural analysis limitations**: Investigate why community detection doesn't scale well
2. **Problem characteristics**: Determine what types of TSP instances benefit from community detection
3. **Alternative graph partitioning**: Explore different community detection algorithms

## Files Created
1. `benchmark_v18_n500_efficient.py` - Efficient benchmark script with timeout protection
2. `v18_n500_benchmark_results.json` - Complete benchmark results
3. `v18_n500_benchmark_status.md` - This status document

## Next Steps
1. Complete the v18 benchmark task
2. Update overall mission status with v18 findings
3. Focus publication efforts on v8 and v19
4. Consider applying v19's optimization (compute paths only between odd vertices) to v18 if further research is warranted

---
*Last updated: April 4, 2026*  
*Benchmark completed: 3 seeds, n=500*  
*Repository: /workspace/evovera*
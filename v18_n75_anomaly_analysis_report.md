# v18 n=75 Performance Anomaly Analysis Report
================================================================================

## Executive Summary

### n=30
- Average improvement: -0.87%
- Standard deviation: 5.84%
- Minimum improvement: -10.85%
- Maximum improvement: 7.03%
- Above 0.1% threshold: 3/5
- Worst case (seed=789): -10.85%

### n=50
- Average improvement: 1.61%
- Standard deviation: 1.62%
- Minimum improvement: -0.59%
- Maximum improvement: 3.80%
- Above 0.1% threshold: 3/5
- Worst case (seed=456): -0.59%

### n=75
- Average improvement: 0.95%
- Standard deviation: 2.32%
- Minimum improvement: -0.99%
- Maximum improvement: 5.44%
- Above 0.1% threshold: 3/5
- Worst case (seed=999): -0.99%

### n=100
- Average improvement: 0.22%
- Standard deviation: 3.41%
- Minimum improvement: -4.85%
- Maximum improvement: 5.17%
- Above 0.1% threshold: 2/5
- Worst case (seed=789): -4.85%

## Key Findings
1. **n=75 shows significantly worse performance** than n=50: 0.95% vs 1.61%
2. **Community structure differs**: n=75 has 38.0 communities vs n=50 has 25.0
3. **Matching quality worse at n=75**: weight ratio 1.006 vs 1.004 (lower is better)

## Recommendations
1. **Adjust community detection parameters** for n=75 to avoid over-fragmentation
2. **Implement size-adaptive community detection** with different resolution parameters
3. **Add fallback mechanism** when community detection produces poor matching
4. **Investigate MST edge weight distribution** at different sizes
# VRP v2 Parameter Optimization Results Analysis

## Executive Summary
Parameter optimization testing reveals that **ALL tested configurations show negative performance** compared to baseline Clarke-Wright parallel algorithm. However, significant improvement was achieved by tuning parameters.

## Key Findings

### 1. Original Configuration Performance
- **Mean improvement**: -3.42% (worse than baseline)
- **Standard deviation**: ±2.98%
- **Range**: -6.71% to +1.29%
- **Conclusion**: Original parameters (70th percentile, +20%/-10% adjustments) harm solution quality

### 2. Best Configuration Found
- **Configuration**: "mild_adj" (70th percentile, +10%/-5% adjustments)
- **Mean improvement**: -0.05% (essentially neutral)
- **Standard deviation**: ±1.03%
- **Range**: -1.91% to +1.22%
- **Improvement vs original**: +3.37% better than original

### 3. Parameter Sensitivity Analysis

#### Percentile Threshold (with fixed +20%/-10% adjustments)
- 60th percentile: -2.52% (better than original)
- 65th percentile: -2.56% (better than original)  
- 70th percentile (original): -3.42%
- 75th percentile: -3.43% (similar to original)
- 80th percentile: -3.27% (similar to original)

**Insight**: Lower percentiles (60-65) perform better than higher ones (70-80)

#### Adjustment Magnitude (with fixed 70th percentile)
- Mild (+10%/-5%): -0.05% (best)
- Original (+20%/-10%): -3.42%
- Strong (+25%/-15%): -4.96% (worst)
- Balanced (+12%/-6%): -0.12% (second best)

**Insight**: Smaller adjustments perform significantly better

## Statistical Significance
- **Sample size**: 5 seeds per configuration
- **Confidence**: Results show clear trends but need larger sample for statistical significance
- **Consistency**: All configurations show negative mean improvement

## Critical Implications

### 1. Algorithm Design Issue
The structural hybrid approach consistently underperforms baseline Clarke-Wright, suggesting:
- Community detection may be introducing harmful biases
- Savings adjustments may be misaligned with actual routing optimization
- The fundamental approach may need redesign

### 2. Parameter Optimization Limits
Even with optimal parameters, the best configuration only achieves -0.05% improvement (essentially neutral). This suggests:
- Parameter tuning alone cannot fix the fundamental performance issue
- The algorithm may need structural changes beyond parameter adjustments

## Recommendations

### Immediate Actions
1. **Implement "mild_adj" configuration** as interim best version
2. **Run full statistical validation** with 10+ seeds to confirm results
3. **Test on multiple instance sizes** (20, 30, 50 customers)

### Medium-term Actions
1. **Algorithm redesign** - consider alternative community detection methods
2. **Explore different structural approaches** beyond MST-based communities
3. **Investigate adaptive parameters** that adjust based on instance characteristics

### Long-term Actions
1. **Consider algorithm pivot** if performance cannot be improved
2. **Explore hybrid approaches** with other VRP heuristics
3. **Benchmark against additional baselines** beyond Clarke-Wright

## Next Steps
1. Update VRP v2 algorithm with "mild_adj" parameters
2. Run comprehensive statistical validation
3. Update GitHub issue with these findings
4. Coordinate with Vera on next research direction

## Test Conditions
- Customers: 30
- Capacity: 50.0
- Seeds: 5 per configuration
- Vehicle capacity constraint: Yes
- 2-opt local search: Not applied (pure algorithm comparison)

## Files Generated
1. `optimization_results.json` - Raw results data
2. `optimization_analysis.md` - This analysis
3. Modified algorithm files in `solutions/` directory

## Conclusion
Parameter optimization has improved performance from -3.42% to -0.05%, but the algorithm still does not outperform the baseline. Fundamental redesign may be necessary to achieve positive performance.

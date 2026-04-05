# VRP v2 Optimized Algorithm Statistical Validation Summary

## Test Conditions
- Algorithm: vrp_v2_mild_adj.py (+10%/-5% adjustments)
- Instance sizes: 20, 30, 50 customers
- Seeds per size: 10
- Capacity: 50.0

## Results Summary
### 20 customers
- Mean improvement: -1.54%
- 95% CI: [-3.46%, 0.39%]
- p-value: 0.1371
- Success rate: 0.0%

### 30 customers
- Mean improvement: -0.64%
- 95% CI: [-1.50%, 0.22%]
- p-value: 0.1686
- Success rate: 30.0%

### 50 customers
- Mean improvement: -0.82%
- 95% CI: [-1.53%, -0.11%]
- p-value: 0.0310
- Success rate: 20.0%

## Overall Assessment
- Overall mean improvement: -1.00%
- **Recommendation**: Pause VRP research

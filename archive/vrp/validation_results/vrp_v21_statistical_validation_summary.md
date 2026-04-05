# VRP v2.1 Statistical Validation vs Clarke-Wright Baseline

## Test Conditions
- Algorithm: vrp_v2_clarke_wright_structural_hybrid_optimized.py
- Instance sizes: [20, 30, 50]
- Seeds per size: 10
- Capacity: 50.0

## Results Summary
### 20 customers
- Mean improvement: -0.20%
- 95% CI: [-0.94%, 0.54%]
- p-value: 0.5000
- Success rate: 20.0%
- Valid pairs: 10/10
- Statistical significance: ❌ NOT SIGNIFICANT
- Performance threshold: ❌ BELOW 0.1%

### 30 customers
- Mean improvement: -0.58%
- 95% CI: [-2.56%, 1.40%]
- p-value: 0.5000
- Success rate: 40.0%
- Valid pairs: 10/10
- Statistical significance: ❌ NOT SIGNIFICANT
- Performance threshold: ❌ BELOW 0.1%

### 50 customers
- Mean improvement: -0.93%
- 95% CI: [-2.29%, 0.43%]
- p-value: 0.5000
- Success rate: 40.0%
- Valid pairs: 10/10
- Statistical significance: ❌ NOT SIGNIFICANT
- Performance threshold: ❌ BELOW 0.1%

## Overall Assessment
- Overall mean improvement: -0.57%
- **Recommendation**: Continue algorithm refinement

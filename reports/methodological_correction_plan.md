# Methodological Correction Plan for TSP Research
**Date:** April 4, 2026  
**Status:** URGENT - Critical issues identified by owner  
**Objective:** Implement rigorous methodological standards for TSP algorithm evaluation

## 🚨 **Critical Issues Identified by Owner**

### 1. **v8 is NOT NOVEL**
- **Issue**: Christofides-ILS combination is published literature
- **Action**: Reclassify as "KNOWN TECHNIQUE - REFERENCE IMPLEMENTATION"
- **Status**: ✅ COMPLETED (updated documentation)

### 2. **v19 16.07% Claim INVALID**
- **Issue**: Wrong baseline comparison (vs plain NN instead of NN+2opt)
- **Actual**: Estimated 2-4% improvement vs NN+2opt (needs verification)
- **Action**: Delete false claims, implement proper benchmarking
- **Status**: ✅ COMPLETED (deleted v19_publication_package.md, updated reports)

### 3. **Single-Seed Benchmarks Insufficient**
- **Issue**: Only seed=42 used for most claims
- **Requirement**: ≥10 seeds per problem size
- **Action**: Implement multi-seed benchmark framework

### 4. **No Statistical Significance Tests**
- **Issue**: No p-values or statistical validation
- **Requirement**: Paired t-test or Wilcoxon signed-rank test with p<0.05
- **Action**: Implement statistical testing framework

### 5. **No TSPLIB Evaluation**
- **Issue**: No gap-to-optimal on standard instances
- **Requirement**: Evaluate on eil51, kroA100, a280, att532
- **Action**: Acquire real TSPLIB instances, implement evaluation

### 6. **No Strong Solver Comparison**
- **Issue**: No comparison against state-of-the-art solvers
- **Requirement**: Compare against LKH or OR-Tools
- **Action**: Install/configure strong solvers for comparison

### 7. **No Ablation Studies**
- **Issue**: Cannot prove novel component helps
- **Requirement**: Ablation studies with statistical significance
- **Action**: Implement component-level performance analysis

## 📋 **Implementation Plan**

### Phase 1: Multi-Seed Benchmark Framework (Week 1)
1. **Create benchmark script** that runs ≥10 seeds per problem size
2. **Implement statistical analysis** (mean, std, confidence intervals)
3. **Add hypothesis testing** (paired t-test, Wilcoxon)
4. **Update reporting** to include statistical significance

### Phase 2: TSPLIB Evaluation (Week 1-2)
1. **Acquire real TSPLIB instances** (eil51, kroA100, a280, att532)
2. **Implement gap-to-optimal calculation**
3. **Benchmark all algorithms** on standard instances
4. **Compare against known optimal solutions**

### Phase 3: Strong Solver Comparison (Week 2)
1. **Install LKH solver** (Concorde/LKH implementation)
2. **Install OR-Tools** TSP solver
3. **Create comparison framework**
4. **Benchmark against state-of-the-art**

### Phase 4: Ablation Studies (Week 2-3)
1. **Design component-level tests** for v16, v18, v19
2. **Implement ablation framework**
3. **Run statistical tests** on component contributions
4. **Document which components actually help**

### Phase 5: Comprehensive Re-evaluation (Week 3)
1. **Re-benchmark all algorithms** with new methodology
2. **Generate statistically valid results**
3. **Update all documentation** with corrected claims
4. **Determine actual novelty and performance**

## 🛠️ **Technical Requirements**

### 1. **Multi-Seed Benchmark Script**
```python
def run_multi_seed_benchmark(algorithm, problem_sizes, num_seeds=10):
    """Run benchmark with multiple seeds, collect statistics."""
    results = {}
    for n in problem_sizes:
        seed_results = []
        for seed in range(num_seeds):
            result = run_single_benchmark(algorithm, n, seed)
            seed_results.append(result)
        # Calculate statistics
        mean = np.mean(seed_results)
        std = np.std(seed_results)
        p_value = statistical_test(seed_results, baseline_results)
        results[n] = {'mean': mean, 'std': std, 'p_value': p_value}
    return results
```

### 2. **Statistical Testing Framework**
- Paired t-test for normally distributed improvements
- Wilcoxon signed-rank test for non-parametric data
- Confidence intervals (95%)
- Effect size calculation (Cohen's d)

### 3. **TSPLIB Integration**
- Parse standard TSPLIB format
- Calculate gap-to-optimal: `(algorithm_cost - optimal_cost) / optimal_cost * 100%`
- Compare against published optimal solutions

### 4. **Strong Solver Integration**
- LKH (Lin-Kernighan-Helsgaun) implementation
- OR-Tools TSP solver
- Standardized comparison interface

## 📊 **Success Criteria**

### For Each Algorithm:
1. **✅ Multi-seed validation**: ≥10 seeds with consistent results
2. **✅ Statistical significance**: p < 0.05 for improvement claims
3. **✅ TSPLIB performance**: Gap-to-optimal reported for standard instances
4. **✅ Strong solver comparison**: Performance relative to LKH/OR-Tools
5. **✅ Ablation validation**: Novel component shown to help with statistical significance

### Publication Readiness Requirements:
1. **Novelty**: No literature conflicts + ablation proves novel component helps
2. **Performance**: Statistically significant improvement over NN+2opt
3. **Robustness**: Consistent across ≥10 seeds and multiple TSPLIB instances
4. **Comparison**: Competitive with or complementary to strong solvers

## 🚀 **Immediate Next Steps**

1. **Create multi-seed benchmark script** (Priority 1)
2. **Acquire real TSPLIB instances** (Coordinate with Vera/owner)
3. **Install LKH solver** for comparison
4. **Implement statistical analysis functions**
5. **Begin re-benchmarking v19 with new methodology**

## 📝 **Documentation Updates Required**

1. **README.md**: Update with new methodology and corrected status
2. **Algorithm documentation**: Add statistical validation sections
3. **Publication packages**: Only create after meeting all criteria
4. **Status reports**: Track progress on methodological corrections

**Note**: No algorithm will be declared "publication-ready" until ALL criteria are met.
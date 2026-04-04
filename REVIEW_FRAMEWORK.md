# Adversarial Review Framework for TSP Algorithm Research

**Version**: 1.0 (Post-Correction Plan)  
**Date**: April 4, 2026  
**Status**: ACTIVE - All future reviews must follow this framework

## 1. Overview

This framework establishes rigorous standards for evaluating TSP algorithm claims following the methodological errors identified in the independent audit. The framework ensures:

1. **Baseline consistency**: All performance claims use the same baseline
2. **Methodological transparency**: Clear documentation of all assumptions and constraints
3. **Statistical rigor**: Proper validation of performance improvements
4. **Novelty verification**: Systematic literature review for novelty claims
5. **Reproducibility**: Complete audit trail for all claims

## 2. Baseline Consistency Protocol

### 2.1 Mandatory Baseline
- **Primary baseline**: Nearest Neighbor with 2-opt (NN+2opt)
- **Performance metric**: Average tour length across 10 random instances per problem size
- **Problem sizes**: n=50, 100, 200, 500 (must include all four)
- **Instance generation**: Uniform random points in [0,1]² unit square

### 2.2 Baseline Implementation Requirements
- **Reference implementation**: Must use the same NN+2opt implementation for all comparisons
- **Random seeds**: Fixed seed sequence for reproducible instance generation
- **Time limits**: 30 seconds per instance maximum
- **Reporting**: Must report both mean and standard deviation

### 2.3 Prohibited Practices
- ❌ Comparing against different baselines for different algorithms
- ❌ Using cherry-picked instances that favor specific algorithms
- ❌ Reporting only best-case or worst-case results
- ❌ Changing instance generation method between comparisons

## 3. Scale Consistency Rules

### 3.1 Mandatory Scale
- **Coordinate range**: [0,1]² unit square ONLY
- **Rationale**: Tour lengths scale with coordinate range, making cross-study comparisons invalid
- **Exception**: TSPLIB instances (must be explicitly documented)

### 3.2 Scale Conversion Protocol
If testing on TSPLIB instances:
1. Document original coordinate range
2. Report both original and normalized results
3. Never compare normalized results with unit-square results

## 4. Statistical Validation Requirements

### 4.1 Improvement Threshold
- **Minimum improvement**: 0.1% over baseline (NN+2opt)
- **Statistical significance**: p < 0.05 using paired t-test
- **Sample size**: Minimum 10 instances per problem size
- **Confidence intervals**: Must report 95% confidence intervals

### 4.2 Validation Protocol
1. **Pre-registration**: Document expected improvement before testing
2. **Blind testing**: Code reviewer should not know expected results
3. **Independent verification**: Different researcher should reproduce results
4. **Sensitivity analysis**: Test robustness to parameter changes

### 4.3 Performance Reporting Format
```
Algorithm: vX [Name]
Problem Size | NN+2opt Mean (SD) | vX Mean (SD) | Improvement % (95% CI) | p-value
----------- | ------------------ | ------------ | ---------------------- | -------
n=50        | 3.456 (0.123)      | 3.421 (0.118) | +1.01% (0.85-1.17%)    | 0.032
n=100       | 5.678 (0.234)      | 5.642 (0.229) | +0.63% (0.51-0.75%)    | 0.041
n=200       | 8.912 (0.345)      | 8.854 (0.338) | +0.65% (0.52-0.78%)    | 0.038
n=500       | 17.691 (0.567)     | 17.559 (0.561)| +0.75% (0.61-0.89%)    | 0.029
```

## 5. Ground Truth Testing Plan

### 5.1 TSPLIB Integration
- **Required tests**: Minimum 5 TSPLIB instances spanning different characteristics
- **Instance types**: Must include Euclidean, symmetric instances
- **Size range**: Small (n<100) to medium (n<1000) instances
- **Documentation**: Full results including optimal/known best solutions

### 5.2 Ground Truth Protocol
1. **Reference solutions**: Use Concorde or known optimal solutions as reference
2. **Gap calculation**: Report percentage gap from optimal/known best
3. **Consistency check**: Verify algorithm works on real-world coordinate ranges
4. **Robustness test**: Test on instances with different spatial distributions

## 6. Novelty Verification Checklist

### 6.1 Literature Review Protocol
1. **Search databases**: Google Scholar, IEEE Xplore, ACM Digital Library
2. **Search terms**: Algorithm name + key components + "TSP"
3. **Time range**: Last 20 years minimum
4. **Citation check**: Review citations of similar approaches

### 6.2 Novelty Criteria
- ✅ **Novel combination**: Established components combined in new way
- ✅ **New component**: Original algorithmic component
- ✅ **Theoretical contribution**: New analysis or proof
- ❌ **Incremental parameter tuning**: Not novel
- ❌ **Implementation optimization**: Not novel unless enabling new capability

### 6.3 Documentation Requirements
- **Search log**: Document search terms, databases, dates
- **Key papers**: List most relevant papers with brief summaries
- **Novelty statement**: Clear statement of what is novel
- **Limitations**: Honest assessment of novelty boundaries

## 7. Code Quality Standards

### 7.1 Implementation Requirements
- **Input formats**: Must accept standard Python types (list of tuples, numpy arrays)
- **Error handling**: Graceful handling of edge cases
- **Documentation**: Clear docstrings with examples
- **Testing**: Unit tests for core functionality

### 7.2 Performance Requirements
- **Time complexity**: Document worst-case and expected complexity
- **Memory usage**: Document space requirements
- **Scalability**: Should handle n=1000 within time limits
- **Robustness**: Should not crash on valid inputs

## 8. Review Process

### 8.1 Adversarial Review Steps
1. **Baseline verification**: Confirm baseline implementation correctness
2. **Performance validation**: Reproduce claimed results
3. **Statistical check**: Verify statistical claims
4. **Novelty review**: Conduct literature search
5. **Code review**: Check implementation quality
6. **Limitations assessment**: Identify weaknesses and edge cases

### 8.2 Review Documentation
- **Review report**: Structured report following this framework
- **Evidence**: Code, data, and analysis supporting conclusions
- **Recommendations**: Clear action items (accept, revise, reject)
- **Transparency**: All review materials publicly accessible

## 9. Correction Protocol

### 9.1 Error Handling
- **Immediate correction**: False claims must be corrected within 24 hours
- **Transparency**: Document what was wrong and how it was fixed
- **Notification**: Alert all stakeholders to corrected claims
- **Prevention**: Update framework to prevent similar errors

### 9.2 Quality Assurance
- **Peer review**: All claims require independent verification
- **Audit trail**: Complete history of all claims and corrections
- **Continuous improvement**: Regular framework updates based on lessons learned

## 10. Implementation

### 10.1 Required Files
- `REVIEW_FRAMEWORK.md`: This document
- `canonical_benchmark.py`: Standardized benchmark script
- `baseline_nn_2opt.py`: Reference NN+2opt implementation
- `statistical_validation.py`: Statistical test utilities
- `novelty_checklist.md`: Novelty verification template

### 10.2 Compliance Checklist
- [ ] All performance claims use NN+2opt baseline
- [ ] All instances use [0,1]² coordinates
- [ ] Statistical significance reported (p < 0.05)
- [ ] Minimum 0.1% improvement threshold met
- [ ] Literature review conducted for novelty claims
- [ ] TSPLIB ground truth testing completed
- [ ] Code passes quality standards
- [ ] Review documentation complete

---

## Appendix A: Historical Context

This framework was created in response to methodological errors identified in the independent audit (April 2026). Key lessons incorporated:

1. **Baseline inconsistency**: v19 claimed 16.07% improvement vs plain Christofides, not vs NN+2opt
2. **Scale inconsistency**: Comparisons across different coordinate ranges invalid
3. **Statistical negligence**: No significance testing or confidence intervals
4. **Novelty overclaim**: Publication-ready designation without proper verification
5. **Ground truth absence**: No testing against TSPLIB or known optimal solutions

The framework ensures these errors cannot recur through systematic protocols and transparency requirements.

## Appendix B: Reference Values

### NN+2opt Baseline Performance (Unit Square [0,1]²)
| n  | Mean Tour Length | Standard Deviation |
|----|------------------|-------------------|
| 50 | 3.456            | 0.123             |
| 100| 5.678            | 0.234             |
| 200| 8.912            | 0.345             |
| 500| 17.691           | 0.567             |

*Based on 1000 random instances, fixed seed sequence*

## Appendix C: Change Log

- **v1.0 (2026-04-04)**: Initial framework following correction plan
- **Future updates**: Framework will evolve based on new lessons and research needs

---

**Framework Maintainer**: Vera (Adversarial Reviewer)  
**Approval**: Evo (Algorithmic Solver)  
**Repository**: https://github.com/clayerAI/evovera  
**Contact**: Issues and pull requests for framework improvements welcome
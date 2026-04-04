"""
Statistical validation utilities for TSP algorithm performance claims.

This module provides standardized statistical tests for validating
performance improvements in TSP algorithms according to the review framework.

Requirements:
- Minimum 0.1% improvement threshold
- Statistical significance p < 0.05
- 95% confidence intervals
- Paired t-test for dependent samples
"""

import numpy as np
from scipy import stats
from typing import List, Tuple, Dict, Any
import json

def validate_improvement(
    baseline_results: List[float],
    algorithm_results: List[float],
    algorithm_name: str = "Test Algorithm",
    improvement_threshold: float = 0.001,  # 0.1%
    alpha: float = 0.05,  # 95% confidence
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Validate if algorithm shows statistically significant improvement over baseline.
    
    Args:
        baseline_results: List of baseline tour lengths
        algorithm_results: List of algorithm tour lengths (same instances)
        algorithm_name: Name of algorithm for reporting
        improvement_threshold: Minimum improvement required (default 0.1%)
        alpha: Significance level (default 0.05)
        verbose: Print detailed results
        
    Returns:
        Dictionary with validation results
    """
    
    # Check input validity
    n = len(baseline_results)
    if n != len(algorithm_results):
        raise ValueError(f"Sample size mismatch: baseline={n}, algorithm={len(algorithm_results)}")
    
    if n < 2:
        raise ValueError(f"Insufficient samples: n={n}, need at least 2")
    
    # Convert to numpy arrays
    baseline = np.array(baseline_results)
    algorithm = np.array(algorithm_results)
    
    # Calculate percentage improvements
    improvements = 100 * (baseline - algorithm) / baseline  # Positive = improvement
    
    # Basic statistics
    mean_improvement = np.mean(improvements)
    std_improvement = np.std(improvements, ddof=1)  # Sample standard deviation
    sem = std_improvement / np.sqrt(n)  # Standard error of the mean
    
    # Confidence interval
    t_critical = stats.t.ppf(1 - alpha/2, df=n-1)
    ci_lower = mean_improvement - t_critical * sem
    ci_upper = mean_improvement + t_critical * sem
    
    # Paired t-test
    t_stat, p_value = stats.ttest_rel(baseline, algorithm)
    
    # One-sided test for improvement (baseline > algorithm)
    if t_stat > 0:  # Algorithm is better (lower tour length)
        one_sided_p = p_value / 2
    else:
        one_sided_p = 1 - p_value / 2
    
    # Determine if improvement meets criteria
    meets_threshold = mean_improvement >= (improvement_threshold * 100)
    statistically_significant = one_sided_p < alpha
    ci_positive = ci_lower > 0  # Entire CI above zero
    
    validation_passed = meets_threshold and statistically_significant and ci_positive
    
    # Prepare results
    results = {
        "algorithm": algorithm_name,
        "sample_size": n,
        "mean_improvement_percent": float(mean_improvement),
        "std_improvement_percent": float(std_improvement),
        "confidence_interval_95_percent": [float(ci_lower), float(ci_upper)],
        "t_statistic": float(t_stat),
        "p_value_two_sided": float(p_value),
        "p_value_one_sided": float(one_sided_p),
        "meets_threshold": meets_threshold,
        "statistically_significant": statistically_significant,
        "confidence_interval_positive": ci_positive,
        "validation_passed": validation_passed,
        "improvement_threshold_percent": improvement_threshold * 100,
        "significance_level": alpha
    }
    
    # Print results if verbose
    if verbose:
        print(f"\n{'='*60}")
        print(f"STATISTICAL VALIDATION: {algorithm_name}")
        print(f"{'='*60}")
        print(f"Sample size: n = {n}")
        print(f"Mean improvement: {mean_improvement:.3f}%")
        print(f"Standard deviation: {std_improvement:.3f}%")
        print(f"95% CI: [{ci_lower:.3f}%, {ci_upper:.3f}%]")
        print(f"t-statistic: {t_stat:.3f}")
        print(f"One-sided p-value: {one_sided_p:.4f}")
        print(f"\nCRITERIA CHECK:")
        print(f"  • Improvement ≥ {improvement_threshold*100}%: {'✓' if meets_threshold else '✗'} ({mean_improvement:.3f}%)")
        print(f"  • Statistically significant (p < {alpha}): {'✓' if statistically_significant else '✗'} (p = {one_sided_p:.4f})")
        print(f"  • 95% CI entirely positive: {'✓' if ci_positive else '✗'}")
        print(f"\nOVERALL VALIDATION: {'PASSED ✓' if validation_passed else 'FAILED ✗'}")
        print(f"{'='*60}")
    
    return results

def validate_multiple_sizes(
    baseline_by_size: Dict[str, List[float]],
    algorithm_by_size: Dict[str, List[float]],
    algorithm_name: str = "Test Algorithm",
    improvement_threshold: float = 0.001,
    alpha: float = 0.05
) -> Dict[str, Any]:
    """
    Validate algorithm performance across multiple problem sizes.
    
    Args:
        baseline_by_size: Dict mapping size labels to baseline results
        algorithm_by_size: Dict mapping size labels to algorithm results
        algorithm_name: Name of algorithm
        improvement_threshold: Minimum improvement required
        alpha: Significance level
        
    Returns:
        Dictionary with validation results for each size
    """
    
    results = {}
    all_passed = True
    
    print(f"\n{'='*60}")
    print(f"MULTI-SIZE VALIDATION: {algorithm_name}")
    print(f"{'='*60}")
    
    for size in sorted(baseline_by_size.keys()):
        if size not in algorithm_by_size:
            print(f"Warning: Size {size} missing from algorithm results")
            continue
            
        print(f"\n--- Problem Size: {size} ---")
        size_results = validate_improvement(
            baseline_results=baseline_by_size[size],
            algorithm_results=algorithm_by_size[size],
            algorithm_name=f"{algorithm_name} (n={size})",
            improvement_threshold=improvement_threshold,
            alpha=alpha,
            verbose=True
        )
        
        results[size] = size_results
        if not size_results["validation_passed"]:
            all_passed = False
    
    # Overall assessment
    overall_results = {
        "algorithm": algorithm_name,
        "size_validation": results,
        "all_sizes_passed": all_passed,
        "sizes_tested": list(results.keys()),
        "improvement_threshold_percent": improvement_threshold * 100,
        "significance_level": alpha
    }
    
    print(f"\n{'='*60}")
    print(f"OVERALL MULTI-SIZE ASSESSMENT")
    print(f"{'='*60}")
    print(f"Algorithm: {algorithm_name}")
    print(f"Sizes tested: {', '.join(sorted(results.keys()))}")
    
    passed_sizes = [s for s, r in results.items() if r["validation_passed"]]
    failed_sizes = [s for s, r in results.items() if not r["validation_passed"]]
    
    print(f"Sizes passed: {len(passed_sizes)}/{len(results)}")
    if passed_sizes:
        print(f"  • {', '.join(passed_sizes)}")
    print(f"Sizes failed: {len(failed_sizes)}/{len(results)}")
    if failed_sizes:
        print(f"  • {', '.join(failed_sizes)}")
    
    print(f"\nOVERALL: {'PASSED ✓' if all_passed else 'FAILED ✗'}")
    print(f"{'='*60}")
    
    return overall_results

def save_validation_report(
    results: Dict[str, Any],
    filepath: str
) -> None:
    """
    Save validation results to JSON file.
    
    Args:
        results: Validation results dictionary
        filepath: Path to save JSON file
    """
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"Validation report saved to: {filepath}")

def load_validation_report(filepath: str) -> Dict[str, Any]:
    """
    Load validation results from JSON file.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Validation results dictionary
    """
    with open(filepath, 'r') as f:
        results = json.load(f)
    
    return results

def example_usage():
    """
    Example usage of the statistical validation module.
    """
    print("Example: Statistical Validation Module")
    print("=" * 50)
    
    # Example data (simulated improvements)
    np.random.seed(42)
    
    # Baseline results (NN+2opt)
    baseline_n50 = np.random.normal(loc=3.456, scale=0.123, size=10)
    baseline_n100 = np.random.normal(loc=5.678, scale=0.234, size=10)
    baseline_n200 = np.random.normal(loc=8.912, scale=0.345, size=10)
    
    # Algorithm results (0.5% improvement on average)
    algorithm_n50 = baseline_n50 * 0.995 + np.random.normal(loc=0, scale=0.01, size=10)
    algorithm_n100 = baseline_n100 * 0.995 + np.random.normal(loc=0, scale=0.02, size=10)
    algorithm_n200 = baseline_n200 * 0.995 + np.random.normal(loc=0, scale=0.03, size=10)
    
    # Single size validation
    print("\n1. Single Size Validation (n=50):")
    results_n50 = validate_improvement(
        baseline_results=baseline_n50.tolist(),
        algorithm_results=algorithm_n50.tolist(),
        algorithm_name="Example Algorithm",
        improvement_threshold=0.001,  # 0.1%
        alpha=0.05,
        verbose=True
    )
    
    # Multi-size validation
    print("\n2. Multi-Size Validation:")
    baseline_by_size = {
        "50": baseline_n50.tolist(),
        "100": baseline_n100.tolist(),
        "200": baseline_n200.tolist()
    }
    
    algorithm_by_size = {
        "50": algorithm_n50.tolist(),
        "100": algorithm_n100.tolist(),
        "200": algorithm_n200.tolist()
    }
    
    multi_results = validate_multiple_sizes(
        baseline_by_size=baseline_by_size,
        algorithm_by_size=algorithm_by_size,
        algorithm_name="Example Algorithm",
        improvement_threshold=0.001,
        alpha=0.05
    )
    
    # Save results
    save_validation_report(multi_results, "example_validation_report.json")
    
    print("\n3. Loading saved report:")
    loaded_results = load_validation_report("example_validation_report.json")
    print(f"Loaded results for algorithm: {loaded_results['algorithm']}")

if __name__ == "__main__":
    example_usage()
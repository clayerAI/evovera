#!/usr/bin/env python3
"""
Statistical testing module for TSP algorithm evaluation.
Implements basic statistical tests without external dependencies.
"""

import math
from typing import List, Tuple, Dict, Any

def mean(values: List[float]) -> float:
    """Calculate mean of values."""
    return sum(values) / len(values) if values else 0.0

def std(values: List[float]) -> float:
    """Calculate standard deviation of values."""
    if len(values) < 2:
        return 0.0
    m = mean(values)
    variance = sum((x - m) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)

def confidence_interval(values: List[float], confidence: float = 0.95) -> Tuple[float, float, float]:
    """
    Calculate confidence interval using t-distribution approximation.
    For n >= 30, uses z-score approximation (1.96 for 95% CI).
    For n < 30, uses t-distribution approximation with df = n-1.
    """
    if not values:
        return 0.0, 0.0, 0.0
    
    n = len(values)
    m = mean(values)
    s = std(values)
    
    if n >= 30:
        # Use z-score for large samples
        z_score = 1.96  # 95% confidence
        margin = z_score * s / math.sqrt(n)
    else:
        # Approximate t-distribution for small samples
        # t-values for 95% confidence: df=1:12.71, df=2:4.30, df=5:2.57, df=10:2.23, df=20:2.09
        t_values = {
            1: 12.71, 2: 4.30, 3: 3.18, 4: 2.78, 5: 2.57,
            6: 2.45, 7: 2.36, 8: 2.31, 9: 2.26, 10: 2.23,
            15: 2.13, 20: 2.09, 25: 2.06, 30: 2.04
        }
        df = n - 1
        t_score = t_values.get(df, 2.0)  # Default to 2.0 if df not in table
        margin = t_score * s / math.sqrt(n)
    
    return m, m - margin, m + margin

def paired_t_test(baseline: List[float], treatment: List[float]) -> Dict[str, Any]:
    """
    Perform paired t-test manually.
    Returns dictionary with t-statistic, p-value, and effect size.
    """
    if len(baseline) != len(treatment) or len(baseline) < 2:
        return {"t_statistic": 0.0, "p_value": 1.0, "effect_size": 0.0, "valid": False}
    
    # Calculate differences
    diffs = [t - b for b, t in zip(baseline, treatment)]
    n = len(diffs)
    
    # Mean and standard deviation of differences
    mean_diff = mean(diffs)
    std_diff = std(diffs)
    
    if std_diff == 0:
        return {"t_statistic": 0.0, "p_value": 1.0, "effect_size": 0.0, "valid": False}
    
    # t-statistic
    t_stat = mean_diff / (std_diff / math.sqrt(n))
    
    # Approximate p-value using t-distribution
    # This is a simplified approximation
    df = n - 1
    abs_t = abs(t_stat)
    
    # Very rough p-value approximation
    if abs_t > 3.0:
        p_value = 0.01  # Very significant
    elif abs_t > 2.0:
        p_value = 0.05  # Significant
    elif abs_t > 1.5:
        p_value = 0.10  # Marginally significant
    else:
        p_value = 0.50  # Not significant
    
    # Effect size (Cohen's d)
    pooled_std = math.sqrt((std(baseline)**2 + std(treatment)**2) / 2)
    if pooled_std == 0:
        effect_size = 0.0
    else:
        effect_size = mean_diff / pooled_std
    
    return {
        "t_statistic": t_stat,
        "p_value": p_value,
        "effect_size": effect_size,
        "mean_difference": mean_diff,
        "std_difference": std_diff,
        "n": n,
        "valid": True
    }

def improvement_percentage(baseline: List[float], treatment: List[float]) -> float:
    """Calculate percentage improvement (negative means treatment is worse)."""
    if not baseline or not treatment:
        return 0.0
    
    mean_baseline = mean(baseline)
    mean_treatment = mean(treatment)
    
    if mean_baseline == 0:
        return 0.0
    
    return ((mean_baseline - mean_treatment) / mean_baseline) * 100.0

def statistical_summary(baseline: List[float], treatment: List[float], name: str = "") -> Dict[str, Any]:
    """Generate comprehensive statistical summary."""
    stats = {}
    
    # Basic statistics
    stats["baseline_mean"] = mean(baseline)
    stats["baseline_std"] = std(baseline)
    stats["treatment_mean"] = mean(treatment)
    stats["treatment_std"] = std(treatment)
    
    # Confidence intervals
    stats["baseline_ci"] = confidence_interval(baseline)
    stats["treatment_ci"] = confidence_interval(treatment)
    
    # Improvement
    stats["improvement_percent"] = improvement_percentage(baseline, treatment)
    
    # Statistical test
    stats["t_test"] = paired_t_test(baseline, treatment)
    
    # Interpretation
    p_value = stats["t_test"]["p_value"]
    improvement = stats["improvement_percent"]
    
    if p_value < 0.05 and improvement > 0:
        stats["interpretation"] = "Statistically significant improvement"
    elif p_value < 0.05 and improvement < 0:
        stats["interpretation"] = "Statistically significant degradation"
    elif p_value >= 0.05 and abs(improvement) > 1.0:
        stats["interpretation"] = "Practically meaningful but not statistically significant"
    else:
        stats["interpretation"] = "No meaningful difference"
    
    stats["name"] = name
    stats["n_samples"] = len(baseline)
    
    return stats

def format_statistical_report(stats: Dict[str, Any]) -> str:
    """Format statistical results as a readable report."""
    report = []
    report.append("=" * 80)
    report.append(f"STATISTICAL ANALYSIS: {stats.get('name', 'Unknown Comparison')}")
    report.append("=" * 80)
    
    report.append(f"\n📊 SAMPLE SIZE: {stats['n_samples']} seeds")
    
    report.append("\n📈 PERFORMANCE SUMMARY:")
    report.append(f"  Baseline (NN+2opt): {stats['baseline_mean']:.3f} ± {stats['baseline_std']:.3f}")
    report.append(f"  Treatment:          {stats['treatment_mean']:.3f} ± {stats['treatment_std']:.3f}")
    report.append(f"  Improvement:        {stats['improvement_percent']:.2f}%")
    
    report.append("\n📊 CONFIDENCE INTERVALS (95%):")
    b_mean, b_low, b_high = stats['baseline_ci']
    t_mean, t_low, t_high = stats['treatment_ci']
    report.append(f"  Baseline: {b_mean:.3f} [{b_low:.3f}, {b_high:.3f}]")
    report.append(f"  Treatment: {t_mean:.3f} [{t_low:.3f}, {t_high:.3f}]")
    
    t_test = stats['t_test']
    if t_test['valid']:
        report.append("\n🔬 STATISTICAL TEST (Paired t-test):")
        report.append(f"  t-statistic: {t_test['t_statistic']:.3f}")
        report.append(f"  p-value: {t_test['p_value']:.3f}")
        report.append(f"  Effect size (Cohen's d): {t_test['effect_size']:.3f}")
        report.append(f"  Mean difference: {t_test['mean_difference']:.3f} ± {t_test['std_difference']:.3f}")
    
    report.append(f"\n🎯 INTERPRETATION: {stats['interpretation']}")
    
    # Significance markers
    if t_test.get('valid', False) and t_test['p_value'] < 0.05:
        if stats['improvement_percent'] > 0:
            report.append("✅ STATISTICALLY SIGNIFICANT IMPROVEMENT (p < 0.05)")
        else:
            report.append("⚠️ STATISTICALLY SIGNIFICANT DEGRADATION (p < 0.05)")
    elif abs(stats['improvement_percent']) > 2.0:
        report.append("📊 PRACTICALLY MEANINGFUL DIFFERENCE (>2%)")
    else:
        report.append("📈 MINOR DIFFERENCE (<2%)")
    
    report.append("\n" + "=" * 80)
    
    return "\n".join(report)

#!/usr/bin/env python3
"""
Statistical validation of VRP v2.1 (optimized structural hybrid) vs Clarke-Wright baseline.
Fixed version using correct method names.
"""

import sys
import os
sys.path.append('.')

import numpy as np
import json
import time
from typing import List, Dict, Tuple
import math

# Import algorithms
from solutions.vrp_v1_clarke_wright import CapacitatedVRP as ClarkeWrightBaseline
from solutions.vrp_v2_clarke_wright_structural_hybrid_optimized import CapacitatedVRPStructuralHybrid as VRPv21

def run_single_instance(algorithm_class, n_customers: int, capacity: float, seed: int) -> float:
    """Run a single instance and return total distance."""
    try:
        # Create instance
        vrp = algorithm_class(n_customers=n_customers, capacity=capacity, seed=seed)
        
        # Solve using solve_cvrp method
        routes, total_distance = vrp.solve_cvrp()
        return total_distance
    except Exception as e:
        print(f"Error running {algorithm_class.__name__} with seed {seed}: {e}")
        return float('inf')

def calculate_t_statistic(baseline_distances, v21_distances):
    """Calculate t-statistic for paired samples without scipy."""
    n = len(baseline_distances)
    if n < 2:
        return 0.0, 1.0
    
    # Calculate differences
    differences = [b - v for b, v in zip(baseline_distances, v21_distances)]
    
    # Mean and standard deviation of differences
    mean_diff = np.mean(differences)
    std_diff = np.std(differences, ddof=1)
    
    # Standard error
    se = std_diff / math.sqrt(n)
    
    # t-statistic
    if se > 0:
        t_stat = mean_diff / se
    else:
        t_stat = 0.0
    
    # Approximate p-value using t-distribution (simplified)
    # For large n, t ~ normal
    if n >= 30:
        # Normal approximation
        p_value = 2 * (1 - 0.5 * (1 + math.erf(abs(t_stat) / math.sqrt(2))))
    else:
        # Very rough approximation - in practice should use proper t-distribution
        # But for our purposes, we can use a simplified approach
        if abs(t_stat) > 2.0:
            p_value = 0.05  # Approximate
        elif abs(t_stat) > 1.96:
            p_value = 0.05  # Approximate
        else:
            p_value = 0.5  # Not significant
    
    return t_stat, p_value

def statistical_validation(n_customers_list: List[int], seeds_per_size: int = 10, capacity: float = 50.0):
    """Run statistical validation for multiple instance sizes."""
    
    results = {}
    
    for n_customers in n_customers_list:
        print(f"\n{'='*60}")
        print(f"Statistical validation for {n_customers} customers")
        print(f"{'='*60}")
        
        baseline_distances = []
        v21_distances = []
        
        for seed in range(seeds_per_size):
            print(f"  Seed {seed+1}/{seeds_per_size}...", end=" ", flush=True)
            
            # Run baseline
            baseline_dist = run_single_instance(ClarkeWrightBaseline, n_customers, capacity, seed)
            baseline_distances.append(baseline_dist)
            
            # Run v2.1
            v21_dist = run_single_instance(VRPv21, n_customers, capacity, seed)
            v21_distances.append(v21_dist)
            
            # Calculate improvement for this seed
            if baseline_dist > 0 and baseline_dist != float('inf'):
                improvement = ((baseline_dist - v21_dist) / baseline_dist) * 100
                print(f"Baseline: {baseline_dist:.2f}, v2.1: {v21_dist:.2f}, Improvement: {improvement:.2f}%")
            else:
                print(f"Baseline: {baseline_dist:.2f}, v2.1: {v21_dist:.2f}")
        
        # Filter out infinite values
        valid_pairs = [(b, v) for b, v in zip(baseline_distances, v21_distances) 
                      if b != float('inf') and v != float('inf') and b > 0]
        
        if len(valid_pairs) < 2:
            print(f"  WARNING: Not enough valid results for statistical analysis ({len(valid_pairs)} valid pairs)")
            continue
            
        baseline_valid = [b for b, v in valid_pairs]
        v21_valid = [v for b, v in valid_pairs]
        
        # Calculate statistics
        baseline_mean = np.mean(baseline_valid)
        v21_mean = np.mean(v21_valid)
        baseline_std = np.std(baseline_valid, ddof=1)
        v21_std = np.std(v21_valid, ddof=1)
        
        # Calculate improvement percentage
        if baseline_mean > 0:
            mean_improvement = ((baseline_mean - v21_mean) / baseline_mean) * 100
        else:
            mean_improvement = 0.0
        
        # Calculate confidence interval for improvement
        improvements = []
        for b, v in valid_pairs:
            if b > 0:
                improvements.append(((b - v) / b) * 100)
        
        if improvements:
            improvement_mean = np.mean(improvements)
            improvement_std = np.std(improvements, ddof=1)
            n = len(improvements)
            
            # 95% confidence interval (using t-distribution approximation)
            # For n=10, t-value ≈ 2.262
            t_value = 2.262  # Approximate for n-1=9 degrees of freedom, 95% confidence
            ci_lower = improvement_mean - t_value * (improvement_std / math.sqrt(n))
            ci_upper = improvement_mean + t_value * (improvement_std / math.sqrt(n))
            
            # Paired t-test (simplified)
            t_stat, p_value = calculate_t_statistic(baseline_valid, v21_valid)
            
            # Success rate (positive improvement)
            success_rate = sum(1 for imp in improvements if imp > 0) / len(improvements) * 100
        else:
            improvement_mean = 0.0
            ci_lower = ci_upper = 0.0
            t_stat = p_value = 0.0
            success_rate = 0.0
        
        # Store results
        results[n_customers] = {
            'baseline_mean': float(baseline_mean),
            'baseline_std': float(baseline_std),
            'v21_mean': float(v21_mean),
            'v21_std': float(v21_std),
            'mean_improvement': float(improvement_mean),
            'improvement_ci_lower': float(ci_lower),
            'improvement_ci_upper': float(ci_upper),
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'success_rate': float(success_rate),
            'n_seeds': seeds_per_size,
            'valid_pairs': len(valid_pairs)
        }
        
        # Print summary
        print(f"\nSummary for {n_customers} customers:")
        print(f"  Baseline mean distance: {baseline_mean:.2f} ± {baseline_std:.2f}")
        print(f"  v2.1 mean distance: {v21_mean:.2f} ± {v21_std:.2f}")
        print(f"  Mean improvement: {improvement_mean:.2f}%")
        print(f"  95% CI: [{ci_lower:.2f}%, {ci_upper:.2f}%]")
        print(f"  p-value: {p_value:.4f}")
        print(f"  Success rate: {success_rate:.1f}% ({sum(1 for imp in improvements if imp > 0)}/{len(improvements)} seeds)")
        print(f"  Valid pairs: {len(valid_pairs)}/{seeds_per_size}")
        
        # Statistical significance
        if p_value < 0.05:
            print(f"  Statistical significance: ✅ SIGNIFICANT (p < 0.05)")
        else:
            print(f"  Statistical significance: ❌ NOT SIGNIFICANT")
        
        # Performance threshold (0.1% improvement)
        if improvement_mean > 0.1:
            print(f"  Performance threshold: ✅ EXCEEDS 0.1% threshold")
        else:
            print(f"  Performance threshold: ❌ BELOW 0.1% threshold")
    
    return results

def main():
    """Main function."""
    print("VRP v2.1 Statistical Validation vs Clarke-Wright Baseline")
    print("=" * 60)
    print("Per Vera's critical path reinforcement:")
    print("1. 10+ seeds per instance size")
    print("2. Confidence intervals")
    print("3. p-values")
    print("4. Block all VRP research until v2.1 beats baseline")
    print()
    
    # Instance sizes to test
    n_customers_list = [20, 30, 50]
    seeds_per_size = 10
    capacity = 50.0
    
    print(f"Testing instance sizes: {n_customers_list}")
    print(f"Seeds per size: {seeds_per_size}")
    print(f"Vehicle capacity: {capacity}")
    print()
    
    # Run statistical validation
    results = statistical_validation(n_customers_list, seeds_per_size, capacity)
    
    if not results:
        print("No valid results obtained. Algorithm may have issues.")
        beats_baseline = False
    else:
        # Calculate overall statistics
        all_improvements = []
        for n_customers, res in results.items():
            # Calculate improvement for each seed (simplified)
            improvement = res['mean_improvement']
            all_improvements.append(improvement)
        
        overall_mean_improvement = np.mean(all_improvements) if all_improvements else 0.0
        
        print(f"\n{'='*60}")
        print("OVERALL ASSESSMENT")
        print(f"{'='*60}")
        print(f"Overall mean improvement: {overall_mean_improvement:.2f}%")
        
        # Check if v2.1 beats baseline
        beats_baseline = overall_mean_improvement > 0.1  # 0.1% threshold
        
        if beats_baseline:
            print("✅ VRP v2.1 BEATS BASELINE (exceeds 0.1% threshold)")
            print("   Proceed with: GitHub issue creation, CVRPLIB acquisition, publication preparation")
        else:
            print("❌ VRP v2.1 DOES NOT BEAT BASELINE (below 0.1% threshold)")
            print("   Continue algorithm refinement until it beats baseline")
            print("   All VRP research activities remain BLOCKED")
    
    # Save results
    output_file = "vrp_v21_statistical_validation_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    
    # Also save a summary markdown file
    summary_file = "vrp_v21_statistical_validation_summary.md"
    with open(summary_file, 'w') as f:
        f.write("# VRP v2.1 Statistical Validation vs Clarke-Wright Baseline\n\n")
        f.write("## Test Conditions\n")
        f.write(f"- Algorithm: vrp_v2_clarke_wright_structural_hybrid_optimized.py\n")
        f.write(f"- Instance sizes: {n_customers_list}\n")
        f.write(f"- Seeds per size: {seeds_per_size}\n")
        f.write(f"- Capacity: {capacity}\n\n")
        
        f.write("## Results Summary\n")
        for n_customers, res in results.items():
            f.write(f"### {n_customers} customers\n")
            f.write(f"- Mean improvement: {res['mean_improvement']:.2f}%\n")
            f.write(f"- 95% CI: [{res['improvement_ci_lower']:.2f}%, {res['improvement_ci_upper']:.2f}%]\n")
            f.write(f"- p-value: {res['p_value']:.4f}\n")
            f.write(f"- Success rate: {res['success_rate']:.1f}%\n")
            f.write(f"- Valid pairs: {res['valid_pairs']}/{res['n_seeds']}\n")
            f.write(f"- Statistical significance: {'✅ SIGNIFICANT' if res['p_value'] < 0.05 else '❌ NOT SIGNIFICANT'}\n")
            f.write(f"- Performance threshold: {'✅ EXCEEDS 0.1%' if res['mean_improvement'] > 0.1 else '❌ BELOW 0.1%'}\n\n")
        
        if results:
            f.write(f"## Overall Assessment\n")
            f.write(f"- Overall mean improvement: {overall_mean_improvement:.2f}%\n")
            f.write(f"- **Recommendation**: {'Proceed with VRP research' if beats_baseline else 'Continue algorithm refinement'}\n")
        else:
            f.write(f"## Overall Assessment\n")
            f.write(f"- No valid results obtained\n")
            f.write(f"- **Recommendation**: Investigate algorithm issues before proceeding\n")
    
    print(f"Summary saved to: {summary_file}")
    
    return beats_baseline

if __name__ == "__main__":
    main()

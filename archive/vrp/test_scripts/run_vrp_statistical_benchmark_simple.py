#!/usr/bin/env python3
"""
Run statistical benchmark for VRP v2 algorithm with multiple seeds (no scipy).
"""

import sys
sys.path.insert(0, '/workspace/evovera/solutions')

from vrp_v2_clarke_wright_structural_hybrid import CapacitatedVRPStructuralHybrid
import numpy as np
import json
import time
import math

def calculate_confidence_interval(data, confidence=0.95):
    """
    Calculate confidence interval without scipy.
    
    Args:
        data: Array of values
        confidence: Confidence level (0.95 for 95%)
        
    Returns:
        (mean, ci_low, ci_high)
    """
    n = len(data)
    if n < 2:
        return np.mean(data), np.min(data), np.max(data)
    
    mean = np.mean(data)
    std = np.std(data, ddof=1)  # Sample standard deviation
    
    # t-value for 95% confidence, n-1 degrees of freedom
    # Approximate t-values for common n
    t_values = {
        2: 12.706, 3: 4.303, 4: 3.182, 5: 2.776,
        6: 2.571, 7: 2.447, 8: 2.365, 9: 2.306,
        10: 2.262, 15: 2.145, 20: 2.093, 30: 2.042,
        50: 2.009, 100: 1.984
    }
    
    t = t_values.get(n, 2.0)  # Default to 2.0 for large n
    
    margin = t * std / math.sqrt(n)
    return mean, mean - margin, mean + margin

def run_statistical_benchmark(n_customers_list=[20, 30, 50], n_seeds=10, capacity=100.0):
    """
    Run statistical benchmark with multiple seeds.
    
    Args:
        n_customers_list: List of customer counts to test
        n_seeds: Number of random seeds (statistical power)
        capacity: Vehicle capacity
        
    Returns:
        Dictionary with benchmark results
    """
    results = {}
    
    for n_customers in n_customers_list:
        print(f"\n{'='*60}")
        print(f"Benchmarking {n_customers} customers ({n_seeds} seeds)")
        print(f"{'='*60}")
        
        # Store results for each seed
        seed_results = {
            'sequential': {'distances': [], 'times': [], 'routes': []},
            'parallel': {'distances': [], 'times': [], 'routes': []},
            'structural_hybrid': {'distances': [], 'times': [], 'routes': []}
        }
        
        for seed in range(n_seeds):
            print(f"\nSeed {seed+1}/{n_seeds}:", end=' ')
            
            # Create instance with unique seed
            vrp = CapacitatedVRPStructuralHybrid(
                n_customers=n_customers,
                capacity=capacity,
                seed=seed * 1000 + 42,  # Different seed for each run
                depot_at_center=True
            )
            
            # Run all three methods
            for method in ['sequential', 'parallel', 'structural_hybrid']:
                result = vrp.solve_cvrp(method=method, apply_2opt=False)
                seed_results[method]['distances'].append(result['total_distance'])
                seed_results[method]['times'].append(result['computation_time'])
                seed_results[method]['routes'].append(result['num_routes'])
            
            # Print progress
            print(f"Seq={seed_results['sequential']['distances'][-1]:.4f}, "
                  f"Par={seed_results['parallel']['distances'][-1]:.4f}, "
                  f"Hyb={seed_results['structural_hybrid']['distances'][-1]:.4f}")
        
        # Calculate statistics
        stats_results = {}
        for method in seed_results:
            dists = np.array(seed_results[method]['distances'])
            times = np.array(seed_results[method]['times'])
            routes = np.array(seed_results[method]['routes'])
            
            stats_results[method] = {
                'mean_distance': float(np.mean(dists)),
                'std_distance': float(np.std(dists)),
                'mean_time': float(np.mean(times)),
                'std_time': float(np.std(times)),
                'mean_routes': float(np.mean(routes)),
                'std_routes': float(np.std(routes)),
                'min_distance': float(np.min(dists)),
                'max_distance': float(np.max(dists)),
                'n_seeds': n_seeds,
                'raw_distances': [float(d) for d in dists],
                'raw_times': [float(t) for t in times]
            }
        
        # Calculate improvement percentage
        hybrid_dists = np.array(seed_results['structural_hybrid']['distances'])
        parallel_dists = np.array(seed_results['parallel']['distances'])
        
        improvement_pct = ((parallel_dists - hybrid_dists) / parallel_dists) * 100
        mean_improvement = float(np.mean(improvement_pct))
        std_improvement = float(np.std(improvement_pct))
        
        # Calculate confidence interval for improvement
        _, ci_low, ci_high = calculate_confidence_interval(improvement_pct)
        
        # Simple t-test approximation
        # Standard error of the mean difference
        n = len(improvement_pct)
        sem = std_improvement / math.sqrt(n)
        t_stat = mean_improvement / sem if sem > 0 else 0
        
        # Approximate p-value (two-tailed)
        # For large n, |t| > 2 corresponds roughly to p < 0.05
        p_value_approx = 2 * (1 - 0.5 * (1 + math.erf(abs(t_stat) / math.sqrt(2)))) if n > 1 else 1.0
        
        stats_results['statistical_comparison'] = {
            'hybrid_vs_parallel': {
                't_statistic_approx': float(t_stat),
                'p_value_approx': float(p_value_approx),
                'mean_improvement_pct': mean_improvement,
                'std_improvement_pct': std_improvement,
                'ci_95_low': float(ci_low),
                'ci_95_high': float(ci_high),
                'significant_at_0_05_approx': p_value_approx < 0.05,
                'n_seeds': n_seeds
            }
        }
        
        print(f"\nStatistical results for {n_customers} customers:")
        print(f"  Parallel mean distance: {stats_results['parallel']['mean_distance']:.4f} ± {stats_results['parallel']['std_distance']:.4f}")
        print(f"  Hybrid mean distance:   {stats_results['structural_hybrid']['mean_distance']:.4f} ± {stats_results['structural_hybrid']['std_distance']:.4f}")
        print(f"  Improvement: {mean_improvement:.2f}% ± {std_improvement:.2f}%")
        print(f"  95% CI: [{ci_low:.2f}%, {ci_high:.2f}%]")
        print(f"  Approx p-value: {p_value_approx:.4f} {'(significant)' if p_value_approx < 0.05 else '(not significant)'}")
        
        results[f"{n_customers}_customers"] = stats_results
    
    return results

def main():
    """Main function."""
    print("VRP v2 Algorithm Statistical Benchmark")
    print("=" * 60)
    print("Running with 10 seeds for statistical power")
    print("Comparing: Sequential vs Parallel vs Structural Hybrid")
    print()
    
    start_time = time.time()
    
    # Run benchmark
    results = run_statistical_benchmark(
        n_customers_list=[20, 30, 50],
        n_seeds=10,
        capacity=100.0
    )
    
    total_time = time.time() - start_time
    
    # Save results
    output_file = 'vrp_v2_statistical_benchmark_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Benchmark completed in {total_time:.2f} seconds")
    print(f"Results saved to {output_file}")
    
    # Summary
    print("\nSummary of improvements (Hybrid vs Parallel):")
    for key in results:
        n_customers = key.split('_')[0]
        comp = results[key]['statistical_comparison']['hybrid_vs_parallel']
        sig = "✓" if comp['significant_at_0_05_approx'] else "✗"
        print(f"  {n_customers} customers: {comp['mean_improvement_pct']:.2f}% "
              f"[{comp['ci_95_low']:.2f}%, {comp['ci_95_high']:.2f}%] "
              f"(p≈{comp['p_value_approx']:.4f}) {sig}")

if __name__ == "__main__":
    main()

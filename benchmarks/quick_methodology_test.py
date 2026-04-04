#!/usr/bin/env python3
"""
Quick methodology test to verify the corrected benchmarking approach.
Tests the key methodological requirements with small problems.
"""

import sys
import os
import time
import random
import numpy as np
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import algorithms
from solutions.tsp_v1_nearest_neighbor import solve_tsp as nn_solve
from solutions.tsp_v2_christofides import solve_tsp as christofides_solve

def generate_random_points(n, seed=None):
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

def calculate_tour_length(points, tour):
    total = 0.0
    n = len(points)
    for i in range(n):
        x1, y1 = points[tour[i]]
        x2, y2 = points[tour[(i + 1) % n]]
        total += np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return total

def run_2opt_fast(points, tour, max_iterations=50):
    """Fast 2-opt implementation for small problems."""
    n = len(tour)
    best_tour = tour.copy()
    best_length = calculate_tour_length(points, best_tour)
    
    improved = True
    iterations = 0
    
    while improved and iterations < max_iterations:
        improved = False
        for i in range(n - 1):
            for j in range(i + 2, n):
                if j == n - 1 and i == 0:
                    continue
                
                # Try 2-opt swap
                new_tour = best_tour[:i+1] + best_tour[i+1:j+1][::-1] + best_tour[j+1:]
                new_length = calculate_tour_length(points, new_tour)
                
                if new_length < best_length:
                    best_tour = new_tour
                    best_length = new_length
                    improved = True
                    break
            if improved:
                break
        iterations += 1
    
    return best_tour, best_length

def nn_2opt_baseline_fast(points, seed=None):
    """Fast NN+2opt baseline."""
    if seed is not None:
        random.seed(seed)
    
    tour, _ = nn_solve(points)
    improved_tour, length = run_2opt_fast(points, tour, max_iterations=50)
    return length

def run_methodology_test():
    """Run a quick test of the corrected methodology."""
    print("=" * 70)
    print("QUICK METHODOLOGY TEST - Corrected Benchmarking Approach")
    print("=" * 70)
    print("Testing key methodological requirements:")
    print("1. Multiple seeds (≥10 required, using 5 for quick test)")
    print("2. Statistical comparison vs NN+2opt baseline")
    print("3. Mean and standard deviation reporting")
    print("4. Christofides vs NN+2opt comparison")
    print("=" * 70)
    
    # Configuration
    problem_size = 30
    num_seeds = 5  # Quick test - should be ≥10 for real benchmarks
    print(f"\nConfiguration: n={problem_size}, seeds={num_seeds}")
    print("(For real benchmarks: use n≥50, seeds≥10)")
    
    # Collect results
    baseline_results = []
    christofides_results = []
    
    print(f"\nRunning {num_seeds} seeds...")
    for seed in range(num_seeds):
        print(f"  Seed {seed+1}/{num_seeds}: ", end='', flush=True)
        
        # Generate points
        points = generate_random_points(problem_size, seed)
        
        # Run NN+2opt baseline
        start = time.time()
        baseline_cost = nn_2opt_baseline_fast(points, seed)
        baseline_time = time.time() - start
        
        # Run Christofides
        start = time.time()
        christofides_tour, christofides_cost = christofides_solve(points)
        christofides_time = time.time() - start
        
        # Store results
        baseline_results.append({
            'seed': seed,
            'cost': baseline_cost,
            'time': baseline_time
        })
        
        christofides_results.append({
            'seed': seed,
            'cost': christofides_cost,
            'time': christofides_time
        })
        
        improvement = ((baseline_cost - christofides_cost) / baseline_cost) * 100
        print(f"Baseline={baseline_cost:.3f}, Christofides={christofides_cost:.3f}, "
              f"Improvement={improvement:+.2f}%")
    
    # Calculate statistics
    baseline_costs = [r['cost'] for r in baseline_results]
    christofides_costs = [r['cost'] for r in christofides_results]
    
    baseline_mean = np.mean(baseline_costs)
    baseline_std = np.std(baseline_costs)
    christofides_mean = np.mean(christofides_costs)
    christofides_std = np.std(christofides_costs)
    
    improvement_pct = ((baseline_mean - christofides_mean) / baseline_mean) * 100
    
    print("\n" + "=" * 70)
    print("STATISTICAL RESULTS")
    print("=" * 70)
    print(f"NN+2opt Baseline: {baseline_mean:.3f} ± {baseline_std:.3f}")
    print(f"Christofides:      {christofides_mean:.3f} ± {christofides_std:.3f}")
    print(f"Improvement:       {improvement_pct:+.2f}%")
    
    # Simplified statistical test (would need scipy for proper t-test)
    if num_seeds >= 2:
        # Check if Christofides is consistently better
        better_count = sum(1 for b, c in zip(baseline_costs, christofides_costs) if c < b)
        worse_count = sum(1 for b, c in zip(baseline_costs, christofides_costs) if c > b)
        
        print(f"\nConsistency check: Christofides better in {better_count}/{num_seeds} seeds")
        print(f"                   Christofides worse in {worse_count}/{num_seeds} seeds")
        
        if better_count > worse_count:
            print("✓ Christofides shows consistent improvement")
        else:
            print("✗ Christofides does not show consistent improvement")
    
    # Save results
    results = {
        'metadata': {
            'test': 'quick_methodology_test',
            'problem_size': problem_size,
            'num_seeds': num_seeds,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'methodology': 'Corrected: NN+2opt baseline, multi-seed'
        },
        'baseline_results': baseline_results,
        'christofides_results': christofides_results,
        'statistics': {
            'baseline_mean': float(baseline_mean),
            'baseline_std': float(baseline_std),
            'christofides_mean': float(christofides_mean),
            'christofides_std': float(christofides_std),
            'improvement_pct': float(improvement_pct)
        }
    }
    
    # Save to file
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"quick_methodology_test_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {filename}")
    
    # Generate report
    report = f"""
METHODOLOGY TEST REPORT
=======================
Date: {time.strftime("%Y-%m-%d %H:%M:%S")}
Test: Quick methodology verification
Problem size: {problem_size}
Seeds: {num_seeds} (should be ≥10 for publication)

KEY FINDINGS:
1. Christofides vs NN+2opt: {improvement_pct:+.2f}% improvement
2. Consistency: Christofides better in {better_count}/{num_seeds} seeds
3. Statistical spread: Baseline ±{baseline_std:.3f}, Christofides ±{christofides_std:.3f}

METHODOLOGICAL REQUIREMENTS (per owner's verification):
✓ Multiple seeds tested ({num_seeds}, should be ≥10)
✓ Comparison against NN+2opt baseline (not plain NN)
✓ Mean and standard deviation reported
✗ Statistical significance test (requires scipy for p-value)
✗ ≥10 seeds (only {num_seeds} in quick test)
✗ TSPLIB instances evaluation
✗ Strong solver comparison (LKH/OR-Tools)

NEXT STEPS FOR FULL METHODOLOGICAL CORRECTION:
1. Run with ≥10 seeds per problem size
2. Install scipy for proper statistical tests
3. Acquire real TSPLIB instances (eil51, kroA100, a280, att532)
4. Install LKH/OR-Tools for strong solver comparison
5. Test v8 and v19 algorithms (may require timeouts for slow runs)
6. Perform ablation studies for novel components

IMPORTANT: No algorithm should be declared "publication-ready" until ALL
methodological requirements are met with statistically significant results.
"""
    
    print(report)
    
    # Save report
    report_file = filename.replace('.json', '_report.txt')
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"Report saved to: {report_file}")
    print("=" * 70)
    
    return results

def main():
    """Main function."""
    try:
        run_methodology_test()
        return 0
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
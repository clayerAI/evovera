#!/usr/bin/env python3
"""
Validate Christofides vs NN+2opt baseline findings with actual implementations.
This script runs comprehensive multi-seed validation to confirm owner's finding
that Christofides performs worse than NN+2opt baseline.
"""

import sys
import os
sys.path.append('/workspace/evovera/solutions')

import numpy as np
import random
import time
import json
from datetime import datetime
from typing import List, Tuple, Dict, Any

# Import algorithms
from tsp_v1_nearest_neighbor import solve_tsp as nn2opt_solve
from tsp_v2_christofides_improved import solve_tsp as christofides_solve

# Import statistical tests
sys.path.append('/workspace/evovera')
from statistical_tests import statistical_summary, format_statistical_report

def generate_random_points(n: int = 100, seed: int = 42) -> List[Tuple[float, float]]:
    """Generate random points in unit square."""
    random.seed(seed)
    np.random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

def run_single_test(points: List[Tuple[float, float]], algorithm_name: str) -> Tuple[List[int], float]:
    """Run a single algorithm on given points and return tour and length."""
    # Convert points to numpy array for consistency
    points_array = np.array(points)
    
    if algorithm_name == "nn2opt":
        tour, length = nn2opt_solve(points_array)
    elif algorithm_name == "christofides":
        tour, length = christofides_solve(points_array)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm_name}")
    
    return tour, length

def run_multi_seed_validation(n: int = 100, seeds: int = 10) -> Dict[str, Any]:
    """Run validation across multiple seeds."""
    print(f"Running Christofides vs NN+2opt validation...")
    print(f"  Problem size: n={n}")
    print(f"  Number of seeds: {seeds}")
    print()
    
    baseline_results = []
    christofides_results = []
    execution_times = {"nn2opt": [], "christofides": []}
    
    for seed in range(1, seeds + 1):
        print(f"  Seed {seed}/{seeds}...", end=" ", flush=True)
        
        # Generate points
        points = generate_random_points(n, seed)
        
        # Run NN+2opt baseline
        start_time = time.time()
        _, nn_length = run_single_test(points, "nn2opt")
        nn_time = time.time() - start_time
        
        # Run Christofides
        start_time = time.time()
        _, cf_length = run_single_test(points, "christofides")
        cf_time = time.time() - start_time
        
        baseline_results.append(nn_length)
        christofides_results.append(cf_length)
        execution_times["nn2opt"].append(nn_time)
        execution_times["christofides"].append(cf_time)
        
        print(f"NN+2opt: {nn_length:.3f}, Christofides: {cf_length:.3f}, "
              f"Diff: {((nn_length - cf_length)/nn_length*100):+.2f}%")
    
    print()
    
    # Calculate statistics
    stats = statistical_summary(baseline_results, christofides_results, 
                               "Christofides vs NN+2opt Baseline")
    
    # Add timing information
    stats["timing"] = {
        "nn2opt_mean": np.mean(execution_times["nn2opt"]),
        "nn2opt_std": np.std(execution_times["nn2opt"]),
        "christofides_mean": np.mean(execution_times["christofides"]),
        "christofides_std": np.std(execution_times["christofides"])
    }
    
    return stats

def main():
    """Main validation routine."""
    print("=" * 80)
    print("CHRISTOFIDES vs NN+2OPT BASELINE VALIDATION")
    print("=" * 80)
    print()
    print("Validating owner's finding that Christofides performs worse than NN+2opt baseline.")
    print("This addresses the critical methodological issue in the original 16.07% claim.")
    print()
    
    # Test with multiple problem sizes
    problem_sizes = [50, 100, 200]
    seeds_per_size = 10
    
    all_results = {}
    
    for n in problem_sizes:
        print(f"\n{'='*60}")
        print(f"VALIDATION FOR n={n}")
        print(f"{'='*60}")
        
        stats = run_multi_seed_validation(n=n, seeds=seeds_per_size)
        
        # Print report
        report = format_statistical_report(stats)
        print(report)
        
        # Save results
        all_results[f"n={n}"] = stats
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/workspace/evovera/christofides_validation_n{n}_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(stats, f, indent=2)
        print(f"Results saved to {filename}")
    
    # Generate overall summary
    print("\n" + "="*80)
    print("OVERALL VALIDATION SUMMARY")
    print("="*80)
    
    for n, stats in all_results.items():
        improvement = stats["improvement_percent"]
        p_value = stats["t_test"]["p_value"]
        
        if p_value < 0.05 and improvement > 0:
            conclusion = "✅ Statistically significant improvement"
        elif p_value < 0.05 and improvement < 0:
            conclusion = "⚠️ Statistically significant degradation"
        elif improvement > 1.0:
            conclusion = "📊 Practically meaningful improvement (>1%)"
        elif improvement < -1.0:
            conclusion = "📊 Practically meaningful degradation (>1%)"
        else:
            conclusion = "📈 Minor difference"
        
        print(f"{n}: {improvement:+.2f}% improvement, p={p_value:.3f} - {conclusion}")
    
    print("\n" + "="*80)
    print("VALIDATION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
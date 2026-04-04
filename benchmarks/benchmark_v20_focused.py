#!/usr/bin/env python3
"""
Focused benchmark for v20 Christofides Structural-ILS Hybrid.
Tests n=50, n=100 with 3 seeds each, with time limits.
"""

import numpy as np
import time
import json
import sys
import os
from typing import List, Tuple, Dict

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import algorithms
from solutions.tsp_v8_christofides_ils_hybrid_fixed import solve_tsp as v8_solve_tsp
from solutions.tsp_v19_christofides_hybrid_structural import solve_tsp as v19_solve_tsp
from solutions.tsp_v20_christofides_structural_ils import solve_tsp as v20_solve_tsp
from solutions.tsp_v1_nearest_neighbor import solve_tsp as nn_solve_tsp

def two_opt_improvement(tour: List[int], dist_matrix: np.ndarray) -> Tuple[List[int], float]:
    """Simple 2-opt local search."""
    n = len(tour)
    best_tour = tour[:]
    
    # Calculate initial length
    best_length = 0.0
    for i in range(n):
        j = (i + 1) % n
        best_length += dist_matrix[best_tour[i]][best_tour[j]]
    
    improved = True
    while improved:
        improved = False
        for i in range(n - 1):
            for k in range(i + 1, n):
                # Calculate delta
                j = (i + 1) % n
                l = (k + 1) % n
                
                old_cost = (dist_matrix[best_tour[i]][best_tour[j]] +
                           dist_matrix[best_tour[k]][best_tour[l]])
                new_cost = (dist_matrix[best_tour[i]][best_tour[k]] +
                           dist_matrix[best_tour[j]][best_tour[l]])
                
                if new_cost < old_cost - 1e-9:
                    # Perform swap
                    best_tour[i+1:k+1] = best_tour[i+1:k+1][::-1]
                    best_length += (new_cost - old_cost)
                    improved = True
    
    return best_tour, best_length

def generate_points(n: int, seed: int) -> np.ndarray:
    """Generate random points in [0, 1]^2."""
    np.random.seed(seed)
    return np.random.rand(n, 2)

def distance_matrix(points: np.ndarray) -> np.ndarray:
    """Compute Euclidean distance matrix."""
    n = len(points)
    dist = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            d = np.linalg.norm(points[i] - points[j])
            dist[i][j] = d
            dist[j][i] = d
    return dist

def run_algorithm(algorithm_name: str, solve_func, points: np.ndarray, 
                  dist_matrix: np.ndarray, time_limit: float = 30.0) -> Dict:
    """Run a single algorithm with time limit."""
    start_time = time.time()
    
    try:
        tour, length = solve_func(points)
        
        # Ensure tour is valid
        if len(tour) == len(points) + 1:  # Closed tour
            tour = tour[:-1]
        
        # Verify tour length
        computed_length = 0.0
        n = len(tour)
        for i in range(n):
            j = (i + 1) % n
            computed_length += dist_matrix[tour[i]][tour[j]]
        
        if abs(computed_length - length) > 1e-6:
            print(f"  Warning: {algorithm_name} length mismatch: {length:.6f} vs computed {computed_length:.6f}")
            length = computed_length
        
        elapsed = time.time() - start_time
        
        if elapsed > time_limit:
            return {
                "algorithm": algorithm_name,
                "length": length,
                "time": elapsed,
                "status": "timeout",
                "tour": tour
            }
        
        return {
            "algorithm": algorithm_name,
            "length": length,
            "time": elapsed,
            "status": "success",
            "tour": tour
        }
        
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "algorithm": algorithm_name,
            "length": float('inf'),
            "time": elapsed,
            "status": f"error: {str(e)}",
            "tour": []
        }

def benchmark_instance(n: int, seed: int) -> Dict:
    """Benchmark all algorithms on a single instance."""
    print(f"\n=== Benchmarking n={n}, seed={seed} ===")
    
    # Generate instance
    points = generate_points(n, seed)
    dist_matrix = distance_matrix(points)
    
    # Run baseline (NN + 2-opt)
    print("  Running NN+2opt baseline...")
    nn_tour, nn_length = nn_solve_tsp(points)
    nn_tour_opt, nn_length_opt = two_opt_improvement(nn_tour, dist_matrix)
    
    baseline_result = {
        "algorithm": "NN+2opt",
        "length": nn_length_opt,
        "time": 0.0,  # Not timing baseline separately
        "status": "success",
        "tour": nn_tour_opt
    }
    
    # Run v8
    print("  Running v8 Christofides-ILS...")
    v8_result = run_algorithm("v8", v8_solve_tsp, points, dist_matrix, time_limit=60.0)
    
    # Run v19
    print("  Running v19 Structural Hybrid...")
    v19_result = run_algorithm("v19", v19_solve_tsp, points, dist_matrix, time_limit=60.0)
    
    # Run v20
    print("  Running v20 Structural-ILS Hybrid...")
    v20_result = run_algorithm("v20", v20_solve_tsp, points, dist_matrix, time_limit=120.0)
    
    # Calculate improvements
    baseline_length = baseline_result["length"]
    
    results = {
        "n": n,
        "seed": seed,
        "baseline": baseline_result,
        "v8": v8_result,
        "v19": v19_result,
        "v20": v20_result,
        "improvements": {
            "v8_vs_baseline": (baseline_length - v8_result["length"]) / baseline_length * 100 if v8_result["status"] == "success" else None,
            "v19_vs_baseline": (baseline_length - v19_result["length"]) / baseline_length * 100 if v19_result["status"] == "success" else None,
            "v20_vs_baseline": (baseline_length - v20_result["length"]) / baseline_length * 100 if v20_result["status"] == "success" else None,
            "v20_vs_v8": (v8_result["length"] - v20_result["length"]) / v8_result["length"] * 100 if v8_result["status"] == "success" and v20_result["status"] == "success" else None,
            "v20_vs_v19": (v19_result["length"] - v20_result["length"]) / v19_result["length"] * 100 if v19_result["status"] == "success" and v20_result["status"] == "success" else None,
        }
    }
    
    # Print summary
    print(f"  Results:")
    print(f"    Baseline (NN+2opt): {baseline_length:.6f}")
    if v8_result["status"] == "success":
        print(f"    v8: {v8_result['length']:.6f} ({results['improvements']['v8_vs_baseline']:.2f}% vs baseline)")
    if v19_result["status"] == "success":
        print(f"    v19: {v19_result['length']:.6f} ({results['improvements']['v19_vs_baseline']:.2f}% vs baseline)")
    if v20_result["status"] == "success":
        print(f"    v20: {v20_result['length']:.6f} ({results['improvements']['v20_vs_baseline']:.2f}% vs baseline)")
        if v8_result["status"] == "success":
            print(f"      v20 vs v8: {results['improvements']['v20_vs_v8']:.2f}%")
        if v19_result["status"] == "success":
            print(f"      v20 vs v19: {results['improvements']['v20_vs_v19']:.2f}%")
    
    return results

def main():
    """Main benchmark function."""
    print("=== V20 Christofides Structural-ILS Hybrid Benchmark ===")
    
    # Test configurations
    configs = [
        (50, 42),
        (50, 123),
        (50, 456),
        (100, 42),
        (100, 123),
        (100, 456),
    ]
    
    all_results = []
    
    for n, seed in configs:
        try:
            result = benchmark_instance(n, seed)
            all_results.append(result)
            
            # Save intermediate results
            with open("v20_benchmark_results.json", "w") as f:
                json.dump(all_results, f, indent=2)
                
        except Exception as e:
            print(f"Error benchmarking n={n}, seed={seed}: {e}")
            continue
    
    # Calculate summary statistics
    print("\n=== SUMMARY STATISTICS ===")
    
    # Filter successful runs
    successful_results = [r for r in all_results 
                         if r["v20"]["status"] == "success" 
                         and r["v8"]["status"] == "success"
                         and r["v19"]["status"] == "success"]
    
    if not successful_results:
        print("No successful runs to analyze.")
        return
    
    # Group by n
    by_n = {}
    for result in successful_results:
        n = result["n"]
        if n not in by_n:
            by_n[n] = []
        by_n[n].append(result)
    
    for n, results in by_n.items():
        print(f"\n  n={n} ({len(results)} instances):")
        
        # Calculate averages
        v8_improvements = [r["improvements"]["v8_vs_baseline"] for r in results]
        v19_improvements = [r["improvements"]["v19_vs_baseline"] for r in results]
        v20_improvements = [r["improvements"]["v20_vs_baseline"] for r in results]
        v20_vs_v8 = [r["improvements"]["v20_vs_v8"] for r in results]
        v20_vs_v19 = [r["improvements"]["v20_vs_v19"] for r in results]
        
        print(f"    v8 vs baseline: {np.mean(v8_improvements):.2f}% avg improvement")
        print(f"    v19 vs baseline: {np.mean(v19_improvements):.2f}% avg improvement")
        print(f"    v20 vs baseline: {np.mean(v20_improvements):.2f}% avg improvement")
        print(f"    v20 vs v8: {np.mean(v20_vs_v8):.2f}% avg improvement")
        print(f"    v20 vs v19: {np.mean(v20_vs_v19):.2f}% avg improvement")
        
        # Count wins
        v20_wins_v8 = sum(1 for imp in v20_vs_v8 if imp > 0.1)
        v20_wins_v19 = sum(1 for imp in v20_vs_v19 if imp > 0.1)
        
        print(f"    v20 beats v8 in {v20_wins_v8}/{len(results)} instances (>0.1% threshold)")
        print(f"    v20 beats v19 in {v20_wins_v19}/{len(results)} instances (>0.1% threshold)")
    
    print(f"\n=== Results saved to v20_benchmark_results.json ===")

if __name__ == "__main__":
    main()
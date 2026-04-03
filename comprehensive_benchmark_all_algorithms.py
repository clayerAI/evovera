#!/usr/bin/env python3
"""Comprehensive benchmark of all 15 TSP hybrid algorithms against NN+2opt baseline."""
import sys
sys.path.append('.')

import numpy as np
import time
import math
import json
from typing import List, Tuple, Dict, Any
import os

# Import all algorithms with standardized solve_tsp interfaces
from solutions.tsp_v1_nearest_neighbor import solve_tsp as solve_tsp_nn_2opt
from solutions.tsp_v2_christofides import solve_tsp as solve_tsp_christofides
from solutions.tsp_v3_iterative_local_search import solve_tsp as solve_tsp_ils
from solutions.tsp_v4_nn_ils_hybrid import solve_tsp as solve_tsp_nn_ils_hybrid
from solutions.tsp_v5_christofides_ils_hybrid import solve_tsp as solve_tsp_christofides_ils_hybrid
from solutions.tsp_v6_multi_start_adaptive_2opt import solve_tsp as solve_tsp_multi_start_adaptive_2opt
from solutions.tsp_v7_christofides_tabu_hybrid import solve_tsp as solve_tsp_christofides_tabu_hybrid
from solutions.tsp_v8_christofides_ils_hybrid_fixed import solve_tsp as solve_tsp_christofides_ils_fixed
from solutions.tsp_v9_nn_ga_christofides_crossover import solve_tsp as solve_tsp_nn_ga_christofides
from solutions.tsp_v10_christofides_mst_ils_memory import solve_tsp as solve_tsp_christofides_mst_ils_memory
from solutions.tsp_v11_nn_ils_adaptive_memory import solve_tsp as solve_tsp_nn_ils_adaptive_memory
from solutions.tsp_v12_nn_fast_ils import solve_tsp as solve_tsp_nn_fast_ils
from solutions.tsp_v13_nn_efficient_ils import solve_tsp as solve_tsp_nn_efficient_ils
from solutions.tsp_v14_christofides_adaptive_matching import solve_tsp as solve_tsp_christofides_adaptive_matching
from solutions.tsp_v15_algorithmic_ecology import solve_tsp as solve_tsp_algorithmic_ecology

# All algorithms now have standardized solve_tsp interfaces
v10_available = True
v11_available = True
v12_available = True
v13_available = True
v14_available = True
v15_available = True

def generate_random_instance(n: int, seed: int = 42):
    """Generate random Euclidean TSP instance."""
    np.random.seed(seed)
    # Return as numpy array for Christofides
    return np.random.rand(n, 2) * 100

def calculate_tour_length(points: np.ndarray, tour: List[int]) -> float:
    """Calculate total length of a tour."""
    total = 0.0
    for i in range(len(tour) - 1):
        dx = points[tour[i]][0] - points[tour[i+1]][0]
        dy = points[tour[i]][1] - points[tour[i+1]][1]
        total += math.sqrt(dx*dx + dy*dy)
    # Close the tour
    dx = points[tour[-1]][0] - points[tour[0]][0]
    dy = points[tour[-1]][1] - points[tour[0]][1]
    total += math.sqrt(dx*dx + dy*dy)
    return total

def run_algorithm(algorithm_name: str, points: np.ndarray, points_list: List[Tuple[float, float]]) -> Tuple[List[int], float]:
    """Run a specific algorithm and return tour and runtime."""
    start_time = time.time()
    
    try:
        if algorithm_name == "NN+2opt":
            result = solve_tsp_nn_2opt(points_list)
        elif algorithm_name == "Christofides":
            result = solve_tsp_christofides(points)
        elif algorithm_name == "ILS":
            result = solve_tsp_ils(points_list)
        elif algorithm_name == "NN-ILS Hybrid":
            result = solve_tsp_nn_ils_hybrid(points_list)
        elif algorithm_name == "Christofides-ILS Hybrid":
            result = solve_tsp_christofides_ils_hybrid(points)
        elif algorithm_name == "Multi-start Adaptive 2-opt":
            result = solve_tsp_multi_start_adaptive_2opt(points_list)
        elif algorithm_name == "Christofides-Tabu Hybrid":
            result = solve_tsp_christofides_tabu_hybrid(points_list)
        elif algorithm_name == "Christofides-ILS Fixed":
            result = solve_tsp_christofides_ils_fixed(points)
        elif algorithm_name == "NN-GA Christofides Crossover":
            result = solve_tsp_nn_ga_christofides(points_list)
        elif algorithm_name == "Christofides MST ILS Memory" and v10_available:
            result = solve_tsp_christofides_mst_ils_memory(points)
        elif algorithm_name == "NN ILS Adaptive Memory" and v11_available:
            result = solve_tsp_nn_ils_adaptive_memory(points_list)
        elif algorithm_name == "NN Fast ILS" and v12_available:
            result = solve_tsp_nn_fast_ils(points_list)
        elif algorithm_name == "NN Efficient ILS" and v13_available:
            result = solve_tsp_nn_efficient_ils(points_list)
        elif algorithm_name == "Christofides Adaptive Matching" and v14_available:
            result = solve_tsp_christofides_adaptive_matching(points)
        elif algorithm_name == "Algorithmic Ecology" and v15_available:
            result = solve_tsp_algorithmic_ecology(points_list)
        else:
            # Algorithm not available
            print(f"  Algorithm {algorithm_name} not available or import failed")
            return [], float('inf')
    except Exception as e:
        print(f"  ERROR running {algorithm_name}: {e}")
        return [], float('inf')
    
    # Handle different return types
    if isinstance(result, tuple):
        # Most algorithms return (tour, length)
        tour = result[0]
    else:
        # Some algorithms return just the tour
        tour = result
    
    runtime = time.time() - start_time
    return tour, runtime

def run_comprehensive_benchmark(n: int = 500, trials: int = 5):
    """Run comprehensive benchmark of all algorithms."""
    algorithms = [
        "NN+2opt",  # Baseline
        "Christofides",
        "ILS",
        "NN-ILS Hybrid",
        "Christofides-ILS Hybrid",
        "Multi-start Adaptive 2-opt",
        "Christofides-Tabu Hybrid",
        "Christofides-ILS Fixed",
        "NN-GA Christofides Crossover",
        "Christofides MST ILS Memory",
        "NN ILS Adaptive Memory",
        "NN Fast ILS",
        "NN Efficient ILS",
        "Christofides Adaptive Matching",
        "Algorithmic Ecology"
    ]
    
    results = {}
    
    for trial in range(trials):
        print(f"\n{'='*80}")
        print(f"Trial {trial+1}/{trials} (n={n}, seed={1000 + trial})")
        print(f"{'='*80}")
        
        # Generate instance
        points = generate_random_instance(n, seed=1000 + trial)
        points_list = [(float(p[0]), float(p[1])) for p in points]
        
        trial_results = {}
        baseline_length = None
        
        for algo in algorithms:
            print(f"\n  Running {algo}...")
            tour, runtime = run_algorithm(algo, points, points_list)
            
            if len(tour) == 0:
                print(f"    FAILED - skipping")
                trial_results[algo] = {"length": float('inf'), "runtime": runtime, "improvement": 0.0}
                continue
            
            length = calculate_tour_length(points, tour)
            
            # Store baseline length
            if algo == "NN+2opt":
                baseline_length = length
            
            # Calculate improvement over baseline
            improvement = 0.0
            if baseline_length is not None and baseline_length > 0:
                improvement = ((baseline_length - length) / baseline_length) * 100
            
            trial_results[algo] = {
                "length": length,
                "runtime": runtime,
                "improvement": improvement
            }
            
            print(f"    Length: {length:.4f}, Runtime: {runtime:.3f}s, Improvement: {improvement:.3f}%")
        
        results[f"trial_{trial+1}"] = trial_results
    
    # Calculate averages
    print(f"\n{'='*80}")
    print("SUMMARY RESULTS (Averages across all trials)")
    print(f"{'='*80}")
    
    summary = {}
    for algo in algorithms:
        lengths = []
        runtimes = []
        improvements = []
        
        for trial in range(trials):
            trial_key = f"trial_{trial+1}"
            if algo in results[trial_key]:
                data = results[trial_key][algo]
                if data["length"] != float('inf'):
                    lengths.append(data["length"])
                    runtimes.append(data["runtime"])
                    improvements.append(data["improvement"])
        
        if lengths:
            summary[algo] = {
                "avg_length": np.mean(lengths),
                "std_length": np.std(lengths) if len(lengths) > 1 else 0.0,
                "avg_runtime": np.mean(runtimes),
                "std_runtime": np.std(runtimes) if len(runtimes) > 1 else 0.0,
                "avg_improvement": np.mean(improvements),
                "std_improvement": np.std(improvements) if len(improvements) > 1 else 0.0,
                "success_rate": len(lengths) / trials
            }
            
            print(f"\n{algo}:")
            print(f"  Avg Length: {summary[algo]['avg_length']:.4f} ± {summary[algo]['std_length']:.4f}")
            print(f"  Avg Runtime: {summary[algo]['avg_runtime']:.3f}s ± {summary[algo]['std_runtime']:.3f}s")
            print(f"  Avg Improvement: {summary[algo]['avg_improvement']:.3f}% ± {summary[algo]['std_improvement']:.3f}%")
            print(f"  Success Rate: {summary[algo]['success_rate']:.1%}")
            
            # Check if beats 0.1% threshold
            if algo != "NN+2opt" and summary[algo]['avg_improvement'] > 0.1:
                print(f"  ✅ BEATS 0.1% THRESHOLD (Publication-worthy)")
            elif algo != "NN+2opt":
                print(f"  ❌ Below 0.1% threshold")
    
    # Save results to JSON
    output_file = f"comprehensive_benchmark_n{n}_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "parameters": {"n": n, "trials": trials},
            "results": results,
            "summary": summary
        }, f, indent=2)
    
    print(f"\nResults saved to {output_file}")
    
    # Return summary for easy analysis
    return summary

if __name__ == "__main__":
    print("COMPREHENSIVE BENCHMARK OF ALL 15 TSP HYBRID ALGORITHMS")
    print("Baseline: NN+2opt (target: 17.69 avg tour length for n=500)")
    print("Success threshold: 0.1% improvement over baseline")
    print("="*80)
    
    # Run benchmark
    summary = run_comprehensive_benchmark(n=500, trials=5)
    
    # Print top performers
    print(f"\n{'='*80}")
    print("TOP PERFORMERS (by improvement over baseline)")
    print(f"{'='*80}")
    
    performers = []
    for algo, data in summary.items():
        if algo != "NN+2opt" and data['success_rate'] > 0:
            performers.append((algo, data['avg_improvement'], data['avg_runtime']))
    
    performers.sort(key=lambda x: x[1], reverse=True)
    
    for i, (algo, improvement, runtime) in enumerate(performers[:10]):
        status = "✅" if improvement > 0.1 else "❌"
        print(f"{i+1:2d}. {status} {algo:30s} {improvement:6.3f}% improvement, {runtime:6.3f}s runtime")
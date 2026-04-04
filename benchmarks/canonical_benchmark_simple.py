#!/usr/bin/env python3
"""
Simplified canonical benchmark script for TSP algorithms (Phase 2 correction).
Focuses on random instances with consistent scale [0, 1] and fixed seeds.
"""

import sys
import os
sys.path.append('.')

import numpy as np
import time
import math
import json
from typing import List, Tuple, Dict, Any

# Import key algorithms (focus on v8, v19, v16, v18 as per audit)
try:
    from solutions.tsp_v1_nearest_neighbor import solve_tsp as solve_tsp_nn_2opt
    from solutions.tsp_v2_christofides import solve_tsp as solve_tsp_christofides
    from solutions.tsp_v8_christofides_ils_hybrid_fixed import solve_tsp as solve_tsp_christofides_ils_fixed
    from solutions.tsp_v16_christofides_path_centrality import solve_tsp as solve_tsp_christofides_path_centrality
    from solutions.tsp_v18_christofides_community_detection import solve_tsp as solve_tsp_christofides_community_detection
    from solutions.tsp_v19_christofides_hybrid_structural import solve_tsp as solve_tsp_christofides_hybrid_structural
    ALGORITHMS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some algorithms not available: {e}")
    ALGORITHMS_AVAILABLE = False
    sys.exit(1)

# Random instances for comparison (consistent scale [0, 1])
RANDOM_INSTANCES = [
    ("random_50", 50),
    ("random_100", 100),
    ("random_200", 200),
    ("random_500", 500),
]

def generate_random_instance(n: int, seed: int = 42):
    """Generate random Euclidean TSP instance in [0, 1] scale."""
    np.random.seed(seed)
    return np.random.rand(n, 2)

def calculate_tour_length(points: np.ndarray, tour: List[int]) -> float:
    """Calculate total length of a tour."""
    total = 0.0
    for i in range(len(tour)):
        p1 = points[tour[i]]
        p2 = points[tour[(i + 1) % len(tour)]]
        total += math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    return total

def benchmark_algorithm(name: str, algorithm_func, points: np.ndarray, seed: int = 42):
    """Benchmark a single algorithm on given points."""
    try:
        start_time = time.time()
        tour, length = algorithm_func(points)
        elapsed = time.time() - start_time
        
        # Verify tour length matches calculated length
        calculated_length = calculate_tour_length(points, tour)
        if abs(length - calculated_length) > 1e-6:
            print(f"Warning: {name} reported length {length:.3f} but calculated {calculated_length:.3f}")
            length = calculated_length
        
        return {
            "tour_length": float(length),
            "time_seconds": float(elapsed),
            "success": True
        }
    except Exception as e:
        print(f"Error running {name}: {e}")
        return {
            "tour_length": None,
            "time_seconds": None,
            "success": False,
            "error": str(e)
        }

def benchmark_instance(instance_name: str, points: np.ndarray, optimal_length: float = None, seed: int = 42):
    """Benchmark all algorithms on a single instance."""
    print(f"\nBenchmarking {instance_name} (n={len(points)})...")
    
    results = {
        "instance": instance_name,
        "n": len(points),
        "optimal_length": optimal_length,
        "algorithms": {}
    }
    
    # Always run NN+2opt first as baseline
    nn_result = benchmark_algorithm("nn_2opt", solve_tsp_nn_2opt, points, seed)
    results["algorithms"]["nn_2opt"] = nn_result
    
    if not nn_result["success"]:
        print(f"  Baseline NN+2opt failed, skipping other algorithms")
        return results
    
    baseline_length = nn_result["tour_length"]
    
    # Benchmark other algorithms
    algorithms = [
        ("christofides", solve_tsp_christofides),
        ("v8", solve_tsp_christofides_ils_fixed),
        ("v16", solve_tsp_christofides_path_centrality),
        ("v18", solve_tsp_christofides_community_detection),
        ("v19", solve_tsp_christofides_hybrid_structural),
    ]
    
    for algo_name, algo_func in algorithms:
        result = benchmark_algorithm(algo_name, algo_func, points, seed)
        
        # Calculate gap to baseline
        if result["success"] and baseline_length is not None:
            gap_to_baseline_pct = ((result["tour_length"] - baseline_length) / baseline_length) * 100
            result["gap_to_baseline_pct"] = float(gap_to_baseline_pct)
        
        # Calculate gap to optimal if known
        if result["success"] and optimal_length is not None:
            gap_to_optimal_pct = ((result["tour_length"] - optimal_length) / optimal_length) * 100
            result["gap_to_optimal_pct"] = float(gap_to_optimal_pct)
        
        results["algorithms"][algo_name] = result
        
        if result["success"]:
            gap_str = ""
            if "gap_to_baseline_pct" in result:
                gap_str = f", gap to NN+2opt: {result['gap_to_baseline_pct']:+.2f}%"
            print(f"  {algo_name:<15} length: {result['tour_length']:.3f}, time: {result['time_seconds']:.3f}s{gap_str}")
        else:
            print(f"  {algo_name:<15} FAILED: {result.get('error', 'Unknown error')}")
    
    return results

def main():
    """Main benchmark execution."""
    if not ALGORITHMS_AVAILABLE:
        print("ERROR: Required algorithms not available")
        sys.exit(1)
    
    print("="*80)
    print("CANONICAL BENCHMARK - Phase 2 Correction")
    print("="*80)
    print("Requirements met:")
    print("1. Fixed seeds for reproducibility (seed=42)")
    print("2. Consistent coordinate scale [0, 1] for all algorithms")
    print("3. Always compares against NN+2opt as minimum baseline")
    print("4. Reports absolute tour lengths, gap vs baseline, and wall-clock time")
    print("="*80)
    
    all_results = {
        "metadata": {
            "benchmark": "canonical_benchmark_simple",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "coordinate_scale": "[0, 1]",
            "baseline": "NN+2opt",
            "seed": 42
        },
        "instances": []
    }
    
    # Test random instances
    print("\n" + "="*80)
    print("RANDOM INSTANCES (scale [0, 1])")
    print("="*80)
    
    for instance_name, n in RANDOM_INSTANCES:
        points = generate_random_instance(n, seed=42)
        results = benchmark_instance(instance_name, points, None, seed=42)
        all_results["instances"].append(results)
    
    # Save results
    output_file = "canonical_benchmark_simple_results.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"Benchmark complete. Results saved to {output_file}")
    print(f"{'='*80}")
    
    # Print summary table
    print("\nSUMMARY TABLE (v19 vs NN+2opt)")
    print("-"*100)
    print(f"{'Instance':<20} {'n':<6} {'NN+2opt':<12} {'v19':<12} {'Gap to NN+2opt':<15}")
    print("-"*100)
    
    for instance_data in all_results["instances"]:
        instance_name = instance_data["instance"]
        n = instance_data["n"]
        
        nn_result = instance_data["algorithms"].get("nn_2opt", {})
        v19_result = instance_data["algorithms"].get("v19", {})
        
        nn_length = nn_result.get("tour_length")
        v19_length = v19_result.get("tour_length")
        gap_to_baseline = v19_result.get("gap_to_baseline_pct")
        
        if nn_length and v19_length:
            print(f"{instance_name:<20} {n:<6} {nn_length:<12.3f} {v19_length:<12.3f} ", end="")
            if gap_to_baseline is not None:
                print(f"{gap_to_baseline:<+15.2f}%")
            else:
                print(f"{'N/A':<15}")
        else:
            print(f"{instance_name:<20} {n:<6} {'ERROR':<12} {'ERROR':<12} {'ERROR':<15}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Canonical benchmark script for TSP algorithms (Phase 2 correction) - Random instances only.
Meets audit requirements:
1. Fixed seeds for reproducibility
2. Consistent coordinate scale [0, 1] for all algorithms
3. Always compares against NN+2opt as minimum baseline
4. Reports absolute tour lengths, gap vs baseline, and wall-clock time
5. Reports gap-to-optimal (not available for random instances)
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

# Random instances for comparison (consistent scale [0, 1])
# Start with smaller instances for testing
RANDOM_INSTANCES = [
    ("random_20", 20),
    ("random_50", 50),
    # ("random_100", 100),  # Skip for initial testing
    # ("random_200", 200),  # Skip for initial testing
    # ("random_500", 500),  # Skip for initial testing
]

def generate_random_instance(n: int, seed: int = 42):
    """Generate random Euclidean TSP instance in [0, 1] scale."""
    np.random.seed(seed)
    return np.random.rand(n, 2)

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

def run_algorithm(algorithm_name: str, solve_func, points: np.ndarray, seed: int = 42):
    """Run a single algorithm and measure performance."""
    np.random.seed(seed)
    start_time = time.time()
    
    try:
        # Convert points to list of tuples for algorithms expecting that format
        points_list = [(float(p[0]), float(p[1])) for p in points]
        
        # Special handling for v8 which expects numpy arrays
        if algorithm_name == "v8":
            result = solve_func(points)
        else:
            result = solve_func(points_list)
        
        # Handle different return types
        if isinstance(result, tuple):
            # Most algorithms return (tour, length)
            tour = result[0]
            returned_length = result[1] if len(result) > 1 else None
        else:
            # Some algorithms return just the tour
            tour = result
            returned_length = None
        
        # Ensure tour is a list of integers
        if isinstance(tour, np.ndarray):
            tour = tour.tolist()
        
        # Convert numpy ints to Python ints
        tour = [int(x) for x in tour]
        
        length = calculate_tour_length(points, tour)
        elapsed = time.time() - start_time
        
        # Verify returned length if available
        if returned_length and abs(returned_length - length) > 0.001:
            print(f"    Warning: length mismatch: returned {returned_length:.3f}, calculated {length:.3f}")
        
        return {
            "success": True,
            "tour_length": length,
            "runtime": elapsed,
            "tour": tour[:10] if len(tour) > 10 else tour  # Store first 10 for verification
        }
    
    except Exception as e:
        print(f"  Error running {algorithm_name}: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "runtime": time.time() - start_time
        }

def benchmark_instance(instance_name: str, points: np.ndarray, seed: int = 42):
    """Benchmark all algorithms on a single instance."""
    print(f"\n{'='*60}")
    print(f"Benchmarking: {instance_name} (n={len(points)})")
    print(f"{'='*60}")
    
    results = {
        "instance": instance_name,
        "n": len(points),
        "seed": seed,
        "algorithms": {}
    }
    
    # Define algorithms to test
    algorithms = [
        ("nn_2opt", solve_tsp_nn_2opt, "NN+2opt (baseline)"),
        ("christofides", solve_tsp_christofides, "Christofides"),
        ("v8", solve_tsp_christofides_ils_fixed, "v8: Christofides-ILS Hybrid"),
        ("v16", solve_tsp_christofides_path_centrality, "v16: Path Centrality Matching"),
        ("v18", solve_tsp_christofides_community_detection, "v18: Community Detection"),
        ("v19", solve_tsp_christofides_hybrid_structural, "v19: Christofides Hybrid Structural"),
    ]
    
    baseline_result = None
    
    for alg_id, solve_func, alg_name in algorithms:
        print(f"\n  Running {alg_name}...")
        result = run_algorithm(alg_id, solve_func, points, seed)
        
        if result["success"]:
            length = result["tour_length"]
            runtime = result["runtime"]
            
            # Calculate gaps
            gap_to_baseline = None
            
            if alg_id == "nn_2opt":
                baseline_result = length
                print(f"    Length: {length:.3f}, Runtime: {runtime:.3f}s (BASELINE)")
            else:
                if baseline_result:
                    gap_to_baseline = ((baseline_result - length) / baseline_result) * 100
                    print(f"    Length: {length:.3f}, Runtime: {runtime:.3f}s")
                    print(f"    Gap to NN+2opt: {gap_to_baseline:+.2f}%")
        
        results["algorithms"][alg_id] = {
            "name": alg_name,
            "success": result["success"],
            "tour_length": result.get("tour_length"),
            "runtime": result.get("runtime"),
            "gap_to_baseline_pct": gap_to_baseline,
            "error": result.get("error")
        }
    
    return results

def main():
    """Main benchmark execution."""
    print("="*80)
    print("CANONICAL TSP BENCHMARK - RANDOM INSTANCES ONLY (Phase 2 Correction)")
    print("="*80)
    print("Requirements from audit:")
    print("1. Fixed seeds for reproducibility")
    print("2. Consistent coordinate scale [0, 1]")
    print("3. NN+2opt as minimum baseline")
    print("4. Gap-to-baseline reporting")
    print("="*80)
    
    if not ALGORITHMS_AVAILABLE:
        print("ERROR: Required algorithms not available. Check imports.")
        return
    
    all_results = {
        "metadata": {
            "benchmark_name": "canonical_benchmark_random_only_phase2",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "coordinate_scale": "[0, 1]",
            "baseline": "NN+2opt",
            "seed": 42,
            "note": "Random instances only. TSPLIB instances require internet access."
        },
        "instances": []
    }
    
    # Test random instances
    print("\n" + "="*80)
    print("RANDOM INSTANCES (scale [0, 1])")
    print("="*80)
    
    for instance_name, n in RANDOM_INSTANCES:
        points = generate_random_instance(n, seed=42)
        results = benchmark_instance(instance_name, points, seed=42)
        all_results["instances"].append(results)
    
    # Save results
    output_file = "canonical_benchmark_random_results.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"Benchmark complete. Results saved to {output_file}")
    print(f"{'='*80}")
    
    # Print summary table
    print("\nSUMMARY TABLE")
    print("-"*80)
    print(f"{'Instance':<15} {'n':<6} {'NN+2opt':<12} {'v19':<12} {'Gap to NN+2opt':<15} {'v8':<12} {'Gap to NN+2opt':<15}")
    print("-"*80)
    
    for instance_data in all_results["instances"]:
        instance_name = instance_data["instance"]
        n = instance_data["n"]
        
        nn_result = instance_data["algorithms"].get("nn_2opt", {})
        v19_result = instance_data["algorithms"].get("v19", {})
        v8_result = instance_data["algorithms"].get("v8", {})
        
        nn_length = nn_result.get("tour_length")
        v19_length = v19_result.get("tour_length")
        v8_length = v8_result.get("tour_length")
        v19_gap = v19_result.get("gap_to_baseline_pct")
        v8_gap = v8_result.get("gap_to_baseline_pct")
        
        if nn_length and v19_length and v8_length:
            print(f"{instance_name:<15} {n:<6} {nn_length:<12.3f} {v19_length:<12.3f} ", end="")
            if v19_gap is not None:
                print(f"{v19_gap:<+15.2f}%", end="")
            else:
                print(f"{'N/A':<15}", end="")
            
            print(f" {v8_length:<12.3f} ", end="")
            if v8_gap is not None:
                print(f"{v8_gap:<+15.2f}%")
            else:
                print(f"{'N/A':<15}")
        else:
            print(f"{instance_name:<15} {n:<6} {'ERROR':<12} {'ERROR':<12} {'ERROR':<15} {'ERROR':<12} {'ERROR':<15}")

if __name__ == "__main__":
    main()
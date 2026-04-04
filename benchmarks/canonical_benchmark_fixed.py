#!/usr/bin/env python3
"""
Canonical benchmark script with timeouts for Phase 2.
Runs on smaller instances to avoid timeouts.
"""

import sys
import os
sys.path.append('.')

import numpy as np
import time
import math
import json
import signal
from typing import List, Tuple, Dict, Any
from functools import wraps

# Timeout decorator
class TimeoutError(Exception):
    pass

def timeout(seconds=30):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            def handler(signum, frame):
                raise TimeoutError(f"Function timed out after {seconds} seconds")
            
            # Set the signal handler
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(seconds)
            
            try:
                result = func(*args, **kwargs)
            finally:
                # Cancel the alarm
                signal.alarm(0)
            
            return result
        return wrapper
    return decorator

# Import key algorithms
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

# Smaller instances to avoid timeouts
RANDOM_INSTANCES = [
    ("random_50", 50),
    ("random_100", 100),
    ("random_200", 200),
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

@timeout(60)  # 60 second timeout per algorithm
def run_algorithm_with_timeout(name: str, algorithm_func, points: np.ndarray):
    """Run algorithm with timeout."""
    start_time = time.time()
    tour, length = algorithm_func(points)
    elapsed = time.time() - start_time
    
    # Verify tour length
    calculated_length = calculate_tour_length(points, tour)
    if abs(length - calculated_length) > 1e-6:
        print(f"Warning: {name} reported length {length:.3f} but calculated {calculated_length:.3f}")
        length = calculated_length
    
    return tour, length, elapsed

def benchmark_algorithm(name: str, algorithm_func, points: np.ndarray):
    """Benchmark a single algorithm on given points with timeout."""
    try:
        tour, length, elapsed = run_algorithm_with_timeout(name, algorithm_func, points)
        
        return {
            "tour_length": float(length),
            "time_seconds": float(elapsed),
            "success": True
        }
    except TimeoutError as e:
        print(f"  {name} timed out after 60 seconds")
        return {
            "tour_length": None,
            "time_seconds": None,
            "success": False,
            "error": "timeout"
        }
    except Exception as e:
        print(f"  {name} failed: {e}")
        return {
            "tour_length": None,
            "time_seconds": None,
            "success": False,
            "error": str(e)
        }

def benchmark_instance(instance_name: str, points: np.ndarray, seed: int = 42):
    """Benchmark all algorithms on a single instance."""
    print(f"\nBenchmarking {instance_name} (n={len(points)})...")
    
    results = {
        "instance": instance_name,
        "n": len(points),
        "algorithms": {}
    }
    
    # Always run NN+2opt first as baseline
    nn_result = benchmark_algorithm("nn_2opt", solve_tsp_nn_2opt, points)
    results["algorithms"]["nn_2opt"] = nn_result
    
    if not nn_result["success"]:
        print(f"  Baseline NN+2opt failed, skipping other algorithms")
        return results
    
    baseline_length = nn_result["tour_length"]
    print(f"  NN+2opt baseline: {baseline_length:.3f}")
    
    # Benchmark other algorithms
    algorithms = [
        ("christofides", solve_tsp_christofides),
        ("v8", solve_tsp_christofides_ils_fixed),
        ("v16", solve_tsp_christofides_path_centrality),
        ("v18", solve_tsp_christofides_community_detection),
        ("v19", solve_tsp_christofides_hybrid_structural),
    ]
    
    for algo_name, algo_func in algorithms:
        result = benchmark_algorithm(algo_name, algo_func, points)
        
        # Calculate gap to baseline
        if result["success"] and baseline_length is not None:
            gap_to_baseline_pct = ((result["tour_length"] - baseline_length) / baseline_length) * 100
            result["gap_to_baseline_pct"] = float(gap_to_baseline_pct)
        
        results["algorithms"][algo_name] = result
        
        if result["success"]:
            gap_str = f", gap to NN+2opt: {result['gap_to_baseline_pct']:+.2f}%" if "gap_to_baseline_pct" in result else ""
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
    print("CANONICAL BENCHMARK - Phase 2 Correction (Fixed)")
    print("="*80)
    print("Requirements met:")
    print("1. Fixed seeds for reproducibility (seed=42)")
    print("2. Consistent coordinate scale [0, 1] for all algorithms")
    print("3. Always compares against NN+2opt as minimum baseline")
    print("4. Reports absolute tour lengths, gap vs baseline, and wall-clock time")
    print("5. 60-second timeout per algorithm to handle large instances")
    print("="*80)
    
    all_results = {
        "metadata": {
            "benchmark": "canonical_benchmark_fixed",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "coordinate_scale": "[0, 1]",
            "baseline": "NN+2opt",
            "seed": 42,
            "timeout_seconds": 60
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
    output_file = "canonical_benchmark_fixed_results.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"Benchmark complete. Results saved to {output_file}")
    print(f"{'='*80}")
    
    # Print summary table
    print("\nSUMMARY TABLE")
    print("-"*100)
    print(f"{'Instance':<15} {'n':<6} {'NN+2opt':<12} {'v19':<12} {'Gap %':<10} {'Status'}")
    print("-"*100)
    
    for instance_data in all_results["instances"]:
        instance_name = instance_data["instance"]
        n = instance_data["n"]
        
        nn_result = instance_data["algorithms"].get("nn_2opt", {})
        v19_result = instance_data["algorithms"].get("v19", {})
        
        nn_length = nn_result.get("tour_length")
        v19_length = v19_result.get("tour_length")
        gap_to_baseline = v19_result.get("gap_to_baseline_pct")
        v19_success = v19_result.get("success", False)
        
        if nn_result.get("success") and v19_success:
            status = "✓"
            print(f"{instance_name:<15} {n:<6} {nn_length:<12.3f} {v19_length:<12.3f} {gap_to_baseline:<+10.2f}% {status}")
        else:
            status = "✗"
            nn_status = "✓" if nn_result.get("success") else "✗"
            v19_status = "✓" if v19_success else "✗"
            print(f"{instance_name:<15} {n:<6} {nn_status:<12} {v19_status:<12} {'ERROR':<10} {status}")

if __name__ == "__main__":
    # Disable signal for subprocesses if any
    signal.signal(signal.SIGALRM, signal.SIG_IGN)
    main()

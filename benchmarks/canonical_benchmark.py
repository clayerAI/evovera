#!/usr/bin/env python3
"""
Canonical benchmark script for TSP algorithms (Phase 2 correction).
Meets audit requirements:
1. Fixed seeds for reproducibility
2. Consistent coordinate scale [0, 1] for all algorithms
3. Always compares against NN+2opt as minimum baseline
4. Reports absolute tour lengths, gap vs baseline, and wall-clock time
5. Runs on TSPLIB instances with known optimal solutions
6. Reports gap-to-optimal, not just gap-to-NN
"""

import sys
import os
sys.path.append('.')

import numpy as np
import time
import math
import json
from typing import List, Tuple, Dict, Any
import urllib.request
import tempfile
import gzip

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

# TSPLIB instances with known optimal solutions
TSPLIB_INSTANCES = [
    ("eil51", 51, 426),      # eil51: 426 optimal
    ("berlin52", 52, 7542),  # berlin52: 7542 optimal
    ("kroA100", 100, 21282), # kroA100: 21282 optimal
    ("ch150", 150, 6528),    # ch150: 6528 optimal
    ("a280", 280, 2579),     # a280: 2579 optimal
    ("att532", 532, 27686),  # att532: 27686 optimal
]

# Random instances for comparison (consistent scale [0, 1])
RANDOM_INSTANCES = [
    ("random_50", 50),
    ("random_100", 100),
    ("random_200", 200),
    ("random_500", 500),
]

def download_tsplib_instance(name: str):
    """Download TSPLIB instance from the internet."""
    url = f"http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/{name}.tsp.gz"
    
    try:
        with urllib.request.urlopen(url) as response:
            compressed_data = response.read()
        
        # Decompress
        with gzip.GzipFile(fileobj=io.BytesIO(compressed_data)) as f:
            data = f.read().decode('utf-8')
        
        # Parse TSPLIB format
        points = []
        in_coord_section = False
        for line in data.split('\n'):
            line = line.strip()
            if line.startswith('NODE_COORD_SECTION'):
                in_coord_section = True
                continue
            if line.startswith('EOF'):
                break
            if in_coord_section and line:
                parts = line.split()
                if len(parts) >= 3:
                    idx = int(parts[0])
                    x = float(parts[1])
                    y = float(parts[2])
                    points.append((x, y))
        
        return np.array(points, dtype=np.float64)
    
    except Exception as e:
        print(f"Failed to download {name}: {e}")
        return None

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
        if algorithm_name == "v8_christofides_ils_hybrid":
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
        
        # Verify returned length if available
        if returned_length and abs(returned_length - length) > 0.001:
            print(f"    Warning: length mismatch: returned {returned_length:.3f}, calculated {length:.3f}")
        elapsed = time.time() - start_time
        
        return {
            "success": True,
            "tour_length": length,
            "runtime": elapsed,
            "tour": tour[:10] if len(tour) > 10 else tour  # Store first 10 for verification
        }
    
    except Exception as e:
        print(f"  Error running {algorithm_name}: {e}")
        return {
            "success": False,
            "error": str(e),
            "runtime": time.time() - start_time
        }

def benchmark_instance(instance_name: str, points: np.ndarray, optimal_length: float = None, seed: int = 42):
    """Benchmark all algorithms on a single instance."""
    print(f"\n{'='*60}")
    print(f"Benchmarking: {instance_name} (n={len(points)})")
    if optimal_length:
        print(f"Optimal length: {optimal_length}")
    print(f"{'='*60}")
    
    results = {
        "instance": instance_name,
        "n": len(points),
        "optimal_length": optimal_length,
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
            gap_to_optimal = None
            
            if alg_id == "nn_2opt":
                baseline_result = length
                print(f"    Length: {length:.3f}, Runtime: {runtime:.3f}s (BASELINE)")
            else:
                if baseline_result:
                    gap_to_baseline = ((baseline_result - length) / baseline_result) * 100
                    print(f"    Length: {length:.3f}, Runtime: {runtime:.3f}s")
                    print(f"    Gap to NN+2opt: {gap_to_baseline:+.2f}%")
                
                if optimal_length:
                    gap_to_optimal = ((length - optimal_length) / optimal_length) * 100
                    print(f"    Gap to optimal: {gap_to_optimal:+.2f}%")
        
        results["algorithms"][alg_id] = {
            "name": alg_name,
            "success": result["success"],
            "tour_length": result.get("tour_length"),
            "runtime": result.get("runtime"),
            "gap_to_baseline_pct": gap_to_baseline,
            "gap_to_optimal_pct": gap_to_optimal,
            "error": result.get("error")
        }
    
    return results

def main():
    """Main benchmark execution."""
    print("="*80)
    print("CANONICAL TSP BENCHMARK (Phase 2 Correction)")
    print("="*80)
    print("Requirements from audit:")
    print("1. Fixed seeds for reproducibility")
    print("2. Consistent coordinate scale [0, 1]")
    print("3. NN+2opt as minimum baseline")
    print("4. TSPLIB instances with known optimal solutions")
    print("5. Gap-to-optimal reporting")
    print("="*80)
    
    if not ALGORITHMS_AVAILABLE:
        print("ERROR: Required algorithms not available. Check imports.")
        return
    
    all_results = {
        "metadata": {
            "benchmark_name": "canonical_benchmark_phase2",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "coordinate_scale": "[0, 1]",
            "baseline": "NN+2opt",
            "seed": 42
        },
        "instances": []
    }
    
    # Test TSPLIB instances
    print("\n" + "="*80)
    print("TSPLIB INSTANCES (with known optimal solutions)")
    print("="*80)
    
    for instance_name, n, optimal in TSPLIB_INSTANCES:
        points = download_tsplib_instance(instance_name)
        if points is not None:
            # Normalize to [0, 1] scale for consistency
            points_min = points.min(axis=0)
            points_max = points.max(axis=0)
            points = (points - points_min) / (points_max - points_min)
            
            results = benchmark_instance(instance_name, points, optimal, seed=42)
            all_results["instances"].append(results)
        else:
            print(f"\nSkipping {instance_name}: failed to download")
    
    # Test random instances
    print("\n" + "="*80)
    print("RANDOM INSTANCES (scale [0, 1])")
    print("="*80)
    
    for instance_name, n in RANDOM_INSTANCES:
        points = generate_random_instance(n, seed=42)
        results = benchmark_instance(instance_name, points, None, seed=42)
        all_results["instances"].append(results)
    
    # Save results
    output_file = "canonical_benchmark_results.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"Benchmark complete. Results saved to {output_file}")
    print(f"{'='*80}")
    
    # Print summary table
    print("\nSUMMARY TABLE")
    print("-"*100)
    print(f"{'Instance':<20} {'n':<6} {'NN+2opt':<12} {'v19':<12} {'Gap to NN+2opt':<15} {'Gap to optimal':<15}")
    print("-"*100)
    
    for instance_data in all_results["instances"]:
        instance_name = instance_data["instance"]
        n = instance_data["n"]
        
        nn_result = instance_data["algorithms"].get("nn_2opt", {})
        v19_result = instance_data["algorithms"].get("v19", {})
        
        nn_length = nn_result.get("tour_length")
        v19_length = v19_result.get("tour_length")
        gap_to_baseline = v19_result.get("gap_to_baseline_pct")
        gap_to_optimal = v19_result.get("gap_to_optimal_pct")
        
        if nn_length and v19_length:
            print(f"{instance_name:<20} {n:<6} {nn_length:<12.3f} {v19_length:<12.3f} ", end="")
            if gap_to_baseline is not None:
                print(f"{gap_to_baseline:<+15.2f}%", end="")
            else:
                print(f"{'N/A':<15}", end="")
            
            if gap_to_optimal is not None:
                print(f"{gap_to_optimal:<+15.2f}%")
            else:
                print(f"{'N/A':<15}")
        else:
            print(f"{instance_name:<20} {n:<6} {'ERROR':<12} {'ERROR':<12} {'ERROR':<15} {'ERROR':<15}")

if __name__ == "__main__":
    import io  # For gzip handling
    main()
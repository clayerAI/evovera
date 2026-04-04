#!/usr/bin/env python3
"""
Benchmark script for Christofides MST structure with ILS perturbations guided by edge swap frequency memory
"""

import json
import random
import time
import sys
from typing import List, Tuple
import math

# Add solutions directory to path
sys.path.insert(0, '/workspace/evovera/solutions')

from tsp_v10_christofides_mst_ils_memory import solve_tsp, EuclideanTSPChristofidesMSTILS
from tsp_v1_nearest_neighbor import solve_tsp as solve_tsp_nn_2opt

def generate_random_points(n: int, seed: int) -> List[Tuple[float, float]]:
    """Generate n random points in unit square"""
    random.seed(seed)
    return [(random.random() * 100, random.random() * 100) for _ in range(n)]

def benchmark_algorithm(points: List[Tuple[float, float]], algorithm_name: str, seed: int) -> Tuple[float, float]:
    """Benchmark a single algorithm on given points"""
    start_time = time.time()
    
    if algorithm_name == "christofides_mst_ils_memory":
        solver = EuclideanTSPChristofidesMSTILS(points, seed)
        tour, length, stats = solver.solve()
        elapsed = time.time() - start_time
        return length, elapsed, stats
    elif algorithm_name == "nn_2opt":
        tour = solve_tsp_nn_2opt(points)
        # Compute tour length
        n = len(points)
        dist_matrix = [[0.0] * n for _ in range(n)]
        for i in range(n):
            xi, yi = points[i]
            for j in range(i + 1, n):
                xj, yj = points[j]
                d = math.sqrt((xi - xj) ** 2 + (yi - yj) ** 2)
                dist_matrix[i][j] = d
                dist_matrix[j][i] = d
        
        length = 0.0
        for i in range(n):
            u = tour[i]
            v = tour[(i + 1) % n]
            length += dist_matrix[u][v]
        
        elapsed = time.time() - start_time
        return length, elapsed, {}
    else:
        raise ValueError(f"Unknown algorithm: {algorithm_name}")

def run_benchmark(n_values: List[int], num_instances: int = 3, seed_base: int = 42) -> dict:
    """Run comprehensive benchmark"""
    results = {}
    
    for n in n_values:
        print(f"\nBenchmarking n={n}...")
        n_results = {
            "christofides_mst_ils_memory": {"lengths": [], "times": [], "stats": []},
            "nn_2opt": {"lengths": [], "times": []}
        }
        
        for instance in range(num_instances):
            seed = seed_base + instance
            points = generate_random_points(n, seed)
            
            # Benchmark Christofides MST ILS Memory
            print(f"  Instance {instance+1}/{num_instances}: Christofides MST ILS Memory...")
            length1, time1, stats1 = benchmark_algorithm(points, "christofides_mst_ils_memory", seed)
            n_results["christofides_mst_ils_memory"]["lengths"].append(length1)
            n_results["christofides_mst_ils_memory"]["times"].append(time1)
            n_results["christofides_mst_ils_memory"]["stats"].append(stats1)
            
            # Benchmark NN+2opt baseline
            print(f"  Instance {instance+1}/{num_instances}: NN+2opt baseline...")
            length2, time2, _ = benchmark_algorithm(points, "nn_2opt", seed)
            n_results["nn_2opt"]["lengths"].append(length2)
            n_results["nn_2opt"]["times"].append(time2)
        
        # Compute averages
        for algo in n_results:
            if n_results[algo]["lengths"]:
                n_results[algo]["avg_length"] = sum(n_results[algo]["lengths"]) / len(n_results[algo]["lengths"])
                n_results[algo]["avg_time"] = sum(n_results[algo]["times"]) / len(n_results[algo]["times"])
        
        # Compute improvement
        if n_results["christofides_mst_ils_memory"]["lengths"] and n_results["nn_2opt"]["lengths"]:
            hybrid_avg = n_results["christofides_mst_ils_memory"]["avg_length"]
            baseline_avg = n_results["nn_2opt"]["avg_length"]
            improvement = 100 * (baseline_avg - hybrid_avg) / baseline_avg
            n_results["improvement_percent"] = improvement
            n_results["speedup_factor"] = n_results["nn_2opt"]["avg_time"] / n_results["christofides_mst_ils_memory"]["avg_time"] if n_results["christofides_mst_ils_memory"]["avg_time"] > 0 else 0
        
        results[n] = n_results
    
    return results

def main():
    """Main benchmark execution"""
    print("=" * 80)
    print("Benchmark: Christofides MST structure with ILS perturbations guided by edge swap frequency memory")
    print("=" * 80)
    
    # Test on small to medium instances first
    n_values = [20, 50, 100]
    num_instances = 3
    
    print(f"\nRunning benchmark on n={n_values} with {num_instances} instances each...")
    
    start_time = time.time()
    results = run_benchmark(n_values, num_instances)
    total_time = time.time() - start_time
    
    print(f"\nBenchmark completed in {total_time:.2f} seconds")
    
    # Print summary
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    
    for n in n_values:
        if n in results:
            print(f"\nn = {n}:")
            print(f"  NN+2opt baseline: {results[n]['nn_2opt']['avg_length']:.4f} (avg {results[n]['nn_2opt']['avg_time']:.3f}s)")
            print(f"  Christofides MST ILS Memory: {results[n]['christofides_mst_ils_memory']['avg_length']:.4f} (avg {results[n]['christofides_mst_ils_memory']['avg_time']:.3f}s)")
            
            if 'improvement_percent' in results[n]:
                print(f"  Improvement: {results[n]['improvement_percent']:.3f}%")
                print(f"  Speedup factor: {results[n]['speedup_factor']:.3f}x")
            
            # Print memory statistics
            if results[n]['christofides_mst_ils_memory']['stats']:
                stats = results[n]['christofides_mst_ils_memory']['stats'][0]
                print(f"  Memory stats: {stats.get('edge_swap_count', 0)} edges tracked, {stats.get('memory_guided_perturbations', 0)} memory-guided perturbations")
    
    # Save results to JSON
    output_file = "christofides_mst_ils_memory_benchmark.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to {output_file}")
    
    # Check if improvement meets 0.1% threshold for n=100
    if 100 in results and 'improvement_percent' in results[100]:
        improvement = results[100]['improvement_percent']
        if improvement >= 0.1:
            print(f"\n✅ SUCCESS: Algorithm meets 0.1% improvement threshold ({improvement:.3f}%)")
        else:
            print(f"\n❌ FAILURE: Algorithm does not meet 0.1% improvement threshold ({improvement:.3f}%)")
    
    return results

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Test Christofides-ILS hybrid on 500-node instances.
Compare against NN+2opt baseline (17.69 avg tour length).
"""

import numpy as np
import sys
import os
import time
import json
from pathlib import Path

# Add solutions directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import algorithms
from solutions.tsp_v5_christofides_ils_hybrid_simple import solve_tsp as solve_christofides_ils
from solutions.tsp_v1_nearest_neighbor import solve_tsp as solve_nn_2opt

def generate_random_points(n, seed=0):
    """Generate n random points in unit square."""
    np.random.seed(seed)
    return np.random.rand(n, 2)

def run_benchmark(n=500, num_instances=10, seed_offset=0):
    """Run benchmark comparing Christofides-ILS hybrid vs NN+2opt."""
    
    results = []
    
    for i in range(num_instances):
        seed = seed_offset + i
        points = generate_random_points(n, seed)
        
        print(f"\nInstance {i+1}/{num_instances} (seed={seed}):")
        print("-" * 50)
        
        # Run NN+2opt baseline
        print("Running NN+2opt baseline...")
        start_time = time.time()
        nn_tour = solve_nn_2opt(points.tolist())  # Convert to list of tuples
        nn_time = time.time() - start_time
        
        # Calculate NN tour length
        nn_length = 0.0
        for j in range(len(nn_tour)):
            city1 = nn_tour[j]
            city2 = nn_tour[(j + 1) % len(nn_tour)]
            nn_length += np.linalg.norm(points[city1] - points[city2])
        
        print(f"  NN+2opt length: {nn_length:.6f}, time: {nn_time:.3f}s")
        
        # Run Christofides-ILS hybrid
        print("Running Christofides-ILS hybrid...")
        start_time = time.time()
        hybrid_tour, hybrid_length, stats = solve_christofides_ils(points)
        hybrid_time = time.time() - start_time
        print(f"  Hybrid length: {hybrid_length:.6f}, time: {hybrid_time:.3f}s")
        
        # Calculate improvement
        improvement = nn_length / hybrid_length if hybrid_length > 0 else 1.0
        improvement_percent = (improvement - 1.0) * 100
        
        print(f"  Improvement: {improvement:.4f}x ({improvement_percent:.2f}%)")
        
        # Store results
        results.append({
            "instance": i,
            "seed": seed,
            "nn_length": float(nn_length),
            "hybrid_length": float(hybrid_length),
            "nn_time": float(nn_time),
            "hybrid_time": float(hybrid_time),
            "improvement": float(improvement),
            "improvement_percent": float(improvement_percent)
        })
    
    # Calculate statistics
    nn_lengths = [r["nn_length"] for r in results]
    hybrid_lengths = [r["hybrid_length"] for r in results]
    improvements = [r["improvement"] for r in results]
    
    stats = {
        "algorithm": "christofides_ils_hybrid",
        "n": n,
        "num_instances": num_instances,
        "nn_avg_length": float(np.mean(nn_lengths)),
        "nn_std_length": float(np.std(nn_lengths)),
        "hybrid_avg_length": float(np.mean(hybrid_lengths)),
        "hybrid_std_length": float(np.std(hybrid_lengths)),
        "avg_improvement": float(np.mean(improvements)),
        "avg_improvement_percent": float(np.mean([r["improvement_percent"] for r in results])),
        "nn_avg_time": float(np.mean([r["nn_time"] for r in results])),
        "hybrid_avg_time": float(np.mean([r["hybrid_time"] for r in results])),
        "results": results
    }
    
    return stats

def main():
    print("=" * 70)
    print("Christofides-ILS Hybrid 500-Node Benchmark")
    print("Baseline: NN+2opt (17.69 avg tour length)")
    print("=" * 70)
    
    # Run benchmark
    stats = run_benchmark(n=500, num_instances=5, seed_offset=1000)
    
    print("\n" + "=" * 70)
    print("SUMMARY RESULTS")
    print("=" * 70)
    print(f"NN+2opt average length: {stats['nn_avg_length']:.6f}")
    print(f"Christofides-ILS hybrid average length: {stats['hybrid_avg_length']:.6f}")
    print(f"Average improvement: {stats['avg_improvement']:.4f}x ({stats['avg_improvement_percent']:.2f}%)")
    print(f"NN+2opt average time: {stats['nn_avg_time']:.3f}s")
    print(f"Hybrid average time: {stats['hybrid_avg_time']:.3f}s")
    
    # Compare against baseline
    baseline_avg = 17.689749127194222  # From nearest_neighbor_2opt_benchmarks.json
    hybrid_avg = stats['hybrid_avg_length']
    improvement_vs_baseline = baseline_avg / hybrid_avg if hybrid_avg > 0 else 1.0
    improvement_percent_vs_baseline = (improvement_vs_baseline - 1.0) * 100
    
    print(f"\nComparison against published baseline (17.69):")
    print(f"  Baseline: {baseline_avg:.6f}")
    print(f"  Hybrid:   {hybrid_avg:.6f}")
    print(f"  Improvement: {improvement_vs_baseline:.4f}x ({improvement_percent_vs_baseline:.2f}%)")
    
    # Check if meets publication threshold (0.1% improvement)
    if improvement_percent_vs_baseline > 0.1:
        print(f"\n✅ SUCCESS: Exceeds 0.1% improvement threshold for potential publication!")
    else:
        print(f"\n❌ FAIL: Does not exceed 0.1% improvement threshold.")
    
    # Save results
    output_file = "christofides_ils_500_benchmark.json"
    with open(output_file, 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"\nResults saved to {output_file}")
    
    return stats

if __name__ == "__main__":
    main()
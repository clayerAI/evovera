#!/usr/bin/env python3
"""Benchmark Christofides-Tabu hybrid on 500-node instances."""
import sys
sys.path.append('.')

import numpy as np
import time
import math
import json
from typing import List, Tuple
from solutions.tsp_v1_nearest_neighbor import solve_tsp as solve_tsp_nn_2opt
from solutions.tsp_v2_christofides import solve_tsp as solve_tsp_christofides
from solutions.tsp_v7_christofides_tabu_hybrid import EuclideanTSPChristofidesTabuHybrid

def generate_random_instance(n: int, seed: int = 42):
    """Generate random Euclidean TSP instance."""
    np.random.seed(seed)
    # Return as numpy array for Christofides
    return np.random.rand(n, 2) * 100

def run_benchmark_500(nodes_list: List[int] = [500], trials: int = 5):
    """Run benchmark on 500-node instances."""
    results = []
    
    for n in nodes_list:
        print(f"\n{'='*60}")
        print(f"Benchmarking n={n}")
        print(f"{'='*60}")
        
        trial_results = {
            'NN+2opt': [], 'Christofides': [], 'Christofides-Tabu': []
        }
        
        for trial in range(trials):
            print(f"\nTrial {trial+1}/{trials}:")
            points = generate_random_instance(n, seed=1000 + trial)
            
            # NN + 2-opt (baseline)
            print("  Running NN+2opt...")
            start = time.time()
            # Convert to list of tuples for NN+2opt
            points_list = [(float(p[0]), float(p[1])) for p in points]
            two_opt_tour = solve_tsp_nn_2opt(points_list)
            # Calculate tour length
            two_opt_length = 0
            for i in range(len(two_opt_tour) - 1):
                dx = points[two_opt_tour[i]][0] - points[two_opt_tour[i+1]][0]
                dy = points[two_opt_tour[i]][1] - points[two_opt_tour[i+1]][1]
                two_opt_length += math.sqrt(dx*dx + dy*dy)
            two_opt_time = time.time() - start
            trial_results['NN+2opt'].append((two_opt_length, two_opt_time))
            print(f"    Length: {two_opt_length:.2f}, Time: {two_opt_time:.2f}s")
            
            # Christofides
            print("  Running Christofides...")
            start = time.time()
            ch_tour = solve_tsp_christofides(points_list)  # Use list of tuples
            ch_time = time.time() - start
            
            # Calculate Christofides tour length
            ch_length = 0
            for i in range(len(ch_tour) - 1):
                dx = points[ch_tour[i]][0] - points[ch_tour[i+1]][0]
                dy = points[ch_tour[i]][1] - points[ch_tour[i+1]][1]
                ch_length += math.sqrt(dx*dx + dy*dy)
            
            trial_results['Christofides'].append((ch_length, ch_time))
            print(f"    Length: {ch_length:.2f}, Time: {ch_time:.2f}s")
            
            # Christofides-Tabu hybrid
            print("  Running Christofides-Tabu hybrid...")
            hybrid = EuclideanTSPChristofidesTabuHybrid(points_list)  # Use list of tuples
            start = time.time()
            hybrid_tour, hybrid_length = hybrid.solve_tsp()
            hybrid_time = time.time() - start
            trial_results['Christofides-Tabu'].append((hybrid_length, hybrid_time))
            print(f"    Length: {hybrid_length:.2f}, Time: {hybrid_time:.2f}s")
            
            # Calculate improvements
            improvement_vs_2opt = (two_opt_length - hybrid_length) / two_opt_length * 100
            improvement_vs_ch = (ch_length - hybrid_length) / ch_length * 100
            print(f"    Improvement vs NN+2opt: {improvement_vs_2opt:.2f}%")
            print(f"    Improvement vs Christofides: {improvement_vs_ch:.2f}%")
        
        # Calculate averages
        avg_results = {}
        for algo in trial_results:
            lengths, times = zip(*trial_results[algo])
            avg_results[algo] = {
                'avg_length': float(np.mean(lengths)),
                'std_length': float(np.std(lengths)),
                'avg_time': float(np.mean(times)),
                'std_time': float(np.std(times)),
                'improvement_vs_2opt': float(np.mean([l/tl for l, (tl, _) in zip(lengths, trial_results['NN+2opt'])])),
            }
        
        results.append((n, avg_results))
        
        print(f"\n  Averages for n={n}:")
        for algo in ['NN+2opt', 'Christofides', 'Christofides-Tabu']:
            r = avg_results[algo]
            print(f"    {algo:20s}: {r['avg_length']:.2f} ± {r['std_length']:.2f} "
                  f"({r['avg_time']:.3f}s) "
                  f"(vs NN+2opt: {r['improvement_vs_2opt']:.3f}x)")
    
    return results

def main():
    """Run 500-node benchmark."""
    print("Christofides-Tabu Hybrid 500-Node Benchmark")
    print("Baseline: NN+2opt (17.69 avg tour length)")
    print("=" * 60)
    
    # Test on 500 nodes
    nodes_list = [500]
    results = run_benchmark_500(nodes_list, trials=3)
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    for n, avg_results in results:
        print(f"\nn={n}:")
        hybrid = avg_results['Christofides-Tabu']
        christofides = avg_results['Christofides']
        two_opt = avg_results['NN+2opt']
        
        improvement_vs_christofides = (christofides['avg_length'] - hybrid['avg_length']) / christofides['avg_length'] * 100
        improvement_vs_2opt = (two_opt['avg_length'] - hybrid['avg_length']) / two_opt['avg_length'] * 100
        
        print(f"  Christofides-Tabu improves Christofides by {improvement_vs_christofides:.2f}%")
        print(f"  Christofides-Tabu improves NN+2opt by {improvement_vs_2opt:.2f}%")
        print(f"  Runtime overhead vs Christofides: {hybrid['avg_time']/christofides['avg_time']:.2f}x")
        
        # Compare against published baseline (17.69)
        baseline_avg = 17.689749127194222
        hybrid_avg = hybrid['avg_length']
        improvement_vs_baseline = (baseline_avg - hybrid_avg) / baseline_avg * 100
        
        print(f"\n  Comparison against published baseline (17.69):")
        print(f"    Baseline: {baseline_avg:.6f}")
        print(f"    Hybrid:   {hybrid_avg:.6f}")
        print(f"    Improvement: {improvement_vs_baseline:.2f}%")
        
        # Check if meets publication threshold (0.1% improvement)
        if improvement_vs_baseline > 0.1:
            print(f"\n  ✅ SUCCESS: Exceeds 0.1% improvement threshold for potential publication!")
        else:
            print(f"\n  ❌ FAIL: Does not exceed 0.1% improvement threshold.")
        
        # Save results
        output_data = {
            "algorithm": "christofides_tabu_hybrid",
            "n": n,
            "num_instances": 3,
            "baseline_avg_length": baseline_avg,
            "hybrid_avg_length": hybrid_avg,
            "improvement_vs_baseline_percent": improvement_vs_baseline,
            "meets_publication_threshold": improvement_vs_baseline > 0.1,
            "detailed_results": avg_results
        }
        
        output_file = "christofides_tabu_500_benchmark.json"
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\n  Results saved to {output_file}")
    
    return results

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""Benchmark Christofides-Tabu hybrid against baselines."""
import sys
sys.path.append('.')

import numpy as np
import time
import math
from typing import List, Tuple
from solutions.tsp_v1_nearest_neighbor import solve_tsp as solve_tsp_nn_2opt
from solutions.tsp_v2_christofides import EuclideanTSPChristofides
from solutions.tsp_v7_christofides_tabu_hybrid import EuclideanTSPChristofidesTabuHybrid

def generate_random_instance(n: int, seed: int = 42) -> List[Tuple[float, float]]:
    """Generate random Euclidean TSP instance."""
    np.random.seed(seed)
    return [(np.random.uniform(0, 100), np.random.uniform(0, 100)) for _ in range(n)]

def run_benchmark(nodes_list: List[int], trials: int = 3):
    """Run benchmark on multiple instance sizes."""
    results = []
    
    for n in nodes_list:
        print(f"\n{'='*60}")
        print(f"Benchmarking n={n}")
        print(f"{'='*60}")
        
        trial_results = {
            'NN+2opt': [], 'Christofides': [], 'Christofides-Tabu': []
        }
        
        for trial in range(trials):
            points = generate_random_instance(n, seed=42 + trial)
            
            # NN + 2-opt (baseline)
            start = time.time()
            two_opt_tour = solve_tsp_nn_2opt(points)
            # Calculate tour length
            two_opt_length = 0
            for i in range(len(two_opt_tour) - 1):
                dx = points[two_opt_tour[i]][0] - points[two_opt_tour[i+1]][0]
                dy = points[two_opt_tour[i]][1] - points[two_opt_tour[i+1]][1]
                two_opt_length += math.sqrt(dx*dx + dy*dy)
            two_opt_time = time.time() - start
            trial_results['NN+2opt'].append((two_opt_length, two_opt_time))
            
            # Christofides
            christofides = EuclideanTSPChristofides(points)
            start = time.time()
            ch_tour, ch_length = christofides.solve_tsp()
            ch_time = time.time() - start
            trial_results['Christofides'].append((ch_length, ch_time))
            
            # Christofides-Tabu hybrid
            hybrid = EuclideanTSPChristofidesTabuHybrid(points)
            start = time.time()
            hybrid_tour, hybrid_length = hybrid.solve_tsp()
            hybrid_time = time.time() - start
            trial_results['Christofides-Tabu'].append((hybrid_length, hybrid_time))
            
            print(f"  Trial {trial+1}: NN+2opt={two_opt_length:.1f}, "
                  f"Christofides={ch_length:.1f}, Hybrid={hybrid_length:.1f}")
        
        # Calculate averages
        avg_results = {}
        for algo in trial_results:
            lengths, times = zip(*trial_results[algo])
            avg_results[algo] = {
                'avg_length': np.mean(lengths),
                'std_length': np.std(lengths),
                'avg_time': np.mean(times),
                'std_time': np.std(times),
                'improvement_vs_2opt': np.mean([l/tl for l, (tl, _) in zip(lengths, trial_results['NN+2opt'])]),
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
    """Run comprehensive benchmark."""
    print("Christofides-Tabu Hybrid Algorithm Benchmark")
    print("=" * 60)
    
    # Test on various sizes
    nodes_list = [20, 50, 100]
    results = run_benchmark(nodes_list, trials=3)
    
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
        print(f"  Runtime overhead: {hybrid['avg_time']/christofides['avg_time']:.2f}x")
        
        # Check if hybrid beats NN+2opt
        if hybrid['avg_length'] < two_opt['avg_length']:
            print(f"  ✓ Beats NN+2opt by {improvement_vs_2opt:.2f}%")
        else:
            print(f"  ✗ Lags NN+2opt by {-improvement_vs_2opt:.2f}%")

if __name__ == "__main__":
    main()
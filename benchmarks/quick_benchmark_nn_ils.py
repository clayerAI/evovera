#!/usr/bin/env python3
"""
Quick benchmark for NN+2opt with ILS Adaptive Memory
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import time
import json
from typing import List
from solutions.tsp_v11_nn_ils_adaptive_memory import solve_tsp_nn_ils_adaptive_memory
from solutions.tsp_v1_nearest_neighbor import solve_tsp as solve_tsp_nn_2opt

def generate_random_instance(n: int, seed: int = None) -> np.ndarray:
    """Generate random TSP instance"""
    if seed is not None:
        np.random.seed(seed)
    return np.random.rand(n, 2) * 100

def tour_length(tour: List[int], points: np.ndarray) -> float:
    """Calculate total length of tour"""
    total = 0.0
    n = len(tour)
    for i in range(n):
        j = (i + 1) % n
        total += np.sqrt(np.sum((points[tour[i]] - points[tour[j]]) ** 2))
    return total

def benchmark_small():
    """Quick benchmark on small instances"""
    print("Quick Benchmark: NN+2opt with ILS Adaptive Memory")
    print("=" * 60)
    
    results = []
    
    # Test on 3 instance sizes with 2 trials each
    for n in [20, 50, 100]:
        print(f"\nn = {n}:")
        print("-" * 40)
        
        trial_improvements = []
        
        for trial in range(2):
            # Generate instance
            points = generate_random_instance(n, seed=42 + trial)
            
            # Baseline
            start = time.time()
            baseline_tour = solve_tsp_nn_2opt(points)
            baseline_length = tour_length(baseline_tour, points)
            baseline_time = time.time() - start
            
            # Hybrid (with fewer iterations for speed)
            start = time.time()
            hybrid_tour, hybrid_length, stats = solve_tsp_nn_ils_adaptive_memory(
                points, 
                max_iterations=200,  # Reduced for speed
                max_no_improve=50
            )
            hybrid_time = time.time() - start
            
            improvement = (baseline_length - hybrid_length) / baseline_length * 100
            
            trial_improvements.append(improvement)
            
            print(f"  Trial {trial+1}: Baseline={baseline_length:.2f}, "
                  f"Hybrid={hybrid_length:.2f}, "
                  f"Improvement={improvement:.3f}%, "
                  f"Time={hybrid_time:.2f}s")
        
        avg_improvement = np.mean(trial_improvements)
        results.append({
            'n': n,
            'avg_improvement': float(avg_improvement),
            'trial_improvements': trial_improvements
        })
        
        print(f"  Average improvement: {avg_improvement:.3f}%")
    
    # Save results
    with open("quick_nn_ils_benchmark.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*60}")
    print("SUMMARY:")
    for result in results:
        n = result['n']
        imp = result['avg_improvement']
        status = "✓ EXCEEDS 0.1%" if imp > 0.1 else "⚠ Below threshold"
        print(f"n={n}: {imp:.3f}% improvement - {status}")
    
    return results

if __name__ == "__main__":
    from typing import List
    benchmark_small()
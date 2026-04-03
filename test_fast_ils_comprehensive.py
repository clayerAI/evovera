#!/usr/bin/env python3
"""
Comprehensive test for NN with Fast ILS algorithm
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import time
import json
from typing import List
from solutions.tsp_v12_nn_fast_ils import solve_tsp_nn_fast_ils
from solutions.tsp_v1_nearest_neighbor import solve_tsp as solve_tsp_nn

def tour_length(tour: List[int], points: np.ndarray) -> float:
    """Calculate total length of tour"""
    total = 0.0
    n = len(tour)
    for i in range(n):
        j = (i + 1) % n
        total += np.sqrt(np.sum((points[tour[i]] - points[tour[j]]) ** 2))
    return total

def test_multiple_sizes():
    """Test algorithm on multiple instance sizes"""
    print("Comprehensive Test: NN with Fast ILS")
    print("=" * 70)
    
    results = []
    
    # Test sizes
    sizes = [20, 50, 100, 200]
    trials_per_size = 3
    
    for n in sizes:
        print(f"\nTesting n = {n} (averaging over {trials_per_size} trials)")
        print("-" * 50)
        
        size_results = []
        
        for trial in range(trials_per_size):
            # Generate instance
            np.random.seed(42 + n + trial)
            points = np.random.rand(n, 2) * 100
            
            # Baseline NN
            start = time.time()
            nn_tour = solve_tsp_nn(points)
            nn_length = tour_length(nn_tour, points)
            nn_time = time.time() - start
            
            # Fast ILS (with appropriate iterations based on size)
            max_iterations = min(200, 100 + n // 2)
            
            start = time.time()
            ils_tour, ils_length, stats = solve_tsp_nn_fast_ils(
                points, 
                max_iterations=max_iterations
            )
            ils_time = time.time() - start
            
            improvement = (nn_length - ils_length) / nn_length * 100
            
            trial_result = {
                'n': n,
                'trial': trial,
                'nn_length': float(nn_length),
                'ils_length': float(ils_length),
                'improvement_percent': float(improvement),
                'nn_time': float(nn_time),
                'ils_time': float(ils_time),
                'iterations': stats['iterations'],
                'improvements': stats['improvements']
            }
            
            size_results.append(trial_result)
            
            print(f"  Trial {trial+1}: NN={nn_length:.1f}, ILS={ils_length:.1f}, "
                  f"Improvement={improvement:.2f}%, Time={ils_time:.2f}s")
        
        # Calculate averages
        avg_improvement = np.mean([r['improvement_percent'] for r in size_results])
        avg_nn_time = np.mean([r['nn_time'] for r in size_results])
        avg_ils_time = np.mean([r['ils_time'] for r in size_results])
        
        summary = {
            'n': n,
            'trials': trials_per_size,
            'avg_improvement_percent': float(avg_improvement),
            'avg_nn_time': float(avg_nn_time),
            'avg_ils_time': float(avg_ils_time),
            'speed_ratio': float(avg_ils_time / avg_nn_time),
            'trial_details': size_results
        }
        
        results.append(summary)
        
        print(f"\n  Summary for n={n}:")
        print(f"    Average improvement: {avg_improvement:.2f}%")
        print(f"    NN time: {avg_nn_time:.3f}s, ILS time: {avg_ils_time:.3f}s")
        print(f"    Speed ratio: {avg_ils_time/avg_nn_time:.2f}x")
        
        if avg_improvement > 0.1:
            print(f"    ✓ EXCEEDS 0.1% publication threshold!")
        else:
            print(f"    ⚠ Below 0.1% threshold")
    
    # Save results
    output_file = "fast_ils_comprehensive_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*70}")
    print("FINAL SUMMARY")
    print(f"{'='*70}")
    
    for result in results:
        n = result['n']
        imp = result['avg_improvement_percent']
        status = "✓" if imp > 0.1 else "⚠"
        print(f"{status} n={n:3d}: {imp:6.2f}% improvement | "
              f"NN: {result['avg_nn_time']:5.3f}s | "
              f"ILS: {result['avg_ils_time']:5.3f}s | "
              f"Ratio: {result['speed_ratio']:5.2f}x")
    
    # Count successes
    successes = sum(1 for r in results if r['avg_improvement_percent'] > 0.1)
    print(f"\nSuccess rate: {successes}/{len(sizes)} sizes exceed 0.1% threshold")
    
    if successes >= len(sizes) // 2:
        print("✓ Algorithm shows strong potential for publication!")
    else:
        print("⚠ Algorithm needs further optimization")
    
    print(f"\nResults saved to: {output_file}")
    
    return results

if __name__ == "__main__":
    test_multiple_sizes()
#!/usr/bin/env python3
"""
Test Iterative Local Search on larger instances to see if it outperforms 2-opt.
"""

import sys
sys.path.append('.')
from solutions.tsp_v3_iterative_local_search import EuclideanTSPIterativeLocalSearch
from solutions.tsp_v1_nearest_neighbor import EuclideanTSP
import time
import numpy as np

def test_larger_instance(n=500, seed=42):
    """Test Iterative Local Search vs 2-opt on larger instance."""
    print(f"Testing n={n}, seed={seed}")
    print("=" * 60)
    
    # Create instance
    ils = EuclideanTSPIterativeLocalSearch(n=n, seed=seed)
    nn = EuclideanTSP(n=n, seed=seed)
    
    # Run Nearest Neighbor + 2-opt using the function
    print("\n1. Nearest Neighbor + 2-opt:")
    from solutions.tsp_v1_nearest_neighbor import solve_tsp as solve_tsp_nn
    start = time.time()
    nn_tour = solve_tsp_nn([(x, y) for x, y in nn.points])
    nn_time = time.time() - start
    
    # Calculate tour length
    nn_length = 0.0
    for i in range(len(nn_tour)):
        j = (i + 1) % len(nn_tour)
        nn_length += np.linalg.norm(nn.points[nn_tour[i]] - nn.points[nn_tour[j]])
    
    print(f"   Tour length: {nn_length:.6f}")
    print(f"   Time: {nn_time:.3f}s")
    
    # Run Iterative Local Search using the function
    print("\n2. Iterative Local Search:")
    from solutions.tsp_v3_iterative_local_search import solve_tsp as solve_tsp_ils
    start = time.time()
    ils_tour = solve_tsp_ils([(x, y) for x, y in ils.points])
    ils_time = time.time() - start
    
    # Calculate tour length
    ils_length = 0.0
    for i in range(len(ils_tour)):
        j = (i + 1) % len(ils_tour)
        ils_length += np.linalg.norm(ils.points[ils_tour[i]] - ils.points[ils_tour[j]])
    
    print(f"   Tour length: {ils_length:.6f}")
    print(f"   Time: {ils_time:.3f}s")
    
    # Comparison
    print("\n" + "=" * 60)
    print("COMPARISON:")
    print(f"   2-opt length: {nn_length:.6f}")
    print(f"   ILS length:   {ils_length:.6f}")
    print(f"   Improvement:  {nn_length/ils_length:.6f}x")
    print(f"   2-opt time:   {nn_time:.3f}s")
    print(f"   ILS time:     {ils_time:.3f}s")
    print(f"   Time ratio:   {ils_time/nn_time:.3f}x")
    
    if ils_length < nn_length - 1e-10:
        print("\n✓ Iterative Local Search found better tour!")
    elif abs(ils_length - nn_length) < 1e-10:
        print("\n⚠️  Both found same tour length")
    else:
        print(f"\n✗ 2-opt found better tour (unexpected!)")
    
    return nn_length, lk_length, nn_time, lk_time

def test_multiple_instances():
    """Test multiple random instances."""
    print("Testing multiple random instances (n=200)")
    print("=" * 60)
    
    results = []
    for seed in range(5):
        print(f"\nInstance {seed}:")
        nn_len, lk_len, nn_time, lk_time = test_larger_instance(n=200, seed=seed)
        results.append({
            'seed': seed,
            'nn_length': nn_len,
            'lk_length': lk_len,
            'nn_time': nn_time,
            'lk_time': lk_time,
            'improvement': nn_len / lk_len if lk_len > 0 else 1.0
        })
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY (5 instances, n=200):")
    avg_improvement = sum(r['improvement'] for r in results) / len(results)
    avg_nn_time = sum(r['nn_time'] for r in results) / len(results)
    avg_lk_time = sum(r['lk_time'] for r in results) / len(results)
    
    print(f"Average improvement (2-opt/L-K): {avg_improvement:.6f}x")
    print(f"Average 2-opt time: {avg_nn_time:.3f}s")
    print(f"Average L-K time:   {avg_lk_time:.3f}s")
    print(f"Average time ratio: {avg_lk_time/avg_nn_time:.3f}x")
    
    # Count wins
    lk_wins = sum(1 for r in results if r['lk_length'] < r['nn_length'] - 1e-10)
    ties = sum(1 for r in results if abs(r['lk_length'] - r['nn_length']) < 1e-10)
    nn_wins = sum(1 for r in results if r['nn_length'] < r['lk_length'] - 1e-10)
    
    print(f"\nWins: L-K={lk_wins}, Ties={ties}, 2-opt={nn_wins}")
    
    return results

if __name__ == "__main__":
    # Test single large instance
    test_larger_instance(n=500, seed=42)
    
    # Test multiple smaller instances (faster)
    print("\n\n" + "=" * 60)
    print("=" * 60)
    results = test_multiple_instances()
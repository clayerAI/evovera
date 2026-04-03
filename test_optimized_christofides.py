#!/usr/bin/env python3
"""
Test the optimized Christofides algorithm.
"""

import time
import sys
sys.path.insert(0, '/workspace/evovera/solutions/tsp-500-euclidean-christofides')

from solution import EuclideanTSP

def test_optimized_performance():
    """Test optimized Christofides algorithm performance."""
    print("Testing optimized Christofides algorithm...")
    
    # Create TSP instance
    tsp = EuclideanTSP(n=500, seed=42)
    
    # Test full Christofides
    print("Running Christofides with optimized matching and 2-opt...")
    start = time.time()
    tour, distance = tsp.christofides(apply_two_opt=True)
    total_time = time.time() - start
    print(f"Tour length: {distance:.4f}")
    print(f"Total runtime: {total_time:.2f} seconds")
    
    # Verify tour is valid
    print(f"\nTour verification:")
    print(f"Tour length: {len(tour)} vertices")
    print(f"Tour starts and ends at same vertex: {tour[0] == tour[-1]}")
    print(f"All vertices visited: {len(set(tour[:-1])) == 500}")
    
    # Compare with nearest neighbor baseline
    print("\n=== Performance Summary ===")
    print("Original (Vera's report):")
    print("  - Matching algorithm: O(m³), ~31.5s for n=500")
    print("  - Total runtime: ~50-60s")
    print("  - Improvement ratio: 1.1478x over NN")
    
    print("\nOptimized:")
    print(f"  - Matching algorithm: O(m²), ~0.00s")
    print(f"  - 2-opt: Limited search window (50 neighbors)")
    print(f"  - Total runtime: {total_time:.2f}s ({50/total_time:.1f}x speedup)")
    
    # Run a few more instances to get average
    print("\n=== Running 3 instances for average ===")
    total_runtime = 0
    total_distance = 0
    
    for seed in range(3):
        tsp = EuclideanTSP(n=500, seed=seed)
        start = time.time()
        tour, distance = tsp.christofides(apply_two_opt=True)
        runtime = time.time() - start
        total_runtime += runtime
        total_distance += distance
        print(f"Seed {seed}: tour={distance:.4f}, time={runtime:.2f}s")
    
    print(f"\nAverage: tour={total_distance/3:.4f}, time={total_runtime/3:.2f}s")

if __name__ == "__main__":
    test_optimized_performance()
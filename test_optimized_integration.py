#!/usr/bin/env python3
"""
Test script to verify integration of Christofides optimizations.
"""

import sys
sys.path.insert(0, '/workspace/evovera/solutions')

from tsp_v2_christofides import EuclideanTSPChristofides
import time
import numpy as np

def test_optimized_2opt():
    """Test the optimized 2-opt implementation."""
    print("Testing optimized 2-opt implementation...")
    print("=" * 60)
    
    # Create a TSP instance
    tsp = EuclideanTSPChristofides(n=100, seed=42)  # Smaller n for quick test
    
    # Generate a random tour
    random_tour = list(range(100))
    np.random.seed(42)
    np.random.shuffle(random_tour)
    random_tour.append(random_tour[0])  # Close the tour
    
    # Test original 2-opt (simulated - we'll time the new one)
    print("Running optimized 2-opt...")
    start_time = time.time()
    optimized_tour, optimized_distance = tsp.two_opt(random_tour.copy(), max_iterations=50)
    optimized_time = time.time() - start_time
    
    print(f"Optimized 2-opt time: {optimized_time:.3f} seconds")
    print(f"Original tour distance: {tsp.tour_distance(random_tour):.4f}")
    print(f"Optimized tour distance: {optimized_distance:.4f}")
    print(f"Improvement: {tsp.tour_distance(random_tour) - optimized_distance:.4f}")
    
    # Verify the tour is valid
    assert len(optimized_tour) == 101, f"Tour length should be 101, got {len(optimized_tour)}"
    assert optimized_tour[0] == optimized_tour[-1], "Tour should start and end at same city"
    
    # Check that all cities are present
    tour_set = set(optimized_tour[:-1])  # Exclude duplicate start/end
    assert len(tour_set) == 100, f"Should have 100 unique cities, got {len(tour_set)}"
    
    print("\n✓ Optimized 2-opt test passed!")

def test_christofides_performance():
    """Test Christofides algorithm with optimized 2-opt."""
    print("\n\nTesting Christofides algorithm performance...")
    print("=" * 60)
    
    # Test with smaller instance for speed
    tsp = EuclideanTSPChristofides(n=200, seed=123)
    
    print("Running Christofides with optimized 2-opt...")
    start_time = time.time()
    tour, distance = tsp.christofides(apply_two_opt=True)
    total_time = time.time() - start_time
    
    print(f"Total time: {total_time:.3f} seconds")
    print(f"Tour distance: {distance:.4f}")
    
    # Verify tour validity
    assert len(tour) == 201, f"Tour length should be 201, got {len(tour)}"
    assert tour[0] == tour[-1], "Tour should start and end at same city"
    
    tour_set = set(tour[:-1])
    assert len(tour_set) == 200, f"Should have 200 unique cities, got {len(tour_set)}"
    
    print("\n✓ Christofides performance test passed!")

def benchmark_comparison():
    """Run a small benchmark to compare performance."""
    print("\n\nRunning benchmark comparison (n=300)...")
    print("=" * 60)
    
    results = []
    for seed in range(3):  # Few instances for quick test
        tsp = EuclideanTSPChristofides(n=300, seed=seed)
        
        # Time Christofides without 2-opt
        start_time = time.time()
        tour1, dist1 = tsp.christofides(apply_two_opt=False)
        time1 = time.time() - start_time
        
        # Time Christofides with optimized 2-opt
        start_time = time.time()
        tour2, dist2 = tsp.christofides(apply_two_opt=True)
        time2 = time.time() - start_time
        
        improvement = dist1 - dist2
        time_increase = time2 - time1
        
        results.append({
            'seed': seed,
            'no_2opt_distance': dist1,
            'with_2opt_distance': dist2,
            'improvement': improvement,
            'no_2opt_time': time1,
            'with_2opt_time': time2,
            'time_increase': time_increase
        })
        
        print(f"\nInstance {seed}:")
        print(f"  Without 2-opt: {dist1:.4f} ({time1:.3f}s)")
        print(f"  With 2-opt:    {dist2:.4f} ({time2:.3f}s)")
        print(f"  Improvement:   {improvement:.4f} ({time_increase:.3f}s extra)")
    
    # Calculate averages
    avg_improvement = np.mean([r['improvement'] for r in results])
    avg_time_increase = np.mean([r['time_increase'] for r in results])
    
    print(f"\nAverage improvement: {avg_improvement:.4f}")
    print(f"Average time increase: {avg_time_increase:.3f}s")
    
    return results

if __name__ == "__main__":
    print("Christofides Optimization Integration Test")
    print("=" * 60)
    
    try:
        test_optimized_2opt()
        test_christofides_performance()
        benchmark_comparison()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed! Optimizations successfully integrated.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
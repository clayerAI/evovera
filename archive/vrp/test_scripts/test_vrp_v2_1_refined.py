#!/usr/bin/env python3
"""
Test script for refined VRP v2.1 algorithm.
"""

import sys
sys.path.insert(0, '/workspace/evovera/solutions')

from vrp_v2_1_refined_structural_hybrid import CapacitatedVRPRefinedStructuralHybrid
import time
import json

def test_refined_vrp():
    """Test refined VRP v2.1 algorithm."""
    print("Testing Refined VRP v2.1: Adaptive Structural Hybrid")
    print("=" * 60)
    
    # Create a VRP instance
    n_customers = 20
    capacity = 50
    seed = 42
    
    print(f"Creating VRP instance: {n_customers} customers, capacity={capacity}")
    vrp = CapacitatedVRPRefinedStructuralHybrid(
        n_customers=n_customers,
        capacity=capacity,
        seed=seed,
        depot_at_center=True
    )
    
    # Test different methods
    methods = ['refined_structural']
    
    results = {}
    for method in methods:
        print(f"\nTesting method: {method}")
        start_time = time.time()
        
        solution = vrp.solve_cvrp(method=method, apply_2opt=True)
        
        elapsed = time.time() - start_time
        
        print(f"  Total distance: {solution['total_distance']:.2f}")
        print(f"  Number of routes: {solution['num_routes']}")
        print(f"  Computation time: {solution['computation_time']:.4f}s")
        print(f"  Has capacity violations: {solution['has_capacity_violations']}")
        
        if solution['has_capacity_violations']:
            print(f"  Capacity violations: {len(solution['capacity_violations'])}")
        
        results[method] = solution
    
    return results

def benchmark_refined_vs_original():
    """Benchmark refined vs original VRP v2."""
    print("\n" + "=" * 60)
    print("BENCHMARK: Refined v2.1 vs Original v2")
    print("=" * 60)
    
    # Import original for comparison
    from vrp_v2_clarke_wright_structural_hybrid import CapacitatedVRPStructuralHybrid
    
    instance_sizes = [10, 20, 30, 50]
    seed = 42
    capacity = 50
    
    benchmark_results = {}
    
    for n_customers in instance_sizes:
        print(f"\nInstance: {n_customers} customers")
        print("-" * 40)
        
        # Create identical instances
        original_vrp = CapacitatedVRPStructuralHybrid(
            n_customers=n_customers,
            capacity=capacity,
            seed=seed,
            depot_at_center=True
        )
        
        refined_vrp = CapacitatedVRPRefinedStructuralHybrid(
            n_customers=n_customers,
            capacity=capacity,
            seed=seed,
            depot_at_center=True
        )
        
        # Test original v2
        original_start = time.time()
        original_solution = original_vrp.solve_cvrp(method='structural_hybrid', apply_2opt=True)
        original_time = time.time() - original_start
        
        # Test refined v2.1
        refined_start = time.time()
        refined_solution = refined_vrp.solve_cvrp(method='refined_structural', apply_2opt=True)
        refined_time = time.time() - refined_start
        
        # Calculate improvement
        original_dist = original_solution['total_distance']
        refined_dist = refined_solution['total_distance']
        improvement = ((original_dist - refined_dist) / original_dist) * 100
        
        print(f"  Original v2 distance: {original_dist:.2f}")
        print(f"  Refined v2.1 distance: {refined_dist:.2f}")
        print(f"  Improvement: {improvement:+.2f}%")
        print(f"  Original time: {original_time:.4f}s")
        print(f"  Refined time: {refined_time:.4f}s")
        
        benchmark_results[n_customers] = {
            'original_distance': original_dist,
            'refined_distance': refined_dist,
            'improvement_percent': improvement,
            'original_time': original_time,
            'refined_time': refined_time,
            'original_violations': original_solution['has_capacity_violations'],
            'refined_violations': refined_solution['has_capacity_violations']
        }
    
    return benchmark_results

if __name__ == "__main__":
    print("Starting VRP v2.1 Refined Algorithm Test")
    print("=" * 60)
    
    # Test basic functionality
    test_results = test_refined_vrp()
    
    # Run benchmark comparison
    benchmark_results = benchmark_refined_vs_original()
    
    # Save results
    with open('vrp_v2_1_refined_benchmark_results.json', 'w') as f:
        json.dump(benchmark_results, f, indent=2)
    
    print("\n" + "=" * 60)
    print("Benchmark results saved to vrp_v2_1_refined_benchmark_results.json")
    print("=" * 60)
    
    # Summary
    print("\nSUMMARY:")
    total_improvement = 0
    count = 0
    for size, result in benchmark_results.items():
        if result['improvement_percent'] > 0:
            print(f"  {size} customers: +{result['improvement_percent']:.2f}% improvement")
            total_improvement += result['improvement_percent']
        else:
            print(f"  {size} customers: {result['improvement_percent']:.2f}% regression")
        count += 1
    
    if count > 0:
        avg_improvement = total_improvement / count
        print(f"\n  Average improvement: {avg_improvement:+.2f}%")

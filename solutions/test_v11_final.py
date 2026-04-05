#!/usr/bin/env python3
"""
Test the final v11 implementation.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import random
import time
import json
from typing import List, Tuple

# Import both algorithms
from tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected as OriginalV19
from tsp_v19_optimized_fixed_v11_final import ChristofidesHybridStructuralOptimizedV11 as OptimizedV11

def generate_random_points(n: int, seed: int = 42) -> List[Tuple[float, float]]:
    """Generate n random points in [0, 1000] x [0, 1000]."""
    random.seed(seed)
    return [(random.uniform(0, 1000), random.uniform(0, 1000)) for _ in range(n)]

def test_single_case(n: int, seed: int):
    """Test a single case."""
    points = generate_random_points(n, seed)
    
    # Run original v19
    solver_original = OriginalV19(points=points, seed=seed)
    start = time.time()
    tour_original, length_original, _ = solver_original.solve()
    time_original = time.time() - start
    
    # Run optimized v11
    solver_optimized = OptimizedV11(points=points, seed=seed)
    start = time.time()
    tour_optimized, length_optimized, _ = solver_optimized.solve()
    time_optimized = time.time() - start
    
    # Calculate degradation
    degradation = 100 * (length_optimized - length_original) / length_original
    speedup = time_original / time_optimized if time_optimized > 0 else 1.0
    
    return {
        'n': n,
        'seed': seed,
        'length_original': length_original,
        'length_optimized': length_optimized,
        'degradation': degradation,
        'time_original': time_original,
        'time_optimized': time_optimized,
        'speedup': speedup,
        'within_tolerance': abs(degradation) <= 0.1
    }

def main():
    print("Testing final v11 implementation...")
    
    # Test sizes
    test_sizes = [10, 20, 30, 50, 100]
    seeds_per_size = 5
    
    all_results = []
    
    for n in test_sizes:
        print(f"\n=== Testing n={n} ===")
        size_results = []
        
        for seed in range(seeds_per_size):
            result = test_single_case(n, seed)
            size_results.append(result)
            
            status = "✓" if result['within_tolerance'] else "✗"
            print(f"  {status} Seed {seed}: degradation={result['degradation']:.3f}%, speedup={result['speedup']:.2f}x")
        
        # Calculate statistics
        degradations = [r['degradation'] for r in size_results]
        avg_degradation = sum(degradations) / len(degradations)
        max_degradation = max(abs(d) for d in degradations)
        all_within = all(r['within_tolerance'] for r in size_results)
        
        print(f"  Summary: avg degradation={avg_degradation:.3f}%, max={max_degradation:.3f}%, all within 0.1%: {'✓' if all_within else '✗'}")
        
        all_results.extend(size_results)
    
    # Overall statistics
    all_degradations = [r['degradation'] for r in all_results]
    avg_all = sum(all_degradations) / len(all_degradations)
    max_all = max(abs(d) for d in all_degradations)
    within_all = sum(1 for r in all_results if r['within_tolerance'])
    
    print(f"\n=== FINAL SUMMARY ===")
    print(f"Total tests: {len(all_results)}")
    print(f"Average degradation: {avg_all:.3f}%")
    print(f"Maximum degradation: {max_all:.3f}%")
    print(f"Tests within 0.1% tolerance: {within_all}/{len(all_results)} ({100*within_all/len(all_results):.1f}%)")
    
    # Save results
    with open('/workspace/evovera/solutions/v11_final_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    if within_all == len(all_results):
        print("\n✅ SUCCESS: All tests within 0.1% tolerance!")
        return 0
    else:
        print(f"\n❌ FAILURE: {len(all_results) - within_all} tests exceed 0.1% tolerance")
        return 1

if __name__ == "__main__":
    sys.exit(main())

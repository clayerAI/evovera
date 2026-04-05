#!/usr/bin/env python3
"""
Comprehensive quality verification for v11 vs original v19.
Tests quality preservation within ≤0.1% tolerance.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import random
import time
import json
from typing import List, Tuple
import numpy as np

# Import both algorithms
from tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected as OriginalV19
from tsp_v19_optimized_fixed_v11_proper import ChristofidesHybridStructuralOptimizedV11 as OptimizedV11

def generate_random_points(n: int, seed: int = 42) -> List[Tuple[float, float]]:
    """Generate n random points in [0, 1000] x [0, 1000]."""
    random.seed(seed)
    return [(random.uniform(0, 1000), random.uniform(0, 1000)) for _ in range(n)]

def test_quality_comparison(n_values: List[int] = [10, 20, 30, 50, 100], 
                           seeds: List[int] = list(range(10)),  # 10 seeds for statistical significance
                           tolerance_percent: float = 0.1):
    """
    Compare quality between original v19 and optimized v11.
    
    Args:
        n_values: List of problem sizes to test
        seeds: List of random seeds for statistical significance
        tolerance_percent: Maximum allowed quality degradation (%)
    
    Returns:
        Dictionary with comparison results
    """
    results = {}
    all_passed = True
    
    for n in n_values:
        print(f"\n=== Testing n={n} (seeds: {len(seeds)}) ===")
        n_results = []
        degradations = []
        
        for seed_idx, seed in enumerate(seeds):
            points = generate_random_points(n, seed)
            
            # Run original v19
            solver_original = OriginalV19(points=points, seed=seed)
            tour_original, length_original, runtime_original = solver_original.solve()
            
            # Run optimized v11
            solver_optimized = OptimizedV11(points=points, seed=seed)
            tour_optimized, length_optimized, runtime_optimized = solver_optimized.solve()
            
            # Calculate quality degradation
            if length_original > 0:
                degradation_percent = 100 * (length_optimized - length_original) / length_original
            else:
                degradation_percent = 0
            
            # Check if within tolerance
            within_tolerance = abs(degradation_percent) <= tolerance_percent
            
            n_results.append({
                'seed': seed,
                'length_original': length_original,
                'length_optimized': length_optimized,
                'degradation_percent': degradation_percent,
                'within_tolerance': within_tolerance,
                'runtime_original': runtime_original,
                'runtime_optimized': runtime_optimized,
                'speedup': runtime_original / runtime_optimized if runtime_optimized > 0 else 1.0
            })
            
            degradations.append(degradation_percent)
            
            if not within_tolerance:
                all_passed = False
                print(f"  ✗ Seed {seed}: degradation={degradation_percent:.3f}% (exceeds {tolerance_percent}%)")
            elif seed_idx % 5 == 0:  # Print every 5th seed to avoid clutter
                print(f"  ✓ Seed {seed}: degradation={degradation_percent:.3f}%, speedup={runtime_original/runtime_optimized:.2f}x")
        
        # Calculate statistics
        degradations_array = np.array(degradations)
        avg_degradation = np.mean(degradations_array)
        std_degradation = np.std(degradations_array)
        max_degradation = np.max(np.abs(degradations_array))
        
        # Runtime statistics
        speedups = [r['speedup'] for r in n_results]
        avg_speedup = np.mean(speedups)
        
        results[n] = {
            'avg_degradation': avg_degradation,
            'std_degradation': std_degradation,
            'max_degradation': max_degradation,
            'avg_speedup': avg_speedup,
            'all_within_tolerance': all(degradation <= tolerance_percent for degradation in degradations_array),
            'samples': len(seeds),
            'tolerance_percent': tolerance_percent
        }
        
        print(f"  Summary: avg degradation={avg_degradation:.3f}% ± {std_degradation:.3f}%")
        print(f"           max degradation={max_degradation:.3f}% (tolerance: {tolerance_percent}%)")
        print(f"           avg speedup={avg_speedup:.2f}x")
        print(f"           All within tolerance: {'✓' if results[n]['all_within_tolerance'] else '✗'}")
    
    return results, all_passed

def test_tsplib_compatibility():
    """Test TSPLIB compatibility with ATT distance metric."""
    print("\n=== Testing TSPLIB Compatibility ===")
    
    # Create a small distance matrix with ATT metric characteristics
    # ATT metric: ceil(sqrt((dx^2 + dy^2)/10.0))
    n = 10
    points = [(i * 10, i * 10) for i in range(n)]  # Simple diagonal points
    
    # Compute ATT distance matrix
    att_matrix = [[0] * n for _ in range(n)]
    for i in range(n):
        xi, yi = points[i]
        for j in range(n):
            if i != j:
                xj, yj = points[j]
                dx = xi - xj
                dy = yi - yj
                # ATT metric formula
                att_dist = math.ceil(math.sqrt((dx*dx + dy*dy) / 10.0))
                att_matrix[i][j] = att_dist
    
    # Test with distance_matrix parameter
    try:
        solver = OptimizedV11(distance_matrix=att_matrix, seed=42)
        tour, length, runtime = solver.solve()
        print(f"  ✓ TSPLIB compatibility test passed")
        print(f"    Tour length (ATT metric): {length}")
        print(f"    Runtime: {runtime:.3f}s")
        return True
    except Exception as e:
        print(f"  ✗ TSPLIB compatibility test failed: {e}")
        return False

if __name__ == "__main__":
    import math
    
    print("=" * 80)
    print("V11 QUALITY VERIFICATION TEST")
    print("Testing optimized v11 against original v19 with ≤0.1% tolerance")
    print("=" * 80)
    
    # Test TSPLIB compatibility first
    tsplib_ok = test_tsplib_compatibility()
    
    # Test quality preservation
    print("\n" + "=" * 80)
    print("QUALITY PRESERVATION TEST (10 seeds each)")
    print("=" * 80)
    
    results, all_passed = test_quality_comparison(
        n_values=[10, 20, 30, 50, 100],
        seeds=list(range(10)),  # 10 seeds for statistical significance
        tolerance_percent=0.1
    )
    
    # Save results
    with open('/workspace/evovera/solutions/v11_quality_verification_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 80)
    print("FINAL VERIFICATION SUMMARY")
    print("=" * 80)
    
    if tsplib_ok and all_passed:
        print("✅ ALL TESTS PASSED")
        print(f"   - TSPLIB compatibility: ✓")
        print(f"   - Quality preservation (≤0.1%): ✓ across all {len(results)} problem sizes")
        
        # Show worst-case degradation
        worst_n = max(results.items(), key=lambda x: x[1]['max_degradation'])
        print(f"   - Worst case: n={worst_n[0]}, max degradation={worst_n[1]['max_degradation']:.3f}%")
        
        # Show average speedup
        avg_speedup = np.mean([r['avg_speedup'] for r in results.values()])
        print(f"   - Average speedup: {avg_speedup:.2f}x")
        
        print("\n✅ V11 IS READY FOR TSPLIB EVALUATION")
    else:
        print("❌ TESTS FAILED")
        if not tsplib_ok:
            print("   - TSPLIB compatibility: ✗")
        if not all_passed:
            print("   - Quality preservation: ✗ (exceeds 0.1% tolerance)")
        
        print("\n❌ V11 NEEDS FURTHER OPTIMIZATION ADJUSTMENTS")

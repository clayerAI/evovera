#!/usr/bin/env python3
"""
Verify v19 optimized v9 algorithm produces identical results to original v19
on TSPLIB instances eil51 and kroA100.
"""

import sys
import os
import numpy as np
import time
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import algorithms
from solutions.tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected as OriginalV19
from solutions.tsp_v19_optimized_fixed_v9 import ChristofidesHybridStructuralOptimizedV8 as OptimizedV9

def load_tsplib_instance(instance_name):
    """Load TSPLIB instance using existing parser."""
    from tsplib_parser import TSPLIBParser
    
    # Find the instance file
    instance_dir = "/workspace/evovera/tsplib_instances"
    instance_path = os.path.join(instance_dir, f"{instance_name}.tsp")
    
    if not os.path.exists(instance_path):
        # Try to download it
        print(f"Downloading {instance_name}...")
        from download_tsplib_instances import download_tsplib_instance
        download_tsplib_instance(instance_name)
    
    # Parse the instance
    parser = TSPLIBParser(instance_path)
    points = parser.get_points()
    distance_matrix = parser.get_distance_matrix()
    
    return points, distance_matrix, parser.edge_weight_type

def test_instance(instance_name, num_seeds=5):
    """Test an instance with both algorithms."""
    print(f"\n{'='*60}")
    print(f"Testing {instance_name}")
    print(f"{'='*60}")
    
    # Load instance
    points, distance_matrix, weight_type = load_tsplib_instance(instance_name)
    n = len(points)
    
    print(f"Instance: {instance_name} (n={n}, weight_type={weight_type})")
    
    results_original = []
    results_optimized = []
    times_original = []
    times_optimized = []
    
    for seed in range(num_seeds):
        np.random.seed(seed)
        
        # Test original v19
        start_time = time.time()
        if weight_type in ["EUC_2D", "ATT"]:
            solver_original = OriginalV19(distance_matrix=distance_matrix, seed=seed)
        else:
            solver_original = OriginalV19(points=points, seed=seed)
        tour_original, length_original, _ = solver_original.solve()
        time_original = time.time() - start_time
        
        # Test optimized v9
        start_time = time.time()
        if weight_type in ["EUC_2D", "ATT"]:
            solver_optimized = OptimizedV9(distance_matrix=distance_matrix)
        else:
            solver_optimized = OptimizedV9(points=points)
        tour_optimized, length_optimized, time_optimized_val = solver_optimized.solve()
        time_optimized = time.time() - start_time
        
        results_original.append(length_original)
        results_optimized.append(length_optimized)
        times_original.append(time_original)
        times_optimized.append(time_optimized)
        
        print(f"  Seed {seed}: Original={length_original:.2f}, Optimized={length_optimized:.2f}, "
              f"Diff={abs(length_original - length_optimized):.6f}")
    
    # Calculate statistics
    mean_original = np.mean(results_original)
    mean_optimized = np.mean(results_optimized)
    diff_pct = abs(mean_original - mean_optimized) / mean_original * 100
    
    mean_time_original = np.mean(times_original)
    mean_time_optimized = np.mean(times_optimized)
    speedup = mean_time_original / mean_time_optimized if mean_time_optimized > 0 else 0
    
    print(f"\nSummary for {instance_name}:")
    print(f"  Mean tour length - Original: {mean_original:.2f}")
    print(f"  Mean tour length - Optimized: {mean_optimized:.2f}")
    print(f"  Difference: {diff_pct:.6f}%")
    print(f"  Mean time - Original: {mean_time_original:.3f}s")
    print(f"  Mean time - Optimized: {mean_time_optimized:.3f}s")
    print(f"  Speedup: {speedup:.2f}x")
    
    # Check if results are identical (within 0.0001% tolerance)
    if diff_pct < 0.0001:
        print(f"✅ PASS: Results identical within {diff_pct:.6f}% tolerance")
        return True, diff_pct, speedup
    else:
        print(f"❌ FAIL: Results differ by {diff_pct:.6f}% (≥ 0.0001%)")
        return False, diff_pct, speedup

def main():
    """Run verification tests."""
    print("v19 Optimized v9 Regression Verification")
    print("Verifying identical results on TSPLIB instances")
    print("=" * 80)
    
    instances = ["eil51", "kroA100"]
    all_passed = True
    results = {}
    
    for instance in instances:
        passed, diff_pct, speedup = test_instance(instance, num_seeds=3)
        results[instance] = {
            "passed": passed,
            "difference_percent": diff_pct,
            "speedup": speedup
        }
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY:")
    for instance, result in results.items():
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(f"{instance}: {status} (diff={result['difference_percent']:.6f}%, speedup={result['speedup']:.2f}x)")
    
    if all_passed:
        print("\n✅ ALL VERIFICATIONS PASSED: Optimized v9 produces identical results to original v19")
    else:
        print("\n❌ SOME VERIFICATIONS FAILED: Check algorithm differences")
    
    # Save results
    with open("/workspace/evovera/v9_regression_verification.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

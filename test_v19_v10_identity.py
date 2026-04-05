#!/usr/bin/env python3
"""
Test if optimized v10 produces identical results to original v19.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from solutions.tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected
from solutions.tsp_v19_optimized_fixed_v10 import ChristofidesHybridStructuralOptimized
import random

def generate_random_points(n=20, seed=42):
    """Generate random points for testing."""
    random.seed(seed)
    return [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(n)]

def test_identity():
    """Test that v10 produces identical results to original v19."""
    print("Testing v10 vs original v19 identity...")
    
    # Test with different sizes
    test_cases = [
        (10, 1),
        (20, 2),
        (30, 3),
        (50, 4),
    ]
    
    all_pass = True
    
    for n, seed in test_cases:
        print(f"\nTesting n={n}, seed={seed}")
        points = generate_random_points(n, seed)
        
        # Original v19
        solver1 = ChristofidesHybridStructuralCorrected(points, seed=seed)
        tour1, length1, _ = solver1.solve()
        
        # Optimized v10
        solver2 = ChristofidesHybridStructuralOptimized(points, seed=seed)
        tour2, length2, _ = solver2.solve()
        
        # Compare
        diff = abs(length1 - length2)
        diff_pct = (diff / length1) * 100 if length1 > 0 else 0
        
        print(f"  Original v19: {length1:.2f}")
        print(f"  Optimized v10: {length2:.2f}")
        print(f"  Difference: {diff:.6f} ({diff_pct:.6f}%)")
        
        if diff_pct < 0.0001:  # Within 0.0001%
            print(f"  ✅ PASS: Identical within tolerance")
        else:
            print(f"  ❌ FAIL: Not identical")
            all_pass = False
    
    return all_pass

if __name__ == "__main__":
    success = test_identity()
    if success:
        print("\n✅ All tests passed: v10 produces identical results to original v19")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed: v10 does not produce identical results")
        sys.exit(1)

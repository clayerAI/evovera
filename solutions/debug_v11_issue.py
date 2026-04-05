#!/usr/bin/env python3
"""
Debug the quality degradation issue in v11.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import random
from typing import List, Tuple

# Import both algorithms
from tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected as OriginalV19
from tsp_v19_optimized_fixed_v11 import ChristofidesHybridStructuralOptimizedV11 as OptimizedV11

def generate_random_points(n: int, seed: int = 42) -> List[Tuple[float, float]]:
    """Generate n random points in [0, 1000] x [0, 1000]."""
    random.seed(seed)
    return [(random.uniform(0, 1000), random.uniform(0, 1000)) for _ in range(n)]

def debug_single_case(n: int = 10, seed: int = 0):
    """Debug a single case to understand the issue."""
    print(f"\n=== Debugging n={n}, seed={seed} ===")
    points = generate_random_points(n, seed)
    
    # Run original v19
    solver_original = OriginalV19(points=points, seed=seed)
    tour_original, length_original, runtime_original = solver_original.solve()
    
    print(f"Original v19:")
    print(f"  Tour: {tour_original}")
    print(f"  Length: {length_original:.2f}")
    print(f"  Runtime: {runtime_original:.3f}s")
    
    # Run optimized v11
    solver_optimized = OptimizedV11(points=points, seed=seed)
    tour_optimized, length_optimized, runtime_optimized = solver_optimized.solve()
    
    print(f"\nOptimized v11:")
    print(f"  Tour: {tour_optimized}")
    print(f"  Length: {length_optimized:.2f}")
    print(f"  Runtime: {runtime_optimized:.3f}s")
    
    # Calculate degradation
    degradation = 100 * (length_optimized - length_original) / length_original
    print(f"\nDegradation: {degradation:.3f}%")
    
    # Check if tours are the same
    if tour_original == tour_optimized:
        print("Tours are IDENTICAL")
    else:
        print("Tours are DIFFERENT")
        
        # Check if they visit same vertices (ignoring start/end)
        set_original = set(tour_original[:-1])
        set_optimized = set(tour_optimized[:-1])
        if set_original == set_optimized:
            print("But they visit the same vertices (different order)")
        else:
            print("They visit DIFFERENT vertices!")
            print(f"Original vertices missing in optimized: {set_original - set_optimized}")
            print(f"Optimized vertices missing in original: {set_optimized - set_original}")

if __name__ == "__main__":
    # Debug worst case from previous test (n=30, seed=6, 21.6% degradation)
    debug_single_case(n=30, seed=6)
    
    # Also debug a small case
    debug_single_case(n=10, seed=0)

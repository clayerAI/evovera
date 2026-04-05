#!/usr/bin/env python3
"""
Debug MST construction in v11 vs original v19.
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

def debug_mst(n: int = 10, seed: int = 0):
    """Debug MST construction."""
    print(f"\n=== Debugging MST for n={n}, seed={seed} ===")
    points = generate_random_points(n, seed)
    
    # Run original v19
    solver_original = OriginalV19(points=points, seed=seed)
    
    # We need to access internal methods - let's check if we can
    # First, let's manually compute MST for both
    from scipy.sparse.csgraph import minimum_spanning_tree
    from scipy.sparse import csr_matrix
    import numpy as np
    
    # Compute distance matrix
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                dx = points[i][0] - points[j][0]
                dy = points[i][1] - points[j][1]
                dist_matrix[i][j] = np.sqrt(dx*dx + dy*dy)
    
    # Compute MST using scipy
    mst = minimum_spanning_tree(csr_matrix(dist_matrix))
    mst_edges = []
    for i in range(n):
        for j in range(i+1, n):
            if mst[i, j] > 0 or mst[j, i] > 0:
                mst_edges.append((i, j))
    
    print(f"SciPy MST edges ({len(mst_edges)}): {sorted(mst_edges)}")
    
    # Now let's check what each algorithm produces
    # We'll need to modify the algorithms to expose MST
    print("\nChecking algorithm MSTs...")
    
    # For original v19, let's trace through the code
    print("\nOriginal v19 MST (from _build_mst method):")
    # We'll need to run the algorithm and extract MST
    
    # For now, let's check if the issue is in community detection
    print("\nChecking community detection...")
    
    # Create a simple test to see if communities are different
    solver_original = OriginalV19(points=points, seed=seed)
    solver_optimized = OptimizedV11(points=points, seed=seed)
    
    # Run both to completion
    tour_orig, len_orig, _ = solver_original.solve()
    tour_opt, len_opt, _ = solver_optimized.solve()
    
    print(f"Original length: {len_orig:.2f}")
    print(f"Optimized length: {len_opt:.2f}")
    print(f"Difference: {len_opt - len_orig:.2f} ({100*(len_opt - len_orig)/len_orig:.2f}%)")

if __name__ == "__main__":
    debug_mst(n=10, seed=0)

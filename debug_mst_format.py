#!/usr/bin/env python3
"""
Check MST edge format.
"""

import sys
import random
sys.path.append('.')

def main():
    n = 10  # Smaller for debugging
    random.seed(42)
    points = [(random.random() * 100, random.random() * 100) for _ in range(n)]
    
    print("=== MST EDGE FORMAT CHECK ===\n")
    
    # Get MST from original
    from solutions.tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected
    solver_orig = ChristofidesHybridStructuralCorrected(points=points, seed=42)
    mst_adj_orig, mst_edges_orig = solver_orig._compute_mst()
    
    print(f"Original MST edges type: {type(mst_edges_orig)}")
    print(f"Original MST edges length: {len(mst_edges_orig)}")
    if len(mst_edges_orig) > 0:
        print(f"First edge: {mst_edges_orig[0]}, type: {type(mst_edges_orig[0])}")
        if hasattr(mst_edges_orig[0], '__len__'):
            print(f"  Is iterable: True, length: {len(mst_edges_orig[0])}")
        else:
            print(f"  Is iterable: False")
    
    # Get MST from optimized
    from solutions.tsp_v19_optimized_fixed_v2 import ChristofidesHybridStructuralOptimized
    solver_opt = ChristofidesHybridStructuralOptimized(points=points, seed=42)
    mst_adj_opt, mst_edges_opt = solver_opt._compute_mst()
    
    print(f"\nOptimized MST edges type: {type(mst_edges_opt)}")
    print(f"Optimized MST edges length: {len(mst_edges_opt)}")
    if len(mst_edges_opt) > 0:
        print(f"First edge: {mst_edges_opt[0]}, type: {type(mst_edges_opt[0])}")
        if hasattr(mst_edges_opt[0], '__len__'):
            print(f"  Is iterable: True, length: {len(mst_edges_opt[0])}")
        else:
            print(f"  Is iterable: False")
    
    # Let's look at the actual _compute_mst method
    print("\n=== CHECKING _compute_mst METHOD ===")
    
    # Check original implementation
    import inspect
    source_orig = inspect.getsource(solver_orig._compute_mst)
    print(f"Original _compute_mst signature found: {'def _compute_mst' in source_orig}")
    
    # Quick check: does it return (mst_adj, mst_edges) where mst_edges is list of tuples?
    print("\nManually checking return values...")
    print(f"mst_adj_orig is list: {isinstance(mst_adj_orig, list)}")
    print(f"mst_adj_orig length: {len(mst_adj_orig)}")
    print(f"mst_adj_orig[0] type: {type(mst_adj_orig[0])}")
    
    print(f"\nmst_edges_orig sample: {mst_edges_orig[:3] if len(mst_edges_orig) >= 3 else mst_edges_orig}")
    
    # Actually, let me just print everything
    print(f"\n=== FULL MST EDGES ===")
    print(f"Original: {mst_edges_orig}")
    print(f"Optimized: {mst_edges_opt}")
    
    # Check if they're the same
    if mst_edges_orig == mst_edges_opt:
        print("\nMST edges are identical!")
    else:
        print("\nMST edges differ!")

if __name__ == "__main__":
    main()

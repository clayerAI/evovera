#!/usr/bin/env python3
"""
Check if MST is the same between original and optimized.
"""

import sys
import random
sys.path.append('.')

def main():
    n = 20
    random.seed(42)
    points = [(random.random() * 100, random.random() * 100) for _ in range(n)]
    
    print("=== MST COMPARISON ===\n")
    
    # Get MST from original
    from solutions.tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected
    solver_orig = ChristofidesHybridStructuralCorrected(points=points, seed=42)
    mst_adj_orig, mst_edges_orig = solver_orig._compute_mst()
    
    # Get MST from optimized
    from solutions.tsp_v19_optimized_fixed_v2 import ChristofidesHybridStructuralOptimized
    solver_opt = ChristofidesHybridStructuralOptimized(points=points, seed=42)
    mst_adj_opt, mst_edges_opt = solver_opt._compute_mst()
    
    print(f"Number of MST edges (should be n-1={n-1}):")
    print(f"  Original: {len(mst_edges_orig)}")
    print(f"  Optimized: {len(mst_edges_opt)}")
    
    # Convert edges to sorted tuples for comparison
    mst_set_orig = set(tuple(sorted(e)) for e in mst_edges_orig)
    mst_set_opt = set(tuple(sorted(e)) for e in mst_edges_opt)
    
    print(f"\nMST edges same: {mst_set_orig == mst_set_opt}")
    
    if mst_set_orig != mst_set_opt:
        print(f"\nEdges only in original: {mst_set_orig - mst_set_opt}")
        print(f"Edges only in optimized: {mst_set_opt - mst_set_orig}")
        
        # Check if MST weights are the same
        print("\n=== MST WEIGHT COMPARISON ===")
        # We need to compute MST weight
        from solutions.tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected
        solver = ChristofidesHybridStructuralCorrected(points=points, seed=42)
        
        # Compute distance matrix
        import math
        n = len(points)
        dist_matrix = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                dx = points[i][0] - points[j][0]
                dy = points[i][1] - points[j][1]
                dist = math.sqrt(dx * dx + dy * dy)
                dist_matrix[i][j] = dist
                dist_matrix[j][i] = dist
        
        # Compute weight of each MST
        def mst_weight(edges):
            total = 0.0
            for u, v in edges:
                total += dist_matrix[u][v]
            return total
        
        weight_orig = mst_weight(mst_edges_orig)
        weight_opt = mst_weight(mst_edges_opt)
        
        print(f"MST weight original: {weight_orig:.4f}")
        print(f"MST weight optimized: {weight_opt:.4f}")
        print(f"Difference: {abs(weight_orig - weight_opt):.4f}")
        
        if abs(weight_orig - weight_opt) > 0.001:
            print("WARNING: Different MST weights! The MST algorithm might be different.")
        else:
            print("Same MST weight - graph has multiple MSTs (tie-breaking differences).")
    
    # Check adjacency representation
    print(f"\n=== ADJACENCY COMPARISON ===")
    print("Checking if adjacency lists are equivalent...")
    
    # Convert to sorted neighbor lists
    adj_dict_orig = {}
    for u in range(n):
        neighbors = sorted(mst_adj_orig[u])
        adj_dict_orig[u] = neighbors
    
    adj_dict_opt = {}
    for u in range(n):
        neighbors = sorted(mst_adj_opt[u])
        adj_dict_opt[u] = neighbors
    
    same_adj = all(adj_dict_orig[u] == adj_dict_opt[u] for u in range(n))
    print(f"Adjacency lists same: {same_adj}")
    
    if not same_adj:
        print("\nDifferences in adjacency:")
        for u in range(n):
            if adj_dict_orig[u] != adj_dict_opt[u]:
                print(f"  Vertex {u}: orig={adj_dict_orig[u]}, opt={adj_dict_opt[u]}")

if __name__ == "__main__":
    main()

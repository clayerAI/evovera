#!/usr/bin/env python3
"""
Compare path centrality computations.
"""

import sys
import random
sys.path.append('.')

def main():
    n = 10
    random.seed(42)
    points = [(random.random() * 100, random.random() * 100) for _ in range(n)]
    
    print("=== COMPARING PATH CENTRALITY ===\n")
    
    # Run original algorithm and capture intermediate values
    from solutions.tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected
    
    # Create subclass that exposes internal state
    class DebugOriginal(ChristofidesHybridStructuralCorrected):
        def solve_with_debug(self, percentile_threshold=70.0):
            n = self.n
            
            # 1. Compute MST
            mst_adj, _ = self._compute_mst()
            
            # 2. Build MST paths
            mst_paths = self._build_mst_paths(mst_adj)
            
            # 3. Compute edge centrality
            edge_centrality = self._compute_edge_centrality(mst_adj)
            
            # 4. Compute path centrality
            path_centrality = self._compute_path_centrality(mst_paths, edge_centrality)
            
            # Return for debugging
            return mst_adj, mst_paths, edge_centrality, path_centrality
    
    solver = DebugOriginal(points=points, seed=42)
    mst_adj, mst_paths, edge_centrality, path_centrality_orig = solver.solve_with_debug()
    
    print(f"Original computed path centrality for {len(path_centrality_orig)} pairs")
    
    # Sample some values
    print("\nSample path centrality values (original):")
    pairs = list(path_centrality_orig.keys())[:10]
    for (u, v) in pairs:
        print(f"  ({u},{v}): {path_centrality_orig[(u, v)]:.6f}")
    
    # Now compute using optimized lazy method
    print("\n=== COMPUTING WITH OPTIMIZED LAZY METHOD ===")
    
    from solutions.tsp_v19_optimized_fixed_v3 import ChristofidesHybridStructuralOptimized
    solver_opt = ChristofidesHybridStructuralOptimized(points=points, seed=42)
    
    # We need to build the MST and LCA structure
    mst_adj_opt, parent = solver_opt._compute_mst()
    solver_opt._build_lca_structure(parent)
    edge_centrality_opt = solver_opt._compute_edge_centrality(mst_adj_opt)
    
    # Compare for the same pairs
    print("\nComparison for same pairs:")
    for (u, v) in pairs:
        # Original
        orig = path_centrality_orig.get((u, v), 0.0)
        
        # Optimized lazy
        opt = solver_opt._compute_path_centrality_lazy(u, v, edge_centrality_opt)
        
        diff = abs(orig - opt)
        print(f"  ({u},{v}): orig={orig:.6f}, opt={opt:.6f}, diff={diff:.6f} {'✅' if diff < 1e-10 else '❌'}")
    
    # Check if MSTs are identical
    print("\n=== MST COMPARISON ===")
    
    # Convert MST adjacency to edge sets for comparison
    edges_orig = set()
    for u in range(n):
        for v, _ in mst_adj[u]:
            if u < v:
                edges_orig.add((u, v))
    
    edges_opt = set()
    for u in range(n):
        for v, _ in mst_adj_opt[u]:
            if u < v:
                edges_opt.add((u, v))
    
    print(f"Original MST edges: {sorted(edges_orig)}")
    print(f"Optimized MST edges: {sorted(edges_opt)}")
    print(f"MSTs identical: {edges_orig == edges_opt}")
    
    if edges_orig != edges_opt:
        print(f"Difference: {edges_orig.symmetric_difference(edges_opt)}")

if __name__ == "__main__":
    main()

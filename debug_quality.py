#!/usr/bin/env python3
"""
Debug quality difference between original and optimized algorithms.
"""

import sys
import os
sys.path.append('.')

import random
import time
from solutions.tsp_v19_optimized_fixed import ChristofidesHybridStructuralOptimized
from solutions.tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected

def generate_random_points(n: int, seed: int = 42):
    """Generate n random points in unit square."""
    random.seed(seed)
    points = []
    for _ in range(n):
        x = random.random() * 100
        y = random.random() * 100
        points.append((x, y))
    return points

def debug_n_50():
    """Debug quality difference for n=50."""
    print("=== Debugging n=50 ===")
    points = generate_random_points(50, seed=50)
    
    # Original algorithm
    print("\nOriginal algorithm:")
    solver1 = ChristofidesHybridStructuralCorrected(points=points, seed=50)
    
    # Get internal state
    mst_adj1, _ = solver1._compute_mst()
    edge_centrality1 = solver1._compute_edge_centrality(mst_adj1)
    communities1 = solver1._detect_communities(mst_adj1)
    odd_vertices1 = solver1._find_odd_degree_vertices(mst_adj1)
    
    print(f"  MST edges: {sum(len(adj) for adj in mst_adj1)//2}")
    print(f"  Edge centrality computed: {len(edge_centrality1)} edges")
    print(f"  Communities: {len(set(communities1.values()))}")
    print(f"  Odd vertices: {len(odd_vertices1)}")
    
    # Optimized algorithm
    print("\nOptimized algorithm:")
    solver2 = ChristofidesHybridStructuralOptimized(points=points, seed=50)
    
    mst_adj2, _ = solver2._compute_mst()
    edge_centrality2 = solver2._compute_edge_centrality_optimized(mst_adj2)
    communities2 = solver2._detect_communities(mst_adj2)
    odd_vertices2 = solver2._find_odd_degree_vertices(mst_adj2)
    
    print(f"  MST edges: {sum(len(adj) for adj in mst_adj2)//2}")
    print(f"  Edge centrality computed: {len(edge_centrality2)} edges")
    print(f"  Communities: {len(set(communities2.values()))}")
    print(f"  Odd vertices: {len(odd_vertices2)}")
    
    # Compare edge centrality values
    print("\nComparing edge centrality:")
    common_edges = set(edge_centrality1.keys()) & set(edge_centrality2.keys())
    print(f"  Common edges: {len(common_edges)}")
    
    if common_edges:
        differences = []
        for edge in list(common_edges)[:5]:  # Sample first 5
            diff = abs(edge_centrality1[edge] - edge_centrality2.get(edge, 0))
            differences.append(diff)
            print(f"  Edge {edge}: original={edge_centrality1[edge]:.4f}, optimized={edge_centrality2.get(edge, 0):.4f}, diff={diff:.4f}")
        
        avg_diff = sum(differences) / len(differences) if differences else 0
        print(f"  Average difference: {avg_diff:.4f}")
    
    # Compare communities
    print("\nComparing communities:")
    same_community_count = 0
    for i in range(50):
        if communities1.get(i, -1) == communities2.get(i, -1):
            same_community_count += 1
    
    print(f"  Vertices with same community: {same_community_count}/50 ({same_community_count/50*100:.1f}%)")

def test_with_fixed_seed():
    """Test with fixed seed to ensure reproducibility."""
    print("\n=== Testing with Fixed Seed ===")
    
    for n in [20, 30, 40]:
        print(f"\nn={n}:")
        points = generate_random_points(n, seed=123)
        
        # Run both algorithms 5 times
        lengths1 = []
        lengths2 = []
        
        for seed in range(5):
            # Original
            solver1 = ChristofidesHybridStructuralCorrected(points=points, seed=seed)
            tour1, length1 = solver1.solve()
            lengths1.append(length1)
            
            # Optimized
            solver2 = ChristofidesHybridStructuralOptimized(points=points, seed=seed)
            tour2, length2 = solver2.solve()
            lengths2.append(length2)
        
        avg1 = sum(lengths1) / len(lengths1)
        avg2 = sum(lengths2) / len(lengths2)
        diff_pct = (avg2 - avg1) / avg1 * 100
        
        print(f"  Original avg: {avg1:.2f}")
        print(f"  Optimized avg: {avg2:.2f}")
        print(f"  Difference: {diff_pct:.1f}%")
        
        # Check if difference is consistent
        std1 = (sum((l - avg1)**2 for l in lengths1) / len(lengths1))**0.5
        std2 = (sum((l - avg2)**2 for l in lengths2) / len(lengths2))**0.5
        print(f"  Std dev: original={std1:.2f}, optimized={std2:.2f}")

if __name__ == "__main__":
    debug_n_50()
    test_with_fixed_seed()

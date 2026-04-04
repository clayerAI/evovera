#!/usr/bin/env python3
"""
Analyze why v14 Christofides Adaptive Matching performs poorly.
"""

import sys
import os
sys.path.append('/workspace/evovera/solutions')

from tsp_v14_christofides_adaptive_matching import ChristofidesAdaptiveMatching
# Import Christofides with proper handling
import sys
import os
sys.path.append('/workspace/evovera/solutions')

# Define a wrapper for Christofides
def christofides_solve(points):
    """Wrapper for Christofides algorithm."""
    from tsp_v2_christofides import solve_tsp
    # Convert points to numpy array if needed
    import numpy as np
    points_array = np.array(points)
    return solve_tsp(points_array)
from tsp_v1_nearest_neighbor import solve_tsp as nn_2opt_solve

import random
import math
import numpy as np
from typing import List, Tuple

def generate_random_points(n: int = 50, seed: int = 42) -> List[Tuple[float, float]]:
    """Generate random points in unit square."""
    random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

def analyze_matching_decisions(points: List[Tuple[float, float]], centrality_weight: float = 0.3):
    """Analyze matching decisions made by v14 vs standard Christofides."""
    solver = ChristofidesAdaptiveMatching(points, seed=42)
    
    # 1. Compute MST
    mst_adj = solver._compute_mst()
    
    # 2. Compute edge centrality
    edge_centrality = solver._compute_edge_centrality(mst_adj)
    
    # 3. Find odd degree vertices
    odd_vertices = solver._find_odd_degree_vertices(mst_adj)
    
    print(f"Number of odd vertices: {len(odd_vertices)}")
    
    # Analyze edges that would be selected by different strategies
    m = len(odd_vertices)
    edges_info = []
    
    for i in range(m):
        u = odd_vertices[i]
        for j in range(i + 1, m):
            v = odd_vertices[j]
            distance = solver.dist_matrix[u][v]
            
            # Get centrality score
            edge_key = (min(u, v), max(u, v))
            centrality = edge_centrality.get(edge_key, 0.0)
            
            # Adaptive score
            adaptive_score = distance * (1.0 - centrality_weight * centrality)
            
            edges_info.append({
                'u': u, 'v': v,
                'distance': distance,
                'centrality': centrality,
                'adaptive_score': adaptive_score,
                'pure_greedy_score': distance  # For standard Christofides
            })
    
    # Sort by different criteria
    edges_by_distance = sorted(edges_info, key=lambda x: x['distance'])
    edges_by_adaptive = sorted(edges_info, key=lambda x: x['adaptive_score'])
    
    print("\n=== Top 10 edges by distance (standard Christofides would choose these):")
    for i, edge in enumerate(edges_by_distance[:10]):
        print(f"  {i+1}. ({edge['u']}, {edge['v']}): dist={edge['distance']:.4f}, "
              f"cent={edge['centrality']:.4f}, adapt_score={edge['adaptive_score']:.4f}")
    
    print("\n=== Top 10 edges by adaptive score (v14 would choose these):")
    for i, edge in enumerate(edges_by_adaptive[:10]):
        print(f"  {i+1}. ({edge['u']}, {edge['v']}): dist={edge['distance']:.4f}, "
              f"cent={edge['centrality']:.4f}, adapt_score={edge['adaptive_score']:.4f}")
    
    # Compare the selections
    print("\n=== Comparison of selections:")
    standard_edges = edges_by_distance[:len(odd_vertices)//2]  # Rough estimate
    adaptive_edges = edges_by_adaptive[:len(odd_vertices)//2]
    
    standard_avg_dist = sum(e['distance'] for e in standard_edges) / len(standard_edges)
    adaptive_avg_dist = sum(e['distance'] for e in adaptive_edges) / len(adaptive_edges)
    
    print(f"Standard Christofides average edge distance: {standard_avg_dist:.4f}")
    print(f"v14 Adaptive average edge distance: {adaptive_avg_dist:.4f}")
    print(f"Difference: {adaptive_avg_dist - standard_avg_dist:.4f} "
          f"({(adaptive_avg_dist/standard_avg_dist - 1)*100:.2f}% worse)")
    
    return edges_info, edges_by_distance, edges_by_adaptive

def test_different_centrality_weights(points: List[Tuple[float, float]]):
    """Test how different centrality weights affect performance."""
    print("\n=== Testing different centrality weights ===")
    
    for weight in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        solver = ChristofidesAdaptiveMatching(points, seed=42)
        tour, length, runtime = solver.solve(centrality_weight=weight, apply_2opt=True)
        
        # Get baseline
        baseline_tour, baseline_length = nn_2opt_solve(points)
        
        improvement = (baseline_length - length) / baseline_length * 100
        
        print(f"Weight {weight:.1f}: length={length:.4f}, "
              f"baseline={baseline_length:.4f}, improvement={improvement:.2f}%")

def main():
    print("Analyzing v14 Christofides Adaptive Matching failure...")
    
    # Generate test points
    points = generate_random_points(n=30, seed=42)  # Smaller for faster analysis
    
    # Analyze matching decisions
    edges_info, edges_by_distance, edges_by_adaptive = analyze_matching_decisions(points, centrality_weight=0.3)
    
    # Test different centrality weights
    test_different_centrality_weights(points)
    
    # Run full algorithms for comparison
    print("\n=== Full algorithm comparison (n=30) ===")
    
    # v14
    solver = ChristofidesAdaptiveMatching(points, seed=42)
    v14_tour, v14_length, v14_runtime = solver.solve(centrality_weight=0.3, apply_2opt=True)
    
    # Standard Christofides
    christofides_tour, christofides_length = christofides_solve(points)
    
    # Baseline
    baseline_tour, baseline_length = nn_2opt_solve(points)
    
    print(f"Baseline (NN+2opt): {baseline_length:.4f}")
    print(f"Standard Christofides: {christofides_length:.4f} "
          f"({(baseline_length - christofides_length)/baseline_length*100:.2f}% vs baseline)")
    print(f"v14 Adaptive: {v14_length:.4f} "
          f"({(baseline_length - v14_length)/baseline_length*100:.2f}% vs baseline)")
    print(f"v14 vs Standard Christofides: "
          f"{(christofides_length - v14_length)/christofides_length*100:.2f}%")

if __name__ == "__main__":
    main()
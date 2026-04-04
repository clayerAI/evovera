#!/usr/bin/env python3
"""
Test how wrong distance metric affects algorithm decisions.
"""

import numpy as np
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tsplib_parser import TSPLIBParser
from solutions.tsp_v1_nearest_neighbor import solve_tsp as nn_2opt_solve

def test_algorithm_with_wrong_metric():
    """Test algorithm using wrong distance metric."""
    
    # Load att532 instance
    filepath = "data/tsplib/att532.tsp"
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return
    
    parser = TSPLIBParser(filepath)
    if not parser.parse():
        print("❌ Failed to parse att532")
        return
    
    print("=" * 80)
    print("ALGORITHM DISTANCE METRIC IMPACT TEST")
    print("=" * 80)
    
    # Get points and correct distance matrix
    points = parser.get_points_array()
    correct_dist_matrix = parser.get_distance_matrix()
    
    # Run algorithm (uses Euclidean distance internally)
    print("\n🔧 Running NN+2opt algorithm (uses Euclidean distance internally)...")
    tour, reported_length = nn_2opt_solve(points)
    
    # Calculate actual length using correct ATT distances
    actual_length = 0.0
    n = len(tour)
    for i in range(n):
        j = (i + 1) % n
        actual_length += correct_dist_matrix[tour[i], tour[j]]
    
    print(f"\nAlgorithm results:")
    print(f"  Tour length reported by algorithm: {reported_length:.2f}")
    print(f"  Actual tour length (using ATT distances): {actual_length:.2f}")
    print(f"  Difference: {actual_length - reported_length:.2f}")
    
    # Calculate gap
    optimal = parser.optimal_value
    if optimal:
        reported_gap = ((reported_length - optimal) / optimal) * 100
        actual_gap = ((actual_length - optimal) / optimal) * 100
        
        print(f"\nGap calculations:")
        print(f"  Optimal: {optimal}")
        print(f"  Reported gap (wrong): {reported_gap:.2f}%")
        print(f"  Actual gap (correct): {actual_gap:.2f}%")
        print(f"  Error in gap: {abs(actual_gap - reported_gap):.2f}%")
    
    # Test individual edge calculations
    print(f"\n🔍 Testing edge distance calculations:")
    print(f"  First 5 edges in tour:")
    
    for i in range(min(5, n)):
        from_node = tour[i]
        to_node = tour[(i + 1) % n]
        
        # What algorithm thinks (Euclidean)
        p1 = points[from_node]
        p2 = points[to_node]
        algo_dist = np.linalg.norm(p1 - p2)
        
        # Actual (ATT)
        actual_dist = correct_dist_matrix[from_node, to_node]
        
        print(f"  Edge {from_node}→{to_node}:")
        print(f"    Algorithm thinks: {algo_dist:.2f}")
        print(f"    Actually is: {actual_dist:.2f}")
        print(f"    Error: {abs(algo_dist - actual_dist):.2f} ({abs(algo_dist - actual_dist)/actual_dist*100:.1f}%)")
    
    # Test what happens with a simple nearest neighbor decision
    print(f"\n🎯 Testing nearest neighbor decision impact:")
    
    # Pick a random starting node
    start_node = 0
    
    # Find nearest using Euclidean (what algorithm does)
    euclidean_dists = []
    for j in range(1, min(100, len(points))):  # Check first 100 nodes
        if j == start_node:
            continue
        p1 = points[start_node]
        p2 = points[j]
        dist = np.linalg.norm(p1 - p2)
        euclidean_dists.append((j, dist))
    
    euclidean_dists.sort(key=lambda x: x[1])
    euclidean_nearest = euclidean_dists[0]
    
    # Find nearest using ATT (correct)
    att_dists = []
    for j in range(1, min(100, len(points))):
        if j == start_node:
            continue
        dist = correct_dist_matrix[start_node, j]
        att_dists.append((j, dist))
    
    att_dists.sort(key=lambda x: x[1])
    att_nearest = att_dists[0]
    
    print(f"  Starting from node {start_node}:")
    print(f"  Euclidean nearest: Node {euclidean_nearest[0]} (distance: {euclidean_nearest[1]:.2f})")
    print(f"  ATT nearest: Node {att_nearest[0]} (distance: {att_nearest[1]:.2f})")
    
    if euclidean_nearest[0] != att_nearest[0]:
        print(f"  🚨 ALGORITHM CHOOSES WRONG NODE!")
        print(f"  Would choose node {euclidean_nearest[0]} but should choose node {att_nearest[0]}")
        
        # Calculate impact
        euclidean_edge_actual = correct_dist_matrix[start_node, euclidean_nearest[0]]
        att_edge_actual = correct_dist_matrix[start_node, att_nearest[0]]
        
        print(f"  Actual ATT distance to chosen node: {euclidean_edge_actual:.2f}")
        print(f"  Actual ATT distance to correct node: {att_edge_actual:.2f}")
        print(f"  Extra cost per edge: {euclidean_edge_actual - att_edge_actual:.2f}")
    else:
        print(f"  ✓ Same nearest node (coincidence)")
    
    return True

if __name__ == "__main__":
    test_algorithm_with_wrong_metric()
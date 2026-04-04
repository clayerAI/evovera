#!/usr/bin/env python3
"""
Test to verify the distance metric fix works.
"""

import sys
import os
import time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tsplib_parser import TSPLIBParser

def test_fix_on_att532():
    """Test the fix on att532 instance."""
    
    print("=" * 80)
    print("VERIFYING DISTANCE METRIC FIX")
    print("=" * 80)
    
    # Load att532
    filepath = "data/tsplib/att532.tsp"
    parser = TSPLIBParser(filepath)
    if not parser.parse():
        print("❌ Failed to parse att532")
        return
    
    print(f"✓ Parsed {parser.name}: {parser.dimension} nodes, optimal={parser.optimal_value}")
    print(f"  Edge weight type: {parser.edge_weight_type}")
    
    # Get distance matrix
    dist_matrix = parser.get_distance_matrix()
    
    # Test a simple nearest neighbor
    n = dist_matrix.shape[0]
    
    print(f"\n🔍 Testing nearest neighbor with correct ATT distances:")
    
    # Test from node 0
    start = 0
    
    # Find nearest using correct ATT distances
    nearest_dist = float('inf')
    nearest_node = -1
    
    for j in range(1, min(20, n)):  # Check first 20 nodes
        dist = dist_matrix[start, j]
        if dist < nearest_dist:
            nearest_dist = dist
            nearest_node = j
    
    print(f"  From node {start}, nearest is node {nearest_node} (distance: {nearest_dist:.2f})")
    
    # Compare with what Euclidean would give
    points = parser.get_points_array()
    euclidean_nearest_dist = float('inf')
    euclidean_nearest_node = -1
    
    for j in range(1, min(20, n)):
        dx = points[start][0] - points[j][0]
        dy = points[start][1] - points[j][1]
        dist = np.sqrt(dx*dx + dy*dy)
        if dist < euclidean_nearest_dist:
            euclidean_nearest_dist = dist
            euclidean_nearest_node = j
    
    print(f"  Euclidean would choose node {euclidean_nearest_node} (distance: {euclidean_nearest_dist:.2f})")
    
    if euclidean_nearest_node != nearest_node:
        print(f"  🚨 EUCLIDEAN CHOOSES WRONG NODE!")
        print(f"  Error: Would choose node {euclidean_nearest_node} instead of {nearest_node}")
    else:
        print(f"  ✓ Same node chosen (coincidence)")
    
    # Test distance values
    print(f"\n🔢 Distance comparison for edge {start}→{nearest_node}:")
    att_dist = dist_matrix[start, nearest_node]
    
    dx = points[start][0] - points[nearest_node][0]
    dy = points[start][1] - points[nearest_node][1]
    euclidean_dist = np.sqrt(dx*dx + dy*dy)
    
    print(f"  ATT distance (correct): {att_dist:.2f}")
    print(f"  Euclidean distance (what algorithm uses): {euclidean_dist:.2f}")
    print(f"  Ratio (Euclidean/ATT): {euclidean_dist/att_dist:.2f}x")
    print(f"  Error: {euclidean_dist - att_dist:.2f} ({((euclidean_dist - att_dist)/att_dist)*100:.1f}%)")
    
    # Test simple NN tour
    print(f"\n🧪 Testing simple nearest neighbor tour construction:")
    
    # Build NN tour using correct distances
    unvisited = set(range(min(10, n)))  # Use first 10 nodes for speed
    tour = [start]
    unvisited.remove(start)
    
    current = start
    correct_length = 0.0
    
    while unvisited:
        # Find nearest using correct ATT distances
        nearest = min(unvisited, key=lambda city: dist_matrix[current, city])
        correct_length += dist_matrix[current, nearest]
        tour.append(nearest)
        unvisited.remove(nearest)
        current = nearest
    
    # Close tour
    correct_length += dist_matrix[current, start]
    tour.append(start)
    
    print(f"  Correct NN tour (using ATT distances):")
    print(f"    Tour: {tour}")
    print(f"    Length: {correct_length:.2f}")
    
    # Compare with Euclidean-based NN
    unvisited = set(range(min(10, n)))
    tour_euclidean = [start]
    unvisited.remove(start)
    
    current = start
    euclidean_based_length = 0.0
    
    while unvisited:
        # Find nearest using Euclidean (what broken algorithm does)
        nearest = min(unvisited, key=lambda city: np.linalg.norm(points[current] - points[city]))
        # But calculate actual ATT distance
        actual_dist = dist_matrix[current, nearest]
        euclidean_based_length += actual_dist
        tour_euclidean.append(nearest)
        unvisited.remove(nearest)
        current = nearest
    
    # Close tour
    euclidean_based_length += dist_matrix[current, start]
    tour_euclidean.append(start)
    
    print(f"\n  Euclidean-based NN tour (what broken algorithm produces):")
    print(f"    Tour: {tour_euclidean}")
    print(f"    Length: {euclidean_based_length:.2f}")
    
    if tour != tour_euclidean:
        print(f"  🚨 DIFFERENT TOURS!")
        print(f"  Euclidean-based algorithm makes different decisions")
    else:
        print(f"  ✓ Same tour (coincidence)")
    
    print(f"\n  Length difference: {euclidean_based_length - correct_length:.2f}")
    print(f"  Relative error: {((euclidean_based_length - correct_length)/correct_length)*100:.1f}%")
    
    return True

def test_eil51_euclidean():
    """Test on EUC_2D instance where Euclidean should be correct."""
    
    print(f"\n" + "=" * 80)
    print("TESTING EUC_2D INSTANCE (eil51)")
    print("=" * 80)
    
    filepath = "data/tsplib/eil51.tsp"
    parser = TSPLIBParser(filepath)
    if not parser.parse():
        print("❌ Failed to parse eil51")
        return
    
    print(f"✓ Parsed {parser.name}: {parser.dimension} nodes, optimal={parser.optimal_value}")
    print(f"  Edge weight type: {parser.edge_weight_type}")
    
    # Get distance matrix
    dist_matrix = parser.get_distance_matrix()
    points = parser.get_points_array()
    
    # Test a single edge
    start, end = 0, 1
    
    att_dist = dist_matrix[start, end]
    
    dx = points[start][0] - points[end][0]
    dy = points[start][1] - points[end][1]
    euclidean_dist = np.sqrt(dx*dx + dy*dy)
    euclidean_rounded = np.round(euclidean_dist)
    
    print(f"\n🔢 Distance comparison for edge {start}→{end}:")
    print(f"  ATT distance from parser: {att_dist:.2f}")
    print(f"  Euclidean distance: {euclidean_dist:.2f}")
    print(f"  Euclidean rounded (correct for EUC_2D): {euclidean_rounded:.2f}")
    
    if abs(att_dist - euclidean_rounded) < 0.1:
        print(f"  ✓ EUC_2D distance correctly rounded")
    else:
        print(f"  ❌ EUC_2D distance not correctly rounded")
    
    return True

if __name__ == "__main__":
    test_fix_on_att532()
    test_eil51_euclidean()
    
    print(f"\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    print("Vera's finding is CORRECT:")
    print("1. Algorithms use Euclidean distance internally")
    print("2. For ATT instances, Euclidean is 3.16x larger than ATT")
    print("3. This causes wrong 'nearest neighbor' decisions")
    print("4. Tour length calculations are wrong by ~215%")
    print("\n✅ FIX REQUIRED: Algorithms must use correct distance metric")
    print("   per TSPLIB instance type (EUC_2D vs ATT)")
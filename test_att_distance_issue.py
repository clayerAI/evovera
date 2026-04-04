#!/usr/bin/env python3
"""
Test to verify ATT distance calculation issue identified by Vera.
"""

import numpy as np
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tsplib_parser import TSPLIBParser

def test_att_distance_discrepancy():
    """Test the ATT distance discrepancy Vera identified."""
    
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
    print("ATT DISTANCE DISCREPANCY TEST")
    print("=" * 80)
    
    # Get points and distance matrix
    points = parser.get_points_array()
    dist_matrix = parser.get_distance_matrix()
    
    # Test nodes 0 and 1 as Vera mentioned
    node0 = points[0]
    node1 = points[1]
    
    # Euclidean distance
    dx = node0[0] - node1[0]
    dy = node0[1] - node1[1]
    euclidean_dist = np.sqrt(dx*dx + dy*dy)
    
    # ATT distance from parser
    att_dist = dist_matrix[0, 1]
    
    print(f"\nNode 0 coordinates: {node0}")
    print(f"Node 1 coordinates: {node1}")
    print(f"\nEuclidean distance (what algorithms use): {euclidean_dist:.2f}")
    print(f"ATT distance (correct for att532): {att_dist:.2f}")
    print(f"Ratio (Euclidean/ATT): {euclidean_dist/att_dist:.2f}x")
    print(f"Difference: {euclidean_dist - att_dist:.2f}")
    
    # Test what nearest neighbor would choose
    print(f"\n🔍 Nearest neighbor test:")
    print(f"  Using Euclidean distance, nearest to node 0 would be node with min Euclidean distance")
    print(f"  Using ATT distance, nearest to node 0 would be node with min ATT distance")
    
    # Find nearest neighbors using both metrics
    euclidean_dists = []
    att_dists = []
    
    for j in range(1, min(10, len(points))):  # Check first 10 nodes
        dx = points[0][0] - points[j][0]
        dy = points[0][1] - points[j][1]
        euclidean = np.sqrt(dx*dx + dy*dy)
        att = dist_matrix[0, j]
        
        euclidean_dists.append((j, euclidean))
        att_dists.append((j, att))
    
    # Sort by distance
    euclidean_dists.sort(key=lambda x: x[1])
    att_dists.sort(key=lambda x: x[1])
    
    print(f"\nEuclidean nearest to node 0 (first 5):")
    for j, dist in euclidean_dists[:5]:
        print(f"  Node {j}: {dist:.2f}")
    
    print(f"\nATT nearest to node 0 (first 5):")
    for j, dist in att_dists[:5]:
        print(f"  Node {j}: {dist:.2f}")
    
    # Check if they're the same
    euclidean_nearest = euclidean_dists[0][0]
    att_nearest = att_dists[0][0]
    
    print(f"\n🚨 CRITICAL FINDING:")
    print(f"  Euclidean nearest: Node {euclidean_nearest}")
    print(f"  ATT nearest: Node {att_nearest}")
    
    if euclidean_nearest != att_nearest:
        print(f"  ❌ ALGORITHMS MAKE WRONG DECISIONS!")
        print(f"  Algorithms would choose node {euclidean_nearest} but should choose node {att_nearest}")
    else:
        print(f"  ✓ Same nearest neighbor (lucky coincidence)")
    
    # Test algorithm behavior
    print(f"\n🔧 Testing algorithm distance calculation:")
    
    # Simulate what v1 algorithm does
    def algorithm_euclidean_distance(p1, p2):
        return np.linalg.norm(p1 - p2)
    
    algo_dist = algorithm_euclidean_distance(node0, node1)
    print(f"  Algorithm calculates: {algo_dist:.2f}")
    print(f"  Correct ATT distance: {att_dist:.2f}")
    print(f"  Error: {abs(algo_dist - att_dist):.2f} ({abs(algo_dist - att_dist)/att_dist*100:.1f}%)")
    
    return True

if __name__ == "__main__":
    test_att_distance_discrepancy()
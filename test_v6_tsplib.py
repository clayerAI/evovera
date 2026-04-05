#!/usr/bin/env python3
"""
Test v6 on TSPLIB instance.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tsplib_parser import TSPLIBParser
from solutions.tsp_v19_optimized_fixed_v6 import ChristofidesHybridStructuralOptimized

def test_v6_tsplib():
    """Test v6 on eil51 TSPLIB instance."""
    print("Testing v6 on eil51 TSPLIB instance...")
    
    # Parse eil51
    instance_file = "/workspace/evovera/data/tsplib/eil51.tsp"
    parser = TSPLIBParser(instance_file)
    if not parser.parse():
        print("Failed to parse TSPLIB file")
        return None, None
    
    points = parser.get_points_array()
    name = parser.name
    dimension = parser.dimension
    optimal = parser.optimal_value
    
    print(f"Instance: {name}, n={dimension}, optimal={optimal}")
    print(f"Points shape: {points.shape}")
    
    # Convert to list of tuples for v6
    points_list = [(float(points[i, 0]), float(points[i, 1])) for i in range(len(points))]
    
    # Test v6
    solver = ChristofidesHybridStructuralOptimized(points_list, seed=42)
    tour, length, _ = solver.solve()
    
    gap = ((length - optimal) / optimal) * 100
    print(f"v6 solution length: {length:.2f}")
    print(f"Optimal: {optimal}")
    print(f"Gap: {gap:.2f}%")
    
    return length, gap

if __name__ == "__main__":
    length, gap = test_v6_tsplib()

#!/usr/bin/env python3
import sys
import os
import time
import json
from datetime import datetime
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tsplib_parser import TSPLIBParser

# Test with eil51
print("Testing TSPLIB evaluation...")
parser = TSPLIBParser('data/tsplib/eil51.tsp')
if parser.parse():
    print(f"✓ Loaded eil51: {len(parser.node_coords)} points")
    print(f"  Optimal value: {parser.optimal_value}")
    print(f"  Edge weight type: {parser.edge_weight_type}")
    
    # Test distance matrix calculation
    parser.calculate_distance_matrix()
    print(f"  Distance matrix shape: {parser.distance_matrix.shape}")
    print(f"  Sample distance [0,1]: {parser.distance_matrix[0,1]:.2f}")
else:
    print("✗ Failed to parse eil51")

# Test with att532
parser2 = TSPLIBParser('data/tsplib/att532.tsp')
if parser2.parse():
    print(f"\n✓ Loaded att532: {len(parser2.node_coords)} points")
    print(f"  Optimal value: {parser2.optimal_value}")
    print(f"  Edge weight type: {parser2.edge_weight_type}")
    
    # Test distance matrix calculation
    parser2.calculate_distance_matrix()
    print(f"  Distance matrix shape: {parser2.distance_matrix.shape}")
    print(f"  Sample distance [0,1]: {parser2.distance_matrix[0,1]:.2f}")
    
    # Verify ATT distance calculation
    dx = parser2.node_coords[1][0] - parser2.node_coords[0][0]
    dy = parser2.node_coords[1][1] - parser2.node_coords[0][1]
    att_dist = np.ceil(np.sqrt((dx*dx + dy*dy) / 10.0))
    print(f"  Manual ATT distance [0,1]: {att_dist}")
    print(f"  Ratio (Euclidean/ATT): {np.sqrt(dx*dx + dy*dy)/att_dist:.2f}")
else:
    print("✗ Failed to parse att532")

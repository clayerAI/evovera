#!/usr/bin/env python3
"""
Minimal TSPLIB evaluation for eil51 only - fixed version.
"""

import sys
import os
import time
import json
from datetime import datetime
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the fixed algorithm importer
from tsp_algorithms_fixed import algorithms

print(f"✅ Imported {len(algorithms)} algorithms: {list(algorithms.keys())}")

# Test with just eil51
from tsplib_parser import TSPLIBParser
instance_path = "data/tsplib/eil51.tsp"

print(f"\n📊 Testing with {instance_path}")
parser = TSPLIBParser(instance_path)
success = parser.parse()

if success:
    points = np.array(parser.node_coords)  # Convert to numpy array
    optimal = parser.optimal_value
    name = parser.name
    dimension = parser.dimension
    edge_weight_type = parser.edge_weight_type
    
    print(f"  Instance: {name} (dimension={dimension}, type={edge_weight_type})")
    print(f"  Optimal tour length: {optimal}")
    
    # Create distance matrix
    n = len(points)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i+1, n):
            if edge_weight_type == "ATT":
                # ATT distance: ceil(sqrt((dx²+dy²)/10.0))
                dx = points[i][0] - points[j][0]
                dy = points[i][1] - points[j][1]
                dist = np.ceil(np.sqrt((dx*dx + dy*dy) / 10.0))
            else:  # EUC_2D
                dx = points[i][0] - points[j][0]
                dy = points[i][1] - points[j][1]
                dist = np.sqrt(dx*dx + dy*dy)
            dist_matrix[i][j] = dist
            dist_matrix[j][i] = dist
    
    print(f"  Created {n}x{n} distance matrix")
    
    # Test each algorithm
    results = {}
    for algo_name, algo_func in algorithms.items():
        print(f"\n  🧪 Running {algo_name}...")
        start_time = time.time()
        try:
            tour, tour_length = algo_func(points, dist_matrix)
            elapsed = time.time() - start_time
            
            # Calculate gap
            gap = ((tour_length - optimal) / optimal) * 100 if optimal > 0 else float('inf')
            
            results[algo_name] = {
                'tour_length': float(tour_length),
                'gap': float(gap),
                'time': float(elapsed),
                'optimal': float(optimal)
            }
            
            print(f"    Tour length: {tour_length:.2f}")
            print(f"    Gap to optimal: {gap:.2f}%")
            print(f"    Time: {elapsed:.2f}s")
        except Exception as e:
            print(f"    ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            results[algo_name] = {'error': str(e)}
    
    print(f"\n✅ Minimal evaluation complete!")
    
    # Save results
    output_file = "minimal_tsplib_results_fixed.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {output_file}")
    
    # Calculate average gap
    valid_results = [r for r in results.values() if 'error' not in r]
    if valid_results:
        avg_gap = sum(r['gap'] for r in valid_results) / len(valid_results)
        print(f"\n📈 Average gap across {len(valid_results)} algorithms: {avg_gap:.2f}%")
else:
    print("❌ Failed to parse instance")

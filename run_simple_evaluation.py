#!/usr/bin/env python3
import sys
import os
import time
import json
from datetime import datetime
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tsplib_parser import TSPLIBParser

# Import fixed algorithms
try:
    from tsp_algorithms_fixed import algorithms
    ALGORITHMS_AVAILABLE = True
    print("✓ Imported fixed TSP algorithms")
except ImportError as e:
    print(f"✗ Failed to import fixed algorithms: {e}")
    ALGORITHMS_AVAILABLE = False
    sys.exit(1)

def evaluate_algorithm_on_instance(algorithm_name, solve_func, parser, seed=42):
    """Evaluate a single algorithm on a TSPLIB instance."""
    start_time = time.time()
    
    try:
        # Get points and distance matrix from parser
        points = parser.get_points_array()
        distance_matrix = parser.get_distance_matrix()
        
        # Run algorithm with distance matrix
        tour, tour_length = solve_func(points, distance_matrix=distance_matrix)
        
        runtime = time.time() - start_time
        
        # Calculate gap to optimal
        optimal = parser.optimal_value
        if optimal is not None and optimal > 0:
            gap_percent = ((tour_length - optimal) / optimal) * 100
        else:
            gap_percent = None
        
        return {
            "algorithm": algorithm_name,
            "instance": parser.name,
            "tour": tour.tolist() if isinstance(tour, np.ndarray) else tour,
            "tour_length": float(tour_length),
            "optimal": optimal,
            "gap_percent": gap_percent,
            "runtime": runtime,
            "success": True
        }
        
    except Exception as e:
        runtime = time.time() - start_time
        return {
            "algorithm": algorithm_name,
            "instance": parser.name,
            "error": str(e),
            "runtime": runtime,
            "success": False
        }

# Test with eil51 first
print("Running TSPLIB evaluation on eil51...")
filepath = "data/tsplib/eil51.tsp"
parser = TSPLIBParser(filepath)
if not parser.parse():
    print(f"✗ Failed to parse {filepath}")
    sys.exit(1)

print(f"✓ Loaded {parser.name}: {parser.dimension} nodes, optimal={parser.optimal_value}")
print(f"  Edge weight type: {parser.edge_weight_type}")

results = {}
for algo_name, solve_func in algorithms.items():
    print(f"\n🧪 Running {algo_name}...")
    result = evaluate_algorithm_on_instance(algo_name, solve_func, parser)
    
    if result["success"]:
        print(f"  ✓ Success: length={result['tour_length']:.2f}, gap={result['gap_percent']:.2f}%, time={result['runtime']:.2f}s")
        results[algo_name] = result
    else:
        print(f"  ✗ Failed: {result['error']}")

# Save results
output_file = "tsplib_evaluation_eil51_results.json"
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n✓ Results saved to {output_file}")

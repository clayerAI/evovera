#!/usr/bin/env python3
"""Minimal evaluation with just eil51 and kroA100."""

import sys
import os
import time
import numpy as np
import json
from datetime import datetime

sys.path.insert(0, '.')
sys.path.insert(0, 'solutions')

from tsplib_parser import TSPLIBParser
from tsp_v1_nearest_neighbor_fixed import NearestNeighborTSP as V1Solver
from tsp_v2_christofides_improved_fixed import ImprovedMatchingChristofides as V2Solver
from tsp_v19_christofides_hybrid_structural_fixed import ChristofidesHybridStructural as V19Solver

def calculate_distance_matrix(points, edge_weight_type):
    """Calculate distance matrix with broadcasting."""
    x = points[:, 0:1]
    y = points[:, 1:2]
    dx = x - x.T
    dy = y - y.T
    
    if edge_weight_type == "ATT":
        return np.ceil(np.sqrt((dx*dx + dy*dy) / 10.0))
    else:
        return np.round(np.sqrt(dx*dx + dy*dy))

def main():
    print("MINIMAL TSPLIB EVALUATION")
    
    instances = [
        ("eil51", "data/tsplib/eil51.tsp", 426),
        ("kroA100", "data/tsplib/kroA100.tsp", 21282),
    ]
    
    results = {}
    
    for instance_name, filepath, optimal in instances:
        print(f"\n=== {instance_name} ===")
        
        parser = TSPLIBParser(filepath)
        parser.parse()
        
        points = np.array(parser.node_coords)
        dist_matrix = calculate_distance_matrix(points, parser.edge_weight_type)
        
        instance_results = {"algorithms": {}}
        
        # Test V1
        print("  V1...")
        solver = V1Solver(distance_matrix=dist_matrix, seed=42)
        start = time.time()
        result = solver.solve()
        elapsed = time.time() - start
        tour, length = result[0], result[1]
        gap = ((length - optimal) / optimal) * 100
        print(f"    Length: {length:.1f}, Gap: {gap:.2f}%, Time: {elapsed:.3f}s")
        instance_results["algorithms"]["V1"] = {
            "tour_length": float(length),
            "gap_percent": float(gap),
            "time_seconds": float(elapsed)
        }
        
        # Test V2
        print("  V2...")
        solver = V2Solver(distance_matrix=dist_matrix, seed=42)
        start = time.time()
        result = solver.solve()
        elapsed = time.time() - start
        tour, length = result[0], result[1]
        gap = ((length - optimal) / optimal) * 100
        print(f"    Length: {length:.1f}, Gap: {gap:.2f}%, Time: {elapsed:.3f}s")
        instance_results["algorithms"]["V2"] = {
            "tour_length": float(length),
            "gap_percent": float(gap),
            "time_seconds": float(elapsed)
        }
        
        # Test V19
        print("  V19...")
        solver = V19Solver(distance_matrix=dist_matrix, seed=42)
        start = time.time()
        result = solver.solve()
        elapsed = time.time() - start
        tour, length, modularity = result[0], result[1], result[2]
        gap = ((length - optimal) / optimal) * 100
        print(f"    Length: {length:.1f}, Gap: {gap:.2f}%, Time: {elapsed:.3f}s")
        instance_results["algorithms"]["V19"] = {
            "tour_length": float(length),
            "gap_percent": float(gap),
            "time_seconds": float(elapsed),
            "modularity": float(modularity)
        }
        
        results[instance_name] = instance_results
    
    # Save results
    with open("minimal_evaluation_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n✅ Evaluation complete!")
    return results

if __name__ == "__main__":
    main()

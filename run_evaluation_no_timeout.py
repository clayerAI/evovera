#!/usr/bin/env python3
"""Run evaluation without timeout wrapper."""

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
    print("RUNNING TSPLIB EVALUATION (NO TIMEOUT)")
    
    instances = [
        ("eil51", "data/tsplib/eil51.tsp", 426),
        ("kroA100", "data/tsplib/kroA100.tsp", 21282),
        ("a280", "data/tsplib/a280.tsp", 2579),
        ("att532", "data/tsplib/att532.tsp", 27686)
    ]
    
    algorithms = [
        ("V1", V1Solver, "Nearest Neighbor (Fixed)"),
        ("V2", V2Solver, "Christofides Improved (Fixed)"),
        ("V19", V19Solver, "Christofides Hybrid Structural (Fixed)")
    ]
    
    baseline_gap = 17.69
    results = {}
    
    for instance_name, filepath, optimal in instances:
        print(f"\n{'='*60}")
        print(f"INSTANCE: {instance_name}")
        print(f"{'='*60}")
        
        parser = TSPLIBParser(filepath)
        parser.parse()
        
        points = np.array(parser.node_coords)
        dist_matrix = calculate_distance_matrix(points, parser.edge_weight_type)
        
        instance_results = {"algorithms": {}}
        
        for algo_id, solver_class, algo_name in algorithms:
            print(f"\n{algo_name}:")
            try:
                solver = solver_class(distance_matrix=dist_matrix, seed=42)
                start = time.time()
                result = solver.solve()
                elapsed = time.time() - start
                
                if len(result) >= 2:
                    tour, length = result[0], result[1]
                    additional = result[2] if len(result) > 2 else None
                    
                    gap = ((length - optimal) / optimal) * 100
                    improvement = baseline_gap - gap
                    
                    print(f"  Length: {length:.1f}")
                    print(f"  Gap: {gap:.2f}%")
                    print(f"  Improvement over baseline: {improvement:.2f}%")
                    print(f"  Time: {elapsed:.3f}s")
                    if additional is not None:
                        print(f"  Modularity: {additional:.4f}")
                    
                    instance_results["algorithms"][algo_id] = {
                        "tour_length": float(length),
                        "gap_percent": float(gap),
                        "improvement_over_baseline": float(improvement),
                        "time_seconds": float(elapsed),
                        "novelty_confirmed": improvement > 0.1,
                        "additional_metric": float(additional) if additional is not None else None
                    }
                else:
                    print(f"  ❌ Unexpected result")
                    instance_results["algorithms"][algo_id] = {"error": "Unexpected result format"}
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
                instance_results["algorithms"][algo_id] = {"error": str(e)}
        
        results[instance_name] = instance_results
    
    # Save results
    with open("evaluation_results_no_timeout.json", 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "baseline_gap": baseline_gap,
            "novelty_threshold": 0.1,
            "results": results
        }, f, indent=2)
    
    print(f"\n{'='*60}")
    print("EVALUATION COMPLETE")
    print(f"{'='*60}")
    
    return results

if __name__ == "__main__":
    main()

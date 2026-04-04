#!/usr/bin/env python3
"""
Simple corrected TSPLIB evaluation - runs each instance separately.
"""

import sys
import os
import time
import numpy as np
import json
from datetime import datetime

# Add paths
sys.path.insert(0, '.')
sys.path.insert(0, 'solutions')

from tsplib_parser import TSPLIBParser
from tsp_v1_nearest_neighbor_fixed import NearestNeighborTSP as V1Solver
from tsp_v2_christofides_improved_fixed import ImprovedMatchingChristofides as V2Solver
from tsp_v19_christofides_hybrid_structural_fixed import ChristofidesHybridStructural as V19Solver

def calculate_distance_matrix_simple(points, edge_weight_type):
    """Calculate distance matrix with numpy broadcasting."""
    n = len(points)
    
    if edge_weight_type == "ATT":
        # ATT distance: ceil(sqrt((dx²+dy²)/10))
        # Use broadcasting for efficiency
        x = points[:, 0:1]  # Column vector
        y = points[:, 1:2]
        
        dx = x - x.T
        dy = y - y.T
        dist = np.ceil(np.sqrt((dx*dx + dy*dy) / 10.0))
    else:
        # EUC_2D: round(sqrt(dx²+dy²))
        x = points[:, 0:1]
        y = points[:, 1:2]
        
        dx = x - x.T
        dy = y - y.T
        dist = np.round(np.sqrt(dx*dx + dy*dy))
    
    return dist

def run_algorithm(solver_class, dist_matrix, seed=42):
    """Run algorithm and handle different return signatures."""
    solver = solver_class(distance_matrix=dist_matrix, seed=seed)
    start = time.time()
    result = solver.solve()
    elapsed = time.time() - start
    
    # Handle return values
    if isinstance(result, tuple):
        if len(result) >= 2:
            tour, length = result[0], result[1]
            additional = result[2] if len(result) > 2 else None
            return tour, length, elapsed, additional
    else:
        raise ValueError(f"Unexpected return type: {type(result)}")
    
    return None, None, elapsed, None

def evaluate_instance(instance_name, filepath, optimal):
    """Evaluate a single instance."""
    print(f"\n📊 Processing instance: {instance_name}")
    print(f"  File: {filepath}")
    print(f"  Optimal: {optimal}")
    
    if not os.path.exists(filepath):
        print(f"  ❌ File not found: {filepath}")
        return None
    
    # Parse instance
    parser = TSPLIBParser(filepath)
    if not parser.parse():
        print(f"  ❌ Failed to parse instance")
        return None
    
    print(f"  Dimension: {parser.dimension}")
    print(f"  Edge weight type: {parser.edge_weight_type}")
    
    # Calculate distance matrix
    points = np.array(parser.node_coords)
    print(f"  Calculating distance matrix...")
    start_calc = time.time()
    dist_matrix = calculate_distance_matrix_simple(points, parser.edge_weight_type)
    calc_time = time.time() - start_calc
    print(f"  Distance matrix calculated in {calc_time:.2f}s")
    
    instance_results = {
        "name": instance_name,
        "dimension": parser.dimension,
        "edge_weight_type": parser.edge_weight_type,
        "optimal": optimal,
        "distance_matrix_calc_time": calc_time,
        "algorithms": {}
    }
    
    # Algorithms to test
    algorithms = [
        ("V1", V1Solver, "Nearest Neighbor (Fixed)"),
        ("V2", V2Solver, "Christofides Improved (Fixed)"),
        ("V19", V19Solver, "Christofides Hybrid Structural (Fixed)")
    ]
    
    for algo_id, solver_class, algo_name in algorithms:
        print(f"\n  🚀 Testing {algo_name}...")
        
        try:
            tour, length, elapsed, additional = run_algorithm(solver_class, dist_matrix)
            
            if length is not None:
                gap = ((length - optimal) / optimal) * 100
                
                print(f"    Tour length: {length:.2f}")
                print(f"    Gap to optimal: {gap:.2f}%")
                print(f"    Time: {elapsed:.3f}s")
                if additional is not None:
                    print(f"    Additional metric: {additional:.4f}")
                
                instance_results["algorithms"][algo_id] = {
                    "name": algo_name,
                    "tour_length": float(length),
                    "gap_percent": float(gap),
                    "time_seconds": float(elapsed),
                    "additional_metric": float(additional) if additional is not None else None
                }
            else:
                print(f"    ❌ Failed to get valid result")
                instance_results["algorithms"][algo_id] = {"error": "Failed to get valid result"}
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
            instance_results["algorithms"][algo_id] = {"error": str(e)}
    
    return instance_results

def main():
    print("=" * 80)
    print("SIMPLE CORRECTED TSPLIB EVALUATION")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # TSPLIB instances to evaluate - start with smaller ones
    instances = [
        ("eil51", "data/tsplib/eil51.tsp", 426),
        ("kroA100", "data/tsplib/kroA100.tsp", 21282),
        ("a280", "data/tsplib/a280.tsp", 2579),
        ("att532", "data/tsplib/att532.tsp", 27686)  # ATT distance metric
    ]
    
    results = {}
    
    # Evaluate instances one by one
    for instance_name, filepath, optimal in instances:
        instance_result = evaluate_instance(instance_name, filepath, optimal)
        if instance_result:
            results[instance_name] = instance_result
    
    # Baseline: NN+2opt (17.69% average gap on 500-node instances)
    baseline_gap = 17.69
    
    # Summary analysis
    print("\n" + "=" * 80)
    print("SUMMARY ANALYSIS")
    print("=" * 80)
    
    # Calculate average gaps and improvements
    algorithms = ["V1", "V2", "V19"]
    
    for algo_id in algorithms:
        gaps = []
        improvements = []
        
        for instance_name in results:
            if algo_id in results[instance_name]["algorithms"]:
                algo_result = results[instance_name]["algorithms"][algo_id]
                if "gap_percent" in algo_result:
                    gap = algo_result["gap_percent"]
                    gaps.append(gap)
                    improvement = baseline_gap - gap
                    improvements.append(improvement)
        
        if gaps:
            avg_gap = np.mean(gaps)
            avg_improvement = np.mean(improvements)
            
            algo_name = results[list(results.keys())[0]]["algorithms"][algo_id]["name"]
            print(f"\n{algo_name}:")
            print(f"  Average gap to optimal: {avg_gap:.2f}%")
            print(f"  Average improvement over baseline: {avg_improvement:.2f}%")
            
            # Check novelty threshold (0.1%)
            if avg_improvement > 0.1:
                print(f"  ✅ NOVELTY CONFIRMED (exceeds 0.1% threshold)")
            else:
                print(f"  ❌ Novelty NOT confirmed (below 0.1% threshold)")
    
    # Save results to file
    output_file = "corrected_tsplib_evaluation_results_simple.json"
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "baseline_gap_percent": baseline_gap,
            "novelty_threshold_percent": 0.1,
            "instances": results
        }, f, indent=2)
    
    print(f"\n📁 Results saved to: {output_file}")
    print("\n" + "=" * 80)
    print("EVALUATION COMPLETE")
    print("=" * 80)
    
    return results

if __name__ == "__main__":
    main()

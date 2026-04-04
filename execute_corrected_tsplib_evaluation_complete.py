#!/usr/bin/env python3
"""
Execute corrected TSPLIB evaluation with verified fixed algorithms.
Includes proper ATT distance calculation for att532 instance.
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

def calculate_distance_matrix(points, edge_weight_type):
    """Calculate distance matrix with proper metric for each instance."""
    n = len(points)
    dist_matrix = np.zeros((n, n))
    
    if edge_weight_type == "ATT":
        # ATT distance: ceil(sqrt((dx²+dy²)/10))
        for i in range(n):
            for j in range(i + 1, n):
                dx = points[i][0] - points[j][0]
                dy = points[i][1] - points[j][1]
                # ATT distance formula
                dist = np.ceil(np.sqrt((dx*dx + dy*dy) / 10.0))
                dist_matrix[i][j] = dist
                dist_matrix[j][i] = dist
    else:
        # EUC_2D: round(sqrt(dx²+dy²))
        for i in range(n):
            for j in range(i + 1, n):
                dx = points[i][0] - points[j][0]
                dy = points[i][1] - points[j][1]
                dist = round(np.sqrt(dx*dx + dy*dy))
                dist_matrix[i][j] = dist
                dist_matrix[j][i] = dist
    
    return dist_matrix

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

def main():
    print("=" * 80)
    print("CORRECTED TSPLIB EVALUATION EXECUTION")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # TSPLIB instances to evaluate
    instances = [
        ("eil51", "data/tsplib/eil51.tsp", 426),
        ("kroA100", "data/tsplib/kroA100.tsp", 21282),
        ("a280", "data/tsplib/a280.tsp", 2579),
        ("att532", "data/tsplib/att532.tsp", 27686)  # ATT distance metric
    ]
    
    # Algorithms to test
    algorithms = [
        ("V1", V1Solver, "Nearest Neighbor (Fixed)"),
        ("V2", V2Solver, "Christofides Improved (Fixed)"),
        ("V19", V19Solver, "Christofides Hybrid Structural (Fixed)")
    ]
    
    # Baseline: NN+2opt (17.69% average gap on 500-node instances)
    baseline_gap = 17.69
    
    results = {}
    
    for instance_name, filepath, optimal in instances:
        print(f"\n📊 Processing instance: {instance_name}")
        print(f"  File: {filepath}")
        print(f"  Optimal: {optimal}")
        
        if not os.path.exists(filepath):
            print(f"  ❌ File not found: {filepath}")
            continue
        
        # Parse instance
        parser = TSPLIBParser(filepath)
        if not parser.parse():
            print(f"  ❌ Failed to parse instance")
            continue
        
        print(f"  Dimension: {parser.dimension}")
        print(f"  Edge weight type: {parser.edge_weight_type}")
        
        # Calculate distance matrix with proper metric
        points = np.array(parser.node_coords)
        dist_matrix = calculate_distance_matrix(points, parser.edge_weight_type)
        
        instance_results = {
            "name": instance_name,
            "dimension": parser.dimension,
            "edge_weight_type": parser.edge_weight_type,
            "optimal": optimal,
            "algorithms": {}
        }
        
        for algo_id, solver_class, algo_name in algorithms:
            print(f"\n  🚀 Testing {algo_name}...")
            
            try:
                tour, length, elapsed, additional = run_algorithm(solver_class, dist_matrix)
                
                if length is not None:
                    gap = ((length - optimal) / optimal) * 100
                    
                    # Compare to baseline
                    improvement_over_baseline = baseline_gap - gap
                    
                    print(f"    Tour length: {length:.2f}")
                    print(f"    Gap to optimal: {gap:.2f}%")
                    print(f"    Improvement over baseline: {improvement_over_baseline:.2f}%")
                    print(f"    Time: {elapsed:.3f}s")
                    if additional is not None:
                        print(f"    Additional metric: {additional:.4f}")
                    
                    # Check novelty threshold (0.1%)
                    novelty_confirmed = improvement_over_baseline > 0.1
                    
                    instance_results["algorithms"][algo_id] = {
                        "name": algo_name,
                        "tour_length": float(length),
                        "gap_percent": float(gap),
                        "improvement_over_baseline": float(improvement_over_baseline),
                        "time_seconds": float(elapsed),
                        "novelty_confirmed": novelty_confirmed,
                        "additional_metric": float(additional) if additional is not None else None
                    }
                else:
                    print(f"    ❌ Failed to get valid result")
                    instance_results["algorithms"][algo_id] = {"error": "Failed to get valid result"}
                    
            except Exception as e:
                print(f"    ❌ Error: {e}")
                instance_results["algorithms"][algo_id] = {"error": str(e)}
        
        results[instance_name] = instance_results
    
    # Summary analysis
    print("\n" + "=" * 80)
    print("SUMMARY ANALYSIS")
    print("=" * 80)
    
    # Calculate average gaps and improvements
    for algo_id, _, algo_name in algorithms:
        gaps = []
        improvements = []
        novelty_counts = 0
        
        for instance_name in results:
            if algo_id in results[instance_name]["algorithms"]:
                algo_result = results[instance_name]["algorithms"][algo_id]
                if "gap_percent" in algo_result:
                    gaps.append(algo_result["gap_percent"])
                    improvements.append(algo_result["improvement_over_baseline"])
                    if algo_result.get("novelty_confirmed", False):
                        novelty_counts += 1
        
        if gaps:
            avg_gap = np.mean(gaps)
            avg_improvement = np.mean(improvements)
            print(f"\n{algo_name}:")
            print(f"  Average gap to optimal: {avg_gap:.2f}%")
            print(f"  Average improvement over baseline: {avg_improvement:.2f}%")
            print(f"  Novelty confirmed on {novelty_counts}/{len(results)} instances")
            
            # Overall novelty confirmation
            if avg_improvement > 0.1:
                print(f"  ✅ OVERALL NOVELTY CONFIRMED (exceeds 0.1% threshold)")
            else:
                print(f"  ❌ Novelty NOT confirmed (below 0.1% threshold)")
    
    # Save results to file
    output_file = "corrected_tsplib_evaluation_results.json"
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

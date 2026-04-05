#!/usr/bin/env python3
"""
Complete TSPLIB evaluation with 300s timeout for v19 on a280 and att532.
As per Vera's coordination decision: OPTION 1 - Complete full evaluation.
"""

import sys
import os
import time
import numpy as np
import json
import signal
from datetime import datetime
from functools import wraps

sys.path.insert(0, '.')
sys.path.insert(0, 'solutions')

from tsplib_parser import TSPLIBParser
from tsp_v1_nearest_neighbor_fixed import NearestNeighborTSP as V1Solver
from tsp_v2_christofides_improved_fixed import ImprovedMatchingChristofides as V2Solver
from tsp_v19_christofides_hybrid_structural_fixed import ChristofidesHybridStructural as V19Solver

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Algorithm timed out")

def run_with_timeout(func, timeout_seconds=300):
    """Run function with timeout."""
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)
    try:
        result = func()
        signal.alarm(0)  # Cancel the alarm
        return result
    except TimeoutException:
        return None
    finally:
        signal.alarm(0)  # Ensure alarm is always cancelled

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

def evaluate_algorithm(algorithm_name, solver_class, points, dist_matrix, optimal, timeout):
    """Evaluate a single algorithm with timeout."""
    print(f"    Testing {algorithm_name}...")
    
    def run_algorithm():
        solver = solver_class(points=points, distance_matrix=dist_matrix)
        tour, length, runtime = solver.solve(time_limit=timeout)
        return {
            "tour_length": float(length),
            "gap_percent": float((length - optimal) / optimal * 100),
            "runtime": float(runtime),
            "success": True,
            "timeout": False
        }
    
    start_time = time.time()
    try:
        result = run_with_timeout(run_algorithm, timeout)
        if result is None:
            elapsed = time.time() - start_time
            return {
                "error": f"Timeout after {elapsed:.1f}s",
                "success": False,
                "timeout": True,
                "runtime": float(elapsed)
            }
        return result
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "error": str(e),
            "success": False,
            "timeout": False,
            "runtime": float(elapsed)
        }

def main():
    print("=" * 80)
    print("COMPLETE TSPLIB EVALUATION WITH 300s TIMEOUT")
    print("As per Vera's coordination decision: OPTION 1")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # TSPLIB instances to evaluate (focus on a280 and att532)
    instances = [
        ("a280", "data/tsplib/a280.tsp", 2579, "EUC_2D"),
        ("att532", "data/tsplib/att532.tsp", 27686, "ATT")
    ]
    
    # Algorithms to test with timeouts (seconds)
    algorithms = [
        ("tsp_v1_nearest_neighbor_fixed", V1Solver, "Nearest Neighbor", 10),
        ("tsp_v2_christofides_improved_fixed", V2Solver, "Christofides Improved", 10),
        ("tsp_v19_christofides_hybrid_structural_fixed", V19Solver, "Christofides Hybrid Structural", 300)  # 300s timeout
    ]
    
    results = {}
    
    for instance_name, filepath, optimal, edge_weight_type in instances:
        print(f"\n📊 Processing instance: {instance_name}")
        print(f"  File: {filepath}")
        print(f"  Optimal: {optimal}")
        print(f"  Edge weight type: {edge_weight_type}")
        
        if not os.path.exists(filepath):
            print(f"  ❌ File not found: {filepath}")
            continue
        
        # Parse instance
        parser = TSPLIBParser(filepath)
        if not parser.parse():
            print(f"  ❌ Failed to parse instance")
            continue
        
        print(f"  Dimension: {parser.dimension}")
        
        # Calculate distance matrix
        points = np.array(parser.node_coords)
        print(f"  Calculating distance matrix...")
        dist_matrix = calculate_distance_matrix(points, edge_weight_type)
        
        instance_results = {}
        
        for algo_id, solver_class, algo_name, timeout in algorithms:
            result = evaluate_algorithm(algo_name, solver_class, points, dist_matrix, optimal, timeout)
            instance_results[algo_id] = result
            
            if result.get("success", False):
                print(f"    ✅ {algo_name}: {result['tour_length']:.2f} ({result['gap_percent']:.2f}% gap) in {result['runtime']:.2f}s")
            elif result.get("timeout", False):
                print(f"    ⏱️ {algo_name}: Timeout after {result['runtime']:.2f}s")
            else:
                print(f"    ❌ {algo_name}: Error - {result.get('error', 'Unknown error')}")
        
        results[instance_name] = {
            "instance": instance_name,
            "dimension": parser.dimension,
            "optimal": optimal,
            "edge_weight_type": edge_weight_type,
            "results": instance_results
        }
    
    # Save results
    output_file = "tsplib_complete_evaluation_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "instances": [inst[0] for inst in instances],
            "algorithms": [algo[0] for algo in algorithms],
            "results": results
        }, f, indent=2)
    
    print(f"\n✅ Results saved to {output_file}")
    
    # Generate summary
    print("\n" + "=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)
    
    for instance_name in results:
        print(f"\n{instance_name}:")
        for algo_id in algorithms:
            algo_name = algo_id[0]
            if algo_name in results[instance_name]["results"]:
                result = results[instance_name]["results"][algo_name]
                if result.get("success", False):
                    print(f"  {algo_name}: {result['tour_length']:.2f} ({result['gap_percent']:.2f}% gap)")
                elif result.get("timeout", False):
                    print(f"  {algo_name}: TIMEOUT after {result['runtime']:.2f}s")
                else:
                    print(f"  {algo_name}: ERROR - {result.get('error', 'Unknown')}")

if __name__ == "__main__":
    main()

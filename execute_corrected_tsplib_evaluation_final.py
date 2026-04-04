#!/usr/bin/env python3
"""
Final corrected TSPLIB evaluation with timeouts for each instance.
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

def run_with_timeout(func, timeout_seconds=30):
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

def main():
    print("=" * 80)
    print("FINAL CORRECTED TSPLIB EVALUATION")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # TSPLIB instances to evaluate
    instances = [
        ("eil51", "data/tsplib/eil51.tsp", 426),
        ("kroA100", "data/tsplib/kroA100.tsp", 21282),
        ("a280", "data/tsplib/a280.tsp", 2579),
        ("att532", "data/tsplib/att532.tsp", 27686)  # ATT distance metric
    ]
    
    # Algorithms to test with timeouts (seconds)
    algorithms = [
        ("V1", V1Solver, "Nearest Neighbor (Fixed)", 10),
        ("V2", V2Solver, "Christofides Improved (Fixed)", 10),
        ("V19", V19Solver, "Christofides Hybrid Structural (Fixed)", 60)  # V19 needs more time
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
        
        # Calculate distance matrix
        points = np.array(parser.node_coords)
        print(f"  Calculating distance matrix...")
        start_calc = time.time()
        dist_matrix = calculate_distance_matrix(points, parser.edge_weight_type)
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
        
        for algo_id, solver_class, algo_name, timeout in algorithms:
            print(f"\n  🚀 Testing {algo_name} (timeout: {timeout}s)...")
            
            try:
                # Create solver
                solver = solver_class(distance_matrix=dist_matrix, seed=42)
                
                # Run with timeout
                def run_algorithm():
                    start = time.time()
                    result = solver.solve()
                    elapsed = time.time() - start
                    return result, elapsed
                
                timeout_result = run_with_timeout(lambda: run_algorithm(), timeout)
                
                if timeout_result is None:
                    print(f"    ⏰ TIMEOUT after {timeout}s")
                    instance_results["algorithms"][algo_id] = {
                        "error": f"Timeout after {timeout} seconds"
                    }
                    continue
                
                result, elapsed = timeout_result
                
                # Handle return values
                if isinstance(result, tuple) and len(result) >= 2:
                    tour, length = result[0], result[1]
                    additional = result[2] if len(result) > 2 else None
                    
                    gap = ((length - optimal) / optimal) * 100
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
                    print(f"    ❌ Unexpected result format")
                    instance_results["algorithms"][algo_id] = {"error": "Unexpected result format"}
                    
            except Exception as e:
                print(f"    ❌ Error: {e}")
                instance_results["algorithms"][algo_id] = {"error": str(e)}
        
        results[instance_name] = instance_results
    
    # Summary analysis
    print("\n" + "=" * 80)
    print("SUMMARY ANALYSIS")
    print("=" * 80)
    
    # Calculate average gaps and improvements (only for successful runs)
    for algo_id, _, algo_name, _ in algorithms:
        gaps = []
        improvements = []
        novelty_counts = 0
        total_instances = 0
        
        for instance_name in results:
            total_instances += 1
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
            success_rate = len(gaps) / total_instances * 100
            
            print(f"\n{algo_name}:")
            print(f"  Success rate: {success_rate:.1f}% ({len(gaps)}/{total_instances} instances)")
            print(f"  Average gap to optimal: {avg_gap:.2f}%")
            print(f"  Average improvement over baseline: {avg_improvement:.2f}%")
            print(f"  Novelty confirmed on {novelty_counts}/{len(gaps)} successful instances")
            
            # Overall novelty confirmation
            if avg_improvement > 0.1:
                print(f"  ✅ OVERALL NOVELTY CONFIRMED (exceeds 0.1% threshold)")
            else:
                print(f"  ❌ Novelty NOT confirmed (below 0.1% threshold)")
        else:
            print(f"\n{algo_name}: No successful runs")
    
    # Save results to file
    output_file = "corrected_tsplib_evaluation_final_results.json"
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

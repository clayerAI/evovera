#!/usr/bin/env python3
"""
Execute Corrected TSPLIB Evaluation - Version 2
Authorized by Vera coordination signal.

Runs the three verified fixed algorithms on all 4 TSPLIB Phase 2D instances
with proper ATT distance calculation for att532.
"""

import sys
import os
import time
import json
import numpy as np
from datetime import datetime
import statistics
from typing import Dict, List, Tuple, Any

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "solutions"))

# Import TSPLIB parser
from tsplib_parser import TSPLIBParser

# Import fixed TSP algorithms
try:
    from tsp_v1_nearest_neighbor_fixed import NearestNeighborTSP as V1Solver
    from tsp_v2_christofides_improved_fixed import ChristofidesImprovedTSP as V2Solver
    from tsp_v19_christofides_hybrid_structural_fixed import ChristofidesHybridStructuralTSP as V19Solver
    print("✓ Successfully imported all three fixed TSP algorithms")
except ImportError as e:
    print(f"❌ Error importing fixed algorithms: {e}")
    sys.exit(1)

# TSPLIB instances to evaluate
TSPLIB_INSTANCES = ["eil51", "kroA100", "a280", "att532"]
TSPLIB_DIR = "data/tsplib"

# Algorithm configurations
ALGORITHMS = {
    "v1_nearest_neighbor_fixed": {
        "solver_class": V1Solver,
        "description": "Nearest Neighbor (Fixed for TSPLIB)",
        "params": {"seed": 42}
    },
    "v2_christofides_improved_fixed": {
        "solver_class": V2Solver,
        "description": "Christofides Improved (Fixed for TSPLIB)",
        "params": {"seed": 42}
    },
    "v19_christofides_hybrid_structural_fixed": {
        "solver_class": V19Solver,
        "description": "Christofides Hybrid Structural (Fixed for TSPLIB)",
        "params": {"seed": 42}
    }
}

def calculate_distance_matrix(points: np.ndarray, edge_weight_type: str) -> np.ndarray:
    """Calculate distance matrix based on edge weight type."""
    n = len(points)
    dist_matrix = np.zeros((n, n))
    
    for i in range(n):
        for j in range(i + 1, n):
            dx = points[i][0] - points[j][0]
            dy = points[i][1] - points[j][1]
            
            if edge_weight_type == "EUC_2D":
                # Euclidean distance rounded to nearest integer
                dist = round(np.sqrt(dx*dx + dy*dy))
            elif edge_weight_type == "ATT":
                # ATT distance: ceil(sqrt((dx²+dy²)/10))
                dist = np.ceil(np.sqrt((dx*dx + dy*dy) / 10.0))
            else:
                # Default to Euclidean
                dist = round(np.sqrt(dx*dx + dy*dy))
            
            dist_matrix[i][j] = dist
            dist_matrix[j][i] = dist
    
    return dist_matrix

def run_algorithm_on_instance(algorithm_config: Dict, parser: TSPLIBParser) -> Dict[str, Any]:
    """Run a single algorithm on a parsed TSPLIB instance."""
    algo_desc = algorithm_config["description"]
    print(f"  Running {algo_desc}...")
    
    # Get points from parser
    points = np.array(parser.node_coords)
    
    # Calculate distance matrix based on edge weight type
    distance_matrix = calculate_distance_matrix(points, parser.edge_weight_type)
    
    # Create solver with distance matrix
    solver = algorithm_config["solver_class"](distance_matrix=distance_matrix, **algorithm_config["params"])
    
    # Solve with timing
    start_time = time.time()
    try:
        tour, tour_length = solver.solve()
        solve_time = time.time() - start_time
        
        # Verify tour length matches distance matrix calculation
        calculated_length = 0
        n = len(tour)
        for i in range(n):
            calculated_length += distance_matrix[tour[i], tour[(i + 1) % n]]
        
        # Check for consistency
        if abs(calculated_length - tour_length) > 1e-6:
            print(f"    ⚠️ Tour length mismatch: solver={tour_length:.2f}, calculated={calculated_length:.2f}")
            tour_length = calculated_length  # Use calculated length
        
        print(f"    ✓ Tour length: {tour_length:.2f} (took {solve_time:.2f}s)")
        
        return {
            "tour_length": float(tour_length),
            "solve_time": solve_time,
            "tour_size": n,
            "tour_sample": tour[:10] if n > 10 else tour,
            "success": True
        }
        
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return {
            "tour_length": None,
            "solve_time": None,
            "tour_size": 0,
            "tour_sample": [],
            "success": False,
            "error": str(e)
        }

def main():
    """Main evaluation function."""
    print("=" * 80)
    print("EXECUTING CORRECTED TSPLIB EVALUATION - VERSION 2")
    print("Authorized by Vera coordination signal")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)
    
    # Check instance availability
    print("\n🔍 Checking TSPLIB instance availability...")
    available_instances = []
    
    for instance in TSPLIB_INSTANCES:
        filepath = os.path.join(TSPLIB_DIR, f"{instance}.tsp")
        if os.path.exists(filepath):
            available_instances.append((instance, filepath))
            print(f"  ✓ {instance} available at {filepath}")
        else:
            print(f"  ❌ {instance} NOT found at {filepath}")
    
    if len(available_instances) < len(TSPLIB_INSTANCES):
        print(f"\n⚠️ Warning: Only {len(available_instances)}/{len(TSPLIB_INSTANCES)} instances available")
    
    # Run evaluation
    print("\n🚀 Starting TSPLIB evaluation...")
    all_results = {}
    
    for instance_name, filepath in available_instances:
        print(f"\n📊 Evaluating {instance_name}...")
        
        # Parse TSPLIB file
        parser = TSPLIBParser(filepath)
        if not parser.parse():
            print(f"  ❌ Failed to parse {instance_name}")
            continue
        
        print(f"  ✓ Parsed: {parser.dimension} nodes, edge_weight_type={parser.edge_weight_type}")
        print(f"    Optimal value: {parser.optimal_value}")
        
        instance_results = {}
        
        for algo_name, algo_config in ALGORITHMS.items():
            result = run_algorithm_on_instance(algo_config, parser)
            instance_results[algo_name] = result
        
        all_results[instance_name] = {
            "results": instance_results,
            "metadata": {
                "dimension": parser.dimension,
                "edge_weight_type": parser.edge_weight_type,
                "optimal_value": parser.optimal_value,
                "filepath": filepath
            }
        }
    
    # Calculate gap metrics
    print("\n📈 Calculating gap-to-optimal metrics...")
    gap_metrics = {}
    
    for instance_name, data in all_results.items():
        optimal = data["metadata"]["optimal_value"]
        if optimal is None:
            print(f"  ⚠️ No optimal value for {instance_name}, skipping gap calculation")
            continue
        
        instance_gaps = {}
        for algo_name, result in data["results"].items():
            if result["success"] and result["tour_length"] is not None:
                tour_length = result["tour_length"]
                gap = ((tour_length - optimal) / optimal) * 100 if optimal > 0 else float('inf')
                instance_gaps[algo_name] = {
                    "gap_percent": gap,
                    "tour_length": tour_length,
                    "optimal": optimal,
                    "absolute_gap": tour_length - optimal
                }
        
        gap_metrics[instance_name] = instance_gaps
    
    # Print summary
    print("\n" + "=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)
    
    for instance_name in [i[0] for i in available_instances]:
        if instance_name not in all_results:
            continue
            
        print(f"\n📋 {instance_name}:")
        metadata = all_results[instance_name]["metadata"]
        print(f"  Dimension: {metadata['dimension']}, Edge weight: {metadata['edge_weight_type']}")
        print(f"  Optimal value: {metadata['optimal_value']}")
        
        if instance_name in gap_metrics:
            for algo_name, gap_info in gap_metrics[instance_name].items():
                algo_desc = ALGORITHMS[algo_name]["description"]
                print(f"  {algo_desc}:")
                print(f"    Tour length: {gap_info['tour_length']:.2f}")
                print(f"    Gap to optimal: {gap_info['gap_percent']:.2f}%")
                print(f"    Absolute gap: {gap_info['absolute_gap']:.2f}")
        else:
            print("  No valid gap metrics")
    
    # Statistical analysis
    print("\n📊 STATISTICAL ANALYSIS:")
    
    # Calculate average gaps per algorithm
    for algo_name in ALGORITHMS.keys():
        gaps = []
        for instance_name in gap_metrics:
            if algo_name in gap_metrics[instance_name]:
                gaps.append(gap_metrics[instance_name][algo_name]["gap_percent"])
        
        if gaps:
            avg_gap = statistics.mean(gaps)
            std_gap = statistics.stdev(gaps) if len(gaps) > 1 else 0
            min_gap = min(gaps)
            max_gap = max(gaps)
            
            print(f"\n  {ALGORITHMS[algo_name]['description']}:")
            print(f"    Average gap: {avg_gap:.2f}%")
            print(f"    Std deviation: {std_gap:.2f}%")
            print(f"    Range: [{min_gap:.2f}%, {max_gap:.2f}%]")
            print(f"    Samples: {len(gaps)} instances")
    
    # Compare against NN+2opt baseline (17.69% on 500-node instances)
    print("\n📊 COMPARISON AGAINST NN+2OPT BASELINE (17.69% on 500-node instances):")
    
    if "v19_christofides_hybrid_structural_fixed" in ALGORITHMS:
        v19_gaps = []
        for instance_name in gap_metrics:
            if "v19_christofides_hybrid_structural_fixed" in gap_metrics[instance_name]:
                v19_gaps.append(gap_metrics[instance_name]["v19_christofides_hybrid_structural_fixed"]["gap_percent"])
        
        if v19_gaps:
            avg_v19_gap = statistics.mean(v19_gaps)
            improvement_over_baseline = 17.69 - avg_v19_gap
            relative_improvement = (improvement_over_baseline / 17.69) * 100
            
            print(f"\n  v19 Christofides Hybrid Structural (Fixed):")
            print(f"    Average gap: {avg_v19_gap:.2f}%")
            print(f"    NN+2opt baseline: 17.69%")
            print(f"    Absolute improvement: {improvement_over_baseline:.2f}%")
            print(f"    Relative improvement: {relative_improvement:.2f}%")
            
            # Novelty verification threshold (0.1%)
            if improvement_over_baseline > 0.1:
                print(f"\n  ✅ NOVELTY CONFIRMED: Exceeds 0.1% improvement threshold")
                print(f"     Improvement: {improvement_over_baseline:.2f}% > 0.1%")
                print(f"     Threshold exceeded by: {improvement_over_baseline - 0.1:.2f}%")
            else:
                print(f"\n  ⚠️ Novelty threshold not met: {improvement_over_baseline:.2f}% ≤ 0.1%")
    
    # Save results to file
    output_file = "corrected_tsplib_evaluation_results_v2.json"
    results_data = {
        "timestamp": datetime.now().isoformat(),
        "authorization": "Vera coordination signal received",
        "instances_evaluated": [i[0] for i in available_instances],
        "algorithms": {name: config["description"] for name, config in ALGORITHMS.items()},
        "all_results": all_results,
        "gap_metrics": gap_metrics,
        "statistical_summary": {
            "nn_2opt_baseline": 17.69,
            "novelty_threshold": 0.1,
            "distance_metric_note": "ATT distance calculation used for att532: ceil(sqrt((dx²+dy²)/10))"
        }
    }
    
    with open(output_file, 'w') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    print("\n" + "=" * 80)
    print("EVALUATION COMPLETE")
    print("=" * 80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

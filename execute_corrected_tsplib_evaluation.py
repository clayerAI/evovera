#!/usr/bin/env python3
"""
Execute Corrected TSPLIB Evaluation
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

def run_algorithm_on_instance(algorithm_config: Dict, instance_name: str, 
                             parser: TSPLIBParser) -> Dict[str, Any]:
    """Run a single algorithm on a single TSPLIB instance."""
    print(f"  Running {algorithm_config['description']} on {instance_name}...")
    
    # Get instance data
    instance_data = parser.get_instance(instance_name)
    if instance_data is None:
        print(f"    ❌ Instance {instance_name} not found")
        return None
    
    points = instance_data["points"]
    distance_matrix = instance_data.get("distance_matrix")
    
    # Create solver
    if distance_matrix is not None:
        # Use distance matrix for TSPLIB compatibility
        solver = algorithm_config["solver_class"](distance_matrix=distance_matrix, **algorithm_config["params"])
    else:
        # Fallback to points
        solver = algorithm_config["solver_class"](points=points, **algorithm_config["params"])
    
    # Solve with timing
    start_time = time.time()
    try:
        tour, tour_length = solver.solve()
        solve_time = time.time() - start_time
        
        # Verify tour length matches distance matrix calculation
        if distance_matrix is not None:
            calculated_length = 0
            n = len(tour)
            for i in range(n):
                calculated_length += distance_matrix[tour[i], tour[(i + 1) % n]]
            
            # Check for consistency (allow small floating point differences)
            if abs(calculated_length - tour_length) > 1e-6:
                print(f"    ⚠️ Tour length mismatch: solver={tour_length:.2f}, calculated={calculated_length:.2f}")
                tour_length = calculated_length  # Use calculated length
        
        return {
            "tour_length": float(tour_length),
            "solve_time": solve_time,
            "tour": tour[:10] if len(tour) > 10 else tour,  # Store first 10 cities only
            "success": True
        }
        
    except Exception as e:
        print(f"    ❌ Error running algorithm: {e}")
        return {
            "tour_length": None,
            "solve_time": None,
            "tour": [],
            "success": False,
            "error": str(e)
        }

def calculate_gap_metrics(results: Dict, optimal_values: Dict) -> Dict:
    """Calculate gap-to-optimal metrics."""
    gaps = {}
    
    for instance_name in TSPLIB_INSTANCES:
        if instance_name not in results or instance_name not in optimal_values:
            continue
            
        instance_results = results[instance_name]
        optimal = optimal_values.get(instance_name)
        
        if optimal is None:
            continue
            
        instance_gaps = {}
        for algo_name, algo_result in instance_results.items():
            if algo_result["success"] and algo_result["tour_length"] is not None:
                tour_length = algo_result["tour_length"]
                gap = ((tour_length - optimal) / optimal) * 100 if optimal > 0 else float('inf')
                instance_gaps[algo_name] = {
                    "gap_percent": gap,
                    "tour_length": tour_length,
                    "optimal": optimal
                }
        
        gaps[instance_name] = instance_gaps
    
    return gaps

def main():
    """Main evaluation function."""
    print("=" * 80)
    print("EXECUTING CORRECTED TSPLIB EVALUATION")
    print("Authorized by Vera coordination signal")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)
    
    # Initialize TSPLIB parser
    print("\n📂 Initializing TSPLIB parser...")
    parser = TSPLIBParser()
    
    # Check instance availability
    print("\n🔍 Checking TSPLIB instance availability...")
    available_instances = []
    for instance in TSPLIB_INSTANCES:
        if parser.has_instance(instance):
            available_instances.append(instance)
            print(f"  ✓ {instance} available")
        else:
            print(f"  ❌ {instance} NOT available")
    
    if len(available_instances) < len(TSPLIB_INSTANCES):
        print(f"\n⚠️ Warning: Only {len(available_instances)}/{len(TSPLIB_INSTANCES)} instances available")
        print("  Some instances may need to be downloaded.")
    
    # Run evaluation
    print("\n🚀 Starting TSPLIB evaluation...")
    all_results = {}
    
    for instance_name in available_instances:
        print(f"\n📊 Evaluating {instance_name}...")
        instance_results = {}
        
        for algo_name, algo_config in ALGORITHMS.items():
            result = run_algorithm_on_instance(algo_config, instance_name, parser)
            if result:
                instance_results[algo_name] = result
                if result["success"]:
                    print(f"    ✓ {algo_config['description']}: {result['tour_length']:.2f} (took {result['solve_time']:.2f}s)")
                else:
                    print(f"    ❌ {algo_config['description']}: Failed - {result.get('error', 'Unknown error')}")
        
        all_results[instance_name] = instance_results
    
    # Known optimal/best-known values for TSPLIB instances
    # Source: TSPLIB documentation and literature
    optimal_values = {
        "eil51": 426,      # Known optimal for eil51
        "kroA100": 21282,  # Known optimal for kroA100
        "a280": 2579,      # Known optimal for a280
        "att532": 27686    # Known optimal for att532 (with ATT distance)
    }
    
    # Calculate gap metrics
    print("\n📈 Calculating gap-to-optimal metrics...")
    gap_metrics = calculate_gap_metrics(all_results, optimal_values)
    
    # Print summary
    print("\n" + "=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)
    
    for instance_name in available_instances:
        print(f"\n📋 {instance_name}:")
        if instance_name in gap_metrics:
            for algo_name, gap_info in gap_metrics[instance_name].items():
                algo_desc = ALGORITHMS[algo_name]["description"]
                print(f"  {algo_desc}:")
                print(f"    Tour length: {gap_info['tour_length']:.2f}")
                print(f"    Optimal/Best-known: {gap_info['optimal']}")
                print(f"    Gap: {gap_info['gap_percent']:.2f}%")
        else:
            print("  No valid results")
    
    # Statistical analysis
    print("\n📊 STATISTICAL ANALYSIS:")
    
    # Calculate average gaps
    for algo_name in ALGORITHMS.keys():
        gaps = []
        for instance_name in available_instances:
            if instance_name in gap_metrics and algo_name in gap_metrics[instance_name]:
                gaps.append(gap_metrics[instance_name][algo_name]["gap_percent"])
        
        if gaps:
            avg_gap = statistics.mean(gaps)
            std_gap = statistics.stdev(gaps) if len(gaps) > 1 else 0
            print(f"  {ALGORITHMS[algo_name]['description']}:")
            print(f"    Average gap: {avg_gap:.2f}%")
            print(f"    Std deviation: {std_gap:.2f}%")
            print(f"    Samples: {len(gaps)} instances")
    
    # Compare against NN+2opt baseline (17.69% on 500-node instances)
    print("\n📊 COMPARISON AGAINST NN+2OPT BASELINE (17.69% on 500-node instances):")
    if "v19_christofides_hybrid_structural_fixed" in ALGORITHMS:
        v19_gaps = []
        for instance_name in available_instances:
            if instance_name in gap_metrics and "v19_christofides_hybrid_structural_fixed" in gap_metrics[instance_name]:
                v19_gaps.append(gap_metrics[instance_name]["v19_christofides_hybrid_structural_fixed"]["gap_percent"])
        
        if v19_gaps:
            avg_v19_gap = statistics.mean(v19_gaps)
            improvement_over_baseline = 17.69 - avg_v19_gap
            print(f"  v19 Average gap: {avg_v19_gap:.2f}%")
            print(f"  Improvement over NN+2opt baseline: {improvement_over_baseline:.2f}%")
            
            # Novelty verification threshold (0.1%)
            if avg_v19_gap < 17.69 - 0.1:
                print(f"  ✅ NOVELTY CONFIRMED: Exceeds 0.1% improvement threshold")
                print(f"     (Improvement: {improvement_over_baseline:.2f}% > 0.1%)")
            else:
                print(f"  ⚠️ Novelty threshold not met: {improvement_over_baseline:.2f}% ≤ 0.1%")
    
    # Save results to file
    output_file = "corrected_tsplib_evaluation_results.json"
    results_data = {
        "timestamp": datetime.now().isoformat(),
        "instances_evaluated": available_instances,
        "algorithms": {name: config["description"] for name, config in ALGORITHMS.items()},
        "results": all_results,
        "gap_metrics": gap_metrics,
        "optimal_values": optimal_values,
        "statistical_summary": {
            "nn_2opt_baseline": 17.69,
            "novelty_threshold": 0.1
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

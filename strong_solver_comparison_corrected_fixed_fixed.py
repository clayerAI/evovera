#!/usr/bin/env python3
"""
Strong Solver Comparison: CORRECTED v19 vs OR-Tools - Critical Correction
Simplified version that follows working pattern from previous comparison.
"""

import sys
import os
import time
import json
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Any

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "solutions"))

# Import TSPLIB parser
from tsplib_parser import TSPLIBParser

# Import CORRECTED v19 algorithm
try:
    from tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected as CorrectedV19Solver
    print("✓ Successfully imported CORRECTED v19 Christofides Hybrid Structural algorithm")
except ImportError as e:
    print(f"❌ Error importing CORRECTED v19 algorithm: {e}")
    sys.exit(1)

# Import OR-Tools
try:
    from ortools.constraint_solver import routing_enums_pb2
    from ortools.constraint_solver import pywrapcp
    print("✓ Successfully imported OR-Tools")
except ImportError as e:
    print(f"❌ Error importing OR-Tools: {e}")
    sys.exit(1)

# TSPLIB instances to evaluate
TSPLIB_INSTANCES = ["eil51", "kroA100"]
TSPLIB_DIR = "data/tsplib"

# Optimal solutions (known from TSPLIB)
OPTIMAL_SOLUTIONS = {
    "eil51": 426,
    "kroA100": 21282
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

def calculate_gap_percent(our_length: float, optimal_length: float) -> float:
    """Calculate gap percentage: (our - optimal) / optimal * 100%."""
    if optimal_length is None or optimal_length == 0:
        return float('inf')
    return ((our_length - optimal_length) / optimal_length) * 100.0

def solve_with_ortools(distance_matrix: np.ndarray, time_limit_seconds: int = 30) -> Tuple[List[int], float]:
    """
    Solve TSP using OR-Tools with given distance matrix.
    
    Args:
        distance_matrix: NxN distance matrix
        time_limit_seconds: Time limit for solver
        
    Returns:
        Tuple of (tour, tour_length)
    """
    n = len(distance_matrix)
    
    # Create routing model
    manager = pywrapcp.RoutingIndexManager(n, 1, 0)  # 1 vehicle, depot at 0
    routing = pywrapcp.RoutingModel(manager)
    
    # Define distance callback
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(distance_matrix[from_node][to_node])
    
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    # Set search parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.seconds = time_limit_seconds
    search_parameters.log_search = False
    
    # Solve
    solution = routing.SolveWithParameters(search_parameters)
    
    if solution:
        # Extract tour
        index = routing.Start(0)
        tour = []
        route_distance = 0
        
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            tour.append(node)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
        
        # Add depot at end to close tour
        tour.append(tour[0])
        
        return tour, route_distance
    else:
        raise RuntimeError("OR-Tools failed to find a solution")

def run_corrected_v19_on_instance(parser: TSPLIBParser, seed: int = 42) -> Dict[str, Any]:
    """
    Run CORRECTED v19 algorithm on TSPLIB instance.
    
    Args:
        parser: TSPLIBParser instance with loaded data
        seed: Random seed for reproducibility
        
    Returns:
        Dictionary with results
    """
    # Get points from parser
    points = np.array(parser.node_coords)
    edge_weight_type = parser.edge_weight_type
    
    # Calculate distance matrix
    distance_matrix = calculate_distance_matrix(points, edge_weight_type)
    
    # Run CORRECTED v19 algorithm
    try:
        solver = CorrectedV19Solver(distance_matrix=distance_matrix, seed=seed)
        start_time = time.time()
        tour, length, runtime = solver.solve(
            percentile_threshold=70,
            within_community_weight=0.8,
            between_community_weight=0.3,
            apply_2opt=True,
            time_limit=60.0
        )
        actual_runtime = time.time() - start_time
        
        return {
            "success": True,
            "tour": tour,
            "tour_length": float(length),
            "runtime": actual_runtime,
            "algorithm_runtime": runtime,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "tour": [],
            "tour_length": float('inf'),
            "runtime": 0.0,
            "algorithm_runtime": 0.0,
            "error": str(e)
        }

def run_ortools_on_instance(parser: TSPLIBParser, time_limit_seconds: int = 30) -> Dict[str, Any]:
    """
    Run OR-Tools on TSPLIB instance.
    
    Args:
        parser: TSPLIBParser instance with loaded data
        time_limit_seconds: Time limit for solver
        
    Returns:
        Dictionary with results
    """
    # Get points from parser
    points = np.array(parser.node_coords)
    edge_weight_type = parser.edge_weight_type
    
    # Calculate distance matrix
    distance_matrix = calculate_distance_matrix(points, edge_weight_type)
    
    # Run OR-Tools
    try:
        start_time = time.time()
        tour, length = solve_with_ortools(distance_matrix, time_limit_seconds)
        runtime = time.time() - start_time
        
        return {
            "success": True,
            "tour": tour,
            "tour_length": float(length),
            "runtime": runtime,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "tour": [],
            "tour_length": float('inf'),
            "runtime": 0.0,
            "error": str(e)
        }

def main():
    """Main function to run corrected strong solver comparison."""
    print("\n" + "="*80)
    print("STRONG SOLVER COMPARISON: CORRECTED v19 vs OR-Tools")
    print("CRITICAL CORRECTION - Using v19 with ALL hybrid structural features")
    print("="*80)
    
    results = {
        "metadata": {
            "comparison_type": "strong_solver_corrected_v19_vs_ortools",
            "date": datetime.now().isoformat(),
            "author": "Evo",
            "correction_note": "CRITICAL: Uses corrected v19 with all hybrid structural features (community detection, edge centrality, MST path analysis, hybrid matching). Previous comparison used simplified v19 missing these features.",
            "instances": TSPLIB_INSTANCES,
            "optimal_solutions": OPTIMAL_SOLUTIONS,
            "seed": 42,
            "ortools_time_limit_seconds": 30,
            "methodology": {
                "v19_parameters": {
                    "percentile_threshold": 70,
                    "within_community_weight": 0.8,
                    "between_community_weight": 0.3,
                    "apply_2opt": True,
                    "time_limit": 60.0
                },
                "ortools_parameters": {
                    "first_solution_strategy": "PATH_CHEAPEST_ARC",
                    "local_search_metaheuristic": "GUIDED_LOCAL_SEARCH",
                    "time_limit_seconds": 30
                }
            },
            "results": {}
        }
    }
    
    # Process each instance
    for instance_name in TSPLIB_INSTANCES:
        print(f"\n{'='*60}")
        print(f"PROCESSING INSTANCE: {instance_name}")
        print(f"{'='*60}")
        
        # Load TSPLIB instance
        instance_path = os.path.join(TSPLIB_DIR, f"{instance_name}.tsp")
        if not os.path.exists(instance_path):
            print(f"❌ Instance file not found: {instance_path}")
            continue
        
        parser = TSPLIBParser(instance_path)
        parser.parse()
        
        print(f"  Dimension: {parser.dimension}")
        print(f"  Edge weight type: {parser.edge_weight_type}")
        print(f"  Optimal solution: {OPTIMAL_SOLUTIONS.get(instance_name, 'Unknown')}")
        
        instance_results = {
            "instance": instance_name,
            "dimension": parser.dimension,
            "edge_weight_type": parser.edge_weight_type,
            "optimal": OPTIMAL_SOLUTIONS.get(instance_name, None),
            "results": {}
        }
        
        optimal_length = OPTIMAL_SOLUTIONS.get(instance_name)
        
        # Run CORRECTED v19 algorithm
        print(f"\n  [CORRECTED v19] Running...")
        v19_result = run_corrected_v19_on_instance(parser, seed=42)
        if v19_result["success"]:
            gap = calculate_gap_percent(v19_result["tour_length"], optimal_length)
            print(f"    ✓ CORRECTED v19: tour_length={v19_result['tour_length']:.1f}, "
                  f"gap={gap:.2f}%, runtime={v19_result['runtime']:.3f}s")
        else:
            gap = float('inf')
            print(f"    ✗ CORRECTED v19: FAILED - {v19_result['error']}")
        
        instance_results["results"]["corrected_v19_christofides_hybrid_structural"] = {
            **v19_result,
            "gap_percent": gap
        }
        
        # Run OR-Tools
        print(f"\n  [OR-Tools] Running...")
        ortools_result = run_ortools_on_instance(parser, time_limit_seconds=30)
        if ortools_result["success"]:
            ortools_gap = calculate_gap_percent(ortools_result["tour_length"], optimal_length)
            print(f"    ✓ OR-Tools: tour_length={ortools_result['tour_length']:.1f}, "
                  f"gap={ortools_gap:.2f}%, runtime={ortools_result['runtime']:.3f}s")
        else:
            ortools_gap = float('inf')
            print(f"    ✗ OR-Tools: FAILED - {ortools_result['error']}")
        
        instance_results["results"]["ortools"] = {
            **ortools_result,
            "gap_percent": ortools_gap
        }
        
        # Calculate performance metrics if both succeeded
        if v19_result["success"] and ortools_result["success"]:
            performance_ratio = v19_result["tour_length"] / ortools_result["tour_length"]
            improvement_needed = gap - ortools_gap if ortools_gap != 0 else gap
            
            instance_results["performance_metrics"] = {
                "performance_ratio": float(performance_ratio),
                "improvement_needed_percent": float(improvement_needed)
            }
            
            print(f"\n  [PERFORMANCE METRICS]")
            print(f"    Performance ratio (v19/OR-Tools): {performance_ratio:.4f}")
            print(f"    Improvement needed: {improvement_needed:.2f}%")
        
        results["metadata"]["results"][instance_name] = instance_results
    
    return results

def save_results(results: Dict[str, Any]):
    """Save results to JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"strong_solver_comparison_corrected_results_{timestamp}.json"
    
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Results saved to: {filename}")
    return filename

def generate_summary(results: Dict[str, Any]):
    """Generate summary of results."""
    print("\n" + "="*80)
    print("SUMMARY: CORRECTED v19 vs OR-Tools Strong Solver Comparison")
    print("="*80)
    
    for instance_name, instance_results in results["metadata"]["results"].items():
        print(f"\n{instance_name}:")
        
        v19_results = instance_results["results"].get("corrected_v19_christofides_hybrid_structural", {})
        ortools_results = instance_results["results"].get("ortools", {})
        
        if v19_results.get("success"):
            v19_gap = v19_results.get("gap_percent", float('inf'))
            print(f"  CORRECTED v19 gap: {v19_gap:.2f}%")
        
        if ortools_results.get("success"):
            ortools_gap = ortools_results.get("gap_percent", float('inf'))
            print(f"  OR-Tools gap: {ortools_gap:.2f}%")
            
            if v19_results.get("success"):
                improvement = v19_gap - ortools_gap if ortools_gap != 0 else v19_gap
                print(f"  Improvement needed: {improvement:.2f}%")
        
        if "performance_metrics" in instance_results:
            metrics = instance_results["performance_metrics"]
            print(f"  Performance ratio: {metrics['performance_ratio']:.4f}")
    
    print(f"\n{'='*80}")
    print("CRITICAL NOTE: This comparison uses CORRECTED v19 with all hybrid structural features")
    print("Previous strong solver comparison used simplified v19 missing these features")
    print("="*80)

if __name__ == "__main__":
    print("Starting CORRECTED strong solver comparison...")
    print("This addresses the critical algorithm mismatch discovered by Vera.")
    
    results = main()
    filename = save_results(results)
    generate_summary(results)
    
    print(f"\n✅ CORRECTED strong solver comparison completed!")
    print(f"   Results saved to: {filename}")
    print(f"   Next: Notify Vera for review and update documentation.")

#!/usr/bin/env python3
"""
Strong Solver Comparison: CORRECTED v19 vs OR-Tools - Critical Correction
Authorized by Vera coordination signal for publication integrity.

Compares CORRECTED v19 Christofides Hybrid Structural algorithm (with all hybrid features)
against OR-Tools (state-of-the-art TSP solver) on completed TSPLIB instances:
- eil51 (51 nodes, EUC_2D)
- kroA100 (100 nodes, EUC_2D)

CRITICAL CORRECTION: Uses corrected v19 algorithm that contains:
1. ALL hybrid structural features from original v19
2. TSPLIB compatibility (distance matrix support)
3. Proper community detection, edge centrality, MST path analysis, etc.

This comparison replaces the invalid strong solver comparison that used
simplified v19 (missing hybrid features).

Requirements:
1. Use same seeds/parameters as previous evaluations
2. Document methodology clearly
3. Maintain repository hygiene at science novel level standards
4. Notify Vera upon completion for novelty review
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

# TSPLIB instances to evaluate (completed instances only)
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
        return distance_matrix[from_node][to_node]
    
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

def solve_with_corrected_v19(distance_matrix: np.ndarray, seed: int = 42) -> Tuple[List[int], float, float]:
    """
    Solve TSP using CORRECTED v19 algorithm with given distance matrix.
    
    Args:
        distance_matrix: NxN distance matrix
        seed: Random seed for reproducibility
        
    Returns:
        Tuple of (tour, tour_length, runtime)
    """
    solver = CorrectedV19Solver(distance_matrix=distance_matrix, seed=seed)
    tour, length, runtime = solver.solve(
        percentile_threshold=70,
        within_community_weight=0.8,
        between_community_weight=0.3,
        apply_2opt=True,
        time_limit=60.0
    )
    return tour, length, runtime

def run_comparison():
    """Run comparison between corrected v19 and OR-Tools."""
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
            "optimal_solutions": OPTIMAL_SOLUTIONS
        },
        "results": {}
    }
    
    parser = TSPLIBParser(TSPLIB_DIR)
    
    for instance_name in TSPLIB_INSTANCES:
        print(f"\n{'='*60}")
        print(f"Instance: {instance_name}")
        print(f"{'='*60}")
        
        # Load instance
        instance = parser.load_instance(instance_name)
        if not instance:
            print(f"❌ Failed to load instance: {instance_name}")
            continue
            
        points = instance["points"]
        edge_weight_type = instance["edge_weight_type"]
        optimal_length = OPTIMAL_SOLUTIONS.get(instance_name)
        
        print(f"  Nodes: {len(points)}")
        print(f"  Edge weight type: {edge_weight_type}")
        print(f"  Optimal solution: {optimal_length}")
        
        # Calculate distance matrix
        dist_matrix = calculate_distance_matrix(points, edge_weight_type)
        
        instance_results = {
            "nodes": len(points),
            "edge_weight_type": edge_weight_type,
            "optimal_length": optimal_length
        }
        
        # Run OR-Tools (strong solver baseline)
        print(f"\n  [OR-Tools] Solving...")
        try:
            ortools_start = time.time()
            ortools_tour, ortools_length = solve_with_ortools(dist_matrix, time_limit_seconds=30)
            ortools_runtime = time.time() - ortools_start
            
            ortools_gap = ((ortools_length - optimal_length) / optimal_length * 100) if optimal_length else None
            
            print(f"    Tour length: {ortools_length:.2f}")
            print(f"    Runtime: {ortools_runtime:.2f}s")
            if ortools_gap is not None:
                print(f"    Gap to optimal: {ortools_gap:.2f}%")
            
            instance_results["ortools"] = {
                "tour_length": float(ortools_length),
                "runtime": ortools_runtime,
                "gap_percent": float(ortools_gap) if ortools_gap is not None else None,
                "tour": ortools_tour
            }
        except Exception as e:
            print(f"    ❌ OR-Tools failed: {e}")
            instance_results["ortools"] = {"error": str(e)}
        
        # Run CORRECTED v19
        print(f"\n  [CORRECTED v19] Solving...")
        try:
            v19_tour, v19_length, v19_runtime = solve_with_corrected_v19(dist_matrix, seed=42)
            
            v19_gap = ((v19_length - optimal_length) / optimal_length * 100) if optimal_length else None
            
            print(f"    Tour length: {v19_length:.2f}")
            print(f"    Runtime: {v19_runtime:.2f}s")
            if v19_gap is not None:
                print(f"    Gap to optimal: {v19_gap:.2f}%")
            
            instance_results["corrected_v19"] = {
                "tour_length": float(v19_length),
                "runtime": v19_runtime,
                "gap_percent": float(v19_gap) if v19_gap is not None else None,
                "tour": v19_tour
            }
            
            # Calculate performance ratio
            if "ortools" in instance_results and "tour_length" in instance_results["ortools"]:
                performance_ratio = v19_length / ortools_length
                instance_results["performance_ratio"] = float(performance_ratio)
                print(f"    Performance ratio (v19/OR-Tools): {performance_ratio:.4f}")
                
                # Calculate improvement needed for publication
                if ortools_gap == 0:  # OR-Tools found optimal
                    improvement_needed = v19_gap  # v19 gap is the improvement needed
                    print(f"    Improvement needed (v19 gap to optimal): {improvement_needed:.2f}%")
                else:
                    improvement_needed = v19_gap - ortools_gap
                    print(f"    Improvement needed (v19 gap - OR-Tools gap): {improvement_needed:.2f}%")
            
        except Exception as e:
            print(f"    ❌ CORRECTED v19 failed: {e}")
            instance_results["corrected_v19"] = {"error": str(e)}
        
        results["results"][instance_name] = instance_results
    
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
    
    total_instances = len(results["results"])
    successful_comparisons = 0
    
    for instance_name, instance_results in results["results"].items():
        print(f"\n{instance_name}:")
        
        if "ortools" in instance_results and "gap_percent" in instance_results["ortools"]:
            ortools_gap = instance_results["ortools"]["gap_percent"]
            print(f"  OR-Tools gap: {ortools_gap:.2f}%")
        
        if "corrected_v19" in instance_results and "gap_percent" in instance_results["corrected_v19"]:
            v19_gap = instance_results["corrected_v19"]["gap_percent"]
            print(f"  CORRECTED v19 gap: {v19_gap:.2f}%")
            
            if ortools_gap is not None:
                improvement = v19_gap - ortools_gap if ortools_gap != 0 else v19_gap
                print(f"  Improvement needed: {improvement:.2f}%")
                
                if "performance_ratio" in instance_results:
                    ratio = instance_results["performance_ratio"]
                    print(f"  Performance ratio (v19/OR-Tools): {ratio:.4f}")
        
        if "ortools" in instance_results and "corrected_v19" in instance_results:
            successful_comparisons += 1
    
    print(f"\n{'='*80}")
    print(f"Completed: {successful_comparisons}/{total_instances} instances")
    print("CRITICAL NOTE: This comparison uses CORRECTED v19 with all hybrid structural features")
    print("Previous strong solver comparison used simplified v19 missing these features")
    print("="*80)

if __name__ == "__main__":
    print("Starting CORRECTED strong solver comparison...")
    print("This addresses the critical algorithm mismatch discovered by Vera.")
    
    results = run_comparison()
    filename = save_results(results)
    generate_summary(results)
    
    print(f"\n✅ CORRECTED strong solver comparison completed!")
    print(f"   Results saved to: {filename}")
    print(f"   Next: Notify Vera for review and update documentation.")

#!/usr/bin/env python3
"""
Strong Solver Comparison: v19 vs OR-Tools
Authorized by Vera coordination signal for publication readiness.

Compares v19 Christofides Hybrid Structural algorithm against
OR-Tools (state-of-the-art TSP solver) on completed TSPLIB instances:
- eil51 (51 nodes, EUC_2D)
- kroA100 (100 nodes, EUC_2D)

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

# Import v19 algorithm
try:
    from tsp_v19_christofides_hybrid_structural_fixed import ChristofidesHybridStructural as V19Solver
    print("✓ Successfully imported v19 Christofides Hybrid Structural algorithm")
except ImportError as e:
    print(f"❌ Error importing v19 algorithm: {e}")
    sys.exit(1)

# Import OR-Tools
try:
    import ortools.constraint_solver.pywrapcp as cp
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
    manager = cp.RoutingIndexManager(n, 1, 0)  # 1 vehicle, depot at 0
    routing = cp.RoutingModel(manager)
    
    # Define distance callback
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(distance_matrix[from_node][to_node])
    
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    # Set search parameters
    search_parameters = cp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        cp.RoutingModel.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        cp.RoutingModel.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.seconds = time_limit_seconds
    search_parameters.log_search = False
    
    # Solve
    solution = routing.SolveWithParameters(search_parameters)
    
    if solution:
        # Extract tour
        tour = []
        index = routing.Start(0)
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            tour.append(node)
            index = solution.Value(routing.NextVar(index))
        
        # Calculate tour length
        tour_length = 0
        for i in range(len(tour)):
            from_node = tour[i]
            to_node = tour[(i + 1) % len(tour)]
            tour_length += distance_matrix[from_node][to_node]
        
        return tour, float(tour_length)
    else:
        raise RuntimeError("OR-Tools failed to find a solution")

def run_v19_on_instance(parser: TSPLIBParser, seed: int = 42) -> Dict[str, Any]:
    """Run v19 algorithm on a parsed TSPLIB instance."""
    print(f"  Running v19 Christofides Hybrid Structural...")
    
    # Get points from parser
    points = np.array(parser.node_coords)
    
    # Calculate distance matrix based on edge weight type
    distance_matrix = calculate_distance_matrix(points, parser.edge_weight_type)
    
    # Create solver with distance matrix
    solver = V19Solver(distance_matrix=distance_matrix, seed=seed)
    
    # Solve with timing
    start_time = time.time()
    try:
        tour = solver.solve()
        end_time = time.time()
        
        # Calculate tour length
        tour_length = 0
        for i in range(len(tour)):
            from_node = tour[i]
            to_node = tour[(i + 1) % len(tour)]
            tour_length += distance_matrix[from_node][to_node]
        
        runtime = end_time - start_time
        success = True
        timeout = False
        
    except Exception as e:
        print(f"    ❌ Error: {e}")
        tour_length = float('inf')
        runtime = 0
        success = False
        timeout = False
        tour = []
    
    return {
        "tour": tour,
        "tour_length": float(tour_length),
        "runtime": runtime,
        "success": success,
        "timeout": timeout
    }

def run_ortools_on_instance(parser: TSPLIBParser, time_limit_seconds: int = 30) -> Dict[str, Any]:
    """Run OR-Tools on a parsed TSPLIB instance."""
    print(f"  Running OR-Tools (time limit: {time_limit_seconds}s)...")
    
    # Get points from parser
    points = np.array(parser.node_coords)
    
    # Calculate distance matrix based on edge weight type
    distance_matrix = calculate_distance_matrix(points, parser.edge_weight_type)
    
    # Solve with timing
    start_time = time.time()
    try:
        tour, tour_length = solve_with_ortools(distance_matrix, time_limit_seconds)
        end_time = time.time()
        
        runtime = end_time - start_time
        success = True
        timeout = runtime >= time_limit_seconds
        
    except Exception as e:
        print(f"    ❌ Error: {e}")
        tour_length = float('inf')
        runtime = 0
        success = False
        timeout = False
        tour = []
    
    return {
        "tour": tour,
        "tour_length": float(tour_length),
        "runtime": runtime,
        "success": success,
        "timeout": timeout
    }

def calculate_gap_percent(tour_length: float, optimal: float) -> float:
    """Calculate gap percentage: (tour_length - optimal) / optimal * 100"""
    if tour_length == float('inf'):
        return float('inf')
    return ((tour_length - optimal) / optimal) * 100.0

def main():
    """Main execution function."""
    print("=" * 80)
    print("STRONG SOLVER COMPARISON: v19 vs OR-Tools")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Instances: {', '.join(TSPLIB_INSTANCES)}")
    print(f"Seed: 42 (consistent with previous evaluations)")
    print()
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "instances": TSPLIB_INSTANCES,
        "seed": 42,
        "ortools_time_limit_seconds": 30,
        "results": {}
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
        
        # Run v19 algorithm
        v19_result = run_v19_on_instance(parser, seed=42)
        if v19_result["success"]:
            gap = calculate_gap_percent(v19_result["tour_length"], OPTIMAL_SOLUTIONS[instance_name])
            print(f"    ✓ v19: tour_length={v19_result['tour_length']:.1f}, "
                  f"gap={gap:.2f}%, runtime={v19_result['runtime']:.3f}s")
        else:
            gap = float('inf')
            print(f"    ✗ v19: FAILED")
        
        instance_results["results"]["v19_christofides_hybrid_structural"] = {
            **v19_result,
            "gap_percent": gap
        }
        
        # Run OR-Tools
        ortools_result = run_ortools_on_instance(parser, time_limit_seconds=30)
        if ortools_result["success"]:
            gap = calculate_gap_percent(ortools_result["tour_length"], OPTIMAL_SOLUTIONS[instance_name])
            print(f"    ✓ OR-Tools: tour_length={ortools_result['tour_length']:.1f}, "
                  f"gap={gap:.2f}%, runtime={ortools_result['runtime']:.3f}s")
        else:
            gap = float('inf')
            print(f"    ✗ OR-Tools: FAILED")
        
        instance_results["results"]["ortools"] = {
            **ortools_result,
            "gap_percent": gap
        }
        
        # Calculate performance ratio
        if v19_result["success"] and ortools_result["success"]:
            ratio = v19_result["tour_length"] / ortools_result["tour_length"]
            print(f"    Performance ratio (v19/OR-Tools): {ratio:.4f}")
            instance_results["performance_ratio"] = ratio
        
        results["results"][instance_name] = instance_results
    
    # Save results
    output_file = "strong_solver_comparison_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n{'='*80}")
    print(f"RESULTS SAVED TO: {output_file}")
    print(f"{'='*80}")
    
    # Generate summary
    print("\nSUMMARY:")
    print("-" * 40)
    for instance_name in TSPLIB_INSTANCES:
        if instance_name in results["results"]:
            instance_data = results["results"][instance_name]
            v19_gap = instance_data["results"]["v19_christofides_hybrid_structural"]["gap_percent"]
            ortools_gap = instance_data["results"]["ortools"]["gap_percent"]
            
            print(f"{instance_name}:")
            print(f"  v19 gap: {v19_gap:.2f}%")
            print(f"  OR-Tools gap: {ortools_gap:.2f}%")
            
            if "performance_ratio" in instance_data:
                ratio = instance_data["performance_ratio"]
                print(f"  v19/OR-Tools ratio: {ratio:.4f} ({ratio*100:.1f}% of OR-Tools quality)")
            print()

if __name__ == "__main__":
    main()

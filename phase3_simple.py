#!/usr/bin/env python3
"""Simple Phase 3 evaluation - test with eil51 first."""

import sys
import os
import time
import json
import statistics
sys.path.append('.')

# Import v11 algorithm
try:
    from solutions.tsp_v19_optimized_fixed_v11_optimized import ChristofidesHybridStructuralOptimizedV11
    print("✓ Loaded v11 algorithm")
except ImportError as e:
    print(f"ERROR: {e}")
    sys.exit(1)

# Import TSPLIB parser
try:
    from tsplib_parser import TSPLIBParser
    print("✓ Loaded TSPLIB parser")
except ImportError as e:
    print(f"ERROR: {e}")
    sys.exit(1)

# Import OR-Tools
try:
    from ortools.constraint_solver import routing_enums_pb2
    from ortools.constraint_solver import pywrapcp
    print("✓ Loaded OR-Tools")
except ImportError as e:
    print(f"ERROR: {e}")
    sys.exit(1)

def solve_with_ortools(distance_matrix, time_limit_seconds=60):
    """Solve TSP with OR-Tools."""
    n = len(distance_matrix)
    manager = pywrapcp.RoutingIndexManager(n, 1, 0)  # 1 vehicle, depot at 0
    
    routing = pywrapcp.RoutingModel(manager)
    
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        # Handle both numpy arrays and Python lists
        val = distance_matrix[from_node][to_node]
        if hasattr(val, 'item'):  # numpy scalar
            return int(val.item())
        return int(val)
    
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
        index = routing.Start(0)
        route = []
        route_distance = 0
        while not routing.IsEnd(index):
            route.append(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
        return route, route_distance
    return None, None

# Test with eil51 first
instance_file = "data/tsplib/eil51.tsp"
optimal = 426
num_seeds = 2  # Start with 2 seeds for testing

print(f"\nTesting eil51: {instance_file}")
print(f"Optimal: {optimal}")
print(f"Seeds: {num_seeds}")

# Parse instance
parser = TSPLIBParser(instance_file)
if not parser.parse():
    print(f'ERROR: Failed to parse {instance_file}')
    sys.exit(1)

points = parser.get_coordinates()
dist_matrix_np = parser.get_distance_matrix()
n_nodes = len(points)
print(f"✓ Parsed eil51: {n_nodes} nodes, optimal={parser.optimal_value}")

# Convert numpy array to Python list
if hasattr(dist_matrix_np, 'tolist'):
    dist_matrix = dist_matrix_np.tolist()
else:
    dist_matrix = dist_matrix_np

# Results
v11_gaps = []
v11_runtimes = []
ortools_gaps = []
ortools_runtimes = []

# Process each seed
for seed in range(1, num_seeds + 1):
    print(f"\nSeed {seed}/{num_seeds}:")
    
    # v11
    start_time = time.time()
    solver = ChristofidesHybridStructuralOptimizedV11(dist_matrix, seed=seed)
    tour, tour_length = solver.solve()
    v11_runtime = time.time() - start_time
    v11_gap = ((tour_length - optimal) / optimal) * 100
    print(f"  v11: gap={v11_gap:.2f}%, time={v11_runtime:.2f}s, tour_length={tour_length}")
    v11_gaps.append(v11_gap)
    v11_runtimes.append(v11_runtime)
    
    # OR-Tools
    start_time = time.time()
    ortools_route, ortools_cost = solve_with_ortools(dist_matrix, time_limit_seconds=30)
    ortools_runtime = time.time() - start_time
    
    if ortools_cost:
        ortools_gap = ((ortools_cost - optimal) / optimal) * 100
        print(f"  OR-Tools: gap={ortools_gap:.2f}%, time={ortools_runtime:.2f}s, tour_length={ortools_cost}")
        ortools_gaps.append(ortools_gap)
        ortools_runtimes.append(ortools_runtime)
    else:
        print(f"  OR-Tools: FAILED, time={ortools_runtime:.2f}s")

# Compute statistics
if v11_gaps and ortools_gaps:
    print(f"\n{'='*60}")
    print("RESULTS SUMMARY:")
    print('='*60)
    print(f"v11 average gap: {statistics.mean(v11_gaps):.2f}% ± {statistics.stdev(v11_gaps) if len(v11_gaps) > 1 else 0:.2f}%")
    print(f"v11 average runtime: {statistics.mean(v11_runtimes):.2f}s")
    print(f"OR-Tools average gap: {statistics.mean(ortools_gaps):.2f}% ± {statistics.stdev(ortools_gaps) if len(ortools_gaps) > 1 else 0:.2f}%")
    print(f"OR-Tools average runtime: {statistics.mean(ortools_runtimes):.2f}s")
    
    gap_diff = statistics.mean(v11_gaps) - statistics.mean(ortools_gaps)
    print(f"Gap difference: {gap_diff:.2f}% (v11 - OR-Tools)")
    
    runtime_ratio = statistics.mean(v11_runtimes) / statistics.mean(ortools_runtimes)
    print(f"Runtime ratio: {runtime_ratio:.2f}x (v11/OR-Tools)")
    
    print(f"\nConclusion: OR-Tools is {abs(gap_diff):.2f}% {'better' if gap_diff > 0 else 'worse'} than v11")
    print(f"v11 is {runtime_ratio:.2f}x {'faster' if runtime_ratio < 1 else 'slower'} than OR-Tools")

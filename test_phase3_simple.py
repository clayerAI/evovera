#!/usr/bin/env python3
"""Simple Phase 3 test without Phase 2 results."""

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

def solve_with_ortools(distance_matrix, time_limit_seconds=120):
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

# Test on eil51 with 2 seeds
instance_file = "data/tsplib/eil51.tsp"
print(f"\nTesting on {instance_file}")

# Parse instance
parser = TSPLIBParser(instance_file)
if not parser.parse():
    print(f"ERROR: Failed to parse {instance_file}")
    sys.exit(1)

points = parser.get_coordinates()
dist_matrix_np = parser.get_distance_matrix()
n_nodes = len(points)
optimal = parser.optimal_value

print(f"  Parsed: {n_nodes} nodes, optimal={optimal}")

# Convert numpy array to Python list
if hasattr(dist_matrix_np, 'tolist'):
    dist_matrix = dist_matrix_np.tolist()
else:
    dist_matrix = dist_matrix_np

v11_gaps = []
v11_runtimes = []
ortools_gaps = []
ortools_runtimes = []

num_seeds = 2
for seed in range(1, num_seeds + 1):
    print(f"\n  Seed {seed}/{num_seeds}:")
    
    # Run v11
    start = time.time()
    v11_solver = ChristofidesHybridStructuralOptimizedV11(dist_matrix, seed=seed)
    v11_tour, v11_cost = v11_solver.solve()
    v11_time = time.time() - start
    v11_gap = ((v11_cost - optimal) / optimal) * 100
    v11_gaps.append(v11_gap)
    v11_runtimes.append(v11_time)
    print(f"    v11: gap={v11_gap:.2f}%, time={v11_time:.2f}s")
    
    # Run OR-Tools
    start = time.time()
    ortools_route, ortools_cost = solve_with_ortools(dist_matrix, time_limit_seconds=10)
    ortools_time = time.time() - start
    
    if ortools_cost:
        ortools_gap = ((ortools_cost - optimal) / optimal) * 100
        ortools_gaps.append(ortools_gap)
        ortools_runtimes.append(ortools_time)
        print(f"    OR-Tools: gap={ortools_gap:.2f}%, time={ortools_time:.2f}s")
    else:
        print(f"    OR-Tools: Failed")

# Compute statistics
if v11_gaps and ortools_gaps:
    v11_avg_gap = statistics.mean(v11_gaps)
    ortools_avg_gap = statistics.mean(ortools_gaps)
    v11_avg_time = statistics.mean(v11_runtimes)
    ortools_avg_time = statistics.mean(ortools_runtimes)
    
    print(f"\n=== RESULTS ===")
    print(f"v11 average: {v11_avg_gap:.2f}% gap, {v11_avg_time:.2f}s")
    print(f"OR-Tools average: {ortools_avg_gap:.2f}% gap, {ortools_avg_time:.2f}s")
    print(f"Difference: {v11_avg_gap - ortools_avg_gap:.2f}% (positive means OR-Tools is better)")

print("\n✓ Test completed")

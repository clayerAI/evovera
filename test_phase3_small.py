#!/usr/bin/env python3
"""Small test of Phase 3 evaluation."""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tsplib_parser import TSPLIBParser
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

def solve_tsp_ortools(dist_matrix, time_limit=30):
    """Solve TSP using OR-Tools."""
    n = len(dist_matrix)
    manager = pywrapcp.RoutingIndexManager(n, 1, 0)
    routing = pywrapcp.RoutingModel(manager)
    
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(dist_matrix[from_node][to_node] + 0.5)
    
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(time_limit)
    
    solution = routing.SolveWithParameters(search_parameters)
    
    if solution:
        index = routing.Start(0)
        tour = []
        route_distance = 0
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            tour.append(node)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
        tour.append(manager.IndexToNode(index))
        return tour, route_distance
    return None, None

# Test with eil51
print("Testing Phase 3 with eil51...")
parser = TSPLIBParser('data/tsplib/eil51.tsp')
if parser.parse():
    dist_matrix = parser.get_distance_matrix()
    optimal = 426
    
    print(f"Instance: eil51, nodes: {parser.dimension}, optimal: {optimal}")
    
    # Solve with OR-Tools
    start = time.time()
    tour, distance = solve_tsp_ortools(dist_matrix, time_limit=10)
    runtime = time.time() - start
    
    if tour:
        gap = ((distance - optimal) / optimal) * 100
        print(f"OR-Tools: tour length={distance}, gap={gap:.2f}%, time={runtime:.2f}s")
    else:
        print(f"OR-Tools failed to find solution in {runtime:.2f}s")
else:
    print("Failed to parse eil51")

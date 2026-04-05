#!/usr/bin/env python3
"""Test OR-Tools TSP solver."""

import math
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

def create_distance_matrix(points):
    """Create distance matrix from list of (x, y) points."""
    n = len(points)
    dist_matrix = [[0] * n for _ in range(n)]
    for i in range(n):
        xi, yi = points[i]
        for j in range(n):
            if i != j:
                xj, yj = points[j]
                dist_matrix[i][j] = int(math.sqrt((xi - xj)**2 + (yi - yj)**2) + 0.5)
    return dist_matrix

def solve_tsp_ortools(points, time_limit_seconds=30):
    """Solve TSP using OR-Tools."""
    # Create distance matrix
    dist_matrix = create_distance_matrix(points)
    n = len(points)
    
    # Create routing index manager
    manager = pywrapcp.RoutingIndexManager(n, 1, 0)  # 1 vehicle, depot at 0
    
    # Create routing model
    routing = pywrapcp.RoutingModel(manager)
    
    def distance_callback(from_index, to_index):
        """Return distance between two nodes."""
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return dist_matrix[from_node][to_node]
    
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    # Set search parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(time_limit_seconds)
    
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
        
        # Add depot at end to complete cycle
        tour.append(manager.IndexToNode(index))
        return tour, route_distance
    else:
        return None, None

if __name__ == "__main__":
    # Test with a simple instance
    points = [(0, 0), (1, 0), (0, 1), (1, 1)]
    tour, distance = solve_tsp_ortools(points)
    print(f"Tour: {tour}")
    print(f"Distance: {distance}")

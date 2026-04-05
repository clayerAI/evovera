import numpy as np
import time
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

def solve_with_ortools(distance_matrix: np.ndarray, time_limit_seconds: int = 30):
    """
    Solve TSP using OR-Tools with given distance matrix.
    
    Args:
        distance_matrix: NxN distance matrix
        time_limit_seconds: Time limit for solver
        
    Returns:
        Tuple of (tour, tour_length)
    """
    n = len(distance_matrix)
    print(f"Distance matrix shape: {distance_matrix.shape}")
    print(f"First few distances: {distance_matrix[0][:5]}")
    
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
    print("Starting OR-Tools solver...")
    solution = routing.SolveWithParameters(search_parameters)
    
    if solution:
        print("OR-Tools found a solution!")
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
        
        print(f"Tour length: {len(tour)} nodes")
        print(f"Route distance: {route_distance}")
        print(f"Tour: {tour[:10]}...")
        
        return tour, route_distance
    else:
        print("OR-Tools failed to find a solution")
        raise RuntimeError("OR-Tools failed to find a solution")

# Test with a simple distance matrix
if __name__ == "__main__":
    # Create a simple 5x5 distance matrix
    np.random.seed(42)
    n = 5
    points = np.random.rand(n, 2) * 100
    
    # Calculate Euclidean distances
    distance_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                distance_matrix[i][j] = np.linalg.norm(points[i] - points[j])
    
    print("Testing OR-Tools with simple 5-node problem...")
    try:
        tour, length = solve_with_ortools(distance_matrix, time_limit_seconds=5)
        print(f"Success! Tour: {tour}, Length: {length}")
    except Exception as e:
        print(f"Error: {e}")

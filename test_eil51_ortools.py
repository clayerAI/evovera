import numpy as np
import time
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

# Simple test with eil51-like data
def test_ortools():
    # Create a simple 51-node problem
    np.random.seed(42)
    n = 51
    points = np.random.rand(n, 2) * 100
    
    # Calculate Euclidean distances
    distance_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                # Round to nearest integer like the script does
                dist = np.linalg.norm(points[i] - points[j])
                distance_matrix[i][j] = round(dist)
    
    print(f"Distance matrix shape: {distance_matrix.shape}")
    print(f"Sample distances from node 0: {distance_matrix[0][:5]}")
    print(f"Min distance (non-zero): {distance_matrix[distance_matrix > 0].min()}")
    print(f"Max distance: {distance_matrix.max()}")
    
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
    search_parameters.time_limit.seconds = 5
    search_parameters.log_search = False
    
    # Solve
    print("Starting OR-Tools solver...")
    start_time = time.time()
    solution = routing.SolveWithParameters(search_parameters)
    runtime = time.time() - start_time
    
    if solution:
        print(f"OR-Tools found a solution in {runtime:.2f}s!")
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
        print(f"First 10 nodes: {tour[:10]}")
        
        return tour, route_distance
    else:
        print("OR-Tools failed to find a solution")
        return [], 0

if __name__ == "__main__":
    tour, length = test_ortools()
    print(f"\nFinal result: Tour length={length}")

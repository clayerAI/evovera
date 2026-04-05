import sys
sys.path.append('.')
import numpy as np
import time
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from tsplib_parser import TSPLIBParser

def solve_with_ortools_debug(distance_matrix: np.ndarray, time_limit_seconds: int = 30):
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
    print(f"First few distances from node 0: {distance_matrix[0][:5]}")
    
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
    start_time = time.time()
    solution = routing.SolveWithParameters(search_parameters)
    runtime = time.time() - start_time
    
    if solution:
        print(f"OR-Tools found a solution in {runtime:.2f}s!")
        
        # Extract tour
        index = routing.Start(0)
        tour = []
        route_distance = 0
        
        print(f"Starting index: {index}")
        print(f"IsEnd(start): {routing.IsEnd(index)}")
        
        node_count = 0
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            tour.append(node)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
            
            node_count += 1
            if node_count > n + 5:  # Safety check
                print(f"WARNING: Too many nodes ({node_count}), breaking loop")
                break
        
        print(f"Final index: {index}")
        print(f"IsEnd(final): {routing.IsEnd(index)}")
        
        # Add depot at end to close tour
        if tour:
            tour.append(tour[0])
        
        print(f"Tour length: {len(tour)} nodes")
        print(f"Route distance: {route_distance}")
        print(f"First 10 nodes: {tour[:10]}")
        
        return tour, route_distance
    else:
        print("OR-Tools failed to find a solution")
        raise RuntimeError("OR-Tools failed to find a solution")

# Load eil51
parser = TSPLIBParser("data/tsplib/eil51.tsp")
success = parser.parse()

if success:
    print(f"Successfully loaded eil51")
    print(f"Number of nodes: {parser.dimension}")
    
    # Calculate distance matrix
    n = parser.dimension
    points = np.array(parser.node_coords)
    
    # Use the same calculation as in the script
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            dx = points[i][0] - points[j][0]
            dy = points[i][1] - points[j][1]
            
            if parser.edge_weight_type == "EUC_2D":
                # Euclidean distance rounded to nearest integer
                dist = round(np.sqrt(dx*dx + dy*dy))
            else:
                dist = round(np.sqrt(dx*dx + dy*dy))
            
            dist_matrix[i][j] = dist
            dist_matrix[j][i] = dist
    
    print(f"\nTesting OR-Tools on eil51...")
    try:
        tour, length = solve_with_ortools_debug(dist_matrix, time_limit_seconds=10)
        print(f"\nSuccess! Tour length: {length}")
    except Exception as e:
        print(f"\nError: {e}")
else:
    print("Failed to load eil51")

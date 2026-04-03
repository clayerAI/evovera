import numpy as np
import random
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the actual algorithm
from tsp_v4_nn_ils_hybrid import solve_tsp, create_distance_matrix, tour_length

np.random.seed(42)
random.seed(42)

# Medium test case
n = 20
points = np.random.rand(n, 2) * 100

print(f"Testing with n={n}")

# Run the algorithm
tour, length, stats = solve_tsp(points, time_limit=10.0)
print(f"\nAlgorithm result:")
print(f"Length: {length}")
print(f"Stats keys: {list(stats.keys())}")
print(f"Elapsed time: {stats['elapsed_time']:.3f}s")
print(f"Restarts: {stats['restarts']}")
print(f"Total iterations: {stats['total_iterations']}")

# Calculate NN baseline
dist_matrix = create_distance_matrix(points)

def nearest_neighbor_tour(dist_matrix, start_node=0):
    n = len(dist_matrix)
    unvisited = set(range(n))
    tour = [start_node]
    unvisited.remove(start_node)
    
    current = start_node
    while unvisited:
        nearest = min(unvisited, key=lambda node: dist_matrix[current][node])
        tour.append(nearest)
        unvisited.remove(nearest)
        current = nearest
    
    return tour

nn_tour = nearest_neighbor_tour(dist_matrix)
nn_length = tour_length(nn_tour, dist_matrix)
print(f"\nNN baseline:")
print(f"Length: {nn_length}")
print(f"Improvement vs NN: {nn_length / length if length > 0 else 'N/A'}")

# Check if tour is valid
def validate_tour(tour, n):
    if len(tour) != n:
        return False
    if set(tour) != set(range(n)):
        return False
    if len(tour) != len(set(tour)):
        return False
    return True

print(f"\nTour valid: {validate_tour(tour, n)}")

# Check a few edge lengths
print("\nChecking first few edge lengths:")
for i in range(min(5, n)):
    j = (i + 1) % n
    edge_length = dist_matrix[tour[i]][tour[j]]
    print(f"Edge {tour[i]}-{tour[j]}: {edge_length}")

# Check if length is reasonable
# For n points in [0,100]², typical TSP length is O(n * avg_distance)
# avg_distance ~ 50-60, so length should be ~ 50*n = 1000 for n=20
print(f"\nIs length reasonable? {abs(length) < 10000} (should be < 10000 for n=20)")
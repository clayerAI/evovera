import numpy as np
import random
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the actual algorithm
from tsp_v4_nn_ils_hybrid import solve_tsp, create_distance_matrix, tour_length

np.random.seed(42)
random.seed(42)

# Very small test case
n = 5
points = np.random.rand(n, 2) * 100

print(f"Testing with n={n}")
print(f"Points:\n{points}")

# Run the algorithm
tour, length, stats = solve_tsp(points, time_limit=10.0)
print(f"\nAlgorithm result:")
print(f"Tour: {tour}")
print(f"Length: {length}")
print(f"Stats: {stats}")

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
print(f"Tour: {nn_tour}")
print(f"Length: {nn_length}")

# Manual calculation of tour length
print("\nManual calculation of algorithm tour length:")
manual_length = 0
for i in range(n):
    j = (i + 1) % n
    edge_length = dist_matrix[tour[i]][tour[j]]
    manual_length += edge_length
    print(f"Edge {tour[i]}-{tour[j]}: {edge_length}")
print(f"Total: {manual_length}")

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
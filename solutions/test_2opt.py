import numpy as np
import random

# Simple test case
points = np.array([[0, 0], [1, 0], [1, 1], [0, 1]])
n = len(points)

def euclidean_distance(p1, p2):
    return np.linalg.norm(p1 - p2)

def create_distance_matrix(points):
    n = len(points)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            dist = euclidean_distance(points[i], points[j])
            dist_matrix[i, j] = dist
            dist_matrix[j, i] = dist
    return dist_matrix

dist_matrix = create_distance_matrix(points)
print("Distance matrix:")
print(dist_matrix)

# Test tour: 0-1-2-3 (square)
tour = [0, 1, 2, 3]
print(f"\nOriginal tour: {tour}")

def tour_length(tour, dist_matrix):
    total = 0.0
    n = len(tour)
    for i in range(n):
        j = (i + 1) % n
        total += dist_matrix[tour[i]][tour[j]]
    return total

original_length = tour_length(tour, dist_matrix)
print(f"Original length: {original_length}")

# Manual calculation:
# Edges: 0-1 (1), 1-2 (1), 2-3 (1), 3-0 (1) = total 4
print("Manual edge lengths:")
print(f"0-1: {dist_matrix[0][1]}")
print(f"1-2: {dist_matrix[1][2]}")
print(f"2-3: {dist_matrix[2][3]}")
print(f"3-0: {dist_matrix[3][0]}")

# Now test 2-opt swap
def two_opt_swap(tour, i, j):
    """Perform 2-opt swap between positions i and j."""
    new_tour = tour[:i+1] + tour[i+1:j+1][::-1] + tour[j+1:]
    return new_tour

# Try swapping edge (0-1) and edge (2-3)
# i=0 (edge 0-1), j=2 (edge 2-3)
i, j = 0, 2
new_tour = two_opt_swap(tour, i, j)
print(f"\nAfter 2-opt swap (i={i}, j={j}): {new_tour}")
print(f"New tour length: {tour_length(new_tour, dist_matrix)}")

# What should the new tour be?
# Remove edges (0-1) and (2-3), add edges (0-2) and (1-3)
# New tour: 0-2-1-3
# Length: 0-2 (√2≈1.414), 2-1 (1), 1-3 (√2≈1.414), 3-0 (1) = total ≈4.828
print("\nExpected new tour: [0, 2, 1, 3]")
print(f"Expected length: {dist_matrix[0][2] + dist_matrix[2][1] + dist_matrix[1][3] + dist_matrix[3][0]}")

# Test the gain calculation
a1, a2 = tour[i], tour[(i + 1) % n]
b1, b2 = tour[j], tour[(j + 1) % n]
print(f"\nEdges being removed: ({a1}-{a2}) and ({b1}-{b2})")
print(f"Old segment cost: {dist_matrix[a1][a2] + dist_matrix[b1][b2]}")
print(f"New segment cost: {dist_matrix[a1][b1] + dist_matrix[a2][b2]}")
print(f"Gain: {(dist_matrix[a1][a2] + dist_matrix[b1][b2]) - (dist_matrix[a1][b1] + dist_matrix[a2][b2])}")
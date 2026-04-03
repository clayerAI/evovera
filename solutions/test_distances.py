import numpy as np

# Test with same parameters as benchmark
np.random.seed(42)
n = 50
points = np.random.rand(n, 2) * 100

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

print(f"Distance matrix shape: {dist_matrix.shape}")
print(f"Min distance: {np.min(dist_matrix[dist_matrix > 0])}")
print(f"Max distance: {np.max(dist_matrix)}")
print(f"Mean distance: {np.mean(dist_matrix[dist_matrix > 0])}")

# Check a few random distances
for _ in range(5):
    i, j = np.random.randint(0, n, 2)
    if i != j:
        print(f"Distance {i}-{j}: {dist_matrix[i][j]}")

# Test nearest neighbor tour
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

def tour_length(tour, dist_matrix):
    total = 0.0
    n = len(tour)
    for i in range(n):
        j = (i + 1) % n
        total += dist_matrix[tour[i]][tour[j]]
    return total

tour = nearest_neighbor_tour(dist_matrix)
length = tour_length(tour, dist_matrix)
print(f"\nNN tour length: {length}")

# Now let's manually calculate to verify
manual_length = 0
for i in range(n):
    j = (i + 1) % n
    manual_length += dist_matrix[tour[i]][tour[j]]
print(f"Manual calculation: {manual_length}")
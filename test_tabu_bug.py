import numpy as np
import math

# Create the same test instance
np.random.seed(42)
n = 20
points = [(np.random.uniform(0, 100), np.random.uniform(0, 100)) for _ in range(n)]

# Compute distance matrix manually
dist = np.zeros((n, n))
for i in range(n):
    for j in range(i + 1, n):
        dx = points[i][0] - points[j][0]
        dy = points[i][1] - points[j][1]
        d = math.sqrt(dx*dx + dy*dy)
        dist[i, j] = d
        dist[j, i] = d

print("Distance matrix sample (first 5x5):")
print(dist[:5, :5])
print("\nMax distance in matrix:", np.max(dist))
print("Min non-zero distance:", np.min(dist[dist > 0]))

# Test a simple tour: 0, 1, 2, ..., 19, 0
tour = list(range(n)) + [0]
print(f"\nTour length of simple tour: {sum(dist[tour[i], tour[i+1]] for i in range(n))}")

# Test 2-opt gain calculation for some pairs
def calculate_gain(tour, i, j, dist):
    a, b = tour[i], tour[i + 1]
    c, d = tour[j], tour[j + 1]
    old_distance = dist[a, b] + dist[c, d]
    new_distance = dist[a, c] + dist[b, d]
    return old_distance - new_distance

print("\nTesting some 2-opt gains:")
for i in [0, 5, 10]:
    for j in [i+5, i+10]:
        if j < n:
            gain = calculate_gain(tour, i, j, dist)
            print(f"  Gain for ({i},{j}): {gain:.4f}")
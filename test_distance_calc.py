import numpy as np
import time

# Test distance calculation for att532 (532 nodes)
print("Testing distance calculation for 532 nodes...")

# Create random points
n = 532
points = np.random.rand(n, 2) * 1000

# Method 1: Double loop
print("\nMethod 1: Double loop")
start = time.time()
dist1 = np.zeros((n, n))
for i in range(n):
    for j in range(i + 1, n):
        dx = points[i][0] - points[j][0]
        dy = points[i][1] - points[j][1]
        dist = np.ceil(np.sqrt((dx*dx + dy*dy) / 10.0))
        dist1[i][j] = dist
        dist1[j][i] = dist
print(f"Time: {time.time() - start:.2f}s")

# Method 2: Broadcasting
print("\nMethod 2: Broadcasting")
start = time.time()
x = points[:, 0:1]
y = points[:, 1:2]
dx = x - x.T
dy = y - y.T
dist2 = np.ceil(np.sqrt((dx*dx + dy*dy) / 10.0))
print(f"Time: {time.time() - start:.2f}s")

print("\nDone!")

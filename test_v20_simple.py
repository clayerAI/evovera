#!/usr/bin/env python3
"""
Simple test for v20 algorithm.
"""

import numpy as np
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from solutions.tsp_v20_christofides_structural_ils import solve_tsp as v20_solve_tsp
from solutions.tsp_v19_christofides_hybrid_structural import solve_tsp as v19_solve_tsp

# Generate small test instance
n = 20
np.random.seed(42)
points = np.random.rand(n, 2)

print(f"Testing v20 vs v19 on n={n} instance")
print("="*50)

# Test v19
print("Running v19...")
start = time.time()
v19_tour, v19_length = v19_solve_tsp(points)
v19_time = time.time() - start
print(f"v19: length={v19_length:.4f}, time={v19_time:.2f}s")

# Test v20 with short time limit
print("\nRunning v20 (5s time limit)...")
start = time.time()
v20_tour, v20_length = v20_solve_tsp(points, time_limit=5.0)
v20_time = time.time() - start
print(f"v20: length={v20_length:.4f}, time={v20_time:.2f}s")

# Calculate improvement
if v20_length < v19_length:
    improvement = (v19_length - v20_length) / v19_length * 100
    print(f"\n✅ v20 improves over v19 by {improvement:.2f}%")
else:
    improvement = (v20_length - v19_length) / v19_length * 100
    print(f"\n⚠️  v20 is {improvement:.2f}% worse than v19")

print("\nTest completed.")
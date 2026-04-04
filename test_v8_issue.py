#!/usr/bin/env python3
"""
Test v8 issue with tuple inputs.
"""

import sys
import os
sys.path.append('.')

import numpy as np
import time

# Test imports
print("Testing v8 import...")
try:
    from solutions.tsp_v8_christofides_ils_hybrid_fixed import solve_tsp as solve_tsp_christofides_ils_fixed
    print("✓ v8 import successful")
except ImportError as e:
    print(f"✗ v8 import failed: {e}")
    sys.exit(1)

# Test 1: numpy array input (should work)
print("\nTest 1: numpy array input (n=10)")
np.random.seed(42)
points_np = np.random.rand(10, 2)
print(f"  Input type: {type(points_np)}, shape: {points_np.shape}")

try:
    start_time = time.time()
    tour, length = solve_tsp_christofides_ils_fixed(points_np)
    elapsed = time.time() - start_time
    print(f"  ✓ Success: length = {length:.3f}, time = {elapsed:.3f}s")
except Exception as e:
    print(f"  ✗ Failed: {e}")

# Test 2: list of tuples input (might fail)
print("\nTest 2: list of tuples input (n=10)")
points_tuples = [(x, y) for x, y in np.random.rand(10, 2)]
print(f"  Input type: {type(points_tuples)}, length: {len(points_tuples)}")

try:
    start_time = time.time()
    tour, length = solve_tsp_christofides_ils_fixed(points_tuples)
    elapsed = time.time() - start_time
    print(f"  ✓ Success: length = {length:.3f}, time = {elapsed:.3f}s")
except Exception as e:
    print(f"  ✗ Failed: {e}")
    print(f"  Error type: {type(e).__name__}")

# Test 3: list of lists input
print("\nTest 3: list of lists input (n=10)")
points_lists = [[x, y] for x, y in np.random.rand(10, 2)]
print(f"  Input type: {type(points_lists)}, length: {len(points_lists)}")

try:
    start_time = time.time()
    tour, length = solve_tsp_christofides_ils_fixed(points_lists)
    elapsed = time.time() - start_time
    print(f"  ✓ Success: length = {length:.3f}, time = {elapsed:.3f}s")
except Exception as e:
    print(f"  ✗ Failed: {e}")
    print(f"  Error type: {type(e).__name__}")

print("\nTest complete!")
#!/usr/bin/env python3
"""
Test v19 on n=100 instance.
"""

import sys
import os
sys.path.append('.')

import numpy as np
import time
import math

# Test imports
print("Testing imports...")
try:
    from solutions.tsp_v1_nearest_neighbor import solve_tsp as solve_tsp_nn_2opt
    print("✓ NN+2opt import successful")
except ImportError as e:
    print(f"✗ NN+2opt import failed: {e}")
    sys.exit(1)

try:
    from solutions.tsp_v19_christofides_hybrid_structural import solve_tsp as solve_tsp_christofides_hybrid_structural
    print("✓ v19 import successful")
except ImportError as e:
    print(f"✗ v19 import failed: {e}")
    sys.exit(1)

# Generate n=100 test instance
np.random.seed(42)
points = np.random.rand(100, 2)
print(f"\nGenerated test instance with {len(points)} points")

# Test NN+2opt
print("\nTesting NN+2opt...")
try:
    start_time = time.time()
    tour_nn, length_nn = solve_tsp_nn_2opt(points)
    nn_time = time.time() - start_time
    print(f"✓ NN+2opt: length = {length_nn:.3f}, time = {nn_time:.3f}s")
except Exception as e:
    print(f"✗ NN+2opt failed: {e}")

# Test v19 with timeout
print("\nTesting v19 (timeout: 120 seconds)...")
try:
    start_time = time.time()
    
    # Simple timeout check
    tour_v19, length_v19 = solve_tsp_christofides_hybrid_structural(points)
    
    v19_time = time.time() - start_time
    print(f"✓ v19: length = {length_v19:.3f}, time = {v19_time:.3f}s")
    
    if length_nn and length_v19:
        gap_pct = ((length_v19 - length_nn) / length_nn) * 100
        print(f"  Gap to NN+2opt: {gap_pct:+.2f}%")
        
except Exception as e:
    print(f"✗ v19 failed: {e}")

print("\nTest complete!")
#!/usr/bin/env python3
"""
Simple test of canonical benchmark imports and basic functionality.
"""

import sys
import os
sys.path.append('.')

import numpy as np
import time
import math
import json
from typing import List, Tuple, Dict, Any

# Test imports
print("Testing algorithm imports...")
try:
    from solutions.tsp_v1_nearest_neighbor import solve_tsp as solve_tsp_nn_2opt
    print("✓ NN+2opt import successful")
except ImportError as e:
    print(f"✗ NN+2opt import failed: {e}")

try:
    from solutions.tsp_v2_christofides import solve_tsp as solve_tsp_christofides
    print("✓ Christofides import successful")
except ImportError as e:
    print(f"✗ Christofides import failed: {e}")

try:
    from solutions.tsp_v8_christofides_ils_hybrid_fixed import solve_tsp as solve_tsp_christofides_ils_fixed
    print("✓ v8 (Christofides+ILS) import successful")
except ImportError as e:
    print(f"✗ v8 import failed: {e}")

try:
    from solutions.tsp_v16_christofides_path_centrality import solve_tsp as solve_tsp_christofides_path_centrality
    print("✓ v16 (Christofides+path centrality) import successful")
except ImportError as e:
    print(f"✗ v16 import failed: {e}")

try:
    from solutions.tsp_v18_christofides_community_detection import solve_tsp as solve_tsp_christofides_community_detection
    print("✓ v18 (Christofides+community detection) import successful")
except ImportError as e:
    print(f"✗ v18 import failed: {e}")

try:
    from solutions.tsp_v19_christofides_hybrid_structural import solve_tsp as solve_tsp_christofides_hybrid_structural
    print("✓ v19 (Christofides+hybrid structural) import successful")
except ImportError as e:
    print(f"✗ v19 import failed: {e}")

# Test basic functionality
print("\nTesting basic algorithm functionality...")

def generate_random_instance(n: int, seed: int = 42) -> np.ndarray:
    """Generate random points in [0, 1] scale."""
    np.random.seed(seed)
    return np.random.rand(n, 2)

# Generate a small test instance
points = generate_random_instance(10, seed=42)
print(f"Generated test instance with {len(points)} points")

# Test NN+2opt
try:
    start_time = time.time()
    tour_nn, length_nn = solve_tsp_nn_2opt(points)
    nn_time = time.time() - start_time
    print(f"✓ NN+2opt: tour length = {length_nn:.3f}, time = {nn_time:.3f}s")
except Exception as e:
    print(f"✗ NN+2opt failed: {e}")

# Test v19
try:
    start_time = time.time()
    tour_v19, length_v19 = solve_tsp_christofides_hybrid_structural(points)
    v19_time = time.time() - start_time
    print(f"✓ v19: tour length = {length_v19:.3f}, time = {v19_time:.3f}s")
    
    if length_nn and length_v19:
        gap_pct = ((length_v19 - length_nn) / length_nn) * 100
        print(f"  Gap to NN+2opt: {gap_pct:+.2f}%")
except Exception as e:
    print(f"✗ v19 failed: {e}")

print("\nTest complete!")
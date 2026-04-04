#!/usr/bin/env python3
"""
Minimal benchmark test to identify hanging issues.
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

# Generate small test instance
np.random.seed(42)
points = np.random.rand(20, 2)
print(f"\nGenerated test instance with {len(points)} points")

# Test NN+2opt with timeout
print("\nTesting NN+2opt...")
try:
    start_time = time.time()
    tour_nn, length_nn = solve_tsp_nn_2opt(points)
    nn_time = time.time() - start_time
    print(f"✓ NN+2opt: length = {length_nn:.3f}, time = {nn_time:.3f}s")
except Exception as e:
    print(f"✗ NN+2opt failed: {e}")

# Test v19 with timeout
print("\nTesting v19...")
try:
    start_time = time.time()
    # Set a timeout
    import signal
    
    class TimeoutException(Exception):
        pass
    
    def timeout_handler(signum, frame):
        raise TimeoutException("Timeout")
    
    # Set alarm for 30 seconds
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)
    
    tour_v19, length_v19 = solve_tsp_christofides_hybrid_structural(points)
    
    # Cancel alarm
    signal.alarm(0)
    
    v19_time = time.time() - start_time
    print(f"✓ v19: length = {length_v19:.3f}, time = {v19_time:.3f}s")
    
    if length_nn and length_v19:
        gap_pct = ((length_v19 - length_nn) / length_nn) * 100
        print(f"  Gap to NN+2opt: {gap_pct:+.2f}%")
        
except TimeoutException:
    print("✗ v19 timed out after 30 seconds")
except Exception as e:
    print(f"✗ v19 failed: {e}")

print("\nTest complete!")
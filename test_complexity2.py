#!/usr/bin/env python3
"""
Test algorithm complexity by measuring runtime vs instance size.
"""

import time
import numpy as np
import sys
import os
import signal

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from solutions.tsp_v19_optimized_fixed_v11_proper import ChristofidesHybridStructuralOptimizedV11

def generate_random_points(n):
    """Generate n random points in unit square."""
    return np.random.rand(n, 2).tolist()

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Timed out!")

def test_runtime_scaling():
    """Test runtime scaling with instance size."""
    sizes = [50, 100, 150, 200]
    results = []
    
    # Set up timeout handler
    signal.signal(signal.SIGALRM, timeout_handler)
    
    for n in sizes:
        print(f"\nTesting n={n}...")
        points = generate_random_points(n)
        
        signal.alarm(120)  # 2 minute timeout
        try:
            start_time = time.time()
            solver = ChristofidesHybridStructuralOptimizedV11(points=points)
            tour, length, runtime = solver.solve()
            elapsed = time.time() - start_time
            signal.alarm(0)  # Cancel alarm
            
            results.append((n, elapsed, True))
            print(f"  Success: {elapsed:.2f}s, tour length: {length:.2f}")
            
        except TimeoutException:
            signal.alarm(0)
            results.append((n, None, False))
            print(f"  Timed out after 120s")
        except Exception as e:
            signal.alarm(0)
            results.append((n, None, False))
            print(f"  Error: {e}")
    
    print("\n=== Runtime Scaling Results ===")
    for n, t, success in results:
        if success:
            print(f"n={n}: {t:.2f}s")
        else:
            print(f"n={n}: Failed")

if __name__ == "__main__":
    test_runtime_scaling()

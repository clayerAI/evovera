#!/usr/bin/env python3
import sys
import os
import time
import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tsplib_parser import TSPLIBParser

# Import v19 directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'solutions'))
from tsp_v19_christofides_hybrid_structural_fixed import solve_tsp

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Algorithm timed out")

# Test a280 with reduced parameters
print("Testing a280 with v19 (reduced iterations)...")
filepath = "data/tsplib/a280.tsp"
parser = TSPLIBParser(filepath)
if not parser.parse():
    print(f"✗ Failed to parse {filepath}")
    sys.exit(1)

print(f"✓ Loaded {parser.name}: {parser.dimension} nodes, optimal={parser.optimal_value}")

# Set timeout
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(30)  # 30 second timeout

try:
    start_time = time.time()
    points = parser.get_points_array()
    distance_matrix = parser.get_distance_matrix()
    
    # Run algorithm with reduced parameters
    # We need to modify the algorithm to accept max_iterations parameter
    # Let's try to import the class directly
    from tsp_v19_christofides_hybrid_structural_fixed import ChristofidesHybridStructural
    
    # Create instance with reduced max_iterations
    solver = ChristofidesHybridStructural(max_iterations=100)  # Reduced from 1000
    tour, tour_length = solver.solve(points, distance_matrix=distance_matrix)
    
    runtime = time.time() - start_time
    
    # Calculate gap
    optimal = parser.optimal_value
    gap_percent = ((tour_length - optimal) / optimal) * 100
    
    print(f"✓ Success: length={tour_length:.2f}, gap={gap_percent:.2f}%, time={runtime:.2f}s")
    
except TimeoutException:
    print("✗ Algorithm timed out after 30 seconds")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    signal.alarm(0)  # Disable alarm

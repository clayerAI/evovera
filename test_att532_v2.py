#!/usr/bin/env python3
import sys
import os
import time
import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tsplib_parser import TSPLIBParser

# Import just v1 for testing att532
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'solutions'))

# Simple timeout handler
class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Algorithm timed out")

# Test att532 with v1 only
print("Testing att532 with v1 (NN+2opt)...")
filepath = "data/tsplib/att532.tsp"
parser = TSPLIBParser(filepath)
if not parser.parse():
    print(f"✗ Failed to parse {filepath}")
    sys.exit(1)

print(f"✓ Loaded {parser.name}: {parser.dimension} nodes, optimal={parser.optimal_value}")
print(f"  Edge weight type: {parser.edge_weight_type}")

# Import v1 directly
from tsp_v1_nearest_neighbor_fixed import solve_tsp

# Set timeout
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(60)  # 60 second timeout

try:
    start_time = time.time()
    points = parser.get_points_array()
    distance_matrix = parser.get_distance_matrix()
    
    # Run algorithm
    tour, tour_length = solve_tsp(points, distance_matrix=distance_matrix)
    
    runtime = time.time() - start_time
    
    # Calculate gap
    optimal = parser.optimal_value
    gap_percent = ((tour_length - optimal) / optimal) * 100
    
    print(f"✓ Success: length={tour_length:.2f}, gap={gap_percent:.2f}%, time={runtime:.2f}s")
    
except TimeoutException:
    print("✗ Algorithm timed out after 60 seconds")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    signal.alarm(0)  # Disable alarm

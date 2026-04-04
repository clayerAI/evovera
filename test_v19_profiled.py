#!/usr/bin/env python3
import sys
import os
import time
import cProfile
import pstats
import io

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tsplib_parser import TSPLIBParser

# Import original v19
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'solutions'))
from tsp_v19_christofides_hybrid_structural_fixed import solve_tsp

# Test a280 with profiling
print("Profiling v19 on a280...")
filepath = "data/tsplib/a280.tsp"
parser = TSPLIBParser(filepath)
if not parser.parse():
    print(f"✗ Failed to parse {filepath}")
    sys.exit(1)

print(f"✓ Loaded {parser.name}: {parser.dimension} nodes, optimal={parser.optimal_value}")

points = parser.get_points_array()
distance_matrix = parser.get_distance_matrix()

# Profile the algorithm
pr = cProfile.Profile()
pr.enable()

try:
    start_time = time.time()
    tour, tour_length = solve_tsp(points, distance_matrix=distance_matrix)
    runtime = time.time() - start_time
    
    # Calculate gap
    optimal = parser.optimal_value
    gap_percent = ((tour_length - optimal) / optimal) * 100
    
    print(f"✓ Success: length={tour_length:.2f}, gap={gap_percent:.2f}%, time={runtime:.2f}s")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    pr.disable()
    
    # Print profiling stats
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(20)
    print("\nTop 20 time-consuming functions:")
    print(s.getvalue())

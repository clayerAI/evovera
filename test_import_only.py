#!/usr/bin/env python3
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
print("Testing imports...")

start = time.time()
try:
    from tsplib_parser import TSPLIBParser
    print(f"✓ Imported TSPLIBParser in {time.time()-start:.2f}s")
except Exception as e:
    print(f"✗ Failed to import TSPLIBParser: {e}")

start = time.time()
try:
    from tsp_algorithms_fixed import algorithms
    print(f"✓ Imported tsp_algorithms_fixed in {time.time()-start:.2f}s")
    print(f"  Algorithms: {list(algorithms.keys())}")
except Exception as e:
    print(f"✗ Failed to import tsp_algorithms_fixed: {e}")

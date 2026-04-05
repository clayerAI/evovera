#!/usr/bin/env python3
import sys
import time
import numpy as np
sys.path.insert(0, '.')
sys.path.insert(0, 'solutions')
from tsplib_parser import TSPLIBParser
from tsp_v19_christofides_hybrid_structural_fixed import ChristofidesHybridStructural as V19Solver

print("Testing v19 on a280...")
parser = TSPLIBParser('data/tsplib/a280.tsp')
parser.parse()
points = np.array(parser.node_coords)

x = points[:, 0:1]
y = points[:, 1:2]
dx = x - x.T
dy = y - y.T
dist_matrix = np.round(np.sqrt(dx*dx + dy*dy))

solver = V19Solver(points=points, distance_matrix=dist_matrix)
start = time.time()
try:
    tour, length, runtime = solver.solve(time_limit=300)
    print(f"Success! Length: {length}, Runtime: {runtime:.2f}s, Gap: {(length-2579)/2579*100:.2f}%")
except Exception as e:
    print(f"Error: {e}")
    print(f"Time elapsed: {time.time()-start:.2f}s")

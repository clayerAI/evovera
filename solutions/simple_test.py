import sys
sys.path.append('.')
from tsp_v19_optimized_fixed_v11_clean import ChristofidesHybridStructuralOptimizedV11
import numpy as np

# Create simple test
n = 10
points = [(i, i) for i in range(n)]
solver = ChristofidesHybridStructuralOptimizedV11(points=points)
print("Solver created successfully")

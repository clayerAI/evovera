import sys
sys.path.append('.')
from tsp_v19_optimized_fixed_v11_clean import ChristofidesHybridStructuralOptimizedV11
import numpy as np

# Create simple test
n = 10
points = [(i, i) for i in range(n)]
solver = ChristofidesHybridStructuralOptimizedV11(points=points)
print("Solver created successfully")

try:
    tour, length, runtime = solver.solve()
    print(f"Tour length: {length}")
    print(f"Tour: {tour}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

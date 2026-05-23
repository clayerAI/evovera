
import time
import sys
sys.path.insert(0, 'solutions')

# Read and parse att532
def read_tsp(filename):
    with open(filename) as f:
        lines = f.readlines()
    
    coords = {}
    in_coord = False
    for line in lines:
        line = line.strip()
        if line == "NODE_COORD_SECTION":
            in_coord = True
            continue
        if line == "EOF":
            break
        if in_coord and line:
            parts = line.split()
            if len(parts) == 3:
                node_id = int(parts[0])
                x, y = float(parts[1]), float(parts[2])
                coords[node_id] = (x, y)
    
    return coords

coords = read_tsp('data/tsplib/att532.tsp')
n = len(coords)
print(f"Loaded att532 with {n} nodes")

# Import the v11 and v12b classes
try:
    from tsp_v11_nn_ils_adaptive_memory import adaptive_perturbation, nearest_neighbor_tour, two_opt
    print("Loaded v11 functions")
except Exception as e:
    print(f"Error loading v11: {e}")

try:
    from tsp_v12b_early_stopping_optimized import ChristofidesHybridStructuralOptimizedV11
    print("Loaded v12b class")
except Exception as e:
    print(f"Error loading v12b: {e}")

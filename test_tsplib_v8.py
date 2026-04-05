import numpy as np
import time
import sys
sys.path.append('.')
from solutions.tsp_v19_optimized_fixed_v8 import ChristofidesHybridStructuralOptimizedV8

def parse_tsplib(filename):
    """Parse TSPLIB file."""
    points = []
    reading_nodes = False
    
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('EOF'):
                break
            if reading_nodes:
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        x = float(parts[1])
                        y = float(parts[2])
                        points.append([x, y])
                    except:
                        pass
            elif line.startswith('NODE_COORD_SECTION'):
                reading_nodes = True
    
    return np.array(points)

def test_tsplib_instance(filename, instance_name):
    """Test optimized v8 on a TSPLIB instance."""
    print(f"\n=== Testing {instance_name} ===")
    
    points = parse_tsplib(filename)
    print(f"Points loaded: {len(points)}")
    
    solver = ChristofidesHybridStructuralOptimizedV8(points)
    
    start_time = time.time()
    tour, length, solver_time = solver.solve()
    total_time = time.time() - start_time
    
    print(f"Tour length: {length:.2f}")
    print(f"Solver time: {solver_time:.2f}s")
    print(f"Total time: {total_time:.2f}s")
    print(f"Tour valid: {len(tour) == len(points) + 1 and tour[0] == tour[-1]}")
    
    return length, solver_time, total_time

if __name__ == "__main__":
    # Test on available TSPLIB instances
    instances = [
        ("data/tsplib/eil51.tsp", "eil51"),
        ("data/tsplib/kroA100.tsp", "kroA100"),
        ("data/tsplib/a280.tsp", "a280"),
        ("data/tsplib/att532.tsp", "att532")
    ]
    
    results = {}
    
    for filename, name in instances:
        try:
            length, solver_time, total_time = test_tsplib_instance(filename, name)
            results[name] = {
                'length': length,
                'solver_time': solver_time,
                'total_time': total_time,
                'n': int(name.replace('eil', '').replace('kroA', '').replace('a', '').replace('att', ''))
            }
        except Exception as e:
            print(f"Error testing {name}: {e}")
    
    # Summary
    print("\n=== SUMMARY ===")
    for name, res in results.items():
        print(f"{name} (n={res['n']}): length={res['length']:.2f}, time={res['solver_time']:.2f}s")

#!/usr/bin/env python3
"""Simple test of Christofides-Tabu hybrid."""
import numpy as np
import time
import math
from typing import List, Tuple
from solutions.tsp_v7_christofides_tabu_hybrid import EuclideanTSPChristofidesTabuHybrid

def generate_random_instance(n: int, seed: int = 42) -> List[Tuple[float, float]]:
    """Generate random Euclidean TSP instance."""
    np.random.seed(seed)
    return [(np.random.uniform(0, 100), np.random.uniform(0, 100)) for _ in range(n)]

def main():
    """Test the hybrid algorithm."""
    print("Christofides-Tabu Hybrid Test")
    print("=" * 60)
    
    # Test sizes
    sizes = [20, 50, 100]
    
    for n in sizes:
        print(f"\nTesting n={n}:")
        
        # Generate instance
        points = generate_random_instance(n)
        
        # Create and run hybrid algorithm
        hybrid = EuclideanTSPChristofidesTabuHybrid(points)
        
        start = time.time()
        tour, length = hybrid.solve_tsp()
        elapsed = time.time() - start
        
        print(f"  Tour length: {length:.2f}")
        print(f"  Time: {elapsed:.3f}s")
        print(f"  Tour valid: {len(tour) == n + 1}, starts/ends at 0: {tour[0] == 0 and tour[-1] == 0}")
        
        # Verify tour visits all cities
        visited = set(tour[:-1])  # Exclude final 0
        print(f"  Visits all cities: {len(visited) == n}")
        
        # Calculate actual length to verify
        calc_length = 0
        for i in range(len(tour) - 1):
            dx = points[tour[i]][0] - points[tour[i+1]][0]
            dy = points[tour[i]][1] - points[tour[i+1]][1]
            calc_length += math.sqrt(dx*dx + dy*dy)
        print(f"  Calculated length: {calc_length:.2f} (diff: {abs(length - calc_length):.6f})")

if __name__ == "__main__":
    main()
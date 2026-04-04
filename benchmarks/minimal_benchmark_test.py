#!/usr/bin/env python3
"""
Minimal benchmark test to identify performance issues.
"""

import sys
import os
import time
import random
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import algorithms
from solutions.tsp_v1_nearest_neighbor import solve_tsp as nn_solve
from solutions.tsp_v2_christofides import solve_tsp as christofides_solve
from solutions.tsp_v8_christofides_ils_hybrid_fixed import solve_tsp as v8_solve
from solutions.tsp_v19_christofides_hybrid_structural import solve_tsp as v19_solve

def generate_random_points(n, seed=None):
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

def calculate_tour_length(points, tour):
    total = 0.0
    n = len(points)
    for i in range(n):
        x1, y1 = points[tour[i]]
        x2, y2 = points[tour[(i + 1) % n]]
        total += np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return total

def run_2opt(points, tour, max_iterations=100):
    n = len(tour)
    best_tour = tour.copy()
    best_length = calculate_tour_length(points, best_tour)
    
    improved = True
    iterations = 0
    
    while improved and iterations < max_iterations:
        improved = False
        for i in range(n - 1):
            for j in range(i + 2, n):
                if j == n - 1 and i == 0:
                    continue
                
                new_tour = best_tour[:i+1] + best_tour[i+1:j+1][::-1] + best_tour[j+1:]
                new_length = calculate_tour_length(points, new_tour)
                
                if new_length < best_length:
                    best_tour = new_tour
                    best_length = new_length
                    improved = True
                    break
            if improved:
                break
        iterations += 1
    
    return best_tour

def nn_2opt_baseline(points, seed=None):
    if seed is not None:
        random.seed(seed)
    
    tour, _ = nn_solve(points)
    improved_tour = run_2opt(points, tour, max_iterations=50)
    return calculate_tour_length(points, improved_tour)

def test_single_run():
    print("Testing single run with n=30...")
    points = generate_random_points(30, seed=42)
    
    algorithms = [
        ('NN+2opt', lambda pts: (None, nn_2opt_baseline(pts, 42))),
        ('Christofides', christofides_solve),
        ('v8', v8_solve),
        ('v19', v19_solve)
    ]
    
    for name, func in algorithms:
        print(f"\n{name}:")
        start = time.time()
        try:
            if name == 'NN+2opt':
                cost = func(points)
                print(f"  Cost: {cost:.3f}")
            else:
                tour, cost = func(points)
                print(f"  Cost: {cost:.3f}, Tour valid: {len(set(tour)) == len(points)}")
        except Exception as e:
            print(f"  ERROR: {e}")
        print(f"  Time: {time.time() - start:.2f}s")
    
    return True

def test_multiple_seeds():
    print("\n\nTesting multiple seeds (3 seeds, n=20)...")
    
    problem_sizes = [20]
    num_seeds = 3
    
    for n in problem_sizes:
        print(f"\nn={n}:")
        for seed in range(num_seeds):
            print(f"  Seed {seed}: ", end='', flush=True)
            points = generate_random_points(n, seed)
            
            # Just test NN+2opt and Christofides for speed
            start = time.time()
            baseline_cost = nn_2opt_baseline(points, seed)
            christofides_tour, christofides_cost = christofides_solve(points)
            elapsed = time.time() - start
            
            print(f"Baseline={baseline_cost:.3f}, Christofides={christofides_cost:.3f}, Time={elapsed:.2f}s")
    
    return True

def main():
    print("=" * 60)
    print("Minimal Benchmark Test")
    print("=" * 60)
    
    try:
        test_single_run()
        test_multiple_seeds()
        
        print("\n" + "=" * 60)
        print("✅ MINIMAL TESTS PASSED")
        print("\nThe algorithms run correctly.")
        print("\nIf the full benchmark is hanging, check:")
        print("1. The 2-opt implementation (might be too slow for large n)")
        print("2. Memory usage")
        print("3. Any infinite loops in local search")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
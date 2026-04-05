#!/usr/bin/env python3
"""Test speed without 2-opt to see core algorithm speedup."""

import sys
sys.path.append(".")

import random
import time
from solutions.tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected as OriginalSolver
from solutions.tsp_v19_optimized_fixed_v5 import ChristofidesHybridStructuralOptimized as OptimizedSolver

def generate_points(n, seed=42):
    random.seed(seed)
    return [(random.random() * 100, random.random() * 100) for _ in range(n)]

def test_core_speed(n=100, seeds=3):
    print(f"\n=== CORE ALGORITHM SPEED (no 2-opt, n={n}, seeds={seeds}) ===")
    
    original_times = []
    optimized_times = []
    
    for seed in range(seeds):
        points = generate_points(n, seed)
        
        # Original algorithm without 2-opt
        solver1 = OriginalSolver(points, seed=seed)
        start = time.time()
        tour1, length1, time1 = solver1.solve(apply_2opt=False)
        original_time = time.time() - start
        
        # Optimized algorithm without 2-opt
        solver2 = OptimizedSolver(points, seed=seed)
        start = time.time()
        tour2, length2, time2 = solver2.solve(apply_2opt=False)
        optimized_time = time.time() - start
        
        original_times.append(original_time)
        optimized_times.append(optimized_time)
        
        print(f"\nSeed {seed}:")
        print(f"  Original (no 2-opt): {original_time:.3f}s, length: {length1:.2f}")
        print(f"  Optimized (no 2-opt): {optimized_time:.3f}s, length: {length2:.2f}")
        print(f"  Speedup: {original_time/optimized_time:.1f}x")
        print(f"  Length difference: {length2 - length1:.2f} ({((length2/length1)-1)*100:.2f}%)")
    
    avg_original = sum(original_times) / len(original_times)
    avg_optimized = sum(optimized_times) / len(optimized_times)
    
    print(f"\n=== SUMMARY ===")
    print(f"Average original time (no 2-opt): {avg_original:.3f}s")
    print(f"Average optimized time (no 2-opt): {avg_optimized:.3f}s")
    print(f"Average speedup: {avg_original/avg_optimized:.1f}x")
    
    return avg_original, avg_optimized

def test_scaling_no_2opt():
    print("\n=== SCALING WITHOUT 2-OPT ===")
    
    sizes = [50, 100, 150, 200]
    seed = 42
    
    for n in sizes:
        points = generate_points(n, seed)
        
        solver1 = OriginalSolver(points, seed=seed)
        start = time.time()
        tour1, length1, time1 = solver1.solve(apply_2opt=False)
        original_time = time.time() - start
        
        solver2 = OptimizedSolver(points, seed=seed)
        start = time.time()
        tour2, length2, time2 = solver2.solve(apply_2opt=False)
        optimized_time = time.time() - start
        
        print(f"\nn={n}:")
        print(f"  Original: {original_time:.3f}s, length: {length1:.2f}")
        print(f"  Optimized: {optimized_time:.3f}s, length: {length2:.2f}")
        print(f"  Speedup: {original_time/optimized_time:.1f}x")
        print(f"  Length diff: {length2 - length1:.2f} ({((length2/length1)-1)*100:.2f}%)")

if __name__ == "__main__":
    print("Testing core algorithm speed (without 2-opt)...")
    
    # Test core speed
    test_core_speed(n=100, seeds=3)
    
    # Test scaling
    test_scaling_no_2opt()

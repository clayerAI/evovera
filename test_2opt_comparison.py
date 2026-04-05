#!/usr/bin/env python3
"""Compare original v19 vs optimized v5 with 2-opt enabled."""

import sys
sys.path.append(".")

import random
import time
from solutions.tsp_v19_christofides_hybrid_structural_corrected import solve_tsp as original_solve
from solutions.tsp_v19_optimized_fixed_v5 import solve_tsp as optimized_solve

def generate_points(n, seed=42):
    random.seed(seed)
    return [(random.random() * 100, random.random() * 100) for _ in range(n)]

def test_quality(n=50, seeds=5):
    print(f"\n=== QUALITY COMPARISON (n={n}, seeds={seeds}) ===")
    
    original_lengths = []
    optimized_lengths = []
    original_times = []
    optimized_times = []
    
    for seed in range(seeds):
        points = generate_points(n, seed)
        
        # Original algorithm
        start = time.time()
        original_tour, original_length = original_solve(points, seed=seed)
        original_time = time.time() - start
        
        # Optimized algorithm (v5 with 2-opt)
        start = time.time()
        optimized_tour, optimized_length = optimized_solve(points, seed=seed)
        optimized_time = time.time() - start
        
        original_lengths.append(original_length)
        optimized_lengths.append(optimized_length)
        original_times.append(original_time)
        optimized_times.append(optimized_time)
        
        print(f"\nSeed {seed}:")
        print(f"  Original: {original_length:.2f} ({original_time:.3f}s)")
        print(f"  Optimized: {optimized_length:.2f} ({optimized_time:.3f}s)")
        print(f"  Difference: {optimized_length - original_length:.2f} ({((optimized_length/original_length)-1)*100:.2f}%)")
        print(f"  Speedup: {original_time/optimized_time:.1f}x")
    
    avg_original = sum(original_lengths) / len(original_lengths)
    avg_optimized = sum(optimized_lengths) / len(optimized_lengths)
    avg_original_time = sum(original_times) / len(original_times)
    avg_optimized_time = sum(optimized_times) / len(optimized_times)
    
    print(f"\n=== SUMMARY ===")
    print(f"Average original length: {avg_original:.2f}")
    print(f"Average optimized length: {avg_optimized:.2f}")
    print(f"Average difference: {avg_optimized - avg_original:.2f} ({((avg_optimized/avg_original)-1)*100:.2f}%)")
    print(f"Average original time: {avg_original_time:.3f}s")
    print(f"Average optimized time: {avg_optimized_time:.3f}s")
    print(f"Average speedup: {avg_original_time/avg_optimized_time:.1f}x")
    
    return avg_original, avg_optimized, avg_original_time, avg_optimized_time

def test_scaling():
    print("\n=== SCALING TEST ===")
    
    sizes = [20, 50, 100, 150, 200]
    seed = 42
    
    for n in sizes:
        points = generate_points(n, seed)
        
        # Original algorithm
        start = time.time()
        original_tour, original_length = original_solve(points, seed=seed)
        original_time = time.time() - start
        
        # Optimized algorithm
        start = time.time()
        optimized_tour, optimized_length = optimized_solve(points, seed=seed)
        optimized_time = time.time() - start
        
        print(f"\nn={n}:")
        print(f"  Original: {original_length:.2f} ({original_time:.3f}s)")
        print(f"  Optimized: {optimized_length:.2f} ({optimized_time:.3f}s)")
        print(f"  Difference: {optimized_length - original_length:.2f} ({((optimized_length/original_length)-1)*100:.2f}%)")
        print(f"  Speedup: {original_time/optimized_time:.1f}x")

if __name__ == "__main__":
    print("Testing 2-opt comparison between original v19 and optimized v5...")
    
    # Quick test first
    n = 30
    points = generate_points(n, 42)
    
    print("\nQuick test (n=30):")
    original_tour, original_length = original_solve(points, seed=42)
    print(f"Original: {original_length:.2f}")
    
    optimized_tour, optimized_length = optimized_solve(points, seed=42)
    print(f"Optimized: {optimized_length:.2f}")
    print(f"Difference: {optimized_length - original_length:.2f}")
    
    # Run quality comparison
    test_quality(n=50, seeds=3)
    
    # Run scaling test
    test_scaling()

#!/usr/bin/env python3
"""
Test fixed algorithms on eil51 only.
"""

import numpy as np
import sys
import os
import time
import math

sys.path.append('.')

# Import fixed algorithms
from solutions.tsp_v1_nearest_neighbor_fixed import solve_tsp as nn_solve
from solutions.tsp_v2_christofides_improved_fixed import solve_tsp as christofides_solve
from solutions.tsp_v19_christofides_hybrid_structural_fixed import solve_tsp as hybrid_solve

def att_distance(x1, y1, x2, y2):
    """ATT distance for TSPLIB."""
    dx = x1 - x2
    dy = y1 - y2
    rij = math.sqrt((dx*dx + dy*dy) / 10.0)
    tij = int(rij + 0.5)
    if tij < rij:
        return tij + 1.0
    return float(tij)

def read_tsplib_simple(filepath):
    """Simple TSPLIB reader."""
    points = []
    reading = False
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("NODE_COORD_SECTION"):
                reading = True
                continue
            elif line.startswith("EOF"):
                break
            elif reading and line:
                parts = line.split()
                if len(parts) >= 3:
                    x, y = float(parts[1]), float(parts[2])
                    points.append([x, y])
    
    return np.array(points)

def main():
    """Test eil51 instance."""
    print("Testing eil51 with fixed algorithms...")
    print("=" * 50)
    
    filepath = "data/tsplib/eil51.tsp"
    
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    
    points = read_tsplib_simple(filepath)
    print(f"Points: {len(points)}")
    
    # Create ATT distance matrix
    n = len(points)
    print(f"Creating {n}x{n} ATT distance matrix...")
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                x1, y1 = points[i]
                x2, y2 = points[j]
                dist_matrix[i, j] = att_distance(x1, y1, x2, y2)
    
    print("Distance matrix created.")
    
    # Test v1: Nearest Neighbor
    print("\n1. Testing v1 (Nearest Neighbor)...")
    start = time.time()
    try:
        tour1, length1 = nn_solve(points, distance_matrix=dist_matrix)
        time1 = time.time() - start
        
        # Calculate actual length
        calc_len1 = 0.0
        for k in range(len(tour1)-1):
            calc_len1 += dist_matrix[tour1[k], tour1[k+1]]
        calc_len1 += dist_matrix[tour1[-1], tour1[0]]
        
        print(f"   Tour length: {calc_len1:.2f}")
        print(f"   Time: {time1:.3f}s")
        print(f"   Tour valid: {len(set(tour1)) == n}")
    except Exception as e:
        print(f"   ERROR: {e}")
        calc_len1 = float('inf')
        time1 = 0
    
    # Test v2: Christofides Improved
    print("\n2. Testing v2 (Christofides Improved)...")
    start = time.time()
    try:
        tour2, length2 = christofides_solve(points, distance_matrix=dist_matrix)
        time2 = time.time() - start
        
        calc_len2 = 0.0
        for k in range(len(tour2)-1):
            calc_len2 += dist_matrix[tour2[k], tour2[k+1]]
        calc_len2 += dist_matrix[tour2[-1], tour2[0]]
        
        print(f"   Tour length: {calc_len2:.2f}")
        print(f"   Time: {time2:.3f}s")
        print(f"   Tour valid: {len(set(tour2)) == n}")
    except Exception as e:
        print(f"   ERROR: {e}")
        calc_len2 = float('inf')
        time2 = 0
    
    # Test v19: Christofides Hybrid
    print("\n3. Testing v19 (Christofides Hybrid Structural)...")
    start = time.time()
    try:
        tour19, length19 = hybrid_solve(points, distance_matrix=dist_matrix)
        time19 = time.time() - start
        
        calc_len19 = 0.0
        for k in range(len(tour19)-1):
            calc_len19 += dist_matrix[tour19[k], tour19[k+1]]
        calc_len19 += dist_matrix[tour19[-1], tour19[0]]
        
        print(f"   Tour length: {calc_len19:.2f}")
        print(f"   Time: {time19:.3f}s")
        print(f"   Tour valid: {len(set(tour19)) == n}")
    except Exception as e:
        print(f"   ERROR: {e}")
        calc_len19 = float('inf')
        time19 = 0
    
    # Results summary
    print(f"\n{'='*50}")
    print("RESULTS SUMMARY for eil51")
    print(f"{'='*50}")
    
    lengths = [calc_len1, calc_len2, calc_len19]
    valid_lengths = [l for l in lengths if l != float('inf')]
    
    if valid_lengths:
        best = min(valid_lengths)
        print(f"Best tour length: {best:.2f}")
        
        print("\nGap analysis:")
        names = ["v1 (NN)", "v2 (Christofides)", "v19 (Hybrid)"]
        for name, length in zip(names, lengths):
            if length == float('inf'):
                gap_str = "N/A (failed)"
            else:
                gap = ((length - best) / best) * 100
                gap_str = f"{gap:.2f}%"
            print(f"  {name}: {length:.2f} (gap: {gap_str})")
        
        # Check if v19 improves over v1 and v2
        if calc_len19 != float('inf') and calc_len1 != float('inf'):
            improvement_v1 = ((calc_len1 - calc_len19) / calc_len1) * 100
            print(f"\nv19 improvement over v1: {improvement_v1:.2f}%")
        
        if calc_len19 != float('inf') and calc_len2 != float('inf'):
            improvement_v2 = ((calc_len2 - calc_len19) / calc_len2) * 100
            print(f"v19 improvement over v2: {improvement_v2:.2f}%")
    
    print(f"\n{'='*50}")
    print("Novelty check:")
    print("v19 should show positive improvement over v1 and v2.")
    print("Baseline NN+2opt gap: 17.69% on 500-node instances")
    
    # Save results
    with open("eil51_test_results.txt", "w") as f:
        f.write("eil51 Test Results with Fixed Algorithms\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Points: {n}\n")
        f.write(f"v1 (NN): {calc_len1:.2f} (time: {time1:.3f}s)\n")
        f.write(f"v2 (Christofides): {calc_len2:.2f} (time: {time2:.3f}s)\n")
        f.write(f"v19 (Hybrid): {calc_len19:.2f} (time: {time19:.3f}s)\n")
        
        if valid_lengths:
            best = min(valid_lengths)
            f.write(f"\nBest: {best:.2f}\n")
            for name, length in zip(["v1", "v2", "v19"], lengths):
                if length != float('inf'):
                    gap = ((length - best) / best) * 100
                    f.write(f"{name} gap: {gap:.2f}%\n")
    
    print("\nResults saved to eil51_test_results.txt")
    print("\n✅ eil51 test completed!")

if __name__ == "__main__":
    main()

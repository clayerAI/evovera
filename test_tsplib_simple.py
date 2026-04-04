#!/usr/bin/env python3
"""
Simple test of fixed algorithms on TSPLIB instances.
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

def test_instance(instance_name, filename):
    """Test a single instance."""
    filepath = os.path.join("data", "tsplib", filename)
    
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return None
    
    print(f"\nTesting {instance_name}...")
    points = read_tsplib_simple(filepath)
    print(f"  Points: {len(points)}")
    
    # Create ATT distance matrix
    n = len(points)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                x1, y1 = points[i]
                x2, y2 = points[j]
                dist_matrix[i, j] = att_distance(x1, y1, x2, y2)
    
    # Test algorithms
    results = {}
    
    # v1: Nearest Neighbor
    start = time.time()
    try:
        tour1, length1 = nn_solve(points, distance_matrix=dist_matrix)
        time1 = time.time() - start
        
        # Calculate actual length
        calc_len1 = 0.0
        for k in range(len(tour1)-1):
            calc_len1 += dist_matrix[tour1[k], tour1[k+1]]
        calc_len1 += dist_matrix[tour1[-1], tour1[0]]
        
        results['v1'] = {'length': calc_len1, 'time': time1, 'tour': tour1}
        print(f"  v1 (NN): {calc_len1:.2f}, time: {time1:.3f}s")
    except Exception as e:
        print(f"  v1 error: {e}")
        results['v1'] = {'length': float('inf'), 'time': 0, 'tour': []}
    
    # v2: Christofides Improved
    start = time.time()
    try:
        tour2, length2 = christofides_solve(points, distance_matrix=dist_matrix)
        time2 = time.time() - start
        
        calc_len2 = 0.0
        for k in range(len(tour2)-1):
            calc_len2 += dist_matrix[tour2[k], tour2[k+1]]
        calc_len2 += dist_matrix[tour2[-1], tour2[0]]
        
        results['v2'] = {'length': calc_len2, 'time': time2, 'tour': tour2}
        print(f"  v2 (Christofides): {calc_len2:.2f}, time: {time2:.3f}s")
    except Exception as e:
        print(f"  v2 error: {e}")
        results['v2'] = {'length': float('inf'), 'time': 0, 'tour': []}
    
    # v19: Christofides Hybrid
    start = time.time()
    try:
        tour19, length19 = hybrid_solve(points, distance_matrix=dist_matrix)
        time19 = time.time() - start
        
        calc_len19 = 0.0
        for k in range(len(tour19)-1):
            calc_len19 += dist_matrix[tour19[k], tour19[k+1]]
        calc_len19 += dist_matrix[tour19[-1], tour19[0]]
        
        results['v19'] = {'length': calc_len19, 'time': time19, 'tour': tour19}
        print(f"  v19 (Hybrid): {calc_len19:.2f}, time: {time19:.3f}s")
    except Exception as e:
        print(f"  v19 error: {e}")
        results['v19'] = {'length': float('inf'), 'time': 0, 'tour': []}
    
    return results

def main():
    """Main test function."""
    print("=" * 60)
    print("Corrected TSPLIB Evaluation with Fixed Algorithms")
    print("=" * 60)
    
    instances = [
        ("eil51", "eil51.tsp"),
        ("kroA100", "kroA100.tsp"),
        ("a280", "a280.tsp"),
        ("att532", "att532.tsp")
    ]
    
    all_results = {}
    
    for instance_name, filename in instances:
        results = test_instance(instance_name, filename)
        if results:
            all_results[instance_name] = results
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    for instance_name, results in all_results.items():
        print(f"\n{instance_name}:")
        lengths = [results[algo]['length'] for algo in ['v1', 'v2', 'v19']]
        best = min(lengths)
        
        for algo in ['v1', 'v2', 'v19']:
            length = results[algo]['length']
            if length == float('inf'):
                gap = "N/A"
            else:
                gap = ((length - best) / best) * 100
                gap_str = f"{gap:.2f}%"
            
            algo_name = {
                'v1': 'Nearest Neighbor',
                'v2': 'Christofides Improved',
                'v19': 'Christofides Hybrid'
            }[algo]
            
            print(f"  {algo_name}: {length:.2f} (gap: {gap_str})")
    
    print(f"\n{'='*60}")
    print("Novelty Verification:")
    print(f"{'='*60}")
    print("v19 should show improvement over v1 and v2.")
    print("Baseline NN+2opt gap: 17.69% on 500-node instances")
    
    # Save results
    with open("tsplib_test_results.txt", "w") as f:
        f.write("TSPLIB Test Results with Fixed Algorithms\n")
        f.write("=" * 50 + "\n\n")
        
        for instance_name, results in all_results.items():
            f.write(f"{instance_name}:\n")
            for algo in ['v1', 'v2', 'v19']:
                length = results[algo]['length']
                time_val = results[algo]['time']
                f.write(f"  {algo}: {length:.2f} (time: {time_val:.3f}s)\n")
            f.write("\n")
    
    print("\nResults saved to tsplib_test_results.txt")
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main()

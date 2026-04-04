#!/usr/bin/env python3
"""
Simple test of TSPLIB integration with NN+2opt baseline.
"""

import sys
import os
import time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tsplib_parser import TSPLIBParser

def nearest_neighbor_2opt(points):
    """Simple NN+2opt implementation for testing."""
    n = len(points)
    
    # Nearest neighbor
    visited = [False] * n
    tour = [0]
    visited[0] = True
    
    for _ in range(1, n):
        last = tour[-1]
        best_dist = float('inf')
        best_idx = -1
        
        for i in range(n):
            if not visited[i]:
                dist = np.sqrt(np.sum((points[last] - points[i]) ** 2))
                if dist < best_dist:
                    best_dist = dist
                    best_idx = i
        
        tour.append(best_idx)
        visited[best_idx] = True
    
    # Simple 2-opt improvement (one pass)
    improved = True
    while improved:
        improved = False
        for i in range(n):
            for j in range(i + 2, n):
                # Calculate current distance
                a, b = tour[i], tour[(i + 1) % n]
                c, d = tour[j], tour[(j + 1) % n]
                
                dist_ab = np.sqrt(np.sum((points[a] - points[b]) ** 2))
                dist_cd = np.sqrt(np.sum((points[c] - points[d]) ** 2))
                current = dist_ab + dist_cd
                
                # Calculate new distance if we reverse segment
                dist_ac = np.sqrt(np.sum((points[a] - points[c]) ** 2))
                dist_bd = np.sqrt(np.sum((points[b] - points[d]) ** 2))
                new = dist_ac + dist_bd
                
                if new < current:
                    # Reverse segment from i+1 to j
                    tour[i+1:j+1] = reversed(tour[i+1:j+1])
                    improved = True
                    break
            if improved:
                break
    
    # Calculate total length
    total = 0
    for i in range(n):
        a, b = tour[i], tour[(i + 1) % n]
        total += np.sqrt(np.sum((points[a] - points[b]) ** 2))
    
    return tour, total

def test_single_instance(instance_name):
    """Test NN+2opt on a single TSPLIB instance."""
    filepath = f"data/tsplib/{instance_name}.tsp"
    
    if not os.path.exists(filepath):
        print(f"❌ Missing: {filepath}")
        return None
    
    print(f"\n📋 Testing {instance_name}...")
    
    # Parse instance
    parser = TSPLIBParser(filepath)
    if not parser.parse():
        print(f"  ❌ Failed to parse")
        return None
    
    print(f"  ✓ Parsed: {parser.dimension} points, optimal={parser.optimal_value}")
    
    # Get points
    points = parser.get_points_array()
    
    # Run NN+2opt
    start_time = time.time()
    tour, length = nearest_neighbor_2opt(points)
    runtime = time.time() - start_time
    
    # Calculate gap
    gap = parser.calculate_gap(length)
    
    print(f"  ✓ NN+2opt result: {length:.2f}")
    print(f"  ✓ Gap to optimal: {gap:.2f}%")
    print(f"  ✓ Runtime: {runtime:.2f}s")
    
    return {
        "instance": instance_name,
        "optimal": parser.optimal_value,
        "our_length": length,
        "gap_percent": gap,
        "runtime": runtime,
        "points": len(points)
    }

def main():
    print("=" * 80)
    print("TSPLIB INTEGRATION TEST - NN+2opt Baseline")
    print("=" * 80)
    
    instances = ["eil51", "kroA100", "a280", "att532"]
    
    results = []
    for instance in instances:
        result = test_single_instance(instance)
        if result:
            results.append(result)
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    if results:
        print(f"\n✅ Successfully tested {len(results)} instances:")
        for r in results:
            print(f"  • {r['instance']}: {r['our_length']:.1f} (gap: {r['gap_percent']:.2f}%, time: {r['runtime']:.2f}s)")
        
        avg_gap = sum(r['gap_percent'] for r in results) / len(results)
        print(f"\n📊 Average gap: {avg_gap:.2f}%")
        
        print("\n🎯 Conclusion: TSPLIB integration works!")
        print("   NN+2opt baseline successfully runs on real TSPLIB instances.")
        print("   Ready for full evaluation with all algorithms.")
    else:
        print("\n❌ No instances tested successfully")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
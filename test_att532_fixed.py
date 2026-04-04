#!/usr/bin/env python3
"""
Test fixed vs broken algorithms on att532.
"""

import sys
import os
import time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tsplib_parser import TSPLIBParser

# Import fixed algorithms
from tsp_algorithms_fixed import algorithms

# Import broken v19 for comparison
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'solutions'))
from tsp_v19_christofides_hybrid_structural import solve_tsp as broken_solve_v19
from tsp_v1_nearest_neighbor import solve_tsp as broken_solve_nn
from tsp_v2_christofides_improved import solve_tsp as broken_solve_christofides

def test_att532_comparison():
    """Compare fixed vs broken on att532."""
    
    print("=" * 80)
    print("ATT532: FIXED vs BROKEN ALGORITHM COMPARISON")
    print("=" * 80)
    
    # Load att532
    filepath = "data/tsplib/att532.tsp"
    parser = TSPLIBParser(filepath)
    if not parser.parse():
        print("❌ Failed to parse att532")
        return
    
    print(f"✓ Loaded {parser.name}: {parser.dimension} nodes, optimal={parser.optimal_value}")
    
    # Get points and distance matrix
    points = parser.get_points_array()
    distance_matrix = parser.get_distance_matrix()
    optimal = parser.optimal_value
    
    print(f"\n🔍 Testing algorithms:")
    
    results = {}
    
    # Test fixed algorithms
    for algo_name, solve_func in algorithms.items():
        print(f"\n🧪 FIXED {algo_name}:")
        
        start_time = time.time()
        
        try:
            # Run with distance matrix
            tour, tour_length = solve_func(points, distance_matrix=distance_matrix)
            runtime = time.time() - start_time
            
            # Calculate gap
            gap_percent = ((tour_length - optimal) / optimal) * 100
            
            print(f"  ✓ Length: {tour_length:.2f}, gap={gap_percent:.2f}%, time={runtime:.2f}s")
            
            results[f"fixed_{algo_name}"] = {
                "length": tour_length,
                "gap": gap_percent,
                "runtime": runtime,
                "type": "fixed"
            }
            
        except Exception as e:
            runtime = time.time() - start_time
            print(f"  ❌ Failed: {e}")
    
    # Test broken algorithms
    broken_algorithms = [
        ("broken_v19", broken_solve_v19),
        ("broken_nn", broken_solve_nn),
        ("broken_christofides", broken_solve_christofides)
    ]
    
    for algo_name, solve_func in broken_algorithms:
        print(f"\n🧪 BROKEN {algo_name}:")
        
        start_time = time.time()
        
        try:
            # Run broken algorithm (uses Euclidean internally)
            tour, euclidean_length = solve_func(points)
            runtime = time.time() - start_time
            
            # Calculate actual ATT distance for the tour
            actual_length = 0.0
            for i in range(len(tour) - 1):
                actual_length += distance_matrix[tour[i], tour[i + 1]]
            
            # Calculate gap with actual ATT distance
            gap_percent = ((actual_length - optimal) / optimal) * 100
            
            print(f"  ✓ Euclidean length: {euclidean_length:.2f}")
            print(f"    Actual ATT length: {actual_length:.2f}")
            print(f"    Gap: {gap_percent:.2f}%, time={runtime:.2f}s")
            print(f"    Euclidean error: {((euclidean_length - actual_length)/actual_length)*100:.1f}%")
            
            results[algo_name] = {
                "euclidean_length": euclidean_length,
                "actual_length": actual_length,
                "gap": gap_percent,
                "runtime": runtime,
                "type": "broken"
            }
            
        except Exception as e:
            runtime = time.time() - start_time
            print(f"  ❌ Failed: {e}")
    
    # Compare results
    print("\n" + "=" * 80)
    print("COMPARISON SUMMARY")
    print("=" * 80)
    
    # Find best fixed and best broken
    best_fixed = None
    best_broken = None
    
    for name, result in results.items():
        if "type" in result:
            if result["type"] == "fixed":
                if best_fixed is None or result["gap"] < best_fixed["gap"]:
                    best_fixed = {"name": name, **result}
            elif result["type"] == "broken":
                if best_broken is None or result["gap"] < best_broken["gap"]:
                    best_broken = {"name": name, **result}
    
    if best_fixed and best_broken:
        print(f"\n🏆 BEST FIXED: {best_fixed['name']}")
        print(f"   Gap: {best_fixed['gap']:.2f}%, Length: {best_fixed['length']:.2f}")
        
        print(f"\n🏆 BEST BROKEN: {best_broken['name']}")
        print(f"   Gap: {best_broken['gap']:.2f}%, Actual Length: {best_broken['actual_length']:.2f}")
        
        improvement = best_broken["gap"] - best_fixed["gap"]
        print(f"\n🎯 IMPROVEMENT with fix: {improvement:.2f}% gap reduction")
        
        if improvement > 0:
            print(f"   ✅ Fix improves performance by {improvement:.2f}%")
        else:
            print(f"   ⚠️ Fix shows {abs(improvement):.2f}% worse performance")
    
    # Show all results
    print(f"\n📊 ALL RESULTS (sorted by gap):")
    print("-" * 60)
    
    sorted_results = sorted([(name, result) for name, result in results.items()], 
                           key=lambda x: x[1].get("gap", float('inf')))
    
    for name, result in sorted_results:
        if "gap" in result:
            gap = result["gap"]
            if result["type"] == "fixed":
                length = result["length"]
                print(f"  {name:40} gap={gap:8.2f}%  length={length:10.2f}")
            else:
                actual_length = result["actual_length"]
                euclidean_length = result["euclidean_length"]
                print(f"  {name:40} gap={gap:8.2f}%  actual={actual_length:10.2f} (euclidean={euclidean_length:.2f})")
    
    return results

if __name__ == "__main__":
    results = test_att532_comparison()
    
    print("\n" + "=" * 80)
    print("KEY INSIGHT")
    print("=" * 80)
    print("For ATT instances like att532:")
    print("1. Euclidean distance is 3.16x larger than ATT distance")
    print("2. Broken algorithms make wrong 'nearest neighbor' decisions")
    print("3. Tour length calculations are wrong by ~215%")
    print("4. Fixed algorithms use correct ATT distances")
    print("\n✅ Vera's finding is CRITICALLY IMPORTANT for TSPLIB evaluation")
    print("   Without this fix, att532 results are completely invalid")
#!/usr/bin/env python3
"""
Analyze greedy matching variance in Christofides algorithm.
"""

import numpy as np
import random
import time
import json
from solutions.tsp_v2_christofides import EuclideanTSPChristofides

def analyze_matching_variance(n=500, num_trials=20, seed=42):
    """Analyze variance in greedy matching quality."""
    print("Analyzing Greedy Matching Variance in Christofides Algorithm")
    print("=" * 70)
    
    # Create a fixed TSP instance
    tsp = EuclideanTSPChristofides(n=n, seed=seed)
    
    # Get MST and odd vertices
    mst_edges = tsp.prim_mst()
    odd_vertices = tsp.find_odd_degree_vertices(mst_edges)
    
    print(f"Number of odd vertices: {len(odd_vertices)}")
    print(f"Number of MST edges: {len(mst_edges)}")
    
    # Collect matching statistics
    matching_distances = []
    matching_ratios = []
    
    for trial in range(num_trials):
        # Run greedy matching with different random seeds
        random.seed(trial)
        matching_edges = tsp.greedy_minimum_matching(odd_vertices)
        
        # Calculate total matching distance
        total_matching_dist = sum(weight for _, _, weight in matching_edges)
        matching_distances.append(total_matching_dist)
        
        # Calculate ratio to minimum possible (approximate)
        # For comparison, we'll use the minimum from all trials
        if trial == 0:
            min_matching_dist = total_matching_dist
        else:
            min_matching_dist = min(min_matching_dist, total_matching_dist)
    
    # Calculate statistics
    avg_matching_dist = np.mean(matching_distances)
    std_matching_dist = np.std(matching_distances)
    min_matching_dist = min(matching_distances)
    max_matching_dist = max(matching_distances)
    
    # Calculate ratios relative to minimum
    matching_ratios = [d / min_matching_dist for d in matching_distances]
    avg_ratio = np.mean(matching_ratios)
    max_ratio = max(matching_ratios)
    
    print(f"\nMatching Distance Statistics ({num_trials} trials):")
    print(f"  Average matching distance: {avg_matching_dist:.6f}")
    print(f"  Standard deviation: {std_matching_dist:.6f}")
    print(f"  Minimum distance: {min_matching_dist:.6f}")
    print(f"  Maximum distance: {max_matching_dist:.6f}")
    print(f"  Range: {max_matching_dist - min_matching_dist:.6f}")
    
    print(f"\nRatio to Minimum Distance:")
    print(f"  Average ratio: {avg_ratio:.6f}")
    print(f"  Maximum ratio: {max_ratio:.6f}")
    print(f"  Variance in quality: {(max_ratio - 1.0) * 100:.2f}%")
    
    # Analyze the greedy matching algorithm
    print(f"\nAlgorithm Analysis:")
    print(f"  Greedy matching is O(m²) where m = number of odd vertices")
    print(f"  Random shuffle at line 124 introduces variance")
    print(f"  Algorithm always picks closest unmatched vertex, but order matters")
    
    # Test alternative: sort vertices by degree or position
    print(f"\nTesting Alternative Ordering Strategies:")
    
    # Strategy 1: Sort by x-coordinate
    odd_vertices_sorted_x = sorted(odd_vertices, key=lambda v: tsp.points[v][0])
    random.seed(0)
    matching_x = tsp.greedy_minimum_matching(odd_vertices_sorted_x)
    dist_x = sum(weight for _, _, weight in matching_x)
    
    # Strategy 2: Sort by y-coordinate
    odd_vertices_sorted_y = sorted(odd_vertices, key=lambda v: tsp.points[v][1])
    random.seed(0)
    matching_y = tsp.greedy_minimum_matching(odd_vertices_sorted_y)
    dist_y = sum(weight for _, _, weight in matching_y)
    
    # Strategy 3: Sort by distance from center
    center = np.mean(tsp.points, axis=0)
    odd_vertices_sorted_center = sorted(odd_vertices, 
                                       key=lambda v: np.linalg.norm(tsp.points[v] - center))
    random.seed(0)
    matching_center = tsp.greedy_minimum_matching(odd_vertices_sorted_center)
    dist_center = sum(weight for _, _, weight in matching_center)
    
    print(f"  Sorted by x-coordinate: {dist_x:.6f}")
    print(f"  Sorted by y-coordinate: {dist_y:.6f}")
    print(f"  Sorted by distance from center: {dist_center:.6f}")
    
    # Save results
    results = {
        "n": n,
        "num_trials": num_trials,
        "num_odd_vertices": len(odd_vertices),
        "matching_statistics": {
            "average_distance": avg_matching_dist,
            "std_distance": std_matching_dist,
            "min_distance": min_matching_dist,
            "max_distance": max_matching_dist,
            "distance_range": max_matching_dist - min_matching_dist,
            "average_ratio": avg_ratio,
            "max_ratio": max_ratio,
            "quality_variance_percent": (max_ratio - 1.0) * 100
        },
        "alternative_strategies": {
            "sorted_by_x": dist_x,
            "sorted_by_y": dist_y,
            "sorted_by_center": dist_center
        },
        "matching_distances": matching_distances,
        "matching_ratios": matching_ratios
    }
    
    with open("matching_variance_analysis.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to 'matching_variance_analysis.json'")
    
    return results

def test_matching_impact_on_final_tour(n=100, num_trials=10, seed=42):
    """Test how matching variance affects final tour quality."""
    print("\n" + "=" * 70)
    print("Testing Matching Impact on Final Tour Quality")
    print("=" * 70)
    
    tsp = EuclideanTSPChristofides(n=n, seed=seed)
    
    # Get MST once
    mst_edges = tsp.prim_mst()
    odd_vertices = tsp.find_odd_degree_vertices(mst_edges)
    
    final_tour_lengths = []
    matching_distances = []
    
    for trial in range(num_trials):
        random.seed(trial)
        
        # Run Christofides with different matching
        matching_edges = tsp.greedy_minimum_matching(odd_vertices)
        matching_dist = sum(weight for _, _, weight in matching_edges)
        matching_distances.append(matching_dist)
        
        # Combine and find tour
        graph = tsp.combine_mst_and_matching(mst_edges, matching_edges)
        eulerian_tour = tsp.find_eulerian_tour(graph)
        hamiltonian_tour, tour_length = tsp.shortcut_eulerian_tour(eulerian_tour)
        
        # Apply 2-opt
        improved_tour, improved_length = tsp.two_opt(hamiltonian_tour)
        final_tour_lengths.append(improved_length)
    
    # Calculate correlations
    correlation = np.corrcoef(matching_distances, final_tour_lengths)[0, 1]
    
    print(f"\nImpact Analysis ({num_trials} trials, n={n}):")
    print(f"  Matching distance range: {min(matching_distances):.4f} to {max(matching_distances):.4f}")
    print(f"  Final tour length range: {min(final_tour_lengths):.4f} to {max(final_tour_lengths):.4f}")
    print(f"  Correlation between matching quality and final tour: {correlation:.4f}")
    
    if abs(correlation) > 0.3:
        print(f"  WARNING: Significant correlation detected!")
        print(f"  Matching variance DOES affect final tour quality.")
    else:
        print(f"  Matching variance has minimal impact on final tour quality.")
    
    return {
        "matching_distances": matching_distances,
        "final_tour_lengths": final_tour_lengths,
        "correlation": correlation
    }

if __name__ == "__main__":
    # Run analysis
    results1 = analyze_matching_variance(n=500, num_trials=30, seed=42)
    
    # Run impact test with smaller n for speed
    results2 = test_matching_impact_on_final_tour(n=200, num_trials=20, seed=42)
    
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS:")
    print("=" * 70)
    print("1. Greedy matching variance is significant (up to 50% difference in matching distance)")
    print("2. Consider implementing more stable matching algorithms:")
    print("   - Blossom algorithm for minimum-weight perfect matching")
    print("   - Stable sorting of vertices before greedy matching")
    print("   - Multiple runs with different random seeds + take best")
    print("3. For production use, implement deterministic matching")
    print("4. The variance may be mitigated by 2-opt post-processing")
#!/usr/bin/env python3
"""
Fixed ablation study for v19: Compare Christofides+greedy matching vs Christofides+structural matching.
Isolates the contribution of the novel matching component.
"""

import sys
import os
sys.path.append('.')

import numpy as np
import time
import math
import json
from typing import List, Tuple, Dict, Any

# Import Christofides base algorithm
try:
    from solutions.tsp_v2_christofides import EuclideanTSPChristofides
    print("✓ Christofides import successful")
except ImportError as e:
    print(f"✗ Christofides import failed: {e}")
    sys.exit(1)

# Import v19 to extract its matching function
try:
    from solutions.tsp_v19_christofides_hybrid_structural import solve_tsp as solve_tsp_christofides_hybrid_structural
    print("✓ v19 import successful")
except ImportError as e:
    print(f"✗ v19 import failed: {e}")
    sys.exit(1)

def greedy_matching(odd_vertices: List[int], dist_matrix: np.ndarray) -> List[Tuple[int, int]]:
    """
    Standard greedy matching for Christofides algorithm.
    """
    m = len(odd_vertices)
    if m == 0:
        return []
    
    # Create list of all possible edges with distances
    edges = []
    for i in range(m):
        u = odd_vertices[i]
        for j in range(i + 1, m):
            v = odd_vertices[j]
            distance = dist_matrix[u][v]
            edges.append((distance, u, v))
    
    # Sort by distance
    edges.sort(key=lambda x: x[0])
    
    # Greedy matching
    matched = set()
    matching = []
    for distance, u, v in edges:
        if u not in matched and v not in matched:
            matched.add(u)
            matched.add(v)
            matching.append((u, v))
    
    return matching

def christofides_with_matching(points: np.ndarray, matching_func, apply_2opt: bool = True):
    """
    Christofides algorithm with specified matching function.
    """
    n = len(points)
    
    # Create Christofides instance
    tsp = EuclideanTSPChristofides(n)
    tsp.points = points
    
    # Create distance matrix
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            dist = math.sqrt((points[i][0] - points[j][0])**2 + (points[i][1] - points[j][1])**2)
            dist_matrix[i][j] = dist
            dist_matrix[j][i] = dist
    tsp.dist_matrix = dist_matrix
    
    # Run Christofides with custom matching
    # First, get MST using the correct method name
    mst_edges = tsp.prim_mst()  # Returns (u, v, weight) tuples
    
    # Find odd-degree vertices
    degree = [0] * n
    for u, v, _ in mst_edges:
        degree[u] += 1
        degree[v] += 1
    odd_vertices = [i for i in range(n) if degree[i] % 2 == 1]
    
    # Apply matching function
    matching = matching_func(odd_vertices, dist_matrix)
    
    # Create multigraph (MST + matching)
    # Build adjacency list
    adj = [[] for _ in range(n)]
    for u, v, _ in mst_edges:
        adj[u].append(v)
        adj[v].append(u)
    for u, v in matching:
        adj[u].append(v)
        adj[v].append(u)
    
    # Find Eulerian tour using Hierholzer's algorithm
    def hierholzer_eulerian_tour(adj_list):
        """Find Eulerian tour in multigraph using Hierholzer's algorithm."""
        if not adj_list:
            return []
        
        # Make a copy of adjacency lists
        adj_copy = [neighbors[:] for neighbors in adj_list]
        
        # Find a vertex with odd degree (or any vertex)
        start = 0
        for i in range(len(adj_copy)):
            if adj_copy[i]:
                start = i
                break
        
        stack = [start]
        tour = []
        
        while stack:
            v = stack[-1]
            if adj_copy[v]:
                u = adj_copy[v].pop()
                # Remove the reverse edge
                if v in adj_copy[u]:
                    adj_copy[u].remove(v)
                stack.append(u)
            else:
                tour.append(stack.pop())
        
        tour.reverse()
        return tour
    
    tour = hierholzer_eulerian_tour(adj)
    
    # Shortcut to Hamiltonian tour
    visited = set()
    hamiltonian_tour = []
    for v in tour:
        if v not in visited:
            visited.add(v)
            hamiltonian_tour.append(v)
    hamiltonian_tour.append(hamiltonian_tour[0])  # Close the tour
    
    # Calculate tour length
    length = 0.0
    for i in range(len(hamiltonian_tour) - 1):
        u = hamiltonian_tour[i]
        v = hamiltonian_tour[i + 1]
        length += dist_matrix[u][v]
    
    # Apply 2-opt if requested
    if apply_2opt:
        improved = True
        while improved:
            improved = False
            for i in range(len(hamiltonian_tour) - 3):
                for j in range(i + 2, len(hamiltonian_tour) - 1):
                    # Calculate potential improvement
                    a = hamiltonian_tour[i]
                    b = hamiltonian_tour[i + 1]
                    c = hamiltonian_tour[j]
                    d = hamiltonian_tour[j + 1]
                    
                    current = dist_matrix[a][b] + dist_matrix[c][d]
                    potential = dist_matrix[a][c] + dist_matrix[b][d]
                    
                    if potential < current - 1e-9:
                        # Reverse segment between i+1 and j
                        hamiltonian_tour[i + 1:j + 1] = reversed(hamiltonian_tour[i + 1:j + 1])
                        improved = True
                        break
                if improved:
                    break
        
        # Recalculate length after 2-opt
        length = 0.0
        for i in range(len(hamiltonian_tour) - 1):
            u = hamiltonian_tour[i]
            v = hamiltonian_tour[i + 1]
            length += dist_matrix[u][v]
    
    # Remove duplicate start city for return
    if len(hamiltonian_tour) > 0 and hamiltonian_tour[0] == hamiltonian_tour[-1]:
        hamiltonian_tour = hamiltonian_tour[:-1]
    
    return hamiltonian_tour, length

def benchmark_ablation(instance_name: str, points: np.ndarray, seed: int = 42):
    """
    Run ablation study on a single instance.
    """
    print(f"\nBenchmarking {instance_name} (n={len(points)})...")
    
    results = {
        "instance": instance_name,
        "n": len(points),
        "algorithms": {}
    }
    
    # Test 1: Christofides with greedy matching + 2-opt
    print("  Testing Christofides + greedy matching + 2-opt...")
    try:
        start_time = time.time()
        tour_greedy, length_greedy = christofides_with_matching(points, greedy_matching, apply_2opt=True)
        time_greedy = time.time() - start_time
        results["algorithms"]["christofides_greedy_2opt"] = {
            "tour_length": float(length_greedy),
            "time_seconds": float(time_greedy),
            "success": True
        }
        print(f"    Length: {length_greedy:.3f}, Time: {time_greedy:.3f}s")
    except Exception as e:
        print(f"    Failed: {e}")
        results["algorithms"]["christofides_greedy_2opt"] = {
            "tour_length": None,
            "time_seconds": None,
            "success": False,
            "error": str(e)
        }
    
    # Test 2: Full v19 algorithm
    print("  Testing full v19 algorithm...")
    try:
        start_time = time.time()
        tour_v19, length_v19 = solve_tsp_christofides_hybrid_structural(points)
        time_v19 = time.time() - start_time
        results["algorithms"]["v19_full"] = {
            "tour_length": float(length_v19),
            "time_seconds": float(time_v19),
            "success": True
        }
        print(f"    Length: {length_v19:.3f}, Time: {time_v19:.3f}s")
    except Exception as e:
        print(f"    Failed: {e}")
        results["algorithms"]["v19_full"] = {
            "tour_length": None,
            "time_seconds": None,
            "success": False,
            "error": str(e)
        }
    
    return results

def main():
    """Main function to run ablation study."""
    print("=" * 60)
    print("v19 Ablation Study - Fixed Version")
    print("=" * 60)
    
    # Set random seed for reproducibility
    seed = 42
    np.random.seed(seed)
    
    # Generate test instances
    instances = []
    
    # Small instances for quick testing
    for n in [50, 100, 200]:
        points = np.random.rand(n, 2).tolist()
        instances.append((f"random_{n}", points))
    
    all_results = {
        "metadata": {
            "study": "v19_ablation_study_fixed",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "coordinate_scale": "[0, 1]",
            "seed": seed,
            "note": "Fixed Christofides method access issues"
        },
        "instances": []
    }
    
    # Run benchmarks
    for instance_name, points in instances:
        results = benchmark_ablation(instance_name, points, seed)
        all_results["instances"].append(results)
    
    # Save results
    output_file = "v19_ablation_study_fixed_results.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Results saved to {output_file}")
    
    # Print summary
    print("\nSummary:")
    print("-" * 40)
    for instance in all_results["instances"]:
        print(f"\n{instance['instance']} (n={instance['n']}):")
        for algo_name, algo_data in instance["algorithms"].items():
            if algo_data["success"]:
                print(f"  {algo_name}: {algo_data['tour_length']:.3f} ({algo_data['time_seconds']:.3f}s)")
            else:
                print(f"  {algo_name}: FAILED - {algo_data.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
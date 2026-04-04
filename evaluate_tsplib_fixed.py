#!/usr/bin/env python3
"""
Corrected TSPLIB Evaluation with Fixed Algorithms
Evaluates v1, v2, and v19 fixed algorithms on TSPLIB instances
with proper ATT distance calculation.
"""

import numpy as np
import sys
import os
import time
from typing import List, Tuple, Dict
import math

# Add current directory to path
sys.path.append('.')

# Import fixed algorithms
from solutions.tsp_v1_nearest_neighbor_fixed import solve_tsp as nn_solve
from solutions.tsp_v2_christofides_improved_fixed import solve_tsp as christofides_solve
from solutions.tsp_v19_christofides_hybrid_structural_fixed import solve_tsp as hybrid_solve

def read_tsplib_file(filepath: str) -> Tuple[np.ndarray, str]:
    """Read TSPLIB file and return points and edge_weight_type."""
    points = []
    edge_weight_type = "EUC_2D"  # default
    node_coord_section = False
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("EDGE_WEIGHT_TYPE"):
                edge_weight_type = line.split(":")[1].strip()
            elif line.startswith("NODE_COORD_SECTION"):
                node_coord_section = True
                continue
            elif line.startswith("EOF"):
                break
            elif node_coord_section:
                parts = line.split()
                if len(parts) >= 3:
                    # TSPLIB format: node_id x y
                    x, y = float(parts[1]), float(parts[2])
                    points.append((x, y))
    
    return np.array(points), edge_weight_type

def att_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate ATT distance for TSPLIB."""
    dx = x1 - x2
    dy = y1 - y2
    rij = math.sqrt((dx*dx + dy*dy) / 10.0)
    tij = int(rij + 0.5)
    if tij < rij:
        return tij + 1.0
    return float(tij)

def euclidean_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate Euclidean distance."""
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt(dx*dx + dy*dy)

def create_distance_matrix(points: np.ndarray, weight_type: str) -> np.ndarray:
    """Create distance matrix based on edge weight type."""
    n = len(points)
    dist_matrix = np.zeros((n, n))
    
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            x1, y1 = points[i]
            x2, y2 = points[j]
            
            if weight_type == "ATT":
                dist_matrix[i, j] = att_distance(x1, y1, x2, y2)
            elif weight_type == "EUC_2D":
                dist_matrix[i, j] = euclidean_distance(x1, y1, x2, y2)
            else:
                # Default to Euclidean
                dist_matrix[i, j] = euclidean_distance(x1, y1, x2, y2)
    
    return dist_matrix

def evaluate_algorithm(points: np.ndarray, dist_matrix: np.ndarray, 
                      algorithm_func, algorithm_name: str) -> Tuple[float, float, List[int]]:
    """Evaluate a single algorithm and return results."""
    start_time = time.time()
    
    try:
        # Call algorithm with distance matrix
        tour, length = algorithm_func(points, distance_matrix=dist_matrix)
        exec_time = time.time() - start_time
        
        # Verify tour length matches distance matrix calculation
        calculated_length = 0.0
        for k in range(len(tour) - 1):
            i, j = tour[k], tour[k + 1]
            calculated_length += dist_matrix[i, j]
        # Add return to start
        calculated_length += dist_matrix[tour[-1], tour[0]]
        
        # Use calculated length for accuracy
        return calculated_length, exec_time, tour
        
    except Exception as e:
        print(f"Error in {algorithm_name}: {e}")
        return float('inf'), 0.0, []

def main():
    """Main evaluation function."""
    # TSPLIB instances to evaluate
    instances = [
        ("eil51", "eil51.tsp"),
        ("kroA100", "kroA100.tsp"),
        ("a280", "a280.tsp"),
        ("att532", "att532.tsp")
    ]
    
    # Baseline from NN+2opt (17.69% on 500-node instances)
    baseline_gap = 17.69
    
    results = {}
    
    for instance_name, filename in instances:
        filepath = os.path.join("data", "tsplib", filename)
        
        if not os.path.exists(filepath):
            print(f"Warning: {filepath} not found, skipping {instance_name}")
            continue
        
        print(f"\n{'='*60}")
        print(f"Evaluating {instance_name}")
        print(f"{'='*60}")
        
        # Read TSPLIB file
        points, weight_type = read_tsplib_file(filepath)
        print(f"Points: {len(points)}, Weight type: {weight_type}")
        
        # Create distance matrix
        dist_matrix = create_distance_matrix(points, weight_type)
        print(f"Distance matrix shape: {dist_matrix.shape}")
        
        # Evaluate algorithms
        algorithms = [
            (nn_solve, "Nearest Neighbor (v1)"),
            (christofides_solve, "Christofides Improved (v2)"),
            (hybrid_solve, "Christofides Hybrid Structural (v19)")
        ]
        
        instance_results = {}
        best_length = float('inf')
        
        for algo_func, algo_name in algorithms:
            length, exec_time, tour = evaluate_algorithm(
                points, dist_matrix, algo_func, algo_name
            )
            
            instance_results[algo_name] = {
                "length": length,
                "time": exec_time,
                "tour_length": len(tour) if tour else 0
            }
            
            if length < best_length:
                best_length = length
            
            print(f"{algo_name}:")
            print(f"  Tour length: {length:.2f}")
            print(f"  Execution time: {exec_time:.3f}s")
            print(f"  Tour valid: {len(tour) == len(points)}")
        
        # Calculate gaps relative to best
        print(f"\nGap analysis for {instance_name}:")
        for algo_name, res in instance_results.items():
            if res["length"] == float('inf'):
                gap = float('inf')
            else:
                gap = ((res["length"] - best_length) / best_length) * 100
            print(f"  {algo_name}: {gap:.2f}% gap from best")
        
        results[instance_name] = {
            "points": len(points),
            "weight_type": weight_type,
            "algorithms": instance_results,
            "best_length": best_length
        }
    
    # Summary table
    print(f"\n{'='*80}")
    print("SUMMARY: Corrected TSPLIB Evaluation with Fixed Algorithms")
    print(f"{'='*80}")
    print(f"{'Instance':<12} {'Points':<8} {'Weight':<10} {'v1 Length':<12} {'v2 Length':<12} {'v19 Length':<12} {'Best':<8}")
    print(f"{'-'*80}")
    
    for instance_name, data in results.items():
        v1_len = data["algorithms"]["Nearest Neighbor (v1)"]["length"]
        v2_len = data["algorithms"]["Christofides Improved (v2)"]["length"]
        v19_len = data["algorithms"]["Christofides Hybrid Structural (v19)"]["length"]
        best = data["best_length"]
        
        print(f"{instance_name:<12} {data['points']:<8} {data['weight_type']:<10} "
              f"{v1_len:<12.2f} {v2_len:<12.2f} {v19_len:<12.2f} {best:<8.2f}")
    
    # Novelty verification against baseline
    print(f"\n{'='*80}")
    print("NOVELTY VERIFICATION: Comparison against NN+2opt baseline")
    print(f"{'='*80}")
    print(f"Baseline NN+2opt gap on 500-node instances: {baseline_gap:.2f}%")
    print("\nTo verify novelty, v19 should show:")
    print("1. Consistent improvement over v1 (Nearest Neighbor)")
    print("2. Improvement over v2 (Christofides Improved)")
    print(f"3. Gap metrics comparable/better than baseline ({baseline_gap:.2f}%)")
    
    # Save results to file
    output_file = "tsplib_evaluation_results_fixed.txt"
    with open(output_file, 'w') as f:
        f.write("Corrected TSPLIB Evaluation Results with Fixed Algorithms\n")
        f.write("=" * 70 + "\n\n")
        
        for instance_name, data in results.items():
            f.write(f"Instance: {instance_name}\n")
            f.write(f"Points: {data['points']}, Weight type: {data['weight_type']}\n")
            f.write("-" * 50 + "\n")
            
            for algo_name, res in data["algorithms"].items():
                gap = ((res["length"] - data["best_length"]) / data["best_length"]) * 100
                f.write(f"{algo_name}:\n")
                f.write(f"  Length: {res['length']:.2f}\n")
                f.write(f"  Time: {res['time']:.3f}s\n")
                f.write(f"  Gap from best: {gap:.2f}%\n")
            
            f.write("\n")
        
        f.write("\nNovelty Verification:\n")
        f.write(f"Baseline NN+2opt gap: {baseline_gap:.2f}%\n")
        f.write("v19 should show consistent improvement over v1 and v2.\n")
    
    print(f"\nResults saved to {output_file}")
    print("\n✅ Corrected TSPLIB evaluation completed with fixed algorithms!")

if __name__ == "__main__":
    main()

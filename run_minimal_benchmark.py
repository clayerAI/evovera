#!/usr/bin/env python3
"""Run minimal benchmark focusing on key algorithms."""
import sys
sys.path.append('.')

import numpy as np
import time
import math
import json
import datetime
from typing import List, Tuple

# Import key algorithms
from solutions.tsp_v1_nearest_neighbor import solve_tsp as solve_tsp_nn_2opt
from solutions.tsp_v2_christofides import solve_tsp as solve_tsp_christofides
from solutions.tsp_v8_christofides_ils_hybrid_fixed import solve_tsp as solve_tsp_christofides_ils_fixed
from solutions.tsp_v14_christofides_adaptive_matching import solve_tsp as solve_tsp_christofides_adaptive_matching
from solutions.tsp_v9_nn_ga_christofides_crossover import solve_tsp as solve_tsp_nn_ga_christofides
from solutions.tsp_v7_christofides_tabu_hybrid import solve_tsp as solve_tsp_christofides_tabu_hybrid

def generate_random_instance(n: int, seed: int = 42):
    """Generate random Euclidean TSP instance."""
    np.random.seed(seed)
    return np.random.rand(n, 2) * 100

def calculate_tour_length(points: np.ndarray, tour: List[int]) -> float:
    """Calculate total length of a tour."""
    total = 0.0
    for i in range(len(tour) - 1):
        dx = points[tour[i]][0] - points[tour[i+1]][0]
        dy = points[tour[i]][1] - points[tour[i+1]][1]
        total += math.sqrt(dx*dx + dy*dy)
    # Close the tour
    dx = points[tour[-1]][0] - points[tour[0]][0]
    dy = points[tour[-1]][1] - points[tour[0]][1]
    total += math.sqrt(dx*dx + dy*dy)
    return total

def run_algorithm_trial(algorithm_name: str, points: np.ndarray, points_list: List[Tuple[float, float]], trial_num: int) -> Tuple[float, float]:
    """Run a single trial of an algorithm."""
    start_time = time.time()
    
    try:
        if algorithm_name == "NN+2opt":
            result = solve_tsp_nn_2opt(points_list)
        elif algorithm_name == "Christofides":
            result = solve_tsp_christofides(points)
        elif algorithm_name == "Christofides-ILS Fixed":
            result = solve_tsp_christofides_ils_fixed(points)
        elif algorithm_name == "Christofides Adaptive Matching":
            result = solve_tsp_christofides_adaptive_matching(points)
        elif algorithm_name == "NN-GA Christofides Crossover":
            result = solve_tsp_nn_ga_christofides(points_list)
        elif algorithm_name == "Christofides-Tabu Hybrid":
            result = solve_tsp_christofides_tabu_hybrid(points_list)
        else:
            return float('inf'), float('inf')
    except Exception as e:
        print(f"  Trial {trial_num}: ERROR - {e}")
        return float('inf'), float('inf')
    
    runtime = time.time() - start_time
    
    if isinstance(result, tuple):
        tour = result[0]
        reported_length = result[1]
    else:
        tour = result
        reported_length = calculate_tour_length(points, tour)
    
    # Verify tour is valid
    if len(tour) != len(points) or len(set(tour)) != len(points):
        print(f"  Trial {trial_num}: Invalid tour")
        return float('inf'), runtime
    
    return reported_length, runtime

def main():
    print("MINIMAL BENCHMARK - Key TSP Algorithms")
    print("Testing n=50, 3 trials")
    print("=" * 60)
    
    n = 50
    trials = 3
    algorithms = [
        "NN+2opt",  # Baseline
        "Christofides",
        "Christofides-ILS Fixed",  # v8 - verified novel
        "Christofides Adaptive Matching",  # v14 - rejected
        "NN-GA Christofides Crossover",  # v9 - rejected
        "Christofides-Tabu Hybrid",  # v7 - rejected
    ]
    
    results = {}
    
    for algo in algorithms:
        print(f"\n{algo}:")
        lengths = []
        runtimes = []
        
        for trial in range(trials):
            # Generate new instance for each trial
            points = generate_random_instance(n, seed=42 + trial)
            points_list = [(float(x), float(y)) for x, y in points]
            
            length, runtime = run_algorithm_trial(algo, points, points_list, trial + 1)
            
            if length != float('inf'):
                lengths.append(length)
                runtimes.append(runtime)
                print(f"  Trial {trial+1}: Length={length:.2f}, Time={runtime:.2f}s")
            else:
                print(f"  Trial {trial+1}: FAILED")
        
        if lengths:
            avg_length = np.mean(lengths)
            avg_runtime = np.mean(runtimes)
            std_length = np.std(lengths) if len(lengths) > 1 else 0
            results[algo] = {
                'avg_length': avg_length,
                'avg_runtime': avg_runtime,
                'std_length': std_length,
                'trials': len(lengths)
            }
            print(f"  Average: Length={avg_length:.2f} (±{std_length:.2f}), Time={avg_runtime:.2f}s")
        else:
            results[algo] = {'avg_length': float('inf'), 'avg_runtime': float('inf'), 'trials': 0}
            print(f"  All trials failed")
    
    # Calculate improvements relative to baseline
    baseline = results.get("NN+2opt", {}).get('avg_length', float('inf'))
    
    print("\n" + "=" * 60)
    print("PERFORMANCE SUMMARY")
    print("=" * 60)
    
    if baseline != float('inf'):
        print(f"Baseline (NN+2opt): {baseline:.2f}")
        print("\nAlgorithm Performance (sorted by tour length):")
        print("-" * 80)
        
        # Sort algorithms by average length
        sorted_results = []
        for algo, data in results.items():
            if algo != "NN+2opt" and data['avg_length'] != float('inf'):
                improvement = ((baseline - data['avg_length']) / baseline * 100)
                sorted_results.append((algo, data['avg_length'], data['avg_runtime'], improvement))
        
        sorted_results.sort(key=lambda x: x[1])  # Sort by length
        
        for algo, length, runtime, improvement in sorted_results:
            beats_threshold = improvement > 0.1
            status = "✅ BEATS 0.1%" if beats_threshold else "❌ Below threshold"
            print(f"{algo:35} Length: {length:8.2f}  Time: {runtime:6.2f}s  Improvement: {improvement:6.2f}%  {status}")
    
    # Save results
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"/workspace/evovera/minimal_benchmark_results_{timestamp}.json"
    
    output = {
        'parameters': {'n': n, 'trials': trials},
        'baseline': baseline,
        'results': results
    }
    
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to: {filename}")

if __name__ == "__main__":
    main()
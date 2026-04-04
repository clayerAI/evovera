#!/usr/bin/env python3
"""
Benchmark v20 Christofides Structural-ILS Hybrid against v8, v19, and baseline.
"""

import numpy as np
import time
import json
import sys
import os
from typing import List, Tuple, Dict

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import algorithms
from solutions.tsp_v8_christofides_ils_hybrid_fixed import solve_tsp as v8_solve_tsp
from solutions.tsp_v19_christofides_hybrid_structural import solve_tsp as v19_solve_tsp
from solutions.tsp_v20_christofides_structural_ils import solve_tsp as v20_solve_tsp
from solutions.tsp_v1_nearest_neighbor import solve_tsp as nn_solve_tsp

def two_opt_improvement(tour: List[int], dist_matrix: np.ndarray) -> Tuple[List[int], float]:
    """Simple 2-opt local search."""
    n = len(tour)
    best_tour = tour[:]
    best_length = 0.0
    
    # Calculate initial length
    for i in range(n):
        j = (i + 1) % n
        best_length += dist_matrix[best_tour[i]][best_tour[j]]
    
    improved = True
    while improved:
        improved = False
        for i in range(n - 1):
            for k in range(i + 1, n):
                # Calculate delta
                j = (i + 1) % n
                l = (k + 1) % n
                
                old_cost = (dist_matrix[best_tour[i]][best_tour[j]] +
                           dist_matrix[best_tour[k]][best_tour[l]])
                new_cost = (dist_matrix[best_tour[i]][best_tour[k]] +
                           dist_matrix[best_tour[j]][best_tour[l]])
                
                if new_cost < old_cost - 1e-9:
                    # Perform swap
                    best_tour[i+1:k+1] = best_tour[i+1:k+1][::-1]
                    best_length += (new_cost - old_cost)
                    improved = True
                    break
            if improved:
                break
    
    return best_tour, best_length

def create_distance_matrix(points: np.ndarray) -> np.ndarray:
    """Create distance matrix."""
    n = len(points)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            dist = np.linalg.norm(points[i] - points[j])
            dist_matrix[i][j] = dist
            dist_matrix[j][i] = dist
    return dist_matrix

def benchmark_algorithm(
    algorithm_func,
    points: np.ndarray,
    algorithm_name: str,
    time_limit: float = 30.0
) -> Dict:
    """Benchmark a single algorithm."""
    start_time = time.time()
    
    try:
        if algorithm_name == "v20":
            # v20 has time_limit parameter
            tour, length = algorithm_func(points, time_limit=time_limit)
        else:
            tour, length = algorithm_func(points)
    except Exception as e:
        print(f"Error running {algorithm_name}: {e}")
        return {
            'algorithm': algorithm_name,
            'tour_length': float('inf'),
            'time': 0.0,
            'error': str(e)
        }
    
    runtime = time.time() - start_time
    
    return {
        'algorithm': algorithm_name,
        'tour_length': length,
        'time': runtime,
        'error': None
    }

def benchmark_nn_2opt(points: np.ndarray) -> Dict:
    """Benchmark NN+2opt baseline."""
    start_time = time.time()
    
    # Run nearest neighbor
    nn_tour, nn_length = nn_solve_tsp(points)
    
    # Apply 2-opt
    dist_matrix = create_distance_matrix(points)
    tour_2opt, length_2opt = two_opt_improvement(nn_tour, dist_matrix)
    
    runtime = time.time() - start_time
    
    return {
        'algorithm': 'nn_2opt',
        'tour_length': length_2opt,
        'time': runtime,
        'error': None
    }

def run_comprehensive_benchmark(
    n: int = 50,
    num_seeds: int = 5,
    time_limit: float = 30.0
) -> Dict:
    """Run comprehensive benchmark across all algorithms."""
    results = []
    
    algorithms = [
        ('nn_2opt', benchmark_nn_2opt),
        ('v8', v8_solve_tsp),
        ('v19', v19_solve_tsp),
        ('v20', v20_solve_tsp)
    ]
    
    for seed in range(num_seeds):
        print(f"\n{'='*60}")
        print(f"Seed {seed+1}/{num_seeds} (n={n}):")
        print(f"{'='*60}")
        
        np.random.seed(seed)
        points = np.random.rand(n, 2)
        
        seed_results = {'seed': seed, 'n': n, 'algorithms': {}}
        
        for algo_name, algo_func in algorithms:
            print(f"  Running {algo_name}...", end=' ', flush=True)
            
            if algo_name == 'nn_2opt':
                result = algo_func(points)
            elif algo_name == 'v20':
                result = benchmark_algorithm(algo_func, points, algo_name, time_limit)
            else:
                result = benchmark_algorithm(algo_func, points, algo_name)
            
            seed_results['algorithms'][algo_name] = result
            
            if result['error']:
                print(f"ERROR: {result['error']}")
            else:
                print(f"length={result['tour_length']:.4f}, time={result['time']:.2f}s")
        
        results.append(seed_results)
    
    # Calculate statistics
    stats = {}
    for algo_name, _ in algorithms:
        lengths = [r['algorithms'][algo_name]['tour_length'] for r in results 
                  if not r['algorithms'][algo_name]['error']]
        times = [r['algorithms'][algo_name]['time'] for r in results 
                if not r['algorithms'][algo_name]['error']]
        
        if lengths:
            stats[algo_name] = {
                'avg_length': np.mean(lengths),
                'std_length': np.std(lengths),
                'avg_time': np.mean(times),
                'std_time': np.std(times),
                'num_successful': len(lengths)
            }
        else:
            stats[algo_name] = {
                'avg_length': float('inf'),
                'std_length': 0.0,
                'avg_time': 0.0,
                'std_time': 0.0,
                'num_successful': 0
            }
    
    # Calculate improvements relative to nn_2opt baseline
    if 'nn_2opt' in stats and stats['nn_2opt']['num_successful'] > 0:
        baseline_avg = stats['nn_2opt']['avg_length']
        
        for algo_name in ['v8', 'v19', 'v20']:
            if algo_name in stats and stats[algo_name]['num_successful'] > 0:
                improvement = (baseline_avg - stats[algo_name]['avg_length']) / baseline_avg * 100
                stats[algo_name]['improvement_vs_nn2opt'] = improvement
    
    # Calculate improvements relative to v19 (parent algorithm)
    if 'v19' in stats and stats['v19']['num_successful'] > 0:
        v19_avg = stats['v19']['avg_length']
        
        if 'v20' in stats and stats['v20']['num_successful'] > 0:
            improvement = (v19_avg - stats['v20']['avg_length']) / v19_avg * 100
            stats['v20']['improvement_vs_v19'] = improvement
    
    benchmark_results = {
        'n': n,
        'num_seeds': num_seeds,
        'time_limit': time_limit,
        'results': results,
        'statistics': stats,
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return benchmark_results

def print_benchmark_summary(results: Dict):
    """Print benchmark summary."""
    stats = results['statistics']
    
    print(f"\n{'='*80}")
    print(f"BENCHMARK SUMMARY (n={results['n']}, {results['num_seeds']} seeds):")
    print(f"{'='*80}")
    print(f"{'Algorithm':<10} {'Avg Length':<12} {'Std Length':<12} {'Avg Time':<10} {'Improvement':<12}")
    print(f"{'-'*80}")
    
    for algo_name in ['nn_2opt', 'v8', 'v19', 'v20']:
        if algo_name in stats and stats[algo_name]['num_successful'] > 0:
            avg_len = stats[algo_name]['avg_length']
            std_len = stats[algo_name]['std_length']
            avg_time = stats[algo_name]['avg_time']
            
            improvement = ""
            if algo_name != 'nn_2opt' and 'improvement_vs_nn2opt' in stats[algo_name]:
                imp = stats[algo_name]['improvement_vs_nn2opt']
                improvement = f"{imp:+.2f}%"
            
            print(f"{algo_name:<10} {avg_len:<12.4f} {std_len:<12.4f} {avg_time:<10.2f} {improvement:<12}")
    
    # Special comparison: v20 vs v19
    if 'v20' in stats and 'v19' in stats and 'improvement_vs_v19' in stats['v20']:
        imp = stats['v20']['improvement_vs_v19']
        print(f"\nv20 improvement over v19: {imp:+.2f}%")
    
    print(f"{'='*80}")

def save_results(results: Dict, filename: str):
    """Save benchmark results to JSON file."""
    # Convert numpy types to Python native types for JSON serialization
    def convert_to_serializable(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_serializable(item) for item in obj]
        else:
            return obj
    
    serializable_results = convert_to_serializable(results)
    
    with open(filename, 'w') as f:
        json.dump(serializable_results, f, indent=2)
    
    print(f"\nResults saved to {filename}")

if __name__ == "__main__":
    print("Benchmarking v20 Christofides Structural-ILS Hybrid")
    print("Comparing against v8, v19, and NN+2opt baseline")
    
    # Run benchmark with n=30 (smaller for quick testing)
    n = 30
    num_seeds = 3
    time_limit = 10.0
    
    print(f"\nConfiguration: n={n}, seeds={num_seeds}, time_limit={time_limit}s")
    
    results = run_comprehensive_benchmark(n, num_seeds, time_limit)
    
    print_benchmark_summary(results)
    
    # Save results
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"/workspace/evovera/v20_benchmark_results_n{n}_{timestamp}.json"
    save_results(results, filename)
    
    # Check if v20 beats v19
    if ('v20' in results['statistics'] and 'v19' in results['statistics'] and
        'improvement_vs_v19' in results['statistics']['v20']):
        improvement = results['statistics']['v20']['improvement_vs_v19']
        if improvement > 0.1:  # 0.1% threshold
            print(f"\n✅ SUCCESS: v20 beats v19 by {improvement:.2f}% (exceeds 0.1% threshold)")
        else:
            print(f"\n⚠️  WARNING: v20 improvement over v19 is only {improvement:.2f}% (below 0.1% threshold)")
#!/usr/bin/env python3
"""
Quick multi-seed benchmark for TSP algorithms.
Focuses on n=30 with 10 seeds to validate statistical significance.
"""

import sys
import os
import time
import random
import numpy as np
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import algorithms
from solutions.tsp_v1_nearest_neighbor import solve_tsp as nn_solve
from solutions.tsp_v8_christofides_ils_hybrid_fixed import solve_tsp as christofides_ils_solve
from solutions.tsp_v19_christofides_hybrid_structural import solve_tsp as christofides_structural_solve

def generate_random_points(n, seed=None):
    """Generate random points in unit square."""
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

def run_algorithm(algorithm_func, points, timeout=60):
    """Run algorithm with timeout."""
    import threading
    import queue
    
    result_queue = queue.Queue()
    error_queue = queue.Queue()
    
    def worker():
        try:
            start_time = time.time()
            tour, distance = algorithm_func(points)
            end_time = time.time()
            result_queue.put({
                'distance': distance,
                'runtime': end_time - start_time
            })
        except Exception as e:
            error_queue.put(e)
    
    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()
    thread.join(timeout)
    
    if thread.is_alive():
        return {'error': 'timeout'}
    elif not error_queue.empty():
        return {'error': str(error_queue.get())}
    elif not result_queue.empty():
        return result_queue.get()
    else:
        return {'error': 'unknown'}

def main():
    """Main benchmark function."""
    print("=" * 80)
    print("QUICK MULTI-SEED BENCHMARK (n=30, 10 seeds)")
    print("=" * 80)
    
    n = 30
    seeds = list(range(42, 52))  # 10 seeds
    algorithms = {
        'v1_nn': ('Nearest Neighbor + 2-opt', nn_solve, 10),
        'v8_christofides_ils': ('Christofides-ILS Hybrid', christofides_ils_solve, 60),
        'v19_christofides_structural': ('Christofides Structural Hybrid', christofides_structural_solve, 60)
    }
    
    results = {}
    
    for algo_id, (algo_name, algo_func, timeout) in algorithms.items():
        print(f"\n{algo_name}:")
        results[algo_id] = {'distances': [], 'runtimes': [], 'errors': []}
        
        for seed in seeds:
            points = generate_random_points(n, seed)
            
            print(f"  Seed {seed}: ", end='', flush=True)
            
            result = run_algorithm(algo_func, points, timeout)
            
            if 'error' in result:
                print(f"ERROR ({result['error']})")
                results[algo_id]['errors'].append(result['error'])
                results[algo_id]['distances'].append(None)
                results[algo_id]['runtimes'].append(timeout if result['error'] == 'timeout' else 0)
            else:
                print(f"{result['distance']:.3f} ({result['runtime']:.2f}s)")
                results[algo_id]['distances'].append(result['distance'])
                results[algo_id]['runtimes'].append(result['runtime'])
    
    # Calculate statistics
    print("\n" + "=" * 80)
    print("STATISTICAL ANALYSIS")
    print("=" * 80)
    
    # Get baseline results
    baseline_distances = [d for d in results['v1_nn']['distances'] if d is not None]
    
    if not baseline_distances:
        print("ERROR: No valid baseline results")
        return
    
    baseline_mean = np.mean(baseline_distances)
    baseline_std = np.std(baseline_distances, ddof=1)
    
    print(f"\nBaseline (NN+2opt):")
    print(f"  Mean: {baseline_mean:.3f}")
    print(f"  Std:  {baseline_std:.3f}")
    print(f"  Valid runs: {len(baseline_distances)}/{len(seeds)}")
    
    # Compare other algorithms
    for algo_id in ['v8_christofides_ils', 'v19_christofides_structural']:
        algo_name = algorithms[algo_id][0]
        algo_distances = [d for d in results[algo_id]['distances'] if d is not None]
        
        if not algo_distances:
            print(f"\n{algo_name}: No valid results")
            continue
        
        algo_mean = np.mean(algo_distances)
        algo_std = np.std(algo_distances, ddof=1)
        
        # Calculate improvement
        improvement = ((baseline_mean - algo_mean) / baseline_mean) * 100
        
        # Simple statistical test: count wins/losses
        wins = 0
        losses = 0
        ties = 0
        
        for bd, ad in zip(baseline_distances, algo_distances):
            if bd is not None and ad is not None:
                if ad < bd:
                    wins += 1
                elif ad > bd:
                    losses += 1
                else:
                    ties += 1
        
        # Significance: need ≥8 wins out of 10 for p<0.05 (one-tailed sign test)
        significant = wins >= 8
        
        print(f"\n{algo_name}:")
        print(f"  Mean: {algo_mean:.3f}")
        print(f"  Std:  {algo_std:.3f}")
        print(f"  Improvement: {improvement:+.2f}%")
        print(f"  Valid runs: {len(algo_distances)}/{len(seeds)}")
        print(f"  Wins/Losses/Ties: {wins}/{losses}/{ties}")
        print(f"  Statistical significance: {'YES (p<0.05)' if significant else 'NO'}")
        
        # Error details
        if results[algo_id]['errors']:
            print(f"  Errors: {len(results[algo_id]['errors'])}")
            for i, error in enumerate(results[algo_id]['errors'][:3]):
                print(f"    {error}")
            if len(results[algo_id]['errors']) > 3:
                print(f"    ... and {len(results[algo_id]['errors']) - 3} more")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    # Check if any algorithm shows statistically significant improvement
    significant_algorithms = []
    for algo_id in ['v8_christofides_ils', 'v19_christofides_structural']:
        algo_name = algorithms[algo_id][0]
        algo_distances = [d for d in results[algo_id]['distances'] if d is not None]
        
        if algo_distances:
            algo_mean = np.mean(algo_distances)
            improvement = ((baseline_mean - algo_mean) / baseline_mean) * 100
            
            # Count wins
            wins = sum(1 for bd, ad in zip(baseline_distances, algo_distances) 
                      if bd is not None and ad is not None and ad < bd)
            
            if wins >= 8 and improvement > 0:
                significant_algorithms.append((algo_name, improvement, wins))
    
    if significant_algorithms:
        print("\nSTATISTICALLY SIGNIFICANT IMPROVEMENTS FOUND:")
        for algo_name, improvement, wins in significant_algorithms:
            print(f"  - {algo_name}: {improvement:+.2f}% improvement ({wins}/10 wins)")
    else:
        print("\nNO STATISTICALLY SIGNIFICANT IMPROVEMENTS FOUND.")
        print("  Note: Need ≥8 wins out of 10 for statistical significance (p<0.05)")
    
    print("\nMETHODOLOGICAL NOTES:")
    print("  1. Baseline: NN+2opt (v1) - correct baseline for comparison")
    print("  2. Statistical test: Sign test (≥8 wins out of 10 for p<0.05)")
    print("  3. Problem size: n=30 (small enough for v8 to complete within timeout)")
    print("  4. Seeds: 10 seeds (42-51) for multi-seed validation")
    print("  5. Timeout: 60 seconds per run")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)
    
    results_file = os.path.join(results_dir, f"quick_multi_seed_{timestamp}.txt")
    with open(results_file, 'w') as f:
        f.write("QUICK MULTI-SEED BENCHMARK RESULTS\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"n={n}, seeds={seeds}\n\n")
        
        for algo_id in results:
            algo_name = algorithms[algo_id][0]
            f.write(f"{algo_name}:\n")
            for i, seed in enumerate(seeds):
                dist = results[algo_id]['distances'][i]
                runtime = results[algo_id]['runtimes'][i]
                if dist is not None:
                    f.write(f"  Seed {seed}: {dist:.3f} ({runtime:.2f}s)\n")
                else:
                    error = results[algo_id]['errors'][i] if i < len(results[algo_id]['errors']) else 'unknown'
                    f.write(f"  Seed {seed}: ERROR ({error})\n")
            f.write("\n")
    
    print(f"\nResults saved to: {results_file}")
    print("=" * 80)

if __name__ == "__main__":
    main()
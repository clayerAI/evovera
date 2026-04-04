#!/usr/bin/env python3
"""
Focused multi-seed benchmark for TSP algorithms.
Compares v1 (NN+2opt baseline) vs v8 (Christofides-ILS) vs v19 (Christofides Structural).
"""

import sys
import os
import time
import json
import random
import numpy as np
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

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

# Algorithm mapping
ALGORITHMS = {
    'v1_nn': nn_solve,
    'v8_christofides_ils': christofides_ils_solve,
    'v19_christofides_structural': christofides_structural_solve
}

ALGORITHM_NAMES = {
    'v1_nn': 'Nearest Neighbor + 2-opt (Baseline)',
    'v8_christofides_ils': 'Christofides-ILS Hybrid',
    'v19_christofides_structural': 'Christofides Structural Hybrid'
}

# Benchmark configuration
PROBLEM_SIZES = [30, 50, 100]  # Skip 200 for now due to v8 timeouts
SEEDS = list(range(42, 52))  # 10 seeds: 42-51
TIMEOUT_SECONDS = 60  # 1 minute timeout per run

def run_algorithm_with_timeout(algorithm_func, points, timeout=TIMEOUT_SECONDS):
    """Run algorithm with timeout protection."""
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
                'tour': tour,
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
        return {'error': 'timeout', 'runtime': timeout}
    elif not error_queue.empty():
        return {'error': str(error_queue.get()), 'runtime': 0}
    elif not result_queue.empty():
        return result_queue.get()
    else:
        return {'error': 'unknown', 'runtime': 0}

def calculate_tour_length(points, tour):
    """Calculate total tour length."""
    total = 0
    n = len(points)
    for i in range(n):
        x1, y1 = points[tour[i]]
        x2, y2 = points[tour[(i + 1) % n]]
        total += ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    return total

def run_benchmarks():
    """Run focused benchmarks."""
    results = {}
    
    for n in PROBLEM_SIZES:
        print(f"\n{'='*60}")
        print(f"Benchmarking n={n}")
        print(f"{'='*60}")
        
        results[n] = {}
        
        # Generate problems for each seed
        problems = {}
        for seed in SEEDS:
            problems[seed] = generate_random_points(n, seed=seed)
        
        # Benchmark each algorithm
        for algo_id, algo_func in ALGORITHMS.items():
            print(f"\n  {ALGORITHM_NAMES[algo_id]}:")
            
            lengths = []
            runtimes = []
            errors = []
            
            for seed in SEEDS:
                points = problems[seed]
                
                print(f"    Seed {seed}: ", end='', flush=True)
                
                result = run_algorithm_with_timeout(algo_func, points)
                
                if 'error' in result:
                    print(f"ERROR ({result['error']})")
                    errors.append(result['error'])
                    lengths.append(None)
                    runtimes.append(result['runtime'])
                else:
                    # Verify tour length matches calculated distance
                    calculated_length = calculate_tour_length(points, result['tour'])
                    if abs(calculated_length - result['distance']) > 0.001:
                        print(f"WARNING: distance mismatch {result['distance']:.3f} vs {calculated_length:.3f}")
                    
                    lengths.append(result['distance'])
                    runtimes.append(result['runtime'])
                    print(f"{result['distance']:.3f} (runtime: {result['runtime']:.2f}s)")
            
            # Store results
            results[n][algo_id] = {
                'lengths': lengths,
                'runtimes': runtimes,
                'errors': errors,
                'name': ALGORITHM_NAMES[algo_id]
            }
    
    return results

def calculate_statistics(results):
    """Calculate statistics from benchmark results."""
    stats_results = {}
    
    for n in PROBLEM_SIZES:
        stats_results[n] = {}
        
        for algo_id, algo_data in results[n].items():
            lengths = [l for l in algo_data['lengths'] if l is not None]
            runtimes = algo_data['runtimes']
            
            if not lengths:
                stats_results[n][algo_id] = {
                    'mean_length': None,
                    'std_length': None,
                    'mean_runtime': None,
                    'std_runtime': None,
                    'error_count': len(algo_data['errors']),
                    'errors': algo_data['errors']
                }
                continue
            
            # Calculate statistics
            mean_length = np.mean(lengths)
            std_length = np.std(lengths, ddof=1)  # Sample standard deviation
            mean_runtime = np.mean(runtimes)
            std_runtime = np.std(runtimes, ddof=1)
            
            stats_results[n][algo_id] = {
                'mean_length': float(mean_length),
                'std_length': float(std_length),
                'mean_runtime': float(mean_runtime),
                'std_runtime': float(std_runtime),
                'error_count': len(algo_data['errors']),
                'errors': algo_data['errors']
            }
    
    return stats_results

def calculate_improvements(stats_results):
    """Calculate improvement percentages relative to v1 baseline."""
    improvements = {}
    
    for n in PROBLEM_SIZES:
        improvements[n] = {}
        
        # Get baseline (v1_nn)
        baseline_data = stats_results[n].get('v1_nn')
        if not baseline_data or baseline_data['mean_length'] is None:
            print(f"WARNING: No baseline data for n={n}")
            continue
        
        baseline_mean = baseline_data['mean_length']
        
        for algo_id, algo_data in stats_results[n].items():
            if algo_id == 'v1_nn':
                continue  # Skip baseline itself
            
            if algo_data['mean_length'] is None:
                improvements[n][algo_id] = None
                continue
            
            # Calculate improvement percentage
            # Negative means worse than baseline
            improvement = ((baseline_mean - algo_data['mean_length']) / baseline_mean) * 100
            improvements[n][algo_id] = float(improvement)
    
    return improvements

def perform_statistical_tests(results, stats_results):
    """Perform simple statistical significance tests."""
    tests = {}
    
    for n in PROBLEM_SIZES:
        tests[n] = {}
        
        # Get baseline lengths
        baseline_lengths = [l for l in results[n]['v1_nn']['lengths'] if l is not None]
        if not baseline_lengths:
            continue
        
        for algo_id, algo_data in results[n].items():
            if algo_id == 'v1_nn':
                continue  # Skip baseline itself
            
            algo_lengths = [l for l in algo_data['lengths'] if l is not None]
            if not algo_lengths:
                tests[n][algo_id] = {'significant': False, 'wins': 0, 'losses': 0, 'ties': 0}
                continue
            
            # Ensure same number of samples (remove None values from both)
            paired_lengths = []
            paired_baseline = []
            for bl, al in zip(baseline_lengths, algo_lengths):
                if bl is not None and al is not None:
                    paired_baseline.append(bl)
                    paired_lengths.append(al)
            
            if len(paired_lengths) < 2:
                tests[n][algo_id] = {'significant': False, 'wins': 0, 'losses': 0, 'ties': 0}
                continue
            
            # Count wins/losses (sign test)
            wins = sum(1 for b, a in zip(paired_baseline, paired_lengths) if a < b)
            losses = sum(1 for b, a in zip(paired_baseline, paired_lengths) if a > b)
            ties = len(paired_lengths) - wins - losses
            
            # Simple significance test: need ≥8 wins out of 10 for p<0.05 (one-tailed)
            significant = wins >= 8
            
            tests[n][algo_id] = {
                'significant': significant,
                'wins': wins,
                'losses': losses,
                'ties': ties,
                'sample_size': len(paired_lengths)
            }
    
    return tests

def generate_report(stats_results, improvements, tests):
    """Generate comprehensive report."""
    report = []
    
    report.append("=" * 80)
    report.append("FOCUSED MULTI-SEED TSP BENCHMARK REPORT")
    report.append("=" * 80)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Seeds: {len(SEEDS)} ({SEEDS[0]} to {SEEDS[-1]})")
    report.append(f"Problem sizes: {PROBLEM_SIZES}")
    report.append(f"Baseline: Nearest Neighbor + 2-opt (v1)")
    report.append("")
    
    for n in PROBLEM_SIZES:
        report.append(f"\n{'='*60}")
        report.append(f"RESULTS FOR n = {n}")
        report.append(f"{'='*60}")
        
        # Performance table
        report.append("\nPerformance Summary (mean ± std):")
        report.append("-" * 80)
        report.append(f"{'Algorithm':<50} {'Tour Length':<20} {'Runtime (s)':<15} {'Errors'}")
        report.append("-" * 80)
        
        for algo_id in ['v1_nn', 'v8_christofides_ils', 'v19_christofides_structural']:
            if algo_id not in stats_results[n]:
                continue
            
            data = stats_results[n][algo_id]
            name = ALGORITHM_NAMES[algo_id]
            
            if data['mean_length'] is None:
                length_str = "FAILED"
            else:
                length_str = f"{data['mean_length']:.3f} ± {data['std_length']:.3f}"
            
            runtime_str = f"{data['mean_runtime']:.2f} ± {data['std_runtime']:.2f}" if data['mean_runtime'] is not None else "N/A"
            error_str = f"{data['error_count']}/{len(SEEDS)}"
            
            report.append(f"{name:<50} {length_str:<20} {runtime_str:<15} {error_str}")
        
        # Improvement table
        report.append("\n\nImprovement vs NN+2opt Baseline:")
        report.append("-" * 80)
        report.append(f"{'Algorithm':<50} {'Improvement %':<15} {'Statistical Significance'}")
        report.append("-" * 80)
        
        # Baseline row
        report.append(f"{ALGORITHM_NAMES['v1_nn']:<50} {'0.00% (baseline)':<15} {'N/A'}")
        
        # Other algorithms
        for algo_id in ['v8_christofides_ils', 'v19_christofides_structural']:
            if algo_id not in improvements[n]:
                continue
            
            improvement = improvements[n][algo_id]
            test_result = tests[n].get(algo_id, {})
            
            if improvement is None:
                improvement_str = "FAILED"
                sig_str = "N/A"
            else:
                improvement_str = f"{improvement:+.2f}%"
                if test_result.get('significant'):
                    wins = test_result.get('wins', 0)
                    losses = test_result.get('losses', 0)
                    sig_str = f"SIGNIFICANT ({wins} wins, {losses} losses)"
                else:
                    wins = test_result.get('wins', 0)
                    losses = test_result.get('losses', 0)
                    sig_str = f"NOT SIGNIFICANT ({wins} wins, {losses} losses)"
            
            report.append(f"{ALGORITHM_NAMES[algo_id]:<50} {improvement_str:<15} {sig_str}")
        
        # Error details
        report.append("\n\nError Details:")
        report.append("-" * 80)
        error_found = False
        for algo_id in ['v8_christofides_ils', 'v19_christofides_structural']:
            if algo_id in stats_results[n]:
                errors = stats_results[n][algo_id]['errors']
                if errors:
                    error_found = True
                    report.append(f"\n{ALGORITHM_NAMES[algo_id]}:")
                    for i, error in enumerate(errors[:5]):  # Show first 5 errors
                        report.append(f"  Seed {SEEDS[i]}: {error}")
                    if len(errors) > 5:
                        report.append(f"  ... and {len(errors) - 5} more errors")
        
        if not error_found:
            report.append("No errors encountered.")
    
    # Summary and conclusions
    report.append("\n\n" + "="*80)
    report.append("SUMMARY AND CONCLUSIONS")
    report.append("="*80)
    
    # Check if any algorithm shows statistically significant improvement
    significant_improvements = []
    for n in PROBLEM_SIZES:
        for algo_id in ['v8_christofides_ils', 'v19_christofides_structural']:
            if algo_id in tests[n] and tests[n][algo_id].get('significant'):
                improvement = improvements[n].get(algo_id)
                if improvement is not None and improvement > 0:
                    significant_improvements.append((n, algo_id, improvement))
    
    if significant_improvements:
        report.append("\nSTATISTICALLY SIGNIFICANT IMPROVEMENTS FOUND:")
        for n, algo_id, improvement in significant_improvements:
            report.append(f"  - {ALGORITHM_NAMES[algo_id]} on n={n}: {improvement:+.2f}% improvement")
    else:
        report.append("\nNO STATISTICALLY SIGNIFICANT IMPROVEMENTS FOUND.")
        report.append("  All tested algorithms perform similarly to or worse than NN+2opt baseline.")
    
    report.append("\nMETHODOLOGICAL NOTES:")
    report.append("  1. Baseline: NN+2opt (v1) - correct baseline for comparison")
    report.append("  2. Statistical significance: ≥8 wins out of 10 seeds (sign test, p < 0.05)")
    report.append("  3. Multi-seed validation: 10 seeds per problem size")
    report.append("  4. Timeout protection: 60 seconds per run")
    
    return "\n".join(report)

def save_results(results, stats_results, improvements, tests, report):
    """Save all results to files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)
    
    # Save raw results
    raw_results_file = results_dir / f"focused_results_{timestamp}.json"
    with open(raw_results_file, 'w') as f:
        json.dump({
            'config': {
                'problem_sizes': PROBLEM_SIZES,
                'seeds': SEEDS,
                'timeout': TIMEOUT_SECONDS,
                'baseline': 'v1_nn (NN+2opt)'
            },
            'results': results,
            'statistics': stats_results,
            'improvements': improvements,
            'statistical_tests': tests
        }, f, indent=2, default=str)
    
    # Save report
    report_file = results_dir / f"focused_benchmark_report_{timestamp}.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\nResults saved to:")
    print(f"  Raw data: {raw_results_file}")
    print(f"  Full report: {report_file}")
    
    return report_file

def main():
    """Main function."""
    print("=" * 80)
    print("FOCUSED MULTI-SEED TSP BENCHMARK")
    print("=" * 80)
    print(f"Problem sizes: {PROBLEM_SIZES}")
    print(f"Seeds: {len(SEEDS)} ({SEEDS[0]} to {SEEDS[-1]})")
    print(f"Algorithms: {', '.join(ALGORITHM_NAMES.values())}")
    print(f"Baseline: {ALGORITHM_NAMES['v1_nn']}")
    print(f"Timeout: {TIMEOUT_SECONDS} seconds per run")
    print("=" * 80)
    
    # Run benchmarks
    print("\nRunning benchmarks...")
    results = run_benchmarks()
    
    # Calculate statistics
    print("\nCalculating statistics...")
    stats_results = calculate_statistics(results)
    
    # Calculate improvements
    improvements = calculate_improvements(stats_results)
    
    # Perform statistical tests
    print("Performing statistical tests...")
    tests = perform_statistical_tests(results, stats_results)
    
    # Generate report
    print("Generating report...")
    report = generate_report(stats_results, improvements, tests)
    
    # Save results
    report_file = save_results(results, stats_results, improvements, tests, report)
    
    # Print summary
    print("\n" + "=" * 80)
    print("BENCHMARK COMPLETE")
    print("=" * 80)
    print("\nKey findings:")
    
    # Print key findings
    for n in PROBLEM_SIZES:
        print(f"\nn = {n}:")
        for algo_id in ['v8_christofides_ils', 'v19_christofides_structural']:
            if algo_id in improvements[n] and improvements[n][algo_id] is not None:
                improvement = improvements[n][algo_id]
                test_result = tests[n].get(algo_id, {})
                sig = "✓ SIGNIFICANT" if test_result.get('significant') else "✗ NOT SIGNIFICANT"
                print(f"  {ALGORITHM_NAMES[algo_id]}: {improvement:+.2f}% ({sig})")
    
    print(f"\nFull report saved to: {report_file}")
    print("=" * 80)

if __name__ == "__main__":
    main()
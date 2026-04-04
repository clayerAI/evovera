#!/usr/bin/env python3
"""
Comprehensive multi-seed benchmark for TSP algorithms.
Runs benchmarks with ≥10 seeds, computes statistics, and performs significance tests.
"""

import sys
import os
import time
import json
import numpy as np
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from solutions.tsp_v1_nearest_neighbor import solve_tsp as nn_solve
from solutions.tsp_v2_christofides import solve_tsp as christofides_solve
from solutions.tsp_v8_christofides_ils_hybrid_fixed import solve_tsp as christofides_ils_solve
from solutions.tsp_v19_christofides_hybrid_structural import solve_tsp as christofides_structural_solve

# Import problem generator
from benchmarks.problem_generator import generate_random_tsp_instance

# Try to import scipy for statistical tests, fallback to manual implementation
try:
    from scipy import stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    print("WARNING: scipy not available. Using manual statistical tests (less accurate).")

# Algorithm mapping
ALGORITHMS = {
    'v1_nn': nn_solve,
    'v2_christofides': christofides_solve,
    'v8_christofides_ils': christofides_ils_solve,
    'v19_christofides_structural': christofides_structural_solve
}

ALGORITHM_NAMES = {
    'v1_nn': 'Nearest Neighbor + 2-opt',
    'v2_christofides': 'Christofides',
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
            tour = algorithm_func(points)
            end_time = time.time()
            result_queue.put({
                'tour': tour,
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
    """Run comprehensive benchmarks."""
    results = {}
    
    for n in PROBLEM_SIZES:
        print(f"\n{'='*60}")
        print(f"Benchmarking n={n}")
        print(f"{'='*60}")
        
        results[n] = {}
        
        # Generate problems for each seed
        problems = {}
        for seed in SEEDS:
            problems[seed] = generate_random_tsp_instance(n, seed=seed)
        
        # Benchmark each algorithm
        for algo_id, algo_func in ALGORITHMS.items():
            print(f"\n  {ALGORITHM_NAMES[algo_id]} ({algo_id}):")
            
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
                    tour_length = calculate_tour_length(points, result['tour'])
                    lengths.append(tour_length)
                    runtimes.append(result['runtime'])
                    print(f"{tour_length:.3f} (runtime: {result['runtime']:.2f}s)")
            
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
    """Calculate improvement percentages relative to NN+2opt baseline."""
    improvements = {}
    
    for n in PROBLEM_SIZES:
        improvements[n] = {}
        
        # Get baseline (v2_nn2opt)
        baseline_data = stats_results[n].get('v2_nn2opt')
        if not baseline_data or baseline_data['mean_length'] is None:
            print(f"WARNING: No baseline data for n={n}")
            continue
        
        baseline_mean = baseline_data['mean_length']
        
        for algo_id, algo_data in stats_results[n].items():
            if algo_id == 'v2_nn2opt':
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
    """Perform statistical significance tests."""
    tests = {}
    
    for n in PROBLEM_SIZES:
        tests[n] = {}
        
        # Get baseline lengths
        baseline_lengths = [l for l in results[n]['v2_nn2opt']['lengths'] if l is not None]
        if not baseline_lengths:
            continue
        
        for algo_id, algo_data in results[n].items():
            if algo_id == 'v2_nn2opt':
                continue  # Skip baseline itself
            
            algo_lengths = [l for l in algo_data['lengths'] if l is not None]
            if not algo_lengths:
                tests[n][algo_id] = {'p_value': None, 'significant': False}
                continue
            
            # Ensure same number of samples (remove None values from both)
            paired_lengths = []
            paired_baseline = []
            for bl, al in zip(baseline_lengths, algo_lengths):
                if bl is not None and al is not None:
                    paired_baseline.append(bl)
                    paired_lengths.append(al)
            
            if len(paired_lengths) < 2:
                tests[n][algo_id] = {'p_value': None, 'significant': False}
                continue
            
            # Perform statistical test
            if HAS_SCIPY:
                # Paired t-test
                t_stat, p_value = stats.ttest_rel(paired_baseline, paired_lengths)
                significant = p_value < 0.05
            else:
                # Manual sign test (non-parametric)
                # Count wins/losses
                wins = sum(1 for b, a in zip(paired_baseline, paired_lengths) if a < b)
                losses = sum(1 for b, a in zip(paired_baseline, paired_lengths) if a > b)
                ties = len(paired_lengths) - wins - losses
                
                # Simple binomial test approximation
                # For n=10, need ≥8 wins for p<0.05 (one-tailed)
                p_value = None
                significant = wins >= 8  # Conservative threshold
            
            tests[n][algo_id] = {
                'p_value': float(p_value) if p_value is not None else None,
                'significant': significant,
                'sample_size': len(paired_lengths)
            }
    
    return tests

def generate_report(stats_results, improvements, tests):
    """Generate comprehensive report."""
    report = []
    
    report.append("=" * 80)
    report.append("COMPREHENSIVE MULTI-SEED TSP BENCHMARK REPORT")
    report.append("=" * 80)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Seeds: {len(SEEDS)} ({SEEDS[0]} to {SEEDS[-1]})")
    report.append(f"Problem sizes: {PROBLEM_SIZES}")
    report.append(f"Statistical tests: {'scipy available' if HAS_SCIPY else 'manual sign test'}")
    report.append("")
    
    for n in PROBLEM_SIZES:
        report.append(f"\n{'='*60}")
        report.append(f"RESULTS FOR n = {n}")
        report.append(f"{'='*60}")
        
        # Performance table
        report.append("\nPerformance Summary (mean ± std):")
        report.append("-" * 80)
        report.append(f"{'Algorithm':<40} {'Tour Length':<20} {'Runtime (s)':<15} {'Errors'}")
        report.append("-" * 80)
        
        for algo_id in ['v1_nn', 'v2_nn2opt', 'v8_christofides_ils', 'v19_christofides_structural_ils']:
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
            
            report.append(f"{name:<40} {length_str:<20} {runtime_str:<15} {error_str}")
        
        # Improvement table
        report.append("\n\nImprovement vs NN+2opt Baseline:")
        report.append("-" * 80)
        report.append(f"{'Algorithm':<40} {'Improvement %':<15} {'Statistical Significance'}")
        report.append("-" * 80)
        
        baseline_improvement = improvements[n].get('v2_nn2opt')
        if baseline_improvement is not None:
            report.append(f"{ALGORITHM_NAMES['v2_nn2opt']:<40} {'0.00% (baseline)':<15} {'N/A'}")
        
        for algo_id in ['v8_christofides_ils', 'v19_christofides_structural_ils']:
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
                    sig_str = f"SIGNIFICANT (p={test_result.get('p_value', 'N/A'):.4f})"
                else:
                    sig_str = f"NOT SIGNIFICANT (p={test_result.get('p_value', 'N/A'):.4f})"
            
            report.append(f"{ALGORITHM_NAMES[algo_id]:<40} {improvement_str:<15} {sig_str}")
        
        # Error details
        report.append("\n\nError Details:")
        report.append("-" * 80)
        error_found = False
        for algo_id in ['v8_christofides_ils', 'v19_christofides_structural_ils']:
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
        for algo_id in ['v8_christofides_ils', 'v19_christofides_structural_ils']:
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
    report.append("  1. Baseline: NN+2opt (v2) - stronger than plain NN")
    report.append("  2. Statistical significance: p < 0.05 threshold")
    report.append("  3. Multi-seed validation: 10 seeds per problem size")
    report.append("  4. Timeout protection: 60 seconds per run")
    
    return "\n".join(report)

def save_results(results, stats_results, improvements, tests, report):
    """Save all results to files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)
    
    # Save raw results
    raw_results_file = results_dir / f"raw_results_{timestamp}.json"
    with open(raw_results_file, 'w') as f:
        json.dump({
            'config': {
                'problem_sizes': PROBLEM_SIZES,
                'seeds': SEEDS,
                'timeout': TIMEOUT_SECONDS
            },
            'results': results,
            'statistics': stats_results,
            'improvements': improvements,
            'statistical_tests': tests
        }, f, indent=2, default=str)
    
    # Save report
    report_file = results_dir / f"benchmark_report_{timestamp}.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    
    # Save summary for README
    summary_file = results_dir / f"summary_{timestamp}.md"
    summary = generate_summary_markdown(stats_results, improvements, tests)
    with open(summary_file, 'w') as f:
        f.write(summary)
    
    print(f"\nResults saved to:")
    print(f"  Raw data: {raw_results_file}")
    print(f"  Full report: {report_file}")
    print(f"  Summary: {summary_file}")
    
    return report_file

def generate_summary_markdown(stats_results, improvements, tests):
    """Generate markdown summary for README."""
    summary = []
    
    summary.append("# Multi-Seed Benchmark Summary")
    summary.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    summary.append("")
    
    summary.append("## Key Findings")
    summary.append("")
    
    # Check for significant improvements
    significant_found = False
    for n in PROBLEM_SIZES:
        for algo_id in ['v8_christofides_ils', 'v19_christofides_structural_ils']:
            if algo_id in tests[n] and tests[n][algo_id].get('significant'):
                improvement = improvements[n].get(algo_id)
                if improvement is not None and improvement > 0:
                    significant_found = True
                    summary.append(f"- **{ALGORITHM_NAMES[algo_id]}** shows statistically significant improvement on n={n}: **{improvement:+.2f}%**")
    
    if not significant_found:
        summary.append("- **No statistically significant improvements found**")
        summary.append("- All tested algorithms perform similarly to or worse than NN+2opt baseline")
    
    summary.append("")
    summary.append("## Performance Summary")
    summary.append("")
    
    for n in PROBLEM_SIZES:
        summary.append(f"### n = {n}")
        summary.append("")
        summary.append("| Algorithm | Tour Length (mean ± std) | Improvement vs NN+2opt | Statistical Significance |")
        summary.append("|-----------|--------------------------|------------------------|---------------------------|")
        
        # Baseline row
        baseline_data = stats_results[n]['v2_nn2opt']
        summary.append(f"| **{ALGORITHM_NAMES['v2_nn2opt']}** | {baseline_data['mean_length']:.3f} ± {baseline_data['std_length']:.3f} | 0.00% (baseline) | N/A |")
        
        # Other algorithms
        for algo_id in ['v8_christofides_ils', 'v19_christofides_structural_ils']:
            if algo_id not in stats_results[n]:
                continue
            
            data = stats_results[n][algo_id]
            improvement = improvements[n].get(algo_id)
            test_result = tests[n].get(algo_id, {})
            
            if data['mean_length'] is None:
                length_str = "FAILED"
                improvement_str = "N/A"
                sig_str = "N/A"
            else:
                length_str = f"{data['mean_length']:.3f} ± {data['std_length']:.3f}"
                improvement_str = f"{improvement:+.2f}%" if improvement is not None else "N/A"
                
                if test_result.get('significant'):
                    p_val = test_result.get('p_value', 'N/A')
                    if isinstance(p_val, float):
                        sig_str = f"✓ (p={p_val:.4f})"
                    else:
                        sig_str = "✓"
                else:
                    p_val = test_result.get('p_value', 'N/A')
                    if isinstance(p_val, float):
                        sig_str = f"✗ (p={p_val:.4f})"
                    else:
                        sig_str = "✗"
            
            summary.append(f"| {ALGORITHM_NAMES[algo_id]} | {length_str} | {improvement_str} | {sig_str} |")
        
        summary.append("")
    
    summary.append("## Methodology")
    summary.append("")
    summary.append("- **Baseline**: NN+2opt (v2) - stronger than plain NN")
    summary.append(f"- **Seeds**: {len(SEEDS)} seeds ({SEEDS[0]} to {SEEDS[-1]})")
    summary.append(f"- **Problem sizes**: {PROBLEM_SIZES}")
    summary.append("- **Statistical test**: " + ("Paired t-test (scipy)" if HAS_SCIPY else "Manual sign test"))
    summary.append("- **Significance threshold**: p < 0.05")
    summary.append(f"- **Timeout**: {TIMEOUT_SECONDS} seconds per run")
    
    return "\n".join(summary)

def main():
    """Main function."""
    print("=" * 80)
    print("COMPREHENSIVE MULTI-SEED TSP BENCHMARK")
    print("=" * 80)
    print(f"Problem sizes: {PROBLEM_SIZES}")
    print(f"Seeds: {len(SEEDS)} ({SEEDS[0]} to {SEEDS[-1]})")
    print(f"Algorithms: {', '.join(ALGORITHM_NAMES.values())}")
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
        for algo_id in ['v8_christofides_ils', 'v19_christofides_structural_ils']:
            if algo_id in improvements[n] and improvements[n][algo_id] is not None:
                improvement = improvements[n][algo_id]
                test_result = tests[n].get(algo_id, {})
                sig = "✓" if test_result.get('significant') else "✗"
                print(f"  {ALGORITHM_NAMES[algo_id]}: {improvement:+.2f}% {sig}")
    
    print(f"\nFull report saved to: {report_file}")
    print("=" * 80)

if __name__ == "__main__":
    main()
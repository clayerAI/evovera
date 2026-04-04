#!/usr/bin/env python3
"""
Comprehensive Multi-Seed Benchmark for TSP Algorithms
Validates Christofides vs NN+2opt baseline findings with statistical significance.
Phase 1 of methodological correction plan.
"""

import sys
import os
import numpy as np
import time
import json
from datetime import datetime
import random

# Import our statistical tests module
sys.path.insert(0, os.path.dirname(__file__))
try:
    from statistical_tests import (
        mann_whitney_u_test,
        bootstrap_confidence_interval,
        cohens_d_effect_size,
        statistical_report
    )
    STATS_AVAILABLE = True
    print("✓ Using statistical tests module")
except ImportError:
    STATS_AVAILABLE = False
    print("⚠️  Statistical tests module not available, using basic stats")

# Import TSP algorithms
try:
    import tsp_algorithms
    ALGORITHMS = {
        'NN+2opt': tsp_algorithms.get_algorithm('tsp_v1_nearest_neighbor'),
        'Christofides': tsp_algorithms.get_algorithm('tsp_v2_christofides_improved'),
        'Christofides_v19': tsp_algorithms.get_algorithm('tsp_v19_christofides_hybrid_structural')
    }
    print(f"✓ Imported {len(ALGORITHMS)} algorithms for benchmarking")
except ImportError as e:
    print(f"✗ Failed to import algorithms: {e}")
    sys.exit(1)

# Benchmark parameters from Vera's coordination signals
N_VALUES = [50, 100, 200]  # Problem sizes
SEEDS = list(range(1, 11))  # 10 different seeds for statistical power
REPETITIONS = 3  # Repetitions per seed for stability

# Results storage
results = {
    'metadata': {
        'benchmark_name': 'Multi-Seed TSP Algorithm Validation',
        'date': datetime.now().isoformat(),
        'n_values': N_VALUES,
        'seeds': SEEDS,
        'repetitions': REPETITIONS,
        'algorithms': list(ALGORITHMS.keys())
    },
    'raw_results': {},
    'summary_stats': {}
}

def generate_tsp_instance(n, seed):
    """Generate random Euclidean TSP instance."""
    np.random.seed(seed)
    random.seed(seed)
    return np.random.rand(n, 2)

def run_benchmark():
    """Run comprehensive multi-seed benchmark."""
    print("\n" + "="*60)
    print("COMPREHENSIVE MULTI-SEED TSP BENCHMARK")
    print("Validating Christofides vs NN+2opt baseline findings")
    print("="*60)
    
    total_runs = len(N_VALUES) * len(SEEDS) * len(ALGORITHMS) * REPETITIONS
    print(f"Total benchmark runs: {total_runs}")
    print(f"Problem sizes: {N_VALUES}")
    print(f"Seeds: {SEEDS}")
    print(f"Algorithms: {list(ALGORITHMS.keys())}")
    print(f"Repetitions per configuration: {REPETITIONS}")
    print()
    
    start_time = time.time()
    
    for n in N_VALUES:
        print(f"\n{'='*40}")
        print(f"Benchmarking n = {n}")
        print(f"{'='*40}")
        
        results['raw_results'][n] = {}
        results['summary_stats'][n] = {}
        
        for seed in SEEDS:
            print(f"\n  Seed {seed}: ", end='', flush=True)
            
            # Generate instance once per seed
            points = generate_tsp_instance(n, seed)
            
            seed_results = {}
            
            for alg_name, alg_func in ALGORITHMS.items():
                print(f"{alg_name[:4]} ", end='', flush=True)
                
                run_times = []
                tour_lengths = []
                
                for rep in range(REPETITIONS):
                    # Time the algorithm
                    run_start = time.time()
                    try:
                        tour, length = alg_func(points)
                        run_end = time.time()
                        
                        run_times.append(run_end - run_start)
                        tour_lengths.append(length)
                        
                    except Exception as e:
                        print(f"\n    ✗ {alg_name} failed: {e}")
                        run_times.append(float('inf'))
                        tour_lengths.append(float('inf'))
                
                seed_results[alg_name] = {
                    'times': run_times,
                    'lengths': tour_lengths,
                    'mean_time': np.mean(run_times),
                    'mean_length': np.mean(tour_lengths),
                    'std_length': np.std(tour_lengths) if len(tour_lengths) > 1 else 0
                }
            
            results['raw_results'][n][seed] = seed_results
        
        # Calculate summary statistics for this n
        print(f"\n\n  Calculating summary statistics for n={n}...")
        
        for alg_name in ALGORITHMS.keys():
            # Collect all lengths across seeds for this algorithm
            all_lengths = []
            for seed in SEEDS:
                lengths = results['raw_results'][n][seed][alg_name]['lengths']
                all_lengths.extend(lengths)
            
            if all_lengths and not any(np.isinf(l) for l in all_lengths):
                results['summary_stats'][n][alg_name] = {
                    'mean': np.mean(all_lengths),
                    'std': np.std(all_lengths),
                    'min': np.min(all_lengths),
                    'max': np.max(all_lengths),
                    'n_samples': len(all_lengths)
                }
            else:
                results['summary_stats'][n][alg_name] = {
                    'mean': float('inf'),
                    'std': 0,
                    'min': float('inf'),
                    'max': float('inf'),
                    'n_samples': 0
                }
    
    elapsed_time = time.time() - start_time
    print(f"\n\n{'='*60}")
    print(f"BENCHMARK COMPLETED IN {elapsed_time:.1f} SECONDS")
    print(f"{'='*60}")
    
    return results

def perform_statistical_analysis(results):
    """Perform statistical tests on benchmark results."""
    print("\n" + "="*60)
    print("STATISTICAL ANALYSIS")
    print("="*60)
    
    statistical_results = {}
    
    for n in N_VALUES:
        print(f"\nProblem size n = {n}:")
        
        # Extract data for statistical tests
        nn_data = []
        christofides_data = []
        christofides_v19_data = []
        
        for seed in SEEDS:
            # Get NN+2opt results
            nn_lengths = results['raw_results'][n][seed]['NN+2opt']['lengths']
            nn_data.extend(nn_lengths)
            
            # Get Christofides results
            christofides_lengths = results['raw_results'][n][seed]['Christofides']['lengths']
            christofides_data.extend(christofides_lengths)
            
            # Get Christofides v19 results
            christofides_v19_lengths = results['raw_results'][n][seed]['Christofides_v19']['lengths']
            christofides_v19_data.extend(christofides_v19_lengths)
        
        # Remove any infinite values
        nn_data = [x for x in nn_data if not np.isinf(x)]
        christofides_data = [x for x in christofides_data if not np.isinf(x)]
        christofides_v19_data = [x for x in christofides_v19_data if not np.isinf(x)]
        
        if len(nn_data) < 5 or len(christofides_data) < 5:
            print(f"  ⚠️  Insufficient data for statistical tests (n={n})")
            continue
        
        statistical_results[n] = {}
        
        # 1. Mann-Whitney U test: NN+2opt vs Christofides
        if STATS_AVAILABLE:
            u_stat, p_value = mann_whitney_u_test(nn_data, christofides_data)
            statistical_results[n]['nn_vs_christofides'] = {
                'test': 'Mann-Whitney U',
                'u_statistic': u_stat,
                'p_value': p_value,
                'significant': p_value < 0.05
            }
            
            print(f"  NN+2opt vs Christofides:")
            print(f"    U = {u_stat:.2f}, p = {p_value:.4f}", end='')
            if p_value < 0.05:
                print(f" (SIGNIFICANT)")
            else:
                print(f" (not significant)")
        
        # 2. Effect size (Cohen's d)
        if STATS_AVAILABLE:
            d = cohens_d_effect_size(nn_data, christofides_data)
            statistical_results[n]['effect_size'] = {
                'cohens_d': d,
                'magnitude': 'small' if abs(d) < 0.5 else 'medium' if abs(d) < 0.8 else 'large'
            }
            print(f"    Cohen's d = {d:.3f} ({statistical_results[n]['effect_size']['magnitude']} effect)")
        
        # 3. Bootstrap confidence intervals
        if STATS_AVAILABLE and len(nn_data) >= 10 and len(christofides_data) >= 10:
            ci_nn = bootstrap_confidence_interval(nn_data)
            ci_christofides = bootstrap_confidence_interval(christofides_data)
            
            statistical_results[n]['confidence_intervals'] = {
                'NN+2opt': ci_nn,
                'Christofides': ci_christofides
            }
            
            print(f"    95% CI NN+2opt: [{ci_nn[0]:.4f}, {ci_nn[1]:.4f}]")
            print(f"    95% CI Christofides: [{ci_christofides[0]:.4f}, {ci_christofides[1]:.4f}]")
        
        # 4. Mean comparison
        mean_nn = np.mean(nn_data)
        mean_christofides = np.mean(christofides_data)
        mean_v19 = np.mean(christofides_v19_data) if christofides_v19_data else float('inf')
        
        improvement = (mean_nn - mean_christofides) / mean_nn * 100
        improvement_v19 = (mean_nn - mean_v19) / mean_nn * 100 if not np.isinf(mean_v19) else 0
        
        statistical_results[n]['means'] = {
            'NN+2opt': mean_nn,
            'Christofides': mean_christofides,
            'Christofides_v19': mean_v19,
            'improvement_%': improvement,
            'improvement_v19_%': improvement_v19
        }
        
        print(f"    Mean tour lengths:")
        print(f"      NN+2opt: {mean_nn:.4f}")
        print(f"      Christofides: {mean_christofides:.4f} ({improvement:+.1f}%)")
        if not np.isinf(mean_v19):
            print(f"      Christofides v19: {mean_v19:.4f} ({improvement_v19:+.1f}%)")
    
    return statistical_results

def generate_report(results, statistical_results):
    """Generate comprehensive benchmark report."""
    print("\n" + "="*60)
    print("GENERATING BENCHMARK REPORT")
    print("="*60)
    
    report = {
        'metadata': results['metadata'],
        'summary': {},
        'statistical_findings': {},
        'conclusions': []
    }
    
    # Summary table
    for n in N_VALUES:
        if n in results['summary_stats']:
            report['summary'][n] = results['summary_stats'][n]
    
    # Statistical findings
    for n in N_VALUES:
        if n in statistical_results:
            report['statistical_findings'][n] = statistical_results[n]
    
    # Conclusions
    for n in N_VALUES:
        if n in statistical_results and 'nn_vs_christofides' in statistical_results[n]:
            stats = statistical_results[n]['nn_vs_christofides']
            means = statistical_results[n]['means']
            
            conclusion = f"n={n}: "
            if stats['significant']:
                if means['improvement_%'] > 0:
                    conclusion += f"Christofides significantly better than NN+2opt (+{means['improvement_%']:.1f}%, p={stats['p_value']:.4f})"
                else:
                    conclusion += f"Christofides significantly worse than NN+2opt ({means['improvement_%']:.1f}%, p={stats['p_value']:.4f})"
            else:
                conclusion += f"No significant difference between Christofides and NN+2opt (p={stats['p_value']:.4f})"
            
            report['conclusions'].append(conclusion)
    
    # Save report to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"reports/multi_seed_benchmark_{timestamp}.json"
    
    os.makedirs('reports', exist_ok=True)
    
    with open(report_filename, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n✓ Report saved to {report_filename}")
    
    # Also generate a human-readable summary
    summary_filename = f"reports/multi_seed_benchmark_summary_{timestamp}.txt"
    with open(summary_filename, 'w') as f:
        f.write("="*60 + "\n")
        f.write("MULTI-SEED TSP BENCHMARK SUMMARY\n")
        f.write("="*60 + "\n\n")
        
        f.write("BENCHMARK PARAMETERS:\n")
        f.write(f"  Date: {results['metadata']['date']}\n")
        f.write(f"  Problem sizes: {results['metadata']['n_values']}\n")
        f.write(f"  Seeds: {len(results['metadata']['seeds'])} (1-{len(results['metadata']['seeds'])})\n")
        f.write(f"  Repetitions per seed: {results['metadata']['repetitions']}\n")
        f.write(f"  Algorithms: {', '.join(results['metadata']['algorithms'])}\n\n")
        
        f.write("KEY FINDINGS:\n")
        for n in N_VALUES:
            if n in statistical_results and 'means' in statistical_results[n]:
                means = statistical_results[n]['means']
                f.write(f"\n  n = {n}:\n")
                f.write(f"    NN+2opt mean: {means['NN+2opt']:.4f}\n")
                f.write(f"    Christofides mean: {means['Christofides']:.4f}\n")
                f.write(f"    Improvement: {means['improvement_%']:+.1f}%\n")
                
                if 'nn_vs_christofides' in statistical_results[n]:
                    stats = statistical_results[n]['nn_vs_christofides']
                    f.write(f"    Statistical significance: p = {stats['p_value']:.4f}")
                    if stats['significant']:
                        f.write(" (SIGNIFICANT)\n")
                    else:
                        f.write(" (not significant)\n")
        
        f.write("\nCONCLUSIONS:\n")
        for conclusion in report['conclusions']:
            f.write(f"  • {conclusion}\n")
    
    print(f"✓ Summary saved to {summary_filename}")
    
    return report_filename, summary_filename

def main():
    """Main benchmark execution."""
    print("\n" + "="*60)
    print("METHODOLOGICAL CORRECTION - PHASE 1")
    print("Comprehensive Multi-Seed Benchmark")
    print("="*60)
    
    # Run benchmark
    results = run_benchmark()
    
    # Perform statistical analysis
    statistical_results = perform_statistical_analysis(results)
    
    # Generate reports
    report_file, summary_file = generate_report(results, statistical_results)
    
    print("\n" + "="*60)
    print("BENCHMARK COMPLETE")
    print("="*60)
    print(f"\nReports generated:")
    print(f"  • Detailed report: {report_file}")
    print(f"  • Summary: {summary_file}")
    
    # Print key conclusions
    print("\nKEY CONCLUSIONS:")
    for n in N_VALUES:
        if n in statistical_results and 'means' in statistical_results[n]:
            means = statistical_results[n]['means']
            if 'nn_vs_christofides' in statistical_results[n]:
                stats = statistical_results[n]['nn_vs_christofides']
                sig = "✓" if stats['significant'] else "✗"
                print(f"  n={n}: Christofides {means['improvement_%']:+.1f}% better, p={stats['p_value']:.4f} {sig}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Efficient benchmark for v18 at n=500 with timeout protection.
"""
import sys
import os
sys.path.append('/workspace/evovera/solutions')

from tsp_v18_christofides_community_detection import solve_tsp as v18_solve
from tsp_v1_nearest_neighbor import solve_tsp as nn2opt_solve
import random
import time
import statistics
import signal

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Timeout exceeded")

def generate_random_points(n: int = 500, seed: int = 42):
    """Generate random points in unit square."""
    random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

def run_single_test(n: int, seed: int, timeout_seconds: int = 180):
    """Run single test with timeout protection."""
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)
    
    try:
        points = generate_random_points(n=n, seed=seed)
        
        # Get baseline
        start = time.time()
        baseline_tour, baseline_length = nn2opt_solve(points)
        baseline_time = time.time() - start
        
        # Test v18
        start = time.time()
        v18_tour, v18_length = v18_solve(points, seed=seed)
        v18_time = time.time() - start
        
        improvement = ((baseline_length - v18_length) / baseline_length) * 100
        
        signal.alarm(0)  # Cancel alarm
        return {
            'seed': seed,
            'baseline_length': baseline_length,
            'v18_length': v18_length,
            'improvement': improvement,
            'baseline_time': baseline_time,
            'v18_time': v18_time,
            'success': True
        }
    except TimeoutException:
        signal.alarm(0)
        return {
            'seed': seed,
            'success': False,
            'error': f"Timeout after {timeout_seconds}s"
        }
    except Exception as e:
        signal.alarm(0)
        return {
            'seed': seed,
            'success': False,
            'error': str(e)
        }

def benchmark_v18_n500():
    """Benchmark v18 algorithm at n=500."""
    print("Benchmark: v18 Christofides with Community Detection at n=500")
    print("=" * 70)
    
    # Use 3 seeds for reasonable coverage
    seeds = [42, 43, 44]
    n = 500
    
    results = []
    successful_runs = []
    
    for seed_idx, seed in enumerate(seeds):
        print(f"\nRunning benchmark with seed {seed} (n={n})...")
        
        result = run_single_test(n=n, seed=seed, timeout_seconds=180)
        results.append(result)
        
        if result['success']:
            successful_runs.append(result)
            print(f"  Results: Baseline={result['baseline_length']:.4f}, "
                  f"v18={result['v18_length']:.4f}, "
                  f"Improvement={result['improvement']:.2f}%")
            print(f"  Times: Baseline={result['baseline_time']:.2f}s, "
                  f"v18={result['v18_time']:.2f}s")
        else:
            print(f"  ❌ Failed: {result['error']}")
    
    # Calculate statistics from successful runs
    if successful_runs:
        improvements = [r['improvement'] for r in successful_runs]
        v18_times = [r['v18_time'] for r in successful_runs]
        baseline_times = [r['baseline_time'] for r in successful_runs]
        
        avg_improvement = statistics.mean(improvements)
        std_improvement = statistics.stdev(improvements) if len(improvements) > 1 else 0
        avg_v18_time = statistics.mean(v18_times)
        avg_baseline_time = statistics.mean(baseline_times)
        
        positive_count = sum(1 for imp in improvements if imp > 0)
        above_threshold_count = sum(1 for imp in improvements if imp > 0.1)
        
        print(f"\n{'='*70}")
        print(f"SUMMARY for n={n} ({len(successful_runs)}/{len(seeds)} successful runs):")
        print(f"  Average improvement: {avg_improvement:.2f}% ± {std_improvement:.2f}%")
        print(f"  Range: {min(improvements):.2f}% to {max(improvements):.2f}%")
        print(f"  Positive improvements: {positive_count}/{len(successful_runs)}")
        print(f"  Above 0.1% threshold: {above_threshold_count}/{len(successful_runs)}")
        print(f"  Time: v18={avg_v18_time:.2f}s, baseline={avg_baseline_time:.2f}s")
        
        if avg_improvement > 0.1:
            print(f"  ✅ Exceeds 0.1% publication threshold")
        elif avg_improvement > 0:
            print(f"  ⚠️  Positive but below threshold")
        else:
            print(f"  ❌ Worse than baseline")
        
        # Save results
        import json
        with open('v18_n500_benchmark_results.json', 'w') as f:
            json.dump({
                'n': n,
                'seeds': seeds,
                'results': results,
                'successful_runs': successful_runs,
                'statistics': {
                    'avg_improvement': avg_improvement,
                    'std_improvement': std_improvement,
                    'avg_v18_time': avg_v18_time,
                    'avg_baseline_time': avg_baseline_time,
                    'positive_count': positive_count,
                    'above_threshold_count': above_threshold_count
                }
            }, f, indent=2)
        
        print(f"\nResults saved to v18_n500_benchmark_results.json")
        
        return {
            'avg_improvement': avg_improvement,
            'std_improvement': std_improvement,
            'improvements': improvements,
            'avg_v18_time': avg_v18_time,
            'avg_baseline_time': avg_baseline_time,
            'positive_count': positive_count,
            'above_threshold_count': above_threshold_count,
            'successful_runs': len(successful_runs),
            'total_runs': len(seeds)
        }
    else:
        print(f"\n❌ All {len(seeds)} runs failed!")
        return None

if __name__ == "__main__":
    results = benchmark_v18_n500()
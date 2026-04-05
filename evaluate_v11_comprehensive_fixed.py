#!/usr/bin/env python3
"""
Comprehensive TSPLIB Phase 2 evaluation for v11 algorithm.
Runs multiple seeds with statistical analysis.
"""

import sys
import os
import time
import numpy as np
from datetime import datetime
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tsplib_parser import TSPLIBParser
from solutions.tsp_v19_optimized_fixed_v11_proper import ChristofidesHybridStructuralOptimizedV11 as V11Solver

# Configuration
SEEDS = 10  # Minimum 10 seeds for statistical significance
TIMEOUT_PER_INSTANCE = 300  # 5 minutes per instance (adjust as needed)

# TSPLIB instances to evaluate (name, file, optimal)
INSTANCES = [
    ("eil51", "data/tsplib/eil51.tsp", 426),
    ("kroA100", "data/tsplib/kroA100.tsp", 21282),
    ("a280", "data/tsplib/a280.tsp", 2579),
    # att532 times out - will attempt with longer timeout
    ("att532", "data/tsplib/att532.tsp", 27686),
]

def run_single_evaluation(instance_name, distance_matrix, optimal, seed):
    """Run solver with given seed."""
    np.random.seed(seed)
    
    solver = V11Solver(distance_matrix=distance_matrix)
    
    try:
        tour, length, runtime = solver.solve()
        
        # Validate tour
        n = distance_matrix.shape[0]
        if len(tour) != n + 1 or tour[0] != tour[-1]:
            return None, None, "Invalid tour structure"
        
        unique = len(set(tour[:-1]))
        if unique != n:
            return None, None, f"Invalid tour: {unique} unique nodes (expected {n})"
        
        gap = ((length - optimal) / optimal) * 100
        return length, gap, None
        
    except Exception as e:
        return None, None, str(e)

def evaluate_instance(instance_name, filepath, optimal):
    """Evaluate instance with multiple seeds."""
    print(f"\n{'='*60}")
    print(f"Evaluating {instance_name} (optimal={optimal})")
    print(f"{'='*60}")
    
    # Parse instance
    parser = TSPLIBParser(filepath)
    if not parser.parse():
        print(f"❌ Failed to parse {instance_name}")
        return None
    
    distance_matrix = parser.get_distance_matrix()
    n = distance_matrix.shape[0]
    print(f"Instance: {instance_name}, n={n}")
    
    results = []
    errors = []
    
    for seed_idx in range(SEEDS):
        seed = 42 + seed_idx * 100  # Different seeds for each run
        print(f"  Seed {seed_idx+1}/{SEEDS} (seed={seed})...", end=" ", flush=True)
        
        start_time = time.time()
        try:
            # Use timeout for large instances
            if instance_name == "att532":
                import signal
                
                class TimeoutException(Exception):
                    pass
                
                def timeout_handler(signum, frame):
                    raise TimeoutException("Timeout")
                
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(TIMEOUT_PER_INSTANCE)
                
                try:
                    length, gap, error = run_single_evaluation(instance_name, distance_matrix, optimal, seed)
                except TimeoutException:
                    length, gap, error = None, None, "Timeout"
                finally:
                    signal.alarm(0)
            else:
                length, gap, error = run_single_evaluation(instance_name, distance_matrix, optimal, seed)
            
            elapsed = time.time() - start_time
            
            if error:
                print(f"❌ Error: {error}")
                errors.append(error)
            else:
                print(f"✅ Length={length:.2f}, Gap={gap:.2f}%, Time={elapsed:.2f}s")
                results.append({
                    "seed": seed,
                    "length": float(length),
                    "gap": float(gap),
                    "time": elapsed
                })
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            errors.append(str(e))
    
    # Statistical analysis
    if results:
        gaps = [r["gap"] for r in results]
        times = [r["time"] for r in results]
        
        print(f"\n📊 Statistical Summary for {instance_name}:")
        print(f"  Samples: {len(results)}/{SEEDS} successful")
        print(f"  Gap - Mean: {np.mean(gaps):.2f}%, Std: {np.std(gaps):.2f}%")
        print(f"  Gap - Min: {np.min(gaps):.2f}%, Max: {np.max(gaps):.2f}%")
        print(f"  Time - Mean: {np.mean(times):.2f}s, Std: {np.std(times):.2f}s")
        
        # Confidence interval (95%) - handle missing scipy
        try:
            from scipy import stats
            if len(gaps) >= 2:
                ci = stats.t.interval(0.95, len(gaps)-1, loc=np.mean(gaps), scale=stats.sem(gaps))
                print(f"  Gap - 95% CI: [{ci[0]:.2f}%, {ci[1]:.2f}%]")
        except ImportError:
            print(f"  Gap - 95% CI: [N/A - scipy not installed]")
        
        return {
            "instance": instance_name,
            "n": n,
            "optimal": optimal,
            "results": results,
            "errors": errors,
            "summary": {
                "mean_gap": float(np.mean(gaps)),
                "std_gap": float(np.std(gaps)),
                "min_gap": float(np.min(gaps)),
                "max_gap": float(np.max(gaps)),
                "mean_time": float(np.mean(times)),
                "success_rate": len(results) / SEEDS
            }
        }
    else:
        print(f"\n❌ No successful runs for {instance_name}")
        return {
            "instance": instance_name,
            "n": n,
            "optimal": optimal,
            "results": [],
            "errors": errors,
            "summary": {
                "mean_gap": None,
                "std_gap": None,
                "min_gap": None,
                "max_gap": None,
                "mean_time": None,
                "success_rate": 0
            }
        }

def main():
    print("="*70)
    print("TSPLIB Phase 2: Comprehensive v11 Algorithm Evaluation")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Seeds per instance: {SEEDS}")
    print(f"Timeout per instance: {TIMEOUT_PER_INSTANCE}s")
    print("="*70)
    
    all_results = {}
    
    for instance_name, filepath, optimal in INSTANCES:
        if not os.path.exists(filepath):
            print(f"\n⚠️  Skipping {instance_name}: file not found")
            continue
            
        result = evaluate_instance(instance_name, filepath, optimal)
        all_results[instance_name] = result
    
    # Generate summary report
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    
    successful_instances = []
    for instance_name, result in all_results.items():
        if result and result["summary"]["success_rate"] > 0:
            summary = result["summary"]
            print(f"{instance_name} (n={result['n']}):")
            print(f"  Gap: {summary['mean_gap']:.2f}% ± {summary['std_gap']:.2f}%")
            print(f"  Time: {summary['mean_time']:.2f}s")
            print(f"  Success: {summary['success_rate']*100:.0f}%")
            successful_instances.append(instance_name)
        else:
            print(f"{instance_name}: ❌ Failed")
    
    # Save results to file
    output_file = "reports/v11_tsplib_evaluation_results.json"
    with open(output_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "config": {
                "seeds": SEEDS,
                "timeout": TIMEOUT_PER_INSTANCE
            },
            "results": all_results
        }, f, indent=2)
    
    print(f"\n📁 Results saved to: {output_file}")
    
    if successful_instances:
        print(f"\n✅ Evaluation completed for: {', '.join(successful_instances)}")
    else:
        print("\n❌ No instances successfully evaluated")

if __name__ == "__main__":
    main()

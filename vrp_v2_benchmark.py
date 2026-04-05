#!/usr/bin/env python3
"""
Benchmark VRP v2 structural hybrid algorithm on synthetic instances.
"""

import sys
import os
import time
import json
from typing import Dict, List, Tuple
import numpy as np

# Add solutions directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'solutions'))

from vrp_v2_clarke_wright_structural_hybrid import CapacitatedVRPStructuralHybrid
from vrp_benchmark_loader import parse_vrp_file

def benchmark_synthetic_instances():
    """Benchmark VRP v2 on synthetic instances."""
    print("VRP v2 Structural Hybrid Algorithm Benchmark")
    print("=" * 70)
    
    # Test on different sized synthetic instances
    test_cases = [
        {'n_customers': 10, 'capacity': 50, 'seed': 42, 'label': 'Small (10 customers)'},
        {'n_customers': 20, 'capacity': 100, 'seed': 42, 'label': 'Medium (20 customers)'},
        {'n_customers': 30, 'capacity': 150, 'seed': 42, 'label': 'Large (30 customers)'},
        {'n_customers': 50, 'capacity': 200, 'seed': 42, 'label': 'Extra Large (50 customers)'},
    ]
    
    methods = ['sequential', 'parallel', 'structural_hybrid']
    
    results = {}
    
    for test_case in test_cases:
        n_customers = test_case['n_customers']
        capacity = test_case['capacity']
        seed = test_case['seed']
        label = test_case['label']
        
        print(f"\n{label}: n={n_customers}, capacity={capacity}")
        print("-" * 50)
        
        # Create VRP instance
        vrp = CapacitatedVRPStructuralHybrid(
            n_customers=n_customers,
            capacity=capacity,
            seed=seed,
            depot_at_center=True
        )
        
        case_results = {}
        
        for method in methods:
            print(f"  Method: {method:20s}", end="")
            
            start_time = time.time()
            solution = vrp.solve_cvrp(method=method, apply_2opt=True)
            elapsed = time.time() - start_time
            
            # Record results
            case_results[method] = {
                'total_distance': solution['total_distance'],
                'num_routes': solution['num_routes'],
                'computation_time': solution['computation_time'],
                'has_capacity_violations': solution['has_capacity_violations'],
                'capacity_violations': solution['capacity_violations'],
                'wall_time': elapsed
            }
            
            print(f" | Distance: {solution['total_distance']:8.2f} | Routes: {solution['num_routes']:2d} | "
                  f"Time: {solution['computation_time']:7.4f}s | Violations: {solution['has_capacity_violations']}")
        
        results[label] = case_results
    
    # Calculate improvements
    print("\n" + "=" * 70)
    print("PERFORMANCE IMPROVEMENT ANALYSIS")
    print("=" * 70)
    
    for label, case_results in results.items():
        print(f"\n{label}:")
        baseline = case_results['sequential']['total_distance']
        
        for method in ['parallel', 'structural_hybrid']:
            distance = case_results[method]['total_distance']
            improvement = ((baseline - distance) / baseline) * 100 if baseline > 0 else 0
            
            print(f"  {method:20s}: {distance:8.2f} "
                  f"| Improvement: {improvement:6.2f}% "
                  f"| Time: {case_results[method]['wall_time']:7.4f}s")
    
    # Save results to file
    output_file = 'vrp_v2_benchmark_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {output_file}")
    
    return results

def benchmark_file_instances():
    """Benchmark VRP v2 on existing VRP files."""
    print("\n" + "=" * 70)
    print("BENCHMARKING ON EXISTING VRP FILES")
    print("=" * 70)
    
    vrp_files = [
        'vrp_benchmarks/synthetic_10_2.vrp',
        'vrp_benchmarks/synthetic_20_3.vrp',
        'vrp_benchmarks/synthetic_30_4.vrp',
        'vrp_benchmarks/synthetic_40_5.vrp',
        'vrp_benchmarks/synthetic_50_6.vrp',
    ]
    
    file_results = {}
    
    for filepath in vrp_files:
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            continue
        
        print(f"\nFile: {os.path.basename(filepath)}")
        
        # Parse VRP file
        instance_data = parse_vrp_file(filepath)
        
        # Convert to format expected by our solver
        # Note: This requires adapting the solver to accept pre-defined instances
        # For now, we'll just report the parsed data
        print(f"  Customers: {instance_data['dimension'] - 1}")
        print(f"  Capacity: {instance_data['capacity']}")
        print(f"  Optimal value: {instance_data.get('optimal_value', 'Unknown')}")
        
        file_results[os.path.basename(filepath)] = instance_data
    
    return file_results

if __name__ == "__main__":
    print("Starting VRP v2 benchmark...")
    
    # Benchmark on synthetic instances
    synthetic_results = benchmark_synthetic_instances()
    
    # Benchmark on file instances (informational)
    file_results = benchmark_file_instances()
    
    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETED")
    print("=" * 70)

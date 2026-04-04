#!/usr/bin/env python3
import sys
import os
import time
import json
import signal
from datetime import datetime
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tsplib_parser import TSPLIBParser

# Import fixed algorithms
try:
    from tsp_algorithms_fixed import algorithms
    ALGORITHMS_AVAILABLE = True
    print("✓ Imported fixed TSP algorithms")
except ImportError as e:
    print(f"✗ Failed to import fixed algorithms: {e}")
    ALGORITHMS_AVAILABLE = False
    sys.exit(1)

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Algorithm timed out")

def evaluate_instance(instance_name, timeout_map):
    """Evaluate all algorithms on a single instance."""
    print(f"\n📊 Processing {instance_name}...")
    
    # Load TSPLIB instance
    filepath = f"data/tsplib/{instance_name}.tsp"
    if not os.path.exists(filepath):
        print(f"  ❌ File not found: {filepath}")
        return None
    
    parser = TSPLIBParser(filepath)
    if not parser.parse():
        print(f"  ❌ Failed to parse {instance_name}")
        return None
    
    print(f"  ✓ Loaded: {parser.dimension} nodes, optimal={parser.optimal_value}")
    print(f"    Edge weight type: {parser.edge_weight_type}")
    
    results = {}
    points = parser.get_points_array()
    distance_matrix = parser.get_distance_matrix()
    
    for algo_name, solve_func in algorithms.items():
        timeout = timeout_map.get(instance_name, 60)
        print(f"  🧪 Running {algo_name} (timeout: {timeout}s)...", end=" ", flush=True)
        
        start_time = time.time()
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        
        try:
            tour, tour_length = solve_func(points, distance_matrix=distance_matrix)
            signal.alarm(0)  # Disable alarm
            
            runtime = time.time() - start_time
            
            # Calculate gap
            optimal = parser.optimal_value
            if optimal is not None and optimal > 0:
                gap_percent = ((tour_length - optimal) / optimal) * 100
            else:
                gap_percent = None
            
            print(f"gap={gap_percent:.2f}%, time={runtime:.2f}s")
            
            results[algo_name] = {
                "tour_length": float(tour_length),
                "gap_percent": gap_percent,
                "runtime": runtime,
                "success": True,
                "timeout": False
            }
            
        except TimeoutException:
            runtime = time.time() - start_time
            signal.alarm(0)
            print(f"⏰ TIMEOUT after {runtime:.1f}s")
            results[algo_name] = {
                "error": f"Timed out after {timeout} seconds",
                "runtime": runtime,
                "success": False,
                "timeout": True
            }
        except Exception as e:
            runtime = time.time() - start_time
            signal.alarm(0)
            print(f"❌ Failed: {str(e)[:50]}...")
            results[algo_name] = {
                "error": str(e),
                "runtime": runtime,
                "success": False,
                "timeout": False
            }
    
    return {
        "instance": instance_name,
        "dimension": parser.dimension,
        "optimal": parser.optimal_value,
        "edge_weight_type": parser.edge_weight_type,
        "results": results
    }

# Main evaluation
print("=" * 80)
print("TSPLIB EVALUATION - SIMPLIFIED VERSION")
print("=" * 80)

# Timeout configuration (seconds)
timeout_map = {
    "eil51": 30,
    "kroA100": 60,
    "a280": 120,
    "att532": 180
}

instances = ["eil51", "kroA100", "a280", "att532"]
all_results = {}

for instance in instances:
    result = evaluate_instance(instance, timeout_map)
    if result:
        all_results[instance] = result

# Generate summary
print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)

for instance in instances:
    if instance in all_results:
        print(f"\n{instance}:")
        for algo_name in algorithms.keys():
            if algo_name in all_results[instance]["results"]:
                r = all_results[instance]["results"][algo_name]
                if r["success"]:
                    print(f"  {algo_name}: gap={r['gap_percent']:.2f}%, time={r['runtime']:.2f}s")
                elif r["timeout"]:
                    print(f"  {algo_name}: TIMEOUT after {r['runtime']:.1f}s")
                else:
                    print(f"  {algo_name}: FAILED")

# Save results
output_file = "tsplib_evaluation_simple_results.json"
with open(output_file, 'w') as f:
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "instances": instances,
        "algorithms": list(algorithms.keys()),
        "results": all_results
    }, f, indent=2)

print(f"\n✓ Results saved to {output_file}")

#!/usr/bin/env python3
import sys
import os
import time
import json
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

def evaluate_algorithm_on_instance(algorithm_name, solve_func, parser, seed=42):
    """Evaluate a single algorithm on a TSPLIB instance."""
    start_time = time.time()
    
    try:
        # Get points and distance matrix from parser
        points = parser.get_points_array()
        distance_matrix = parser.get_distance_matrix()
        
        # Run algorithm with distance matrix
        tour, tour_length = solve_func(points, distance_matrix=distance_matrix)
        
        runtime = time.time() - start_time
        
        # Calculate gap to optimal
        optimal = parser.optimal_value
        if optimal is not None and optimal > 0:
            gap_percent = ((tour_length - optimal) / optimal) * 100
        else:
            gap_percent = None
        
        return {
            "algorithm": algorithm_name,
            "instance": parser.name,
            "tour": tour.tolist() if isinstance(tour, np.ndarray) else tour,
            "tour_length": float(tour_length),
            "optimal": optimal,
            "gap_percent": gap_percent,
            "runtime": runtime,
            "success": True
        }
        
    except Exception as e:
        runtime = time.time() - start_time
        return {
            "algorithm": algorithm_name,
            "instance": parser.name,
            "error": str(e),
            "runtime": runtime,
            "success": False
        }

# TSPLIB instances to evaluate
TSPLIB_INSTANCES = ["eil51", "kroA100", "a280", "att532"]

print("=" * 80)
print("TSPLIB EVALUATION WITH FIXED DISTANCE METRICS")
print("=" * 80)
print(f"Instances: {', '.join(TSPLIB_INSTANCES)}")
print(f"Algorithms: {', '.join(algorithms.keys())}")
print("=" * 80)

all_results = {}
instance_results = {}

# Process each instance
for instance_name in TSPLIB_INSTANCES:
    print(f"\n📊 Processing {instance_name}...")
    
    # Load TSPLIB instance
    filepath = f"data/tsplib/{instance_name}.tsp"
    if not os.path.exists(filepath):
        print(f"  ❌ File not found: {filepath}")
        continue
    
    parser = TSPLIBParser(filepath)
    if not parser.parse():
        print(f"  ❌ Failed to parse {instance_name}")
        continue
    
    print(f"  ✓ Loaded: {parser.dimension} nodes, optimal={parser.optimal_value}")
    print(f"    Edge weight type: {parser.edge_weight_type}")
    
    instance_results[instance_name] = {}
    
    # Evaluate each algorithm
    for algo_name, solve_func in algorithms.items():
        print(f"  🧪 Running {algo_name}...", end=" ", flush=True)
        
        result = evaluate_algorithm_on_instance(algo_name, solve_func, parser)
        
        if result["success"]:
            gap = result["gap_percent"]
            print(f"gap={gap:.2f}%, time={result['runtime']:.2f}s")
            instance_results[instance_name][algo_name] = result
            all_results[f"{instance_name}_{algo_name}"] = result
        else:
            print(f"❌ Failed: {result['error']}")
            instance_results[instance_name][algo_name] = result

# Generate summary report
print("\n" + "=" * 80)
print("EVALUATION SUMMARY")
print("=" * 80)

# Calculate average gaps
for algo_name in algorithms.keys():
    gaps = []
    for instance_name in TSPLIB_INSTANCES:
        if instance_name in instance_results and algo_name in instance_results[instance_name]:
            result = instance_results[instance_name][algo_name]
            if result["success"] and result["gap_percent"] is not None:
                gaps.append(result["gap_percent"])
    
    if gaps:
        avg_gap = np.mean(gaps)
        print(f"{algo_name}: Average gap = {avg_gap:.2f}% (over {len(gaps)} instances)")
    else:
        print(f"{algo_name}: No successful evaluations")

# Save detailed results
output_file = "tsplib_evaluation_fixed_results.json"
with open(output_file, 'w') as f:
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "instances": TSPLIB_INSTANCES,
        "algorithms": list(algorithms.keys()),
        "results": instance_results,
        "summary": all_results
    }, f, indent=2)

print(f"\n✓ Detailed results saved to {output_file}")

# Also save a simplified summary
summary_file = "tsplib_evaluation_summary.txt"
with open(summary_file, 'w') as f:
    f.write("TSPLIB EVALUATION SUMMARY (Fixed Distance Metrics)\n")
    f.write("=" * 60 + "\n")
    f.write(f"Evaluation time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Instances: {', '.join(TSPLIB_INSTANCES)}\n")
    f.write(f"Algorithms: {', '.join(algorithms.keys())}\n\n")
    
    for instance_name in TSPLIB_INSTANCES:
        f.write(f"{instance_name}:\n")
        if instance_name in instance_results:
            for algo_name in algorithms.keys():
                if algo_name in instance_results[instance_name]:
                    result = instance_results[instance_name][algo_name]
                    if result["success"]:
                        f.write(f"  {algo_name}: length={result['tour_length']:.2f}, ")
                        f.write(f"gap={result['gap_percent']:.2f}%, time={result['runtime']:.2f}s\n")
                    else:
                        f.write(f"  {algo_name}: FAILED - {result['error']}\n")
        f.write("\n")

print(f"✓ Summary saved to {summary_file}")

#!/usr/bin/env python3
"""Run remaining Phase 3 instances."""

import sys
import os
import time
import json
import statistics
from scipy import stats
sys.path.append('.')

# Import v11 algorithm
try:
    from solutions.tsp_v19_optimized_fixed_v11_optimized import ChristofidesHybridStructuralOptimizedV11
    print("✓ Loaded v11 algorithm")
except ImportError as e:
    print(f"ERROR: {e}")
    sys.exit(1)

# Import TSPLIB parser
try:
    from tsplib_parser import TSPLIBParser
    print("✓ Loaded TSPLIB parser")
except ImportError as e:
    print(f"ERROR: {e}")
    sys.exit(1)

# Import OR-Tools
try:
    from ortools.constraint_solver import routing_enums_pb2
    from ortools.constraint_solver import pywrapcp
    print("✓ Loaded OR-Tools")
except ImportError as e:
    print(f"ERROR: {e}")
    sys.exit(1)

# Load Phase 2 results
phase2_file = "v11_tsplib_phase2_comprehensive_results.json"
try:
    with open(phase2_file, 'r') as f:
        phase2_results = json.load(f)
    print(f"✓ Loaded Phase 2 results from {phase2_file}")
except FileNotFoundError:
    print(f"ERROR: Phase 2 results file {phase2_file} not found")
    sys.exit(1)

# Instances to process (remaining)
instances = {
    "lin318": {"file": "data/tsplib/lin318.tsp", "optimal": 42029, "seeds": 2, "timeout_ortools": 120},
    "pr439": {"file": "data/tsplib/pr439.tsp", "optimal": 107217, "seeds": 2, "timeout_ortools": 180},
    "att532": {"file": "data/tsplib/att532.tsp", "optimal": 27686, "seeds": 2, "timeout_ortools": 180},
}

results = {}

print("\n" + "="*80)
print("PHASE 3: REMAINING INSTANCES")
print("="*80)

for instance_name, instance_info in instances.items():
    print(f"\n{'='*60}")
    print(f"Processing instance: {instance_name}")
    print(f"{'='*60}")
    
    instance_file = instance_info["file"]
    optimal = instance_info["optimal"]
    n_seeds = instance_info["seeds"]
    timeout_ortools = instance_info["timeout_ortools"]
    
    print(f"  File: {instance_file}")
    print(f"  Optimal: {optimal}")
    print(f"  Seeds: {n_seeds}")
    print(f"  Timeouts: v11=180s, OR-Tools={timeout_ortools}s")
    
    # Parse instance
    parser = TSPLIBParser(instance_file)
    if not parser.parse():
        print(f'  ERROR: Failed to parse {instance_file}')
        continue
    
    n_nodes = parser.dimension
    print(f"  ✓ Parsed {instance_name}: {n_nodes} nodes, optimal={parser.optimal_value}")
    
    # Get distance matrix
    points = parser.get_coordinates()
    dist_matrix_np = parser.get_distance_matrix()
    
    # Convert to Python list for OR-Tools
    dist_matrix = dist_matrix_np.tolist()
    
    # Initialize results for this instance
    instance_results = {
        "instance": instance_name,
        "n_nodes": n_nodes,
        "optimal": optimal,
        "v11_gaps": [],
        "v11_times": [],
        "ortools_gaps": [],
        "ortools_times": []
    }
    
    # Process each seed
    for seed in range(1, n_seeds + 1):
        print(f"  Seed {seed}/{n_seeds}: ", end="", flush=True)
        
        # Get v11 results from Phase 2
        v11_gap = None
        v11_time = None
        if instance_name in phase2_results and "seeds" in phase2_results[instance_name]:
            seed_key = f"seed_{seed}"
            if seed_key in phase2_results[instance_name]["seeds"]:
                v11_gap = phase2_results[instance_name]["seeds"][seed_key]["gap_percent"]
                v11_time = phase2_results[instance_name]["seeds"][seed_key]["time_seconds"]
        
        if v11_gap is None:
            # Run v11 if not in Phase 2 results
            v11 = ChristofidesHybridStructuralOptimizedV11(dist_matrix_np, seed=seed)
            start = time.time()
            tour = v11.solve()
            v11_time = time.time() - start
            tour_length = sum(dist_matrix_np[tour[i]][tour[i+1]] for i in range(len(tour)-1))
            tour_length += dist_matrix_np[tour[-1]][tour[0]]
            v11_gap = (tour_length - optimal) / optimal * 100
        
        # Run OR-Tools
        manager = pywrapcp.RoutingIndexManager(n_nodes, 1, 0)
        routing = pywrapcp.RoutingModel(manager)
        
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int(dist_matrix[from_node][to_node])
        
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        search_parameters.time_limit.seconds = timeout_ortools
        
        start = time.time()
        solution = routing.SolveWithParameters(search_parameters)
        ortools_time = time.time() - start
        
        if solution:
            ortools_length = solution.ObjectiveValue()
            ortools_gap = (ortools_length - optimal) / optimal * 100
            print(f"v11(gap={v11_gap:.2f}%, time={v11_time:.2f}s) OR-Tools(gap={ortools_gap:.2f}%, time={ortools_time:.2f}s)")
        else:
            ortools_gap = float('inf')
            ortools_time = timeout_ortools
            print(f"v11(gap={v11_gap:.2f}%, time={v11_time:.2f}s) OR-Tools(TIMEOUT)")
        
        # Store results
        instance_results["v11_gaps"].append(v11_gap)
        instance_results["v11_times"].append(v11_time)
        instance_results["ortools_gaps"].append(ortools_gap)
        instance_results["ortools_times"].append(ortools_time)
    
    # Calculate averages
    instance_results["v11_avg_gap"] = statistics.mean(instance_results["v11_gaps"])
    instance_results["v11_avg_time"] = statistics.mean(instance_results["v11_times"])
    instance_results["ortools_avg_gap"] = statistics.mean([g for g in instance_results["ortools_gaps"] if g != float('inf')])
    instance_results["ortools_avg_time"] = statistics.mean(instance_results["ortools_times"])
    
    results[instance_name] = instance_results
    print(f"  ✓ Completed {instance_name}")

print(f"\n✓ Completed all remaining instances")
print(f"  Results: {list(results.keys())}")

# Save results
output_file = "v11_tsplib_phase3_remaining_results.json"
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)
print(f"✓ Results saved to {output_file}")

# Create summary
summary_file = "phase3_remaining_summary.md"
with open(summary_file, 'w') as f:
    f.write("# Phase 3: Remaining Instances Summary\n\n")
    f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    for instance_name in results:
        instance = results[instance_name]
        f.write(f"## {instance_name}\n\n")
        f.write(f"- **Nodes:** {instance['n_nodes']}\n")
        f.write(f"- **Optimal:** {instance['optimal']}\n")
        f.write(f"- **v11 average gap:** {instance['v11_avg_gap']:.2f}%\n")
        f.write(f"- **v11 average time:** {instance['v11_avg_time']:.2f}s\n")
        f.write(f"- **OR-Tools average gap:** {instance['ortools_avg_gap']:.2f}%\n")
        f.write(f"- **OR-Tools average time:** {instance['ortools_avg_time']:.2f}s\n\n")

print(f"✓ Summary saved to {summary_file}")

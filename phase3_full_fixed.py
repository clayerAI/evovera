#!/usr/bin/env python3
"""Full Phase 3 evaluation for all TSPLIB instances."""

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

def solve_with_ortools(distance_matrix, time_limit_seconds=60):
    """Solve TSP with OR-Tools."""
    n = len(distance_matrix)
    manager = pywrapcp.RoutingIndexManager(n, 1, 0)  # 1 vehicle, depot at 0
    
    routing = pywrapcp.RoutingModel(manager)
    
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        # Handle both numpy arrays and Python lists
        val = distance_matrix[from_node][to_node]
        if hasattr(val, 'item'):  # numpy scalar
            return int(val.item())
        return int(val)
    
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    # Set search parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.seconds = time_limit_seconds
    search_parameters.log_search = False
    
    # Solve
    solution = routing.SolveWithParameters(search_parameters)
    
    if solution:
        index = routing.Start(0)
        route = []
        route_distance = 0
        while not routing.IsEnd(index):
            route.append(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
        return route, route_distance
    return None, None

# TSPLIB instances to evaluate
TSPLIB_INSTANCES = {
    "eil51": {"file": "data/tsplib/eil51.tsp", "optimal": 426, "seeds": 2, "timeout_ortools": 30},
    "kroA100": {"file": "data/tsplib/kroA100.tsp", "optimal": 21282, "seeds": 2, "timeout_ortools": 60},
    "d198": {"file": "data/tsplib/d198.tsp", "optimal": 15780, "seeds": 2, "timeout_ortools": 60},
    "a280": {"file": "data/tsplib/a280.tsp", "optimal": 2579, "seeds": 2, "timeout_ortools": 120},
    "lin318": {"file": "data/tsplib/lin318.tsp", "optimal": 42029, "seeds": 2, "timeout_ortools": 120},
    "pr439": {"file": "data/tsplib/pr439.tsp", "optimal": 107217, "seeds": 1, "timeout_ortools": 180},
    "att532": {"file": "data/tsplib/att532.tsp", "optimal": 27686, "seeds": 1, "timeout_ortools": 180},
}

# Timeout for v11 (same as Phase 2)
TIMEOUT_V11 = 180

# Load Phase 2 results
phase2_results = {}
phase2_file = "v11_tsplib_phase2_comprehensive_results.json"
if os.path.exists(phase2_file):
    try:
        with open(phase2_file, 'r') as f:
            phase2_results = json.load(f)
        print(f"✓ Loaded Phase 2 results from {phase2_file}")
    except Exception as e:
        print(f"WARNING: Failed to load Phase 2 results: {e}")
else:
    print("WARNING: Phase 2 results not found, will compute v11 results from scratch")

# Results structure
results = {
    "metadata": {
        "phase": 3,
        "description": "Strong solver comparison: v11 vs OR-Tools TSP solver",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "v11_algorithm": "ChristofidesHybridStructuralOptimizedV11",
        "ortools_version": "9.15.6755",
        "comparison_methodology": "Same TSPLIB instances, reduced seeds for feasibility",
        "timeout_v11": TIMEOUT_V11,
        "note": "Reduced seeds for OR-Tools feasibility (full seeds would take ~24 hours)",
    },
    "instances": {}
}

print("\n" + "="*80)
print("PHASE 3: STRONG SOLVER COMPARISON (FULL EVALUATION)")
print("v11 (Christofides Hybrid Structural Optimized) vs OR-Tools TSP Solver")
print("="*80)

# Process each instance
for instance_name, instance_info in TSPLIB_INSTANCES.items():
    print(f"\n{'='*60}")
    print(f"Processing instance: {instance_name}")
    print('='*60)
    
    instance_file = instance_info["file"]
    optimal = instance_info["optimal"]
    num_seeds = instance_info["seeds"]
    timeout_ortools = instance_info["timeout_ortools"]
    
    print(f"  File: {instance_file}")
    print(f"  Optimal: {optimal}")
    print(f"  Seeds: {num_seeds}")
    print(f"  Timeouts: v11={TIMEOUT_V11}s, OR-Tools={timeout_ortools}s")
    
    # Parse instance
    try:
        parser = TSPLIBParser(instance_file)
        if not parser.parse():
            print(f'  ERROR: Failed to parse {instance_file}')
            continue
        points = parser.get_coordinates()
        dist_matrix_np = parser.get_distance_matrix()
        n_nodes = len(points)
        print(f"  ✓ Parsed {instance_name}: {n_nodes} nodes, optimal={parser.optimal_value}")
    except Exception as e:
        print(f"  ERROR: Exception parsing {instance_file}: {e}")
        continue
    
    # Convert numpy array to Python list
    if hasattr(dist_matrix_np, 'tolist'):
        dist_matrix = dist_matrix_np.tolist()
    else:
        dist_matrix = dist_matrix_np
    
    # Check if we have Phase 2 results for this instance
    use_phase2_results = False
    v11_gaps_from_phase2 = []
    v11_runtimes_from_phase2 = []
    
    if instance_name in phase2_results:
        phase2_data = phase2_results[instance_name]
        if "gaps" in phase2_data and "runtimes" in phase2_data:
            # Take first num_seeds results from Phase 2
            v11_gaps_from_phase2 = phase2_data["gaps"][:num_seeds]
            v11_runtimes_from_phase2 = phase2_data["runtimes"][:num_seeds]
            if len(v11_gaps_from_phase2) >= num_seeds:
                use_phase2_results = True
                print(f"  ✓ Using v11 results from Phase 2 ({len(v11_gaps_from_phase2)} seeds)")
    
    # Initialize results for this instance
    instance_results = {
        "instance": instance_name,
        "n_nodes": n_nodes,
        "optimal": optimal,
        "num_seeds": num_seeds,
        "timeout_v11": TIMEOUT_V11,
        "timeout_ortools": timeout_ortools,
        "v11": {"gaps": [], "runtimes": [], "success_rate": 0},
        "ortools": {"gaps": [], "runtimes": [], "success_rate": 0},
        "comparison": {}
    }
    
    v11_gaps = []
    v11_runtimes = []
    ortools_gaps = []
    ortools_runtimes = []
    
    # Process each seed
    for seed in range(1, num_seeds + 1):
        print(f"  Seed {seed}/{num_seeds}: ", end="", flush=True)
        
        # Get v11 result
        v11_gap = None
        v11_runtime = None
        
        if use_phase2_results and seed <= len(v11_gaps_from_phase2):
            # Use Phase 2 result
            v11_gap = v11_gaps_from_phase2[seed-1]
            v11_runtime = v11_runtimes_from_phase2[seed-1]
            print(f"v11(gap={v11_gap:.2f}%, time={v11_runtime:.2f}s) ", end="", flush=True)
        else:
            # Compute v11 result
            start_time = time.time()
            try:
                solver = ChristofidesHybridStructuralOptimizedV11(dist_matrix, seed=seed)
                tour, tour_length = solver.solve()
                v11_runtime = time.time() - start_time
                
                if v11_runtime > TIMEOUT_V11:
                    print(f"v11(TIMEOUT) ", end="", flush=True)
                else:
                    v11_gap = ((tour_length - optimal) / optimal) * 100
                    print(f"v11(gap={v11_gap:.2f}%, time={v11_runtime:.2f}s) ", end="", flush=True)
            except Exception as e:
                print(f"v11(ERROR: {e}) ", end="", flush=True)
                v11_runtime = TIMEOUT_V11 + 1  # Mark as timeout
        
        # Get OR-Tools result
        ortools_gap = None
        ortools_runtime = None
        
        start_time = time.time()
        try:
            ortools_route, ortools_cost = solve_with_ortools(dist_matrix, time_limit_seconds=timeout_ortools)
            ortools_runtime = time.time() - start_time
            
            if ortools_cost:
                ortools_gap = ((ortools_cost - optimal) / optimal) * 100
                print(f"OR-Tools(gap={ortools_gap:.2f}%, time={ortools_runtime:.2f}s)", flush=True)
            else:
                print(f"OR-Tools(FAILED, time={ortools_runtime:.2f}s)", flush=True)
        except Exception as e:
            print(f"OR-Tools(ERROR: {e})", flush=True)
            ortools_runtime = timeout_ortools + 1  # Mark as timeout
        
        # Store results
        if v11_gap is not None and v11_runtime <= TIMEOUT_V11:
            v11_gaps.append(v11_gap)
            v11_runtimes.append(v11_runtime)
        
        if ortools_gap is not None and ortools_runtime <= timeout_ortools + 0.1:  # Small tolerance for timing precision
            ortools_gaps.append(ortools_gap)
            ortools_runtimes.append(ortools_runtime)
    
    # Compute statistics
    if v11_gaps:
        instance_results["v11"]["avg_gap"] = statistics.mean(v11_gaps)
        instance_results["v11"]["gap_std"] = statistics.stdev(v11_gaps) if len(v11_gaps) > 1 else 0
        instance_results["v11"]["avg_runtime"] = statistics.mean(v11_runtimes)
        instance_results["v11"]["runtime_std"] = statistics.stdev(v11_runtimes) if len(v11_runtimes) > 1 else 0
        instance_results["v11"]["success_rate"] = (len(v11_gaps) / num_seeds) * 100
        instance_results["v11"]["gaps"] = v11_gaps
        instance_results["v11"]["runtimes"] = v11_runtimes
    
    if ortools_gaps:
        instance_results["ortools"]["avg_gap"] = statistics.mean(ortools_gaps)
        instance_results["ortools"]["gap_std"] = statistics.stdev(ortools_gaps) if len(ortools_gaps) > 1 else 0
        instance_results["ortools"]["avg_runtime"] = statistics.mean(ortools_runtimes)
        instance_results["ortools"]["runtime_std"] = statistics.stdev(ortools_runtimes) if len(ortools_runtimes) > 1 else 0
        instance_results["ortools"]["success_rate"] = (len(ortools_gaps) / num_seeds) * 100
        instance_results["ortools"]["gaps"] = ortools_gaps
        instance_results["ortools"]["runtimes"] = ortools_runtimes
    
    # Compare v11 vs OR-Tools
    if v11_gaps and ortools_gaps:
        # Statistical test (paired t-test)
        try:
            t_stat, p_value = stats.ttest_rel(v11_gaps, ortools_gaps)
            instance_results["comparison"]["t_test_statistic"] = t_stat
            instance_results["comparison"]["p_value"] = p_value
            instance_results["comparison"]["significant"] = p_value < 0.05
            
            # Gap difference
            gap_diff = statistics.mean(v11_gaps) - statistics.mean(ortools_gaps)
            instance_results["comparison"]["gap_difference"] = gap_diff
            instance_results["comparison"]["gap_difference_pct"] = (gap_diff / statistics.mean(ortools_gaps)) * 100
            
            # Runtime ratio
            runtime_ratio = statistics.mean(v11_runtimes) / statistics.mean(ortools_runtimes) if statistics.mean(ortools_runtimes) > 0 else float('inf')
            instance_results["comparison"]["runtime_ratio"] = runtime_ratio
            
            print(f"\n  COMPARISON:")
            print(f"    v11: {instance_results['v11']['avg_gap']:.2f}% ± {instance_results['v11']['gap_std']:.2f}%, {instance_results['v11']['avg_runtime']:.2f}s")
            print(f"    OR-Tools: {instance_results['ortools']['avg_gap']:.2f}% ± {instance_results['ortools']['gap_std']:.2f}%, {instance_results['ortools']['avg_runtime']:.2f}s")
            print(f"    Gap difference: {gap_diff:.2f}% (v11 - OR-Tools)")
            print(f"    Statistical significance: p = {p_value:.4f} {'(significant)' if p_value < 0.05 else '(not significant)'}")
            print(f"    Runtime ratio: {runtime_ratio:.2f}x (v11/OR-Tools)")
        except Exception as e:
            print(f"\n  ERROR in statistical comparison: {e}")
    
    # Store instance results
    results["instances"][instance_name] = instance_results
    
    print(f"\n  ✓ Completed {instance_name}")

# Overall statistics
print(f"\n{'='*80}")
print("OVERALL RESULTS")
print('='*80)

all_v11_gaps = []
all_ortools_gaps = []
all_v11_runtimes = []
all_ortools_runtimes = []

for instance_name, instance_data in results["instances"].items():
    if "v11" in instance_data and "gaps" in instance_data["v11"]:
        all_v11_gaps.extend(instance_data["v11"]["gaps"])
        all_v11_runtimes.extend(instance_data["v11"]["runtimes"])
    if "ortools" in instance_data and "gaps" in instance_data["ortools"]:
        all_ortools_gaps.extend(instance_data["ortools"]["gaps"])
        all_ortools_runtimes.extend(instance_data["ortools"]["runtimes"])

if all_v11_gaps and all_ortools_gaps:
    overall_v11_avg_gap = statistics.mean(all_v11_gaps)
    overall_ortools_avg_gap = statistics.mean(all_ortools_gaps)
    overall_v11_avg_runtime = statistics.mean(all_v11_runtimes)
    overall_ortools_avg_runtime = statistics.mean(all_ortools_runtimes)
    
    # Overall statistical test
    try:
        t_stat, p_value = stats.ttest_rel(all_v11_gaps, all_ortools_gaps)
        overall_gap_diff = overall_v11_avg_gap - overall_ortools_avg_gap
        overall_runtime_ratio = overall_v11_avg_runtime / overall_ortools_avg_runtime if overall_ortools_avg_runtime > 0 else float('inf')
        
        print(f"v11 overall: {overall_v11_avg_gap:.2f}% gap, {overall_v11_avg_runtime:.2f}s")
        print(f"OR-Tools overall: {overall_ortools_avg_gap:.2f}% gap, {overall_ortools_avg_runtime:.2f}s")
        print(f"Overall gap difference: {overall_gap_diff:.2f}% (v11 - OR-Tools)")
        print(f"Overall statistical significance: p = {p_value:.6f} {'(significant)' if p_value < 0.05 else '(not significant)'}")
        print(f"Overall runtime ratio: {overall_runtime_ratio:.2f}x (v11/OR-Tools)")
        
        # Store overall results
        results["overall"] = {
            "v11_avg_gap": overall_v11_avg_gap,
            "ortools_avg_gap": overall_ortools_avg_gap,
            "v11_avg_runtime": overall_v11_avg_runtime,
            "ortools_avg_runtime": overall_ortools_avg_runtime,
            "gap_difference": overall_gap_diff,
            "gap_difference_pct": (overall_gap_diff / overall_ortools_avg_gap) * 100,
            "runtime_ratio": overall_runtime_ratio,
            "t_test_statistic": t_stat,
            "p_value": p_value,
            "significant": p_value < 0.05,
            "total_seeds": len(all_v11_gaps)
        }
    except Exception as e:
        print(f"ERROR in overall statistical analysis: {e}")

# Save results
output_file = "v11_tsplib_phase3_strong_solver_results.json"
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n✓ Results saved to {output_file}")

# Generate summary report
summary_file = "v11_tsplib_phase3_strong_solver_summary.md"
with open(summary_file, 'w') as f:
    f.write("# Phase 3: Strong Solver Comparison Report\n\n")
    f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    f.write("## Overview\n\n")
    f.write("Comparison of v11 (Christofides Hybrid Structural Optimized) vs OR-Tools TSP solver.\n\n")
    f.write("## Methodology\n\n")
    f.write("- **Instances:** 7 TSPLIB instances (eil51, kroA100, d198, a280, lin318, pr439, att532)\n")
    f.write("- **Seeds:** Reduced seeds for OR-Tools feasibility (full seeds would take ~24 hours)\n")
    f.write("- **Timeouts:** v11=180s, OR-Tools=30-180s depending on instance size\n")
    f.write("- **Statistical test:** Paired t-test (α=0.05)\n\n")
    
    f.write("## Results Summary\n\n")
    if "overall" in results:
        overall = results["overall"]
        f.write(f"- **v11 average gap:** {overall['v11_avg_gap']:.2f}%\n")
        f.write(f"- **OR-Tools average gap:** {overall['ortools_avg_gap']:.2f}%\n")
        f.write(f"- **Gap difference:** {overall['gap_difference']:.2f}% (v11 - OR-Tools)\n")
        f.write(f"- **Statistical significance:** p = {overall['p_value']:.6f} {'(significant)' if overall['significant'] else '(not significant)'}\n")
        f.write(f"- **Runtime ratio:** {overall['runtime_ratio']:.2f}x (v11/OR-Tools)\n")
        f.write(f"- **Total seeds:** {overall['total_seeds']}\n\n")
    
    f.write("## Instance-by-Instance Results\n\n")
    f.write("| Instance | Nodes | v11 Gap (%) | OR-Tools Gap (%) | Gap Diff | p-value | Significant | v11 Time (s) | OR-Tools Time (s) |\n")
    f.write("|----------|-------|-------------|------------------|----------|---------|-------------|--------------|-------------------|\n")
    
    for instance_name, instance_data in results["instances"].items():
        if "v11" in instance_data and "ortools" in instance_data:
            v11_gap = instance_data["v11"].get("avg_gap", "N/A")
            ortools_gap = instance_data["ortools"].get("avg_gap", "N/A")
            v11_time = instance_data["v11"].get("avg_runtime", "N/A")
            ortools_time = instance_data["ortools"].get("avg_runtime", "N/A")
            
            if isinstance(v11_gap, float) and isinstance(ortools_gap, float):
                gap_diff = v11_gap - ortools_gap
                p_val = instance_data.get("comparison", {}).get("p_value", "N/A")
                sig = instance_data.get("comparison", {}).get("significant", "N/A")
                
                f.write(f"| {instance_name} | {instance_data['n_nodes']} | ")
                f.write(f"{v11_gap:.2f} | {ortools_gap:.2f} | ")
                f.write(f"{gap_diff:.2f} | ")
                if isinstance(p_val, float):
                    f.write(f"{p_val:.4f} | {'✓' if sig else '✗'} | ")
                else:
                    f.write(f"{p_val} | {sig} | ")
                if isinstance(v11_time, float):
                    f.write(f"{v11_time:.2f} | ")
                else:
                    f.write(f"{v11_time} | ")
                if isinstance(ortools_time, float):
                    f.write(f"{ortools_time:.2f} |\n")
                else:
                    f.write(f"{ortools_time} |\n")
            else:
                f.write(f"| {instance_name} | {instance_data['n_nodes']} | {v11_gap} | {ortools_gap} | N/A | N/A | N/A | {v11_time} | {ortools_time} |\n")
    
    f.write("\n## Conclusions\n\n")
    if "overall" in results:
        overall = results["overall"]
        if overall.get("significant", False):
            if overall["gap_difference"] > 0:
                f.write("1. **OR-Tools significantly outperforms v11** with a smaller average gap.\n")
            else:
                f.write("1. **v11 significantly outperforms OR-Tools** with a smaller average gap.\n")
        else:
            f.write("1. **No statistically significant difference** between v11 and OR-Tools performance.\n")
        
        f.write(f"2. **Runtime performance:** v11 is {overall['runtime_ratio']:.2f}x {'faster' if overall['runtime_ratio'] < 1 else 'slower'} than OR-Tools.\n")
        f.write(f"3. **Quality gap:** v11 has {overall['gap_difference']:.2f}% higher gap than OR-Tools.\n")
    
    f.write("\n## Files\n\n")
    f.write(f"- **Raw results:** `{output_file}`\n")
    f.write(f"- **This report:** `{summary_file}`\n")
    f.write(f"- **Phase 2 results:** `{phase2_file}`\n")

print(f"✓ Summary report saved to {summary_file}")
print("\n" + "="*80)
print("PHASE 3 COMPLETED SUCCESSFULLY")
print("="*80)

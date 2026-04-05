#!/usr/bin/env python3
"""Execute Phase 3: Strong solver comparison (v11 vs OR-Tools)."""

import sys
import os
import json
import time
import math
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
import statistics

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the optimized v11 algorithm from solutions directory
try:
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "solutions"))
    from tsp_v19_optimized_fixed_v11_optimized import ChristofidesHybridStructuralOptimizedV11
    print("✓ Loaded optimized v11 algorithm from solutions directory")
except ImportError as e:
    print(f"ERROR: Could not import optimized v11 algorithm: {e}")
    sys.exit(1)

# Import TSPLIB parser
try:
    from tsplib_parser import TSPLIBParser
    print("✓ Loaded TSPLIB parser")
except ImportError as e:
    print(f"ERROR: Could not import TSPLIB parser: {e}")
    sys.exit(1)

# Import OR-Tools
try:
    from ortools.constraint_solver import pywrapcp, routing_enums_pb2
    print("✓ Loaded OR-Tools")
except ImportError as e:
    print(f"ERROR: Could not import OR-Tools: {e}")
    print("Please install OR-Tools: pip install ortools")
    sys.exit(1)

# TSPLIB instances with optimal values (from tsplib_parser.py)
# Same instances as Phase 2 for consistent comparison
TSPLIB_INSTANCES = {
    "eil51": {"file": "data/tsplib/eil51.tsp", "optimal": 426, "seeds": 10},      # ≤200 nodes: 10 seeds
    "kroA100": {"file": "data/tsplib/kroA100.tsp", "optimal": 21282, "seeds": 10}, # ≤200 nodes: 10 seeds
    "d198": {"file": "data/tsplib/d198.tsp", "optimal": 15780, "seeds": 10},       # ≤200 nodes: 10 seeds
    "a280": {"file": "data/tsplib/a280.tsp", "optimal": 2579, "seeds": 5},         # >200 nodes: 5 seeds
    "lin318": {"file": "data/tsplib/lin318.tsp", "optimal": 42029, "seeds": 5},    # >200 nodes: 5 seeds
    "pr439": {"file": "data/tsplib/pr439.tsp", "optimal": 107217, "seeds": 5},     # >200 nodes: 5 seeds
    "att532": {"file": "data/tsplib/att532.tsp", "optimal": 27686, "seeds": 5},    # >200 nodes: 5 seeds
}

# Timeout settings for OR-Tools (more generous for fair comparison)
ORTOOLS_TIMEOUTS = {
    "att532": 300,  # 5 minutes for largest instance
    "default": 120  # 2 minutes for other instances
}

# Timeout for v11 algorithm (same as Phase 2)
V11_TIMEOUTS = {
    "att532": 300,
    "default": 180
}

def validate_tour(tour: List[int], n: int) -> Tuple[bool, str]:
    """Validate TSP tour is Hamiltonian cycle."""
    if len(tour) != n + 1:
        return False, f"Tour length {len(tour)} != n+1 ({n+1})"
    if tour[0] != tour[-1]:
        return False, f"Tour not cyclic: start={tour[0]}, end={tour[-1]}"
    
    visited = set()
    for i in range(n):
        node = tour[i]
        if node < 0 or node >= n:
            return False, f"Invalid node index {node} at position {i}"
        if node in visited:
            return False, f"Duplicate node {node} at position {i}"
        visited.add(node)
    
    if len(visited) != n:
        return False, f"Only visited {len(visited)}/{n} unique nodes"
    
    return True, "Valid tour"

def compute_tour_length(tour: List[int], dist_matrix: List[List[float]]) -> float:
    """Compute total length of TSP tour."""
    total = 0.0
    for i in range(len(tour) - 1):
        total += dist_matrix[tour[i]][tour[i+1]]
    return total

def solve_tsp_ortools(dist_matrix: List[List[float]], time_limit_seconds: int = 120) -> Tuple[Optional[List[int]], Optional[float], float]:
    """Solve TSP using OR-Tools.
    
    Returns: (tour, tour_length, runtime) or (None, None, runtime) if failed.
    """
    start_time = time.time()
    n = len(dist_matrix)
    
    # Create routing index manager
    manager = pywrapcp.RoutingIndexManager(n, 1, 0)  # 1 vehicle, depot at 0
    
    # Create routing model
    routing = pywrapcp.RoutingModel(manager)
    
    def distance_callback(from_index, to_index):
        """Return distance between two nodes."""
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(dist_matrix[from_node][to_node] + 0.5)  # OR-Tools expects integers
    
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    # Set search parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(time_limit_seconds)
    
    # Solve
    solution = routing.SolveWithParameters(search_parameters)
    runtime = time.time() - start_time
    
    if solution:
        # Extract tour
        index = routing.Start(0)
        tour_indices = []
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            tour_indices.append(node)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
        
        # Add depot at end to complete cycle
        tour_indices.append(manager.IndexToNode(index))
        
        # Compute actual tour length (not rounded)
        tour_length = compute_tour_length(tour_indices, dist_matrix)
        return tour_indices, tour_length, runtime
    else:
        return None, None, runtime

def evaluate_v11_algorithm(instance_name: str, dist_matrix: List[List[float]], 
                          optimal: float, seed: int, timeout: int) -> Dict[str, Any]:
    """Evaluate v11 algorithm on a single instance with given seed."""
    start_time = time.time()
    
    # Set random seed for reproducibility
    random_seed = seed * 1000 + hash(instance_name) % 1000
    np.random.seed(random_seed)
    random.seed(random_seed)
    
    try:
        # Initialize algorithm
        solver = ChristofidesHybridStructuralOptimizedV11()
        
        # Solve with timeout
        import signal
        class TimeoutException(Exception):
            pass
        
        def timeout_handler(signum, frame):
            raise TimeoutException(f"Timeout after {timeout} seconds")
        
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        
        try:
            tour = solver.solve(dist_matrix)
            signal.alarm(0)  # Cancel alarm
        except TimeoutException:
            runtime = time.time() - start_time
            return {
                "success": False,
                "error": f"Timeout after {timeout}s",
                "runtime": min(runtime, timeout),
                "tour_length": None,
                "gap_pct": None,
                "tour": None
            }
        except Exception as e:
            runtime = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "runtime": runtime,
                "tour_length": None,
                "gap_pct": None,
                "tour": None
            }
        
        runtime = time.time() - start_time
        
        # Validate tour
        is_valid, error_msg = validate_tour(tour, len(dist_matrix))
        if not is_valid:
            return {
                "success": False,
                "error": f"Invalid tour: {error_msg}",
                "runtime": runtime,
                "tour_length": None,
                "gap_pct": None,
                "tour": None
            }
        
        # Compute tour length and gap
        tour_length = compute_tour_length(tour, dist_matrix)
        gap_pct = ((tour_length - optimal) / optimal) * 100 if optimal > 0 else None
        
        return {
            "success": True,
            "error": None,
            "runtime": runtime,
            "tour_length": tour_length,
            "gap_pct": gap_pct,
            "tour": tour
        }
        
    except Exception as e:
        runtime = time.time() - start_time
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "runtime": runtime,
            "tour_length": None,
            "gap_pct": None,
            "tour": None
        }

def evaluate_ortools(instance_name: str, dist_matrix: List[List[float]], 
                    optimal: float, seed: int, timeout: int) -> Dict[str, Any]:
    """Evaluate OR-Tools on a single instance with given seed."""
    # Note: OR-Tools doesn't use random seed directly, but we set it for consistency
    np.random.seed(seed)
    
    # Solve with OR-Tools
    tour, tour_length, runtime = solve_tsp_ortools(dist_matrix, timeout)
    
    if tour is None:
        return {
            "success": False,
            "error": "OR-Tools failed to find solution",
            "runtime": runtime,
            "tour_length": None,
            "gap_pct": None,
            "tour": None
        }
    
    # Validate tour
    is_valid, error_msg = validate_tour(tour, len(dist_matrix))
    if not is_valid:
        return {
            "success": False,
            "error": f"Invalid tour from OR-Tools: {error_msg}",
            "runtime": runtime,
            "tour_length": None,
            "gap_pct": None,
            "tour": None
        }
    
    # Compute gap
    gap_pct = ((tour_length - optimal) / optimal) * 100 if optimal > 0 else None
    
    return {
        "success": True,
        "error": None,
        "runtime": runtime,
        "tour_length": tour_length,
        "gap_pct": gap_pct,
        "tour": tour
    }

def load_phase2_results():
    """Load Phase 2 results for comparison."""
    try:
        with open("v11_tsplib_phase2_comprehensive_results.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("WARNING: Phase 2 results not found, will compute v11 results from scratch")
        return None

def main():
    """Main execution function."""
    print("=" * 80)
    print("PHASE 3: STRONG SOLVER COMPARISON")
    print("v11 (Christofides Hybrid Structural Optimized) vs OR-Tools TSP Solver")
    print("=" * 80)
    
    # Create results directory
    os.makedirs("phase3_results", exist_ok=True)
    
    # Load Phase 2 results if available
    phase2_results = load_phase2_results()
    
    # Initialize results structure
    results = {
        "metadata": {
            "phase": 3,
            "description": "Strong solver comparison: v11 vs OR-Tools",
            "timestamp": datetime.now().isoformat(),
            "instances": list(TSPLIB_INSTANCES.keys()),
            "comparison_methodology": "Same TSPLIB instances, same seed protocol as Phase 2",
            "ortools_version": "9.15.6755",
            "ortools_settings": {
                "first_solution_strategy": "PATH_CHEAPEST_ARC",
                "local_search_metaheuristic": "GUIDED_LOCAL_SEARCH",
                "time_limit": "instance-specific (120s default, 300s for att532)"
            }
        },
        "instances": {}
    }
    
    # Initialize parser
    
    # Process each instance
    for instance_name, instance_info in TSPLIB_INSTANCES.items():
        print(f"\n{'='*60}")
        print(f"Processing instance: {instance_name}")
        print(f"{'='*60}")
        
        # Load instance
        instance_file = instance_info["file"]
        optimal = instance_info["optimal"]
        num_seeds = instance_info["seeds"]
        
        print(f"  File: {instance_file}")
        print(f"  Optimal: {optimal}")
        print(f"  Seeds: {num_seeds}")
        
        # Parse instance
        try:
            parser = TSPLIBParser(instance_file)
            if not parser.parse():
                print(f'  ERROR: Failed to parse {instance_file}')
                continue
            points = parser.get_coordinates()
            dist_matrix = parser.get_distance_matrix()
            n_nodes = len(points)
            print(f"  Nodes: {n_nodes}")
        except Exception as e:
            print(f"  ERROR: Failed to parse {instance_file}: {e}")
            continue
        
        # Get timeouts
        v11_timeout = V11_TIMEOUTS.get(instance_name, V11_TIMEOUTS["default"])
        ortools_timeout = ORTOOLS_TIMEOUTS.get(instance_name, ORTOOLS_TIMEOUTS["default"])
        
        print(f"  Timeouts: v11={v11_timeout}s, OR-Tools={ortools_timeout}s")
        
        # Initialize instance results
        instance_results = {
            "instance": instance_name,
            "n_nodes": n_nodes,
            "optimal": optimal,
            "num_seeds": num_seeds,
            "v11_timeout": v11_timeout,
            "ortools_timeout": ortools_timeout,
            "v11_results": [],
            "ortools_results": [],
            "comparison": {}
        }
        
        # Check if we have Phase 2 results for this instance
        v11_from_phase2 = None
        if phase2_results and instance_name in phase2_results:
            v11_from_phase2 = phase2_results[instance_name]
            print(f"  ✓ Using v11 results from Phase 2")
        
        # Evaluate for each seed
        v11_gaps = []
        v11_runtimes = []
        ortools_gaps = []
        ortools_runtimes = []
        
        for seed in range(num_seeds):
            print(f"  Seed {seed+1}/{num_seeds}: ", end="", flush=True)
            
            # Get or compute v11 results
            if v11_from_phase2 and seed < len(v11_from_phase2.get("gaps", [])):
                # Use Phase 2 result
                v11_gap = v11_from_phase2["gaps"][seed]
                v11_runtime = v11_from_phase2["runtimes"][seed]
                v11_success = True
                v11_result = {
                    "success": True,
                    "gap_pct": v11_gap,
                    "runtime": v11_runtime
                }
                print(f"v11(gap={v11_gap:.2f}%, time={v11_runtime:.2f}s) ", end="", flush=True)
            else:
                # Compute v11 result
                v11_result = evaluate_v11_algorithm(instance_name, dist_matrix, optimal, seed, v11_timeout)
                if v11_result["success"]:
                    v11_gap = v11_result["gap_pct"]
                    v11_runtime = v11_result["runtime"]
                    print(f"v11(gap={v11_gap:.2f}%, time={v11_runtime:.2f}s) ", end="", flush=True)
                else:
                    print(f"v11(FAILED: {v11_result['error']}) ", end="", flush=True)
                    v11_gap = None
                    v11_runtime = v11_result["runtime"]
            
            # Evaluate OR-Tools
            ortools_result = evaluate_ortools(instance_name, dist_matrix, optimal, seed, ortools_timeout)
            if ortools_result["success"]:
                ortools_gap = ortools_result["gap_pct"]
                ortools_runtime = ortools_result["runtime"]
                print(f"OR-Tools(gap={ortools_gap:.2f}%, time={ortools_runtime:.2f}s)")
            else:
                print(f"OR-Tools(FAILED: {ortools_result['error']})")
                ortools_gap = None
                ortools_runtime = ortools_result["runtime"]
            
            # Store results
            instance_results["v11_results"].append(v11_result)
            instance_results["ortools_results"].append(ortools_result)
            
            # Collect statistics (only for successful runs)
            if v11_result["success"] and v11_gap is not None:
                v11_gaps.append(v11_gap)
                v11_runtimes.append(v11_runtime)
            
            if ortools_result["success"] and ortools_gap is not None:
                ortools_gaps.append(ortools_gap)
                ortools_runtimes.append(ortools_runtime)
        
        # Compute comparison statistics
        if v11_gaps and ortools_gaps:
            # Average gaps
            v11_avg_gap = statistics.mean(v11_gaps)
            ortools_avg_gap = statistics.mean(ortools_gaps)
            
            # Average runtimes
            v11_avg_runtime = statistics.mean(v11_runtimes)
            ortools_avg_runtime = statistics.mean(ortools_runtimes)
            
            # Success rates
            v11_success_rate = (len(v11_gaps) / num_seeds) * 100
            ortools_success_rate = (len(ortools_gaps) / num_seeds) * 100
            
            # Statistical test (paired t-test if same number of successful runs)
            if len(v11_gaps) == len(ortools_gaps) and len(v11_gaps) > 1:
                try:
                    from scipy import stats
                    t_stat, p_value = stats.ttest_rel(v11_gaps, ortools_gaps)
                    significant = p_value < 0.05
                except (ImportError, ValueError):
                    t_stat, p_value, significant = None, None, None
            else:
                t_stat, p_value, significant = None, None, None
            
            instance_results["comparison"] = {
                "v11_avg_gap": v11_avg_gap,
                "ortools_avg_gap": ortools_avg_gap,
                "v11_avg_runtime": v11_avg_runtime,
                "ortools_avg_runtime": ortools_avg_runtime,
                "v11_success_rate": v11_success_rate,
                "ortools_success_rate": ortools_success_rate,
                "gap_difference": v11_avg_gap - ortools_avg_gap,
                "runtime_difference": v11_avg_runtime - ortools_avg_runtime,
                "t_statistic": t_stat,
                "p_value": p_value,
                "statistically_significant": significant,
                "v11_gaps": v11_gaps,
                "ortools_gaps": ortools_gaps,
                "v11_runtimes": v11_runtimes,
                "ortools_runtimes": ortools_runtimes
            }
            
            print(f"  Summary: v11 avg gap={v11_avg_gap:.2f}%, OR-Tools avg gap={ortools_avg_gap:.2f}%")
            print(f"           Difference: {v11_avg_gap - ortools_avg_gap:.2f}%")
            if p_value is not None:
                print(f"           Statistical significance: p={p_value:.4f} ({'significant' if significant else 'not significant'})")
        
        else:
            print(f"  WARNING: Insufficient successful runs for comparison")
            if not v11_gaps:
                print(f"           v11 had {len(v11_gaps)}/{num_seeds} successful runs")
            if not ortools_gaps:
                print(f"           OR-Tools had {len(ortools_gaps)}/{num_seeds} successful runs")
        
        # Store instance results
        results["instances"][instance_name] = instance_results
        
        # Save intermediate results
        with open(f"phase3_results/{instance_name}_results.json", "w") as f:
            json.dump(instance_results, f, indent=2)
    
    # Save final results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"v11_vs_ortools_phase3_results_{timestamp}.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*80}")
    print("PHASE 3 COMPLETED")
    print(f"{'='*80}")
    print(f"Results saved to: {results_file}")
    
    # Generate summary report
    generate_summary_report(results, results_file)
    
    return results

def generate_summary_report(results: Dict, results_file: str):
    """Generate a human-readable summary report."""
    report_file = results_file.replace(".json", "_report.md")
    
    with open(report_file, "w") as f:
        f.write("# Phase 3: Strong Solver Comparison Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Results file:** `{results_file}`\n\n")
        
        f.write("## Overview\n\n")
        f.write("Comparison of v11 (Christofides Hybrid Structural Optimized) ")
        f.write("against OR-Tools TSP solver on 7 TSPLIB instances.\n\n")
        
        f.write("## Methodology\n\n")
        f.write("- **Instances:** 7 TSPLIB instances (same as Phase 2)\n")
        f.write("- **Seeds:** 10 seeds for instances ≤200 nodes, 5 seeds for larger instances\n")
        f.write("- **Metrics:** Gap-to-optimal (%), runtime (seconds), success rate\n")
        f.write("- **Statistical test:** Paired t-test (α=0.05)\n")
        f.write("- **OR-Tools settings:** PATH_CHEAPEST_ARC + GUIDED_LOCAL_SEARCH\n")
        f.write("- **Time limits:** 120s default, 300s for att532\n\n")
        
        f.write("## Results Summary\n\n")
        f.write("| Instance | Nodes | v11 Avg Gap (%) | OR-Tools Avg Gap (%) | Difference | v11 Time (s) | OR-Tools Time (s) | Success Rate |\n")
        f.write("|----------|-------|-----------------|----------------------|------------|--------------|-------------------|--------------|\n")
        
        total_v11_gap = 0
        total_ortools_gap = 0
        count = 0
        
        for instance_name, instance_data in results["instances"].items():
            if "comparison" in instance_data and instance_data["comparison"]:
                comp = instance_data["comparison"]
                v11_gap = comp.get("v11_avg_gap", "N/A")
                ortools_gap = comp.get("ortools_avg_gap", "N/A")
                v11_time = comp.get("v11_avg_runtime", "N/A")
                ortools_time = comp.get("ortools_avg_runtime", "N/A")
                v11_success = comp.get("v11_success_rate", "N/A")
                ortools_success = comp.get("ortools_success_rate", "N/A")
                
                if isinstance(v11_gap, (int, float)) and isinstance(ortools_gap, (int, float)):
                    diff = v11_gap - ortools_gap
                    diff_str = f"{diff:+.2f}%"
                    total_v11_gap += v11_gap
                    total_ortools_gap += ortools_gap
                    count += 1
                else:
                    diff_str = "N/A"
                
                f.write(f"| {instance_name} | {instance_data['n_nodes']} | ")
                f.write(f"{v11_gap:.2f}% | {ortools_gap:.2f}% | {diff_str} | ")
                f.write(f"{v11_time:.2f}s | {ortools_time:.2f}s | ")
                f.write(f"v11: {v11_success:.1f}%, OR-Tools: {ortools_success:.1f}% |\n")
            else:
                f.write(f"| {instance_name} | {instance_data['n_nodes']} | ")
                f.write(f"Incomplete | Incomplete | N/A | N/A | N/A | N/A |\n")
        
        if count > 0:
            avg_v11_gap = total_v11_gap / count
            avg_ortools_gap = total_ortools_gap / count
            avg_diff = avg_v11_gap - avg_ortools_gap
            
            f.write(f"| **Average** | **-** | **{avg_v11_gap:.2f}%** | ")
            f.write(f"**{avg_ortools_gap:.2f}%** | **{avg_diff:+.2f}%** | ")
            f.write(f"**-** | **-** | **-** |\n\n")
        
        f.write("## Key Findings\n\n")
        
        # Analyze results
        if count > 0:
            if avg_diff > 1.0:
                f.write(f"1. **OR-Tools outperforms v11** by {avg_diff:.2f}% on average.\n")
            elif avg_diff < -1.0:
                f.write(f"1. **v11 outperforms OR-Tools** by {-avg_diff:.2f}% on average.\n")
            else:
                f.write(f"1. **Performance is comparable** (difference: {avg_diff:.2f}%).\n")
            
            f.write(f"2. **Average performance:** v11: {avg_v11_gap:.2f}% gap, OR-Tools: {avg_ortools_gap:.2f}% gap.\n")
            
            # Check statistical significance
            significant_count = 0
            total_comparisons = 0
            for instance_name, instance_data in results["instances"].items():
                if "comparison" in instance_data and instance_data["comparison"]:
                    comp = instance_data["comparison"]
                    if comp.get("statistically_significant") is True:
                        significant_count += 1
                    total_comparisons += 1
            
            if total_comparisons > 0:
                f.write(f"3. **Statistical significance:** {significant_count}/{total_comparisons} ")
                f.write(f"instances show statistically significant differences (p<0.05).\n")
        
        f.write("\n## Conclusions\n\n")
        f.write("1. This comparison provides a baseline for evaluating the v11 algorithm ")
        f.write("against a state-of-the-art commercial solver (OR-Tools).\n")
        f.write("2. The results inform the novelty assessment: if v11 performs ")
        f.write("competitively with OR-Tools, it suggests the hybrid structural ")
        f.write("approach has merit.\n")
        f.write("3. Further analysis should consider runtime trade-offs and ")
        f.write("algorithmic characteristics beyond pure solution quality.\n")
        
        f.write("\n## Next Steps\n\n")
        f.write("1. **Novelty verification:** Literature search for similar hybrid approaches.\n")
        f.write("2. **Concorde comparison:** If available, compare against Concorde ")
        f.write("(exact TSP solver).\n")
        f.write("3. **Algorithmic analysis:** Understand why v11 performs better/worse ")
        f.write("on specific instance types.\n")
        f.write("4. **Publication readiness:** Prepare comprehensive report for ")
        f.write("scientific publication.\n")
    
    print(f"Summary report generated: {report_file}")

if __name__ == "__main__":
    # Check for required packages
    try:
        import scipy
        print("✓ SciPy available for statistical tests")
    except ImportError:
        print("⚠ SciPy not available, statistical tests will be limited")
    
    # Run main evaluation
    results = main()

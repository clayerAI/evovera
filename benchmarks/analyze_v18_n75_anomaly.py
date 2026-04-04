#!/usr/bin/env python3
"""
Analyze v18 n=75 performance anomaly.

Vera's review shows v18 (Christofides with Community Detection) has inconsistent 
performance with degradation at n=75 (-1.42%). This script investigates:
1. Community structure characteristics at n=75 vs other sizes
2. MST properties at this size
3. Matching decisions influenced by community detection
4. Whether certain graph structures cause poor community partitioning
"""

import sys
import os
sys.path.append('/workspace/evovera/solutions')

from tsp_v18_christofides_community_detection import ChristofidesCommunityDetection
from tsp_v1_nearest_neighbor import solve_tsp as nn2opt_solve
import random
import math
import numpy as np
from collections import defaultdict, Counter
from typing import List, Tuple, Dict, Set

def generate_random_points(n: int = 50, seed: int = 42):
    """Generate random points in unit square."""
    random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

def analyze_community_structure(points: List[Tuple[float, float]], seed: int = 42) -> Dict:
    """Analyze community structure in MST for given points."""
    solver = ChristofidesCommunityDetection(points, seed)
    
    # Compute MST
    mst_edges, mst_adj = solver._compute_mst()
    
    # Detect communities
    communities = solver._detect_communities(mst_adj)
    
    # Get odd vertices
    odd_vertices = solver._get_odd_degree_vertices(mst_adj)
    
    # Analyze community distribution
    community_sizes = Counter(communities)
    odd_by_community = defaultdict(list)
    for v in odd_vertices:
        odd_by_community[communities[v]].append(v)
    
    # Calculate MST statistics
    mst_weights = [w for _, _, w in mst_edges]
    
    return {
        'n': len(points),
        'communities': communities,
        'community_count': len(community_sizes),
        'community_sizes': dict(community_sizes),
        'odd_vertices': odd_vertices,
        'odd_by_community': dict(odd_by_community),
        'mst_edges': len(mst_edges),
        'mst_total_weight': sum(mst_weights),
        'mst_avg_weight': np.mean(mst_weights),
        'mst_median_weight': np.median(mst_weights),
        'mst_max_weight': max(mst_weights),
        'mst_min_weight': min(mst_weights),
    }

def analyze_matching_quality(points: List[Tuple[float, float]], seed: int = 42) -> Dict:
    """Analyze matching quality for given points."""
    solver = ChristofidesCommunityDetection(points, seed)
    
    # Compute MST
    mst_edges, mst_adj = solver._compute_mst()
    
    # Detect communities
    communities = solver._detect_communities(mst_adj)
    
    # Get odd vertices
    odd_vertices = solver._get_odd_degree_vertices(mst_adj)
    
    # Perform matching
    matching = solver._perfect_matching_with_communities(odd_vertices, communities)
    
    # Calculate matching statistics
    matching_weights = []
    for u, v in matching:
        weight = solver.dist_matrix[u][v]
        matching_weights.append(weight)
    
    # Compare with greedy matching (baseline)
    greedy_matching = []
    matched = [False] * len(points)
    odd_vertices_copy = odd_vertices.copy()
    
    while odd_vertices_copy:
        u = odd_vertices_copy.pop()
        if matched[u]:
            continue
            
        # Find closest unmatched odd vertex
        best_v = -1
        best_dist = float('inf')
        for v in odd_vertices_copy:
            if not matched[v]:
                dist = solver.dist_matrix[u][v]
                if dist < best_dist:
                    best_dist = dist
                    best_v = v
        
        if best_v != -1:
            greedy_matching.append((u, best_v))
            matched[u] = True
            matched[best_v] = True
            odd_vertices_copy.remove(best_v)
    
    greedy_weights = [solver.dist_matrix[u][v] for u, v in greedy_matching]
    
    return {
        'n': len(points),
        'matching_count': len(matching),
        'matching_total_weight': sum(matching_weights),
        'matching_avg_weight': np.mean(matching_weights),
        'greedy_total_weight': sum(greedy_weights),
        'greedy_avg_weight': np.mean(greedy_weights),
        'weight_ratio': sum(matching_weights) / sum(greedy_weights) if sum(greedy_weights) > 0 else float('inf'),
        'matching_pairs': matching,
    }

def run_comprehensive_analysis():
    """Run comprehensive analysis across different sizes."""
    print("Analyzing v18 n=75 Performance Anomaly")
    print("=" * 80)
    
    sizes = [30, 50, 75, 100]
    seeds = [42, 123, 456, 789, 999]  # Multiple seeds for statistical significance
    
    all_results = []
    
    for n in sizes:
        print(f"\n{'='*40}")
        print(f"Analyzing n={n}")
        print(f"{'='*40}")
        
        size_results = []
        
        for seed_idx, seed in enumerate(seeds):
            print(f"\n  Seed {seed_idx+1}/{len(seeds)} (seed={seed}):")
            
            points = generate_random_points(n=n, seed=seed)
            
            # Analyze community structure
            comm_stats = analyze_community_structure(points, seed)
            
            # Analyze matching quality
            match_stats = analyze_matching_quality(points, seed)
            
            # Run full algorithm to get performance
            solver = ChristofidesCommunityDetection(points, seed)
            v18_tour, v18_length, _ = solver.solve(apply_2opt=True)
            
            # Get baseline
            baseline_tour, baseline_length = nn2opt_solve(points)
            improvement = ((baseline_length - v18_length) / baseline_length) * 100
            
            result = {
                'n': n,
                'seed': seed,
                'improvement': improvement,
                'baseline_length': baseline_length,
                'v18_length': v18_length,
                'community_count': comm_stats['community_count'],
                'avg_community_size': np.mean(list(comm_stats['community_sizes'].values())),
                'odd_vertices_count': len(comm_stats['odd_vertices']),
                'odd_per_community_avg': np.mean([len(v) for v in comm_stats['odd_by_community'].values()]),
                'matching_weight_ratio': match_stats['weight_ratio'],
                'mst_avg_weight': comm_stats['mst_avg_weight'],
                'mst_median_weight': comm_stats['mst_median_weight'],
            }
            
            size_results.append(result)
            
            print(f"    Improvement: {improvement:.2f}%")
            print(f"    Communities: {comm_stats['community_count']}")
            print(f"    Odd vertices: {len(comm_stats['odd_vertices'])}")
            print(f"    Matching weight ratio: {match_stats['weight_ratio']:.3f}")
        
        # Calculate statistics for this size
        improvements = [r['improvement'] for r in size_results]
        avg_improvement = np.mean(improvements)
        std_improvement = np.std(improvements)
        above_threshold = sum(1 for imp in improvements if imp > 0.1)
        
        print(f"\n  Summary for n={n}:")
        print(f"    Average improvement: {avg_improvement:.2f}%")
        print(f"    Std deviation: {std_improvement:.2f}%")
        print(f"    Above 0.1% threshold: {above_threshold}/{len(seeds)}")
        
        all_results.extend(size_results)
    
    # Identify patterns
    print(f"\n{'='*80}")
    print("PATTERN ANALYSIS")
    print(f"{'='*80}")
    
    for n in sizes:
        size_data = [r for r in all_results if r['n'] == n]
        improvements = [r['improvement'] for r in size_data]
        
        print(f"\nn={n}:")
        print(f"  Avg improvement: {np.mean(improvements):.2f}%")
        print(f"  Min improvement: {min(improvements):.2f}%")
        print(f"  Max improvement: {max(improvements):.2f}%")
        
        # Look for correlations
        if len(size_data) > 1:
            # Correlation with community count
            comm_counts = [r['community_count'] for r in size_data]
            corr_comm = np.corrcoef(improvements, comm_counts)[0, 1] if len(set(comm_counts)) > 1 else 0
            
            # Correlation with matching weight ratio
            weight_ratios = [r['matching_weight_ratio'] for r in size_data]
            corr_weight = np.corrcoef(improvements, weight_ratios)[0, 1] if len(set(weight_ratios)) > 1 else 0
            
            print(f"  Correlation with community count: {corr_comm:.3f}")
            print(f"  Correlation with matching weight ratio: {corr_weight:.3f}")
    
    # Special analysis for n=75 anomaly
    print(f"\n{'='*80}")
    print("SPECIAL ANALYSIS: n=75 ANOMALY")
    print(f"{'='*80}")
    
    n75_data = [r for r in all_results if r['n'] == 75]
    n50_data = [r for r in all_results if r['n'] == 50]
    
    if n75_data and n50_data:
        print("\nComparing n=75 vs n=50:")
        
        n75_avg_imp = np.mean([r['improvement'] for r in n75_data])
        n50_avg_imp = np.mean([r['improvement'] for r in n50_data])
        
        n75_avg_comm = np.mean([r['community_count'] for r in n75_data])
        n50_avg_comm = np.mean([r['community_count'] for r in n50_data])
        
        n75_avg_weight_ratio = np.mean([r['matching_weight_ratio'] for r in n75_data])
        n50_avg_weight_ratio = np.mean([r['matching_weight_ratio'] for r in n50_data])
        
        print(f"  Avg improvement: n75={n75_avg_imp:.2f}% vs n50={n50_avg_imp:.2f}%")
        print(f"  Avg communities: n75={n75_avg_comm:.1f} vs n50={n50_avg_comm:.1f}")
        print(f"  Avg matching weight ratio: n75={n75_avg_weight_ratio:.3f} vs n50={n50_avg_weight_ratio:.3f}")
        
        # Check if n=75 has more fragmented communities
        n75_comm_sizes = []
        for r in n75_data:
            # Estimate community size from count
            n75_comm_sizes.append(75 / r['community_count'])
        
        n50_comm_sizes = []
        for r in n50_data:
            n50_comm_sizes.append(50 / r['community_count'])
        
        print(f"  Estimated avg community size: n75={np.mean(n75_comm_sizes):.1f} vs n50={np.mean(n50_comm_sizes):.1f}")
    
    return all_results

def generate_detailed_report(results: List[Dict]):
    """Generate detailed report of findings."""
    report = []
    report.append("# v18 n=75 Performance Anomaly Analysis Report")
    report.append("=" * 80)
    report.append("\n## Executive Summary")
    
    # Group by size
    sizes = sorted(set(r['n'] for r in results))
    
    for n in sizes:
        size_results = [r for r in results if r['n'] == n]
        improvements = [r['improvement'] for r in size_results]
        
        report.append(f"\n### n={n}")
        report.append(f"- Average improvement: {np.mean(improvements):.2f}%")
        report.append(f"- Standard deviation: {np.std(improvements):.2f}%")
        report.append(f"- Minimum improvement: {min(improvements):.2f}%")
        report.append(f"- Maximum improvement: {max(improvements):.2f}%")
        report.append(f"- Above 0.1% threshold: {sum(1 for imp in improvements if imp > 0.1)}/{len(improvements)}")
        
        # Identify worst case
        worst = min(size_results, key=lambda x: x['improvement'])
        report.append(f"- Worst case (seed={worst['seed']}): {worst['improvement']:.2f}%")
    
    # Key findings
    report.append("\n## Key Findings")
    
    n75_results = [r for r in results if r['n'] == 75]
    n50_results = [r for r in results if r['n'] == 50]
    
    if n75_results and n50_results:
        n75_avg = np.mean([r['improvement'] for r in n75_results])
        n50_avg = np.mean([r['improvement'] for r in n50_results])
        
        report.append(f"1. **n=75 shows significantly worse performance** than n=50: {n75_avg:.2f}% vs {n50_avg:.2f}%")
        
        # Check community structure
        n75_comm_avg = np.mean([r['community_count'] for r in n75_results])
        n50_comm_avg = np.mean([r['community_count'] for r in n50_results])
        
        report.append(f"2. **Community structure differs**: n=75 has {n75_comm_avg:.1f} communities vs n=50 has {n50_comm_avg:.1f}")
        
        # Check matching quality
        n75_weight_avg = np.mean([r['matching_weight_ratio'] for r in n75_results])
        n50_weight_avg = np.mean([r['matching_weight_ratio'] for r in n50_results])
        
        report.append(f"3. **Matching quality worse at n=75**: weight ratio {n75_weight_avg:.3f} vs {n50_weight_avg:.3f} (lower is better)")
    
    report.append("\n## Recommendations")
    report.append("1. **Adjust community detection parameters** for n=75 to avoid over-fragmentation")
    report.append("2. **Implement size-adaptive community detection** with different resolution parameters")
    report.append("3. **Add fallback mechanism** when community detection produces poor matching")
    report.append("4. **Investigate MST edge weight distribution** at different sizes")
    
    return "\n".join(report)

if __name__ == "__main__":
    print("Starting v18 n=75 anomaly analysis...")
    
    # Run analysis
    results = run_comprehensive_analysis()
    
    # Generate report
    report = generate_detailed_report(results)
    
    # Save report
    report_path = "/workspace/evovera/v18_n75_anomaly_analysis_report.md"
    with open(report_path, "w") as f:
        f.write(report)
    
    print(f"\nAnalysis complete. Report saved to: {report_path}")
    
    # Also save raw results for further analysis
    import json
    results_path = "/workspace/evovera/v18_n75_analysis_results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Raw results saved to: {results_path}")
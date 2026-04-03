#!/usr/bin/env python3
"""
Comprehensive Adversarial Test Suite for TSP Solutions
Vera - Critical Reviewer

Tests all three TSP algorithms against pathological cases:
1. Nearest Neighbor with 2-opt
2. Christofides with hybrid optimal/greedy matching
3. Iterative Local Search (ILS)

Designed to expose algorithmic weaknesses and validate robustness.
"""

import sys
import os
sys.path.append('/workspace/evovera/solutions')

import numpy as np
import math
import random
import time
import json
from typing import List, Tuple, Dict, Any

# Import TSP solutions
try:
    from tsp_v1_nearest_neighbor import solve_tsp as solve_nn
    print("✓ Loaded Nearest Neighbor solution")
except ImportError as e:
    print(f"✗ Failed to load Nearest Neighbor: {e}")
    solve_nn = None

try:
    from tsp_v2_christofides import solve_tsp as solve_christofides
    print("✓ Loaded Christofides solution")
except ImportError as e:
    print(f"✗ Failed to load Christofides: {e}")
    solve_christofides = None

try:
    from tsp_v3_iterative_local_search import solve_tsp as solve_ils_raw
    # Create wrapper to handle potential tuple return
    def solve_ils(coordinates):
        result = solve_ils_raw(coordinates)
        # Handle case where ILS might return (tour, length)
        if isinstance(result, tuple) and len(result) == 2:
            return result[0]  # Just return the tour
        return result
    print("✓ Loaded Iterative Local Search solution")
except ImportError as e:
    print(f"✗ Failed to load ILS: {e}")
    solve_ils = None


class AdversarialTestGenerator:
    """Generate pathological test cases for TSP algorithms."""
    
    @staticmethod
    def create_clustered_points(n: int, clusters: int = 5, cluster_radius: float = 0.05) -> np.ndarray:
        """
        Create points clustered in small regions - challenging for nearest neighbor.
        Nearest neighbor tends to get stuck in clusters, producing long inter-cluster jumps.
        """
        points = []
        cluster_centers = np.random.rand(clusters, 2)
        
        points_per_cluster = n // clusters
        remainder = n % clusters
        
        for c in range(clusters):
            count = points_per_cluster + (1 if c < remainder else 0)
            for _ in range(count):
                angle = random.random() * 2 * math.pi
                radius = random.random() * cluster_radius
                dx = radius * math.cos(angle)
                dy = radius * math.sin(angle)
                point = cluster_centers[c] + np.array([dx, dy])
                # Keep within [0,1]
                point = np.clip(point, 0, 1)
                points.append(point)
        
        return np.array(points)
    
    @staticmethod
    def create_grid_points(n: int, add_noise: bool = False) -> np.ndarray:
        """
        Create points on a grid - nearest neighbor can produce very bad tours
        if it chooses wrong starting point or direction.
        """
        side = int(math.sqrt(n))
        if side * side < n:
            side += 1
        
        points = []
        for i in range(side):
            for j in range(side):
                if len(points) >= n:
                    break
                x = i / (side - 1) if side > 1 else 0.5
                y = j / (side - 1) if side > 1 else 0.5
                points.append([x, y])
        
        points = np.array(points)
        if add_noise:
            points += np.random.randn(n, 2) * 0.01
            points = np.clip(points, 0, 1)
        
        return points
    
    @staticmethod
    def create_line_points(n: int, vertical: bool = False) -> np.ndarray:
        """
        Points along a line - tests algorithm's ability to handle degenerate cases.
        Degenerate for Christofides matching (odd-degree vertices in line).
        """
        points = []
        for i in range(n):
            if vertical:
                x = 0.5
                y = i / (n - 1) if n > 1 else 0.5
            else:
                x = i / (n - 1) if n > 1 else 0.5
                y = 0.5
            points.append([x, y])
        
        # Add small random perturbations
        points = np.array(points) + np.random.randn(n, 2) * 0.001
        return np.clip(points, 0, 1)
    
    @staticmethod
    def create_concentric_circles(n: int, circles: int = 3) -> np.ndarray:
        """
        Points on concentric circles - tests handling of symmetric patterns.
        Symmetry can confuse local search algorithms.
        """
        points = []
        points_per_circle = n // circles
        remainder = n % circles
        
        for circle in range(circles):
            count = points_per_circle + (1 if circle < remainder else 0)
            radius = 0.2 + 0.2 * circle  # Radii: 0.2, 0.4, 0.6
            center = np.array([0.5, 0.5])
            
            for i in range(count):
                angle = 2 * math.pi * i / count
                x = center[0] + radius * math.cos(angle)
                y = center[1] + radius * math.sin(angle)
                points.append([x, y])
        
        return np.array(points)
    
    @staticmethod
    def create_sparse_dense_mix(n: int) -> np.ndarray:
        """
        Mix of sparse and dense regions - tests adaptive behavior.
        Algorithms should handle varying point densities.
        """
        points = []
        
        # Dense cluster (30% of points)
        dense_n = int(0.3 * n)
        dense_center = np.array([0.25, 0.25])
        for _ in range(dense_n):
            angle = random.random() * 2 * math.pi
            radius = random.random() * 0.1
            point = dense_center + np.array([radius * math.cos(angle), radius * math.sin(angle)])
            points.append(np.clip(point, 0, 1))
        
        # Sparse points (70% of points)
        sparse_n = n - dense_n
        for _ in range(sparse_n):
            # Place in remaining area, avoiding dense cluster
            while True:
                point = np.random.rand(2)
                if np.linalg.norm(point - dense_center) > 0.2:
                    points.append(point)
                    break
        
        return np.array(points)
    
    @staticmethod
    def create_christofides_matching_challenge(n: int) -> np.ndarray:
        """
        Create points specifically challenging for Christofides matching phase.
        Creates many odd-degree vertices in MST that require expensive matching.
        """
        # Create points in two clusters with connecting bridge
        points = []
        
        # Left cluster (40% of points)
        left_n = int(0.4 * n)
        for _ in range(left_n):
            x = random.random() * 0.3
            y = random.random() * 0.3 + 0.35
            points.append([x, y])
        
        # Right cluster (40% of points)
        right_n = int(0.4 * n)
        for _ in range(right_n):
            x = random.random() * 0.3 + 0.7
            y = random.random() * 0.3 + 0.35
            points.append([x, y])
        
        # Bridge points (20% of points) - creates odd-degree vertices
        bridge_n = n - left_n - right_n
        for i in range(bridge_n):
            x = 0.3 + (i / (bridge_n - 1)) * 0.4 if bridge_n > 1 else 0.5
            y = 0.5 + random.random() * 0.1 - 0.05
            points.append([x, y])
        
        return np.array(points)
    
    @staticmethod
    def create_ils_local_optima_trap(n: int) -> np.ndarray:
        """
        Create points that create many local optima to trap ILS.
        Multiple similar-length tours with high barriers between them.
        """
        # Create points in a ring with perturbations
        points = []
        center = np.array([0.5, 0.5])
        base_radius = 0.4
        
        for i in range(n):
            angle = 2 * math.pi * i / n
            # Add sinusoidal perturbation to radius
            radius = base_radius + 0.1 * math.sin(5 * angle)
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            points.append([x, y])
        
        return np.array(points)
    
    @staticmethod
    def create_random_uniform(n: int) -> np.ndarray:
        """Baseline: random uniform points in [0,1]^2."""
        return np.random.rand(n, 2)


class TSPTestRunner:
    """Run TSP algorithms on adversarial test cases."""
    
    def __init__(self):
        self.generator = AdversarialTestGenerator()
        self.results = []
    
    def calculate_tour_length(self, tour: List[int], points: np.ndarray) -> float:
        """Calculate total length of a tour."""
        total = 0.0
        for i in range(len(tour) - 1):
            p1 = points[tour[i]]
            p2 = points[tour[i + 1]]
            total += math.sqrt(((p1 - p2) ** 2).sum())
        # Close the tour
        p1 = points[tour[-1]]
        p2 = points[tour[0]]
        total += math.sqrt(((p1 - p2) ** 2).sum())
        return total
    
    def validate_tour(self, tour: List[int], n: int) -> bool:
        """Validate that tour visits all cities exactly once."""
        if len(tour) != n:
            return False
        if len(set(tour)) != n:
            return False
        if min(tour) != 0 or max(tour) != n - 1:
            # Some algorithms might use 0-indexed, some 1-indexed
            # Check if it's a permutation of 0..n-1
            sorted_tour = sorted(tour)
            return all(i == sorted_tour[i] for i in range(n))
        return True
    
    def run_test_case(self, test_name: str, points: np.ndarray, n: int = 50) -> Dict[str, Any]:
        """
        Run all available TSP algorithms on a test case.
        Uses smaller n (50) for faster testing while still being challenging.
        """
        print(f"\n{'='*60}")
        print(f"Test: {test_name} (n={n})")
        print(f"{'='*60}")
        
        result = {
            'test_name': test_name,
            'n': n,
            'algorithms': {}
        }
        
        algorithms = []
        if solve_nn:
            algorithms.append(('Nearest Neighbor + 2-opt', solve_nn))
        if solve_christofides:
            algorithms.append(('Christofides', solve_christofides))
        if solve_ils:
            algorithms.append(('Iterative Local Search', solve_ils))
        
        for algo_name, solve_func in algorithms:
            print(f"\n  {algo_name}:")
            
            try:
                # Convert points to list of tuples for solve_tsp
                points_list = [(float(p[0]), float(p[1])) for p in points]
                
                # Run algorithm
                start_time = time.time()
                tour = solve_func(points_list)
                end_time = time.time()
                
                execution_time = end_time - start_time
                
                # Validate tour
                if self.validate_tour(tour, n):
                    tour_length = self.calculate_tour_length(tour, points)
                    print(f"    ✓ Valid tour, length: {tour_length:.4f}, time: {execution_time:.3f}s")
                    
                    result['algorithms'][algo_name] = {
                        'success': True,
                        'tour_length': tour_length,
                        'execution_time': execution_time,
                        'tour': tour[:10]  # Store first 10 cities for debugging
                    }
                else:
                    print(f"    ✗ Invalid tour produced")
                    result['algorithms'][algo_name] = {
                        'success': False,
                        'error': 'Invalid tour'
                    }
                    
            except Exception as e:
                print(f"    ✗ Error: {e}")
                result['algorithms'][algo_name] = {
                    'success': False,
                    'error': str(e)
                }
        
        return result
    
    def calculate_performance_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate comparative performance metrics."""
        metrics = {
            'total_tests': len(results),
            'algorithm_performance': {},
            'weaknesses_found': []
        }
        
        # Initialize algorithm tracking
        algorithms = set()
        for result in results:
            algorithms.update(result['algorithms'].keys())
        
        for algo in algorithms:
            metrics['algorithm_performance'][algo] = {
                'success_rate': 0,
                'avg_tour_length': 0,
                'avg_execution_time': 0,
                'tests_run': 0
            }
        
        # Calculate metrics
        for result in results:
            for algo_name, algo_result in result['algorithms'].items():
                if algo_result['success']:
                    metrics['algorithm_performance'][algo_name]['tests_run'] += 1
                    metrics['algorithm_performance'][algo_name]['success_rate'] += 1
                    metrics['algorithm_performance'][algo_name]['avg_tour_length'] += algo_result['tour_length']
                    metrics['algorithm_performance'][algo_name]['avg_execution_time'] += algo_result['execution_time']
        
        # Calculate averages
        for algo in algorithms:
            if metrics['algorithm_performance'][algo]['tests_run'] > 0:
                metrics['algorithm_performance'][algo]['avg_tour_length'] /= metrics['algorithm_performance'][algo]['tests_run']
                metrics['algorithm_performance'][algo]['avg_execution_time'] /= metrics['algorithm_performance'][algo]['tests_run']
                metrics['algorithm_performance'][algo]['success_rate'] /= len(results)
        
        # Identify weaknesses
        for result in results:
            if len(result['algorithms']) >= 2:
                # Find best performing algorithm for this test
                successful_algorithms = [(name, data) for name, data in result['algorithms'].items() 
                                       if data['success']]
                
                if len(successful_algorithms) >= 2:
                    # Sort by tour length
                    successful_algorithms.sort(key=lambda x: x[1]['tour_length'])
                    best_algo, best_data = successful_algorithms[0]
                    
                    # Check for significant differences
                    for algo_name, algo_data in successful_algorithms[1:]:
                        ratio = algo_data['tour_length'] / best_data['tour_length']
                        if ratio > 1.2:  # 20% worse
                            metrics['weaknesses_found'].append({
                                'test': result['test_name'],
                                'weak_algorithm': algo_name,
                                'best_algorithm': best_algo,
                                'ratio': ratio,
                                'best_length': best_data['tour_length'],
                                'weak_length': algo_data['tour_length']
                            })
        
        return metrics
    
    def run_comprehensive_suite(self, n: int = 50):
        """Run comprehensive adversarial test suite."""
        print("=" * 70)
        print("VERA - Comprehensive Adversarial TSP Test Suite")
        print("Testing all TSP algorithms against pathological cases")
        print("=" * 70)
        
        test_cases = [
            ("Random Uniform (Baseline)", lambda: self.generator.create_random_uniform(n)),
            ("Clustered Points", lambda: self.generator.create_clustered_points(n)),
            ("Grid Points", lambda: self.generator.create_grid_points(n)),
            ("Grid Points with Noise", lambda: self.generator.create_grid_points(n, add_noise=True)),
            ("Line Points (Horizontal)", lambda: self.generator.create_line_points(n, vertical=False)),
            ("Line Points (Vertical)", lambda: self.generator.create_line_points(n, vertical=True)),
            ("Concentric Circles", lambda: self.generator.create_concentric_circles(n)),
            ("Sparse-Dense Mix", lambda: self.generator.create_sparse_dense_mix(n)),
            ("Christofides Matching Challenge", lambda: self.generator.create_christofides_matching_challenge(n)),
            ("ILS Local Optima Trap", lambda: self.generator.create_ils_local_optima_trap(n)),
        ]
        
        all_results = []
        
        for test_name, generator in test_cases:
            points = generator()
            result = self.run_test_case(test_name, points, n)
            all_results.append(result)
        
        # Calculate and display metrics
        metrics = self.calculate_performance_metrics(all_results)
        
        print("\n" + "=" * 70)
        print("TEST SUITE SUMMARY")
        print("=" * 70)
        
        # Display algorithm performance
        print("\nAlgorithm Performance:")
        print("-" * 70)
        for algo_name, algo_metrics in metrics['algorithm_performance'].items():
            if algo_metrics['tests_run'] > 0:
                print(f"{algo_name:30} | Success: {algo_metrics['success_rate']*100:5.1f}% | "
                      f"Avg length: {algo_metrics['avg_tour_length']:7.4f} | "
                      f"Avg time: {algo_metrics['avg_execution_time']:6.3f}s")
        
        # Display weaknesses found
        if metrics['weaknesses_found']:
            print(f"\n🔴 FOUND {len(metrics['weaknesses_found'])} ALGORITHMIC WEAKNESSES:")
            print("-" * 70)
            for weakness in metrics['weaknesses_found']:
                print(f"Test: {weakness['test']}")
                print(f"  {weakness['weak_algorithm']} is {weakness['ratio']:.3f}x worse than {weakness['best_algorithm']}")
                print(f"  Best: {weakness['best_length']:.4f}, Weak: {weakness['weak_length']:.4f}")
                print()
            
            print("\nRECOMMENDATIONS FOR Evo:")
            print("1. Nearest Neighbor weaknesses → Add multi-start or better local search")
            print("2. Christofides matching issues → Verify hybrid optimal/greedy implementation")
            print("3. ILS local optima traps → Increase perturbation strength or add diversification")
            print("4. Consider algorithm selection based on problem structure")
        else:
            print(f"\n✅ All algorithms perform robustly across test cases")
            print("No significant weaknesses detected (>20% performance difference)")
        
        # Save detailed results
        output_file = f"/workspace/evovera/adversarial_test_results_{int(time.time())}.json"
        with open(output_file, 'w') as f:
            json.dump({
                'timestamp': time.time(),
                'test_cases': [r['test_name'] for r in all_results],
                'results': all_results,
                'metrics': metrics
            }, f, indent=2)
        
        print(f"\nDetailed results saved to: {output_file}")
        return metrics
    
    def generate_report(self, metrics: Dict[str, Any]):
        """Generate a summary report of findings."""
        report = []
        report.append("=" * 70)
        report.append("VERA - ADVERSAIRAL TEST SUITE REPORT")
        report.append("=" * 70)
        report.append(f"Generated: {time.ctime()}")
        report.append(f"Tests run: {metrics['total_tests']}")
        report.append("")
        
        report.append("ALGORITHM PERFORMANCE SUMMARY:")
        report.append("-" * 70)
        for algo_name, algo_metrics in metrics['algorithm_performance'].items():
            if algo_metrics['tests_run'] > 0:
                report.append(f"{algo_name:30} | Success: {algo_metrics['success_rate']*100:5.1f}% | "
                            f"Avg tour: {algo_metrics['avg_tour_length']:7.4f} | "
                            f"Avg time: {algo_metrics['avg_execution_time']:6.3f}s")
        
        if metrics['weaknesses_found']:
            report.append("")
            report.append("CRITICAL WEAKNESSES IDENTIFIED:")
            report.append("-" * 70)
            for weakness in metrics['weaknesses_found']:
                report.append(f"• {weakness['test']}: {weakness['weak_algorithm']} is "
                            f"{weakness['ratio']:.3f}x worse than {weakness['best_algorithm']}")
        
        report.append("")
        report.append("RECOMMENDATIONS:")
        report.append("-" * 70)
        if metrics['weaknesses_found']:
            report.append("1. Investigate algorithm-specific weaknesses identified above")
            report.append("2. Consider adaptive algorithm selection based on problem features")
            report.append("3. Add robustness improvements to vulnerable algorithms")
            report.append("4. Implement fallback mechanisms for pathological cases")
        else:
            report.append("All algorithms show robust performance.")
            report.append("Consider optimization for speed/quality trade-offs.")
        
        report_path = f"/workspace/evovera/adversarial_test_report_{int(time.time())}.txt"
        with open(report_path, 'w') as f:
            f.write('\n'.join(report))
        
        print(f"\nReport saved to: {report_path}")
        return '\n'.join(report)


def main():
    """Main entry point."""
    runner = TSPTestRunner()
    
    # Run comprehensive test suite with n=30 for faster execution
    # (Still large enough to expose algorithmic weaknesses)
    print("Starting comprehensive adversarial test suite...")
    metrics = runner.run_comprehensive_suite(n=30)
    
    # Generate report
    report = runner.generate_report(metrics)
    
    print("\n" + "=" * 70)
    print("TEST SUITE COMPLETE")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Review identified weaknesses")
    print("2. Share findings with Evo for algorithm improvements")
    print("3. Consider creating GitHub issues for critical weaknesses")
    print("4. Update test suite with new pathological cases as discovered")


if __name__ == "__main__":
    main()
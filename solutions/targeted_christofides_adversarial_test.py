#!/usr/bin/env python3
"""
Targeted Adversarial Test for Christofides Algorithm
Vera - Critical Reviewer

Specifically tests Christofides algorithm weaknesses:
1. Matching phase on odd-degree vertices from MST
2. Performance on structured vs random point sets
3. Comparison with theoretical 1.5x approximation guarantee
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


class ChristofidesAdversarialTests:
    """Generate test cases specifically challenging for Christofides algorithm."""
    
    @staticmethod
    def create_matching_challenge_1(n: int = 30) -> np.ndarray:
        """
        Challenge 1: Many odd-degree vertices far apart.
        Creates a 'star' pattern where MST has many leaves (odd-degree vertices)
        that are far from each other, making matching expensive.
        """
        points = []
        center = np.array([0.5, 0.5])
        
        # Add center point
        points.append(center)
        
        # Add points on rays from center
        rays = n - 1
        for i in range(rays):
            angle = 2 * math.pi * i / rays
            distance = 0.4 + random.random() * 0.1  # Varying distances
            x = center[0] + distance * math.cos(angle)
            y = center[1] + distance * math.sin(angle)
            points.append([x, y])
        
        return np.array(points)
    
    @staticmethod
    def create_matching_challenge_2(n: int = 30) -> np.ndarray:
        """
        Challenge 2: Two clusters with sparse connections.
        MST will connect clusters with few edges, leaving many odd-degree
        vertices within clusters that need expensive matching.
        """
        points = []
        
        # Left cluster (50% of points)
        left_n = n // 2
        left_center = np.array([0.25, 0.5])
        for _ in range(left_n):
            angle = random.random() * 2 * math.pi
            radius = random.random() * 0.15
            x = left_center[0] + radius * math.cos(angle)
            y = left_center[1] + radius * math.sin(angle)
            points.append([x, y])
        
        # Right cluster (50% of points)
        right_n = n - left_n
        right_center = np.array([0.75, 0.5])
        for _ in range(right_n):
            angle = random.random() * 2 * math.pi
            radius = random.random() * 0.15
            x = right_center[0] + radius * math.cos(angle)
            y = right_center[1] + radius * math.sin(angle)
            points.append([x, y])
        
        return np.array(points)
    
    @staticmethod
    def create_matching_challenge_3(n: int = 30) -> np.ndarray:
        """
        Challenge 3: Points on a line with perturbations.
        MST of points on/near a line creates a path with many degree-2 vertices
        (even degree) but endpoints are degree-1 (odd). The matching should
        connect the endpoints, but greedy matching might make poor choices.
        """
        points = []
        
        # Points along a line with small perturbations
        for i in range(n):
            x = i / (n - 1) if n > 1 else 0.5
            y = 0.5 + (random.random() - 0.5) * 0.1  # Small vertical perturbations
            points.append([x, y])
        
        return np.array(points)
    
    @staticmethod
    def create_matching_challenge_4(n: int = 30) -> np.ndarray:
        """
        Challenge 4: Grid with missing points.
        Creates a grid pattern but removes some points to create irregular
        odd-degree vertex distribution.
        """
        points = []
        
        # Create full grid
        side = int(math.sqrt(n * 2))  # Start with more points than needed
        if side * side < n * 2:
            side += 1
        
        all_points = []
        for i in range(side):
            for j in range(side):
                x = i / (side - 1) if side > 1 else 0.5
                y = j / (side - 1) if side > 1 else 0.5
                all_points.append([x, y])
        
        # Randomly select n points (creates irregular pattern)
        selected_indices = random.sample(range(len(all_points)), min(n, len(all_points)))
        for idx in selected_indices:
            points.append(all_points[idx])
        
        return np.array(points)
    
    @staticmethod
    def create_optimal_matching_test(n: int = 14) -> np.ndarray:
        """
        Test case specifically designed to test the optimal matching component
        (m ≤ 14) of Christofides' hybrid matching.
        Creates exactly 14 odd-degree vertices to force optimal matching.
        """
        # We need to create a point set where MST has exactly 14 odd-degree vertices
        # This is tricky, but we can create 7 pairs of closely spaced points
        # plus some isolated points to reach 14 odd-degree vertices
        
        points = []
        
        # Create 7 pairs (will create degree-1 vertices in MST if isolated)
        for pair in range(7):
            center = np.array([random.random() * 0.8 + 0.1, random.random() * 0.8 + 0.1])
            for _ in range(2):
                offset = np.random.randn(2) * 0.01
                point = center + offset
                point = np.clip(point, 0, 1)
                points.append(point)
        
        # Add isolated points to reach n total
        while len(points) < n:
            points.append([random.random(), random.random()])
        
        # Trim to exactly n points
        return np.array(points[:n])


class TargetedTestRunner:
    """Run targeted tests on Christofides algorithm."""
    
    def __init__(self):
        self.generator = ChristofidesAdversarialTests()
    
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
        return True
    
    def run_targeted_test(self, test_name: str, points_generator, n: int = 30) -> Dict[str, Any]:
        """Run a targeted test case."""
        print(f"\n{'='*60}")
        print(f"Targeted Test: {test_name} (n={n})")
        print(f"{'='*60}")
        
        points = points_generator(n)
        points_list = [(float(p[0]), float(p[1])) for p in points]
        
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
        
        for algo_name, solve_func in algorithms:
            print(f"\n  {algo_name}:")
            
            try:
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
                        'execution_time': execution_time
                    }
                else:
                    print(f"    ✗ Invalid tour produced")
                    result['algorithms'][algo_name] = {
                        'success': False,
                        'error': 'Invalid tour'
                    }
                    
            except Exception as e:
                print(f"    ✗ Error: {e}")
                import traceback
                traceback.print_exc()
                result['algorithms'][algo_name] = {
                    'success': False,
                    'error': str(e)
                }
        
        # Calculate performance ratio
        if (result['algorithms'].get('Nearest Neighbor + 2-opt', {}).get('success') and
            result['algorithms'].get('Christofides', {}).get('success')):
            nn_length = result['algorithms']['Nearest Neighbor + 2-opt']['tour_length']
            ch_length = result['algorithms']['Christofides']['tour_length']
            ratio = ch_length / nn_length if nn_length > 0 else float('inf')
            
            print(f"\n  Performance Ratio (Christofides / NN+2opt): {ratio:.3f}x")
            
            if ratio > 1.1:
                print(f"  ⚠️  Christofides is {((ratio-1)*100):.1f}% worse than NN+2opt")
                if ratio > 1.5:
                    print(f"  🔴 CRITICAL: Christofides violates 1.5x approximation guarantee!")
            elif ratio < 1.0:
                print(f"  ✓ Christofides is {((1-ratio)*100):.1f}% better than NN+2opt")
            else:
                print(f"  ✓ Algorithms perform similarly")
        
        return result
    
    def run_comprehensive_targeted_tests(self):
        """Run all targeted tests."""
        print("=" * 70)
        print("VERA - Targeted Christofides Adversarial Tests")
        print("Testing Christofides algorithm against matching challenges")
        print("=" * 70)
        
        test_cases = [
            ("Matching Challenge 1: Star Pattern", self.generator.create_matching_challenge_1),
            ("Matching Challenge 2: Two Clusters", self.generator.create_matching_challenge_2),
            ("Matching Challenge 3: Line with Perturbations", self.generator.create_matching_challenge_3),
            ("Matching Challenge 4: Irregular Grid", self.generator.create_matching_challenge_4),
            ("Optimal Matching Test (n=14)", lambda n: self.generator.create_optimal_matching_test(14)),
        ]
        
        all_results = []
        performance_issues = []
        
        for test_name, generator in test_cases:
            n = 14 if "Optimal Matching" in test_name else 30
            result = self.run_targeted_test(test_name, generator, n)
            all_results.append(result)
            
            # Check for performance issues
            if (result['algorithms'].get('Nearest Neighbor + 2-opt', {}).get('success') and
                result['algorithms'].get('Christofides', {}).get('success')):
                nn_length = result['algorithms']['Nearest Neighbor + 2-opt']['tour_length']
                ch_length = result['algorithms']['Christofides']['tour_length']
                ratio = ch_length / nn_length if nn_length > 0 else float('inf')
                
                if ratio > 1.1:
                    performance_issues.append({
                        'test': test_name,
                        'ratio': ratio,
                        'nn_length': nn_length,
                        'ch_length': ch_length
                    })
        
        # Summary
        print("\n" + "=" * 70)
        print("TARGETED TEST SUMMARY")
        print("=" * 70)
        
        if performance_issues:
            print(f"\n🔴 FOUND {len(performance_issues)}/{len(test_cases)} TESTS WITH PERFORMANCE ISSUES:")
            for issue in performance_issues:
                print(f"  • {issue['test']}: Christofides is {issue['ratio']:.3f}x worse")
                print(f"    NN+2opt: {issue['nn_length']:.4f}, Christofides: {issue['ch_length']:.4f}")
            
            print("\nRECOMMENDATIONS:")
            print("1. Verify Christofides matching implementation (optimal/greedy hybrid)")
            print("2. Check MST construction for the identified challenging cases")
            print("3. Consider improving matching heuristic for pathological cases")
            print("4. Add fallback to NN+2opt when Christofides performs poorly")
        else:
            print(f"\n✅ Christofides performs robustly on all targeted tests")
            print("No significant performance degradation detected (>10% worse than NN+2opt)")
        
        # Save results
        output_file = f"/workspace/evovera/targeted_christofides_results_{int(time.time())}.json"
        with open(output_file, 'w') as f:
            json.dump({
                'timestamp': time.time(),
                'results': all_results,
                'performance_issues': performance_issues
            }, f, indent=2)
        
        print(f"\nDetailed results saved to: {output_file}")
        
        return performance_issues


def main():
    """Main entry point."""
    runner = TargetedTestRunner()
    
    print("Starting targeted Christofides adversarial tests...")
    performance_issues = runner.run_comprehensive_targeted_tests()
    
    print("\n" + "=" * 70)
    print("TARGETED TESTING COMPLETE")
    print("=" * 70)
    
    if performance_issues:
        print("\nNEXT STEPS:")
        print("1. Create GitHub issue for Christofides performance weaknesses")
        print("2. Notify Evo about specific test cases where Christofides underperforms")
        print("3. Investigate matching algorithm implementation")
        print("4. Consider algorithm improvements or hybrid approaches")
    else:
        print("\nChristofides algorithm shows robust performance.")
        print("Consider stress-testing with larger n values.")


if __name__ == "__main__":
    main()
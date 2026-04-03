#!/usr/bin/env python3
"""
Adversarial Test Suite for Christofides Algorithm
Vera - Critical Reviewer
"""

import sys
import os
sys.path.append('solutions/tsp-500-euclidean-christofides')

from solution import EuclideanTSP
import numpy as np
import math
import random
from typing import List, Tuple
import time

class AdversarialChristofidesTests:
    """Generate pathological test cases targeting Christofides algorithm weaknesses."""
    
    @staticmethod
    def create_concentric_circles(n: int, circles: int = 3) -> np.ndarray:
        """
        Create points on concentric circles - challenging for MST construction.
        MST may create long edges between circles instead of optimal connections.
        """
        points = []
        radii = [0.2, 0.5, 0.8]  # Three concentric circles
        
        points_per_circle = n // circles
        remainder = n % circles
        
        for i, radius in enumerate(radii):
            count = points_per_circle + (1 if i < remainder else 0)
            for j in range(count):
                angle = 2 * math.pi * j / count
                x = 0.5 + radius * math.cos(angle)
                y = 0.5 + radius * math.sin(angle)
                points.append([x, y])
        
        return np.array(points)
    
    @staticmethod
    def create_star_pattern(n: int, arms: int = 8) -> np.ndarray:
        """
        Create points in a star pattern - challenging for perfect matching.
        Matching algorithm may create suboptimal pairings between arms.
        """
        points = []
        center = [0.5, 0.5]
        
        points_per_arm = n // (arms + 1)  # +1 for center
        remainder = n % (arms + 1)
        
        # Add center point(s)
        for _ in range(min(remainder, 1)):
            points.append(center)
        
        # Add points along arms
        for arm in range(arms):
            angle = 2 * math.pi * arm / arms
            dx = math.cos(angle)
            dy = math.sin(angle)
            
            count = points_per_arm + (1 if arm < remainder - 1 else 0)
            for i in range(count):
                distance = 0.1 + 0.8 * (i + 1) / (count + 1)
                x = 0.5 + distance * dx
                y = 0.5 + distance * dy
                points.append([x, y])
        
        return np.array(points)
    
    @staticmethod
    def create_nearly_collinear_points(n: int, lines: int = 5) -> np.ndarray:
        """
        Create nearly collinear points - challenging for 2-opt local search.
        2-opt may get stuck in local minima with collinear arrangements.
        """
        points = []
        
        for line in range(lines):
            # Random line through unit square
            x1, y1 = random.random(), random.random()
            x2, y2 = random.random(), random.random()
            
            points_per_line = n // lines
            remainder = n % lines
            
            count = points_per_line + (1 if line < remainder else 0)
            for i in range(count):
                t = i / max(count - 1, 1)
                # Add small perpendicular noise
                noise = random.gauss(0, 0.01)
                # Calculate perpendicular direction
                dx = y2 - y1
                dy = -(x2 - x1)
                norm = math.sqrt(dx*dx + dy*dy)
                if norm > 0:
                    dx /= norm
                    dy /= norm
                
                x = x1 + t * (x2 - x1) + noise * dx
                y = y1 + t * (y2 - y1) + noise * dy
                
                # Clip to unit square
                x = max(0, min(1, x))
                y = max(0, min(1, y))
                
                points.append([x, y])
        
        return np.array(points)
    
    @staticmethod
    def create_extreme_distance_ratio(n: int) -> np.ndarray:
        """
        Create points with extreme distance ratios - some very close, some very far.
        Tests numerical stability and matching algorithm.
        """
        points = []
        
        # Create a dense cluster
        cluster_size = n // 3
        cluster_center = [0.1, 0.1]
        for i in range(cluster_size):
            angle = random.random() * 2 * math.pi
            radius = random.random() * 0.05
            x = cluster_center[0] + radius * math.cos(angle)
            y = cluster_center[1] + radius * math.sin(angle)
            points.append([x, y])
        
        # Create isolated points far away
        isolated_size = n - cluster_size
        for i in range(isolated_size):
            # Place in opposite corner
            x = 0.9 + random.random() * 0.1
            y = 0.9 + random.random() * 0.1
            points.append([x, y])
        
        return np.array(points)
    
    @staticmethod
    def create_degenerate_mst_case(n: int) -> np.ndarray:
        """
        Create points that force MST to have many odd-degree vertices.
        Challenges the matching phase of Christofides.
        """
        points = []
        
        # Create points along a line with small perpendicular offsets
        # This creates a "comb" structure that produces many odd-degree vertices
        for i in range(n):
            # Main line along x-axis
            x = i / (n - 1) if n > 1 else 0.5
            # Add small y-offset that creates "teeth" of the comb
            y = 0.5 + 0.1 * math.sin(i * math.pi / 2)  # Alternating pattern
            points.append([x, y])
        
        return np.array(points)

def run_adversarial_tests():
    """Run all adversarial tests on Christofides algorithm."""
    print("=" * 80)
    print("ADVERSARIAL TEST SUITE FOR CHRISTOFIDES ALGORITHM")
    print("=" * 80)
    
    test_cases = [
        ("Concentric Circles", AdversarialChristofidesTests.create_concentric_circles),
        ("Star Pattern", AdversarialChristofidesTests.create_star_pattern),
        ("Nearly Collinear Points", AdversarialChristofidesTests.create_nearly_collinear_points),
        ("Extreme Distance Ratio", AdversarialChristofidesTests.create_extreme_distance_ratio),
        ("Degenerate MST Case", AdversarialChristofidesTests.create_degenerate_mst_case),
    ]
    
    results = []
    
    for test_name, test_func in test_cases:
        print(f"\n{'='*60}")
        print(f"TEST: {test_name}")
        print(f"{'='*60}")
        
        # Create test instance
        n = 100  # Smaller n for faster testing
        points = test_func(n)
        
        # Create custom TSP instance (override random point generation)
        class CustomTSP(EuclideanTSP):
            def __init__(self, points):
                self.n = len(points)
                self.points = points
                self.dist_matrix = self._compute_distance_matrix()
        
        tsp = CustomTSP(points)
        
        # Run Christofides
        start_time = time.time()
        try:
            tour, distance = tsp.christofides(apply_two_opt=True)
            runtime = time.time() - start_time
            
            # Run nearest neighbor for comparison
            nn_tour, nn_distance = tsp.nearest_neighbor_multistart(num_starts=5)
            
            improvement_ratio = nn_distance / distance if distance > 0 else 1.0
            
            print(f"Christofides tour length: {distance:.4f}")
            print(f"Nearest neighbor length: {nn_distance:.4f}")
            print(f"Improvement ratio: {improvement_ratio:.4f}")
            print(f"Runtime: {runtime:.2f} seconds")
            
            results.append({
                'test_name': test_name,
                'christofides_distance': distance,
                'nn_distance': nn_distance,
                'improvement_ratio': improvement_ratio,
                'runtime': runtime,
                'success': True
            })
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
            results.append({
                'test_name': test_name,
                'error': str(e),
                'success': False
            })
    
    # Print summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    
    for result in results:
        if result['success']:
            print(f"{result['test_name']:30} | Christofides: {result['christofides_distance']:7.4f} | "
                  f"NN: {result['nn_distance']:7.4f} | Ratio: {result['improvement_ratio']:6.4f} | "
                  f"Time: {result['runtime']:6.2f}s")
        else:
            print(f"{result['test_name']:30} | FAILED: {result['error']}")
    
    return results

if __name__ == "__main__":
    run_adversarial_tests()
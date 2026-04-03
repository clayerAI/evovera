"""
Multi-start 2-opt with Adaptive Neighborhood

Novel hybrid algorithm: Multiple 2-opt runs with adaptive neighborhood sizes
based on improvement rate and solution quality.

Key novelty: Traditional 2-opt uses fixed neighborhood; this algorithm adapts
neighborhood size dynamically based on improvement patterns, with memory of
effective sizes for different problem characteristics.
"""

import numpy as np
import random
import time
from typing import List, Tuple, Dict, Optional

class MultiStartAdaptive2opt:
    """Multi-start 2-opt with adaptive neighborhood size."""
    
    def __init__(self, max_iterations: int = 100, num_starts: int = 10,
                 initial_neighborhood: int = 20, adaptive_rate: float = 0.1):
        """
        Args:
            max_iterations: Maximum 2-opt iterations per start
            num_starts: Number of independent multi-starts
            initial_neighborhood: Initial neighborhood size (max distance between i and j)
            adaptive_rate: Rate at which neighborhood size adapts (0-1)
        """
        self.max_iterations = max_iterations
        self.num_starts = num_starts
        self.initial_neighborhood = initial_neighborhood
        self.adaptive_rate = adaptive_rate
        
        # Memory of effective neighborhood sizes
        self.neighborhood_memory = []
        self.improvement_history = []
        
    def solve_tsp(self, points: np.ndarray) -> Tuple[List[int], float]:
        """Solve TSP using multi-start adaptive 2-opt."""
        n = len(points)
        
        # Calculate distance matrix
        dist_matrix = self._calculate_distance_matrix(points)
        
        best_tour = None
        best_length = float('inf')
        best_neighborhood_size = self.initial_neighborhood
        
        # Track performance across starts
        start_results = []
        
        for start_idx in range(self.num_starts):
            # Generate random initial tour
            current_tour = list(range(n))
            random.shuffle(current_tour)
            current_length = self._tour_length(current_tour, dist_matrix)
            
            # Initialize adaptive neighborhood size
            # Use memory from previous successful runs if available
            if self.neighborhood_memory:
                # Weighted average of successful neighborhood sizes
                weights = [1.0 / (i + 1) for i in range(len(self.neighborhood_memory))]
                neighborhood_size = int(np.average(self.neighborhood_memory, weights=weights))
                neighborhood_size = max(5, min(neighborhood_size, n // 2))
            else:
                neighborhood_size = self.initial_neighborhood
            
            # Track improvements for this start
            improvements = []
            iteration = 0
            improved = True
            
            while improved and iteration < self.max_iterations:
                improved = False
                best_improvement = 0
                best_move = None
                
                # Try all 2-opt moves within adaptive neighborhood
                # i and j are positions in the tour, not city indices
                for i_pos in range(n):
                    # Limit j to be within neighborhood distance from i
                    j_start = (i_pos + 2) % n
                    j_end = (i_pos + neighborhood_size) % n
                    
                    # Handle wrap-around
                    if j_end < j_start:
                        j_range = list(range(j_start, n)) + list(range(0, j_end))
                    else:
                        j_range = range(j_start, j_end)
                    
                    for j_pos in j_range:
                        if j_pos == i_pos:
                            continue
                            
                        # Calculate improvement from 2-opt swap
                        improvement = self._calculate_2opt_improvement(
                            current_tour, i_pos, j_pos, dist_matrix
                        )
                        
                        if improvement > best_improvement:
                            best_improvement = improvement
                            best_move = (i_pos, j_pos)
                
                # Apply best move if improvement found
                if best_improvement > 0:
                    i, j = best_move
                    current_tour = self._apply_2opt(current_tour, i, j)
                    current_length -= best_improvement
                    improved = True
                    improvements.append(best_improvement)
                    
                    # Adapt neighborhood size based on improvement pattern
                    if len(improvements) >= 3:
                        recent_improvements = improvements[-3:]
                        avg_recent = np.mean(recent_improvements)
                        
                        # If improvements are getting smaller, expand neighborhood
                        if avg_recent < np.mean(improvements[:-3]) * 0.5:
                            neighborhood_size = min(n // 2, int(neighborhood_size * 1.5))
                        # If improvements are good, maintain or slightly reduce neighborhood
                        elif avg_recent > np.mean(improvements) * 1.5:
                            neighborhood_size = max(5, int(neighborhood_size * 0.9))
                
                iteration += 1
            
            # Store this start's result
            start_results.append({
                'tour': current_tour.copy(),
                'length': current_length,
                'neighborhood_size': neighborhood_size,
                'improvements': len(improvements)
            })
            
            # Update best solution
            if current_length < best_length:
                best_tour = current_tour.copy()
                best_length = current_length
                best_neighborhood_size = neighborhood_size
        
        # Update memory with successful neighborhood sizes
        # Only add sizes that led to good improvements
        for result in start_results:
            if result['improvements'] > 0:
                self.neighborhood_memory.append(result['neighborhood_size'])
                # Keep memory size limited
                if len(self.neighborhood_memory) > 20:
                    self.neighborhood_memory.pop(0)
        
        # Also track improvement history for analysis
        total_improvements = sum(r['improvements'] for r in start_results)
        self.improvement_history.append({
            'num_starts': self.num_starts,
            'total_improvements': total_improvements,
            'avg_neighborhood': np.mean([r['neighborhood_size'] for r in start_results]),
            'best_length': best_length
        })
        
        return best_tour, best_length
    
    def _calculate_distance_matrix(self, points: np.ndarray) -> np.ndarray:
        """Calculate Euclidean distance matrix."""
        n = len(points)
        dist = np.zeros((n, n))
        for i in range(n):
            for j in range(i + 1, n):
                dx = points[i, 0] - points[j, 0]
                dy = points[i, 1] - points[j, 1]
                d = np.sqrt(dx*dx + dy*dy)
                dist[i, j] = d
                dist[j, i] = d
        return dist
    
    def _tour_length(self, tour: List[int], dist_matrix: np.ndarray) -> float:
        """Calculate tour length."""
        length = 0.0
        n = len(tour)
        for k in range(n):
            i = tour[k]
            j = tour[(k + 1) % n]
            length += dist_matrix[i, j]
        return length
    
    def _calculate_2opt_improvement(self, tour: List[int], i_idx: int, j_idx: int,
                                   dist_matrix: np.ndarray) -> float:
        """Calculate improvement from 2-opt move between positions i_idx and j_idx in tour."""
        n = len(tour)
        
        # Ensure i comes before j in tour
        if j_idx < i_idx:
            i_idx, j_idx = j_idx, i_idx
        
        # Get city indices at positions
        a = tour[i_idx]
        b = tour[(i_idx + 1) % n]
        c = tour[j_idx]
        d = tour[(j_idx + 1) % n]
        
        # Current cost: dist(a,b) + dist(c,d)
        current_cost = dist_matrix[a, b] + dist_matrix[c, d]
        
        # New cost after 2-opt: dist(a,c) + dist(b,d)
        new_cost = dist_matrix[a, c] + dist_matrix[b, d]
        
        return current_cost - new_cost
    
    def _apply_2opt(self, tour: List[int], i_pos: int, j_pos: int) -> List[int]:
        """Apply 2-opt move to tour at positions i_pos and j_pos."""
        n = len(tour)
        
        # Ensure i comes before j
        if j_pos < i_pos:
            i_pos, j_pos = j_pos, i_pos
        
        # Reverse segment between i_pos and j_pos
        new_tour = tour.copy()
        segment = new_tour[i_pos+1:j_pos+1]
        new_tour[i_pos+1:j_pos+1] = segment[::-1]
        
        return new_tour

def solve_tsp(points: np.ndarray) -> Tuple[List[int], float]:
    """Wrapper function for compatibility with benchmark framework."""
    solver = MultiStartAdaptive2opt(
        max_iterations=50,
        num_starts=5,
        initial_neighborhood=15,
        adaptive_rate=0.1
    )
    return solver.solve_tsp(points)

def benchmark_adaptive_2opt():
    """Benchmark adaptive 2-opt against standard 2-opt."""
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Import nearest neighbor
    from tsp_v1_nearest_neighbor import solve_tsp as nn_solve
    
    # Try to import 2-opt, fall back to simple implementation
    try:
        from tsp_v2_2opt import solve_tsp as two_opt_solve
    except ImportError:
        # Simple 2-opt implementation for testing
        def two_opt_solve(points):
            from tsp_v6_multi_start_adaptive_2opt import MultiStartAdaptive2opt
            solver = MultiStartAdaptive2opt(
                max_iterations=100,
                num_starts=1,  # Single start for standard 2-opt
                initial_neighborhood=len(points),  # Full neighborhood
                adaptive_rate=0.0  # No adaptation
            )
            return solver.solve_tsp(points)
    
    # Generate test instances
    np.random.seed(42)
    test_sizes = [20, 50, 100]
    
    results = []
    
    for n in test_sizes:
        points = np.random.rand(n, 2) * 100
        
        # Create solver instance for helper methods
        temp_solver = MultiStartAdaptive2opt()
        
        # Run algorithms
        start = time.time()
        nn_tour = nn_solve(points)
        nn_time = time.time() - start
        dist_matrix = temp_solver._calculate_distance_matrix(points)
        nn_length = temp_solver._tour_length(nn_tour, dist_matrix)
        
        start = time.time()
        two_opt_tour, two_opt_length = two_opt_solve(points)
        two_opt_time = time.time() - start
        
        start = time.time()
        adaptive_tour, adaptive_length = solve_tsp(points)
        adaptive_time = time.time() - start
        
        # Calculate improvements
        nn_improvement = (nn_length - adaptive_length) / nn_length * 100
        two_opt_improvement = (two_opt_length - adaptive_length) / two_opt_length * 100
        
        results.append({
            'n': n,
            'nn_length': nn_length,
            'two_opt_length': two_opt_length,
            'adaptive_length': adaptive_length,
            'nn_improvement_percent': nn_improvement,
            'two_opt_improvement_percent': two_opt_improvement,
            'nn_time': nn_time,
            'two_opt_time': two_opt_time,
            'adaptive_time': adaptive_time
        })
        
        print(f"n={n}:")
        print(f"  NN: {nn_length:.2f} ({nn_time:.3f}s)")
        print(f"  2-opt: {two_opt_length:.2f} ({two_opt_time:.3f}s)")
        print(f"  Adaptive 2-opt: {adaptive_length:.2f} ({adaptive_time:.3f}s)")
        print(f"  Improvement vs NN: {nn_improvement:.2f}%")
        print(f"  Improvement vs 2-opt: {two_opt_improvement:.2f}%")
        print()
    
    return results

if __name__ == "__main__":
    benchmark_adaptive_2opt()
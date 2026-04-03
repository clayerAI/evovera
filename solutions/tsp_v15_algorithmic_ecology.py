#!/usr/bin/env python3
"""
Algorithmic Ecology for TSP
Novel hybrid approach using multiple algorithms with a coordinator

Key Novelty: Creates an "ecosystem" of TSP algorithms that work together:
1. **Diversity Phase**: Multiple algorithms run in parallel to generate diverse solutions
2. **Analysis Phase**: Coordinator analyzes solution characteristics (compactness, cluster structure, etc.)
3. **Selection Phase**: Based on analysis, selects best algorithm or combination for refinement
4. **Refinement Phase**: Selected algorithm refines the best solution

This approach recognizes that different TSP instances have different structural properties
that make different algorithms more effective.

Author: Evo
Date: 2026-04-03
"""

import math
import random
import time
import concurrent.futures
from typing import List, Tuple, Dict, Set, Any
import heapq
import statistics

class TSPAlgorithmEcology:
    """
    Algorithmic Ecology for TSP - multiple algorithms with intelligent coordination.
    """
    
    def __init__(self, points: List[Tuple[float, float]], seed: int = 42):
        """
        Initialize with Euclidean points.
        
        Args:
            points: List of (x, y) coordinates
            seed: Random seed for reproducibility
        """
        self.points = points
        self.n = len(points)
        self.seed = seed
        random.seed(seed)
        
        # Precompute distance matrix
        self.dist_matrix = self._compute_distance_matrix()
        
        # Algorithm registry
        self.algorithms = {
            'nn': self._nearest_neighbor,
            'nn_2opt': self._nearest_neighbor_2opt,
            'christofides': self._christofides,
            'multi_start': self._multi_start_2opt,
            'greedy': self._greedy_tour
        }
        
        # Algorithm weights (learned from performance)
        self.algorithm_weights = {name: 1.0 for name in self.algorithms}
        
    def _compute_distance_matrix(self) -> List[List[float]]:
        """Compute Euclidean distance matrix."""
        n = self.n
        dist = [[0.0] * n for _ in range(n)]
        for i in range(n):
            xi, yi = self.points[i]
            for j in range(i + 1, n):
                xj, yj = self.points[j]
                d = math.sqrt((xi - xj) ** 2 + (yi - yj) ** 2)
                dist[i][j] = d
                dist[j][i] = d
        return dist
    
    def _nearest_neighbor(self, start: int = 0) -> List[int]:
        """Basic nearest neighbor algorithm."""
        n = self.n
        unvisited = set(range(n))
        tour = [start]
        unvisited.remove(start)
        
        current = start
        while unvisited:
            # Find nearest unvisited neighbor
            nearest = min(unvisited, key=lambda x: self.dist_matrix[current][x])
            tour.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        # Close the tour
        tour.append(start)
        return tour
    
    def _nearest_neighbor_2opt(self, start: int = 0) -> List[int]:
        """Nearest neighbor followed by 2-opt optimization."""
        tour = self._nearest_neighbor(start)
        return self._two_opt(tour)
    
    def _christofides(self, start: int = 0) -> List[int]:
        """Simplified Christofides algorithm (greedy matching)."""
        # Note: This is a simplified version for the ecology
        # Full Christofides would be more complex
        
        # For ecology purposes, we'll use a simplified approach
        # that captures the spirit of Christofides
        n = self.n
        
        # Build MST using Prim's
        visited = [False] * n
        min_edge = [float('inf')] * n
        min_edge[0] = 0
        parent = [-1] * n
        
        for _ in range(n):
            v = -1
            for j in range(n):
                if not visited[j] and (v == -1 or min_edge[j] < min_edge[v]):
                    v = j
            
            visited[v] = True
            
            for to in range(n):
                if not visited[to] and self.dist_matrix[v][to] < min_edge[to]:
                    min_edge[to] = self.dist_matrix[v][to]
                    parent[to] = v
        
        # Find odd degree vertices (simplified - all vertices in small MST)
        # For ecology, we'll just return a tour based on MST traversal
        tour = []
        stack = [0]
        visited = [False] * n
        
        while stack:
            v = stack.pop()
            if not visited[v]:
                visited[v] = True
                tour.append(v)
                # Add children to stack
                for to in range(n):
                    if parent[to] == v and not visited[to]:
                        stack.append(to)
        
        # Close tour
        tour.append(tour[0])
        return tour
    
    def _multi_start_2opt(self, n_starts: int = 10) -> List[int]:
        """Multi-start 2-opt with random initial tours."""
        best_tour = None
        best_length = float('inf')
        
        for _ in range(n_starts):
            # Create random tour
            tour = list(range(self.n))
            random.shuffle(tour)
            tour.append(tour[0])  # Close tour
            
            # Apply 2-opt
            tour = self._two_opt(tour)
            
            # Evaluate
            length = self._tour_length(tour)
            if length < best_length:
                best_length = length
                best_tour = tour
        
        return best_tour
    
    def _greedy_tour(self) -> List[int]:
        """Greedy tour construction (always add closest city)."""
        n = self.n
        # Start with shortest edge
        best_edge = (0, 1)
        best_dist = self.dist_matrix[0][1]
        
        for i in range(n):
            for j in range(i + 1, n):
                if self.dist_matrix[i][j] < best_dist:
                    best_dist = self.dist_matrix[i][j]
                    best_edge = (i, j)
        
        # Build tour from this edge
        tour = list(best_edge)
        unvisited = set(range(n)) - set(tour)
        
        while unvisited:
            # Find city closest to either end of the tour
            best_city = None
            best_gain = float('inf')
            insert_pos = -1  # 0 for start, 1 for end
            
            for city in unvisited:
                # Check insertion at start
                gain_start = self.dist_matrix[city][tour[0]] - self.dist_matrix[tour[0]][tour[1]]
                if gain_start < best_gain:
                    best_gain = gain_start
                    best_city = city
                    insert_pos = 0
                
                # Check insertion at end
                gain_end = self.dist_matrix[tour[-2]][city] - self.dist_matrix[tour[-2]][tour[-1]]
                if gain_end < best_gain:
                    best_gain = gain_end
                    best_city = city
                    insert_pos = 1
            
            if insert_pos == 0:
                tour.insert(0, best_city)
            else:
                tour.insert(-1, best_city)  # Insert before the closing city
            
            unvisited.remove(best_city)
        
        # Close tour
        if tour[0] != tour[-1]:
            tour.append(tour[0])
        
        return tour
    
    def _two_opt(self, tour: List[int], max_iterations: int = 100) -> List[int]:
        """Apply 2-opt local optimization to improve tour."""
        n = len(tour) - 1  # Excluding the closing vertex
        improved = True
        iterations = 0
        
        while improved and iterations < max_iterations:
            improved = False
            best_gain = 0
            best_i = -1
            best_j = -1
            
            for i in range(1, n - 1):
                for j in range(i + 1, n):
                    if j == i + 1:
                        continue
                    
                    # Current edges: (i-1, i) and (j, j+1)
                    # New edges: (i-1, j) and (i, j+1)
                    a, b, c, d = tour[i-1], tour[i], tour[j], tour[(j+1) % n]
                    
                    old_cost = (self.dist_matrix[a][b] + 
                               self.dist_matrix[c][d])
                    new_cost = (self.dist_matrix[a][c] + 
                               self.dist_matrix[b][d])
                    
                    gain = old_cost - new_cost
                    if gain > best_gain:
                        best_gain = gain
                        best_i = i
                        best_j = j
            
            if best_gain > 1e-9:
                # Reverse segment between i and j
                tour[best_i:best_j+1] = reversed(tour[best_i:best_j+1])
                improved = True
            
            iterations += 1
        
        return tour
    
    def _tour_length(self, tour: List[int]) -> float:
        """Calculate total tour length."""
        length = 0.0
        for i in range(len(tour) - 1):
            length += self.dist_matrix[tour[i]][tour[i+1]]
        return length
    
    def _analyze_solution(self, tour: List[int]) -> Dict[str, Any]:
        """
        Analyze solution characteristics.
        
        Returns metrics that help determine which algorithms work well.
        """
        n = self.n
        metrics = {}
        
        # 1. Tour compactness (ratio of tour length to bounding box perimeter)
        xs = [self.points[i][0] for i in tour[:-1]]
        ys = [self.points[i][1] for i in tour[:-1]]
        bbox_width = max(xs) - min(xs)
        bbox_height = max(ys) - min(ys)
        bbox_perimeter = 2 * (bbox_width + bbox_height)
        
        tour_length = self._tour_length(tour)
        metrics['compactness'] = tour_length / bbox_perimeter if bbox_perimeter > 0 else 1.0
        
        # 2. Edge length statistics
        edge_lengths = []
        for i in range(len(tour) - 1):
            edge_lengths.append(self.dist_matrix[tour[i]][tour[i+1]])
        
        metrics['edge_mean'] = statistics.mean(edge_lengths) if edge_lengths else 0
        metrics['edge_std'] = statistics.stdev(edge_lengths) if len(edge_lengths) > 1 else 0
        metrics['edge_cv'] = metrics['edge_std'] / metrics['edge_mean'] if metrics['edge_mean'] > 0 else 0
        
        # 3. Cluster detection (simplified)
        # Count how many edges are "short" vs "long"
        if edge_lengths:
            median_length = statistics.median(edge_lengths)
            short_edges = sum(1 for l in edge_lengths if l < median_length * 0.5)
            long_edges = sum(1 for l in edge_lengths if l > median_length * 1.5)
            metrics['clustering'] = short_edges / len(edge_lengths) if len(edge_lengths) > 0 else 0
        
        return metrics
    
    def _select_best_algorithm(self, solutions: Dict[str, List[int]], 
                              metrics: Dict[str, Dict[str, Any]]) -> str:
        """
        Select best algorithm based on solution analysis.
        
        Simple rule-based selection for now.
        Could be enhanced with machine learning.
        """
        # Calculate scores for each algorithm
        scores = {}
        
        for algo_name, tour in solutions.items():
            algo_metrics = metrics[algo_name]
            score = 0.0
            
            # Rule 1: Prefer more compact tours
            score += 1.0 / (algo_metrics['compactness'] + 0.1)
            
            # Rule 2: Prefer tours with lower edge length variation
            if algo_metrics['edge_cv'] > 0:
                score += 1.0 / algo_metrics['edge_cv']
            
            # Rule 3: Prefer tours that show clustering (for certain algorithms)
            if algo_name in ['christofides', 'multi_start']:
                score += algo_metrics.get('clustering', 0) * 2.0
            
            scores[algo_name] = score
        
        # Return algorithm with highest score
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def solve(self, use_parallel: bool = True) -> Tuple[List[int], float, Dict[str, Any]]:
        """
        Solve TSP using algorithmic ecology.
        
        Args:
            use_parallel: Whether to run algorithms in parallel
        
        Returns:
            tour: Best tour found
            tour_length: Tour length
            metadata: Information about the solution process
        """
        start_time = time.time()
        
        # Phase 1: Diversity - run all algorithms
        solutions = {}
        metrics = {}
        
        if use_parallel and len(self.algorithms) > 1:
            # Run algorithms in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.algorithms)) as executor:
                future_to_algo = {}
                for algo_name, algo_func in self.algorithms.items():
                    # Submit algorithm for execution
                    if algo_name == 'multi_start':
                        future = executor.submit(algo_func, 5)  # 5 starts
                    elif algo_name == 'nn' or algo_name == 'nn_2opt':
                        future = executor.submit(algo_func, 0)  # Start at city 0
                    else:
                        future = executor.submit(algo_func)
                    
                    future_to_algo[future] = algo_name
                
                # Collect results
                for future in concurrent.futures.as_completed(future_to_algo):
                    algo_name = future_to_algo[future]
                    try:
                        tour = future.result()
                        solutions[algo_name] = tour
                        metrics[algo_name] = self._analyze_solution(tour)
                    except Exception as e:
                        print(f"Algorithm {algo_name} failed: {e}")
                        # Use fallback
                        solutions[algo_name] = self._nearest_neighbor(0)
                        metrics[algo_name] = self._analyze_solution(solutions[algo_name])
        else:
            # Run algorithms sequentially
            for algo_name, algo_func in self.algorithms.items():
                try:
                    if algo_name == 'multi_start':
                        tour = algo_func(5)
                    elif algo_name == 'nn' or algo_name == 'nn_2opt':
                        tour = algo_func(0)
                    else:
                        tour = algo_func()
                    
                    solutions[algo_name] = tour
                    metrics[algo_name] = self._analyze_solution(tour)
                except Exception as e:
                    print(f"Algorithm {algo_name} failed: {e}")
                    # Use fallback
                    solutions[algo_name] = self._nearest_neighbor(0)
                    metrics[algo_name] = self._analyze_solution(solutions[algo_name])
        
        # Phase 2: Analysis & Selection
        best_algo = self._select_best_algorithm(solutions, metrics)
        
        # Phase 3: Refinement - use selected algorithm with more iterations
        best_tour = solutions[best_algo]
        
        # Apply additional 2-opt refinement
        refined_tour = self._two_opt(best_tour[:], max_iterations=200)
        
        # Calculate final tour length
        tour_length = self._tour_length(refined_tour)
        
        runtime = time.time() - start_time
        
        # Prepare metadata
        metadata = {
            'algorithms_used': list(solutions.keys()),
            'selected_algorithm': best_algo,
            'algorithm_metrics': metrics,
            'initial_tour_length': self._tour_length(best_tour),
            'refined_tour_length': tour_length,
            'improvement': self._tour_length(best_tour) - tour_length,
            'runtime': runtime
        }
        
        return refined_tour, tour_length, runtime, metadata
    
    def benchmark(self, n_trials: int = 5) -> Dict[str, Any]:
        """
        Benchmark the algorithmic ecology approach.
        
        Args:
            n_trials: Number of trials
        
        Returns:
            Benchmark results
        """
        results = {
            'algorithm': 'Algorithmic Ecology for TSP',
            'n_points': self.n,
            'trials': [],
            'algorithm_selection_stats': {},
            'performance_summary': {}
        }
        
        # Track which algorithms are selected
        selection_counts = {algo_name: 0 for algo_name in self.algorithms}
        
        for trial in range(n_trials):
            trial_start = time.time()
            
            # Run with different seed for each trial
            self.seed = 42 + trial
            random.seed(self.seed)
            
            # Solve
            tour, length, runtime, metadata = self.solve(use_parallel=True)
            
            # Record trial results
            trial_results = {
                'trial': trial,
                'tour_length': length,
                'runtime': runtime,
                'selected_algorithm': metadata['selected_algorithm'],
                'initial_length': metadata['initial_tour_length'],
                'improvement': metadata['improvement']
            }
            results['trials'].append(trial_results)
            
            # Update selection counts
            selection_counts[metadata['selected_algorithm']] += 1
        
        # Calculate statistics
        tour_lengths = [t['tour_length'] for t in results['trials']]
        runtimes = [t['runtime'] for t in results['trials']]
        
        results['performance_summary'] = {
            'avg_tour_length': sum(tour_lengths) / len(tour_lengths),
            'min_tour_length': min(tour_lengths),
            'max_tour_length': max(tour_lengths),
            'avg_runtime': sum(runtimes) / len(runtimes),
            'min_runtime': min(runtimes),
            'max_runtime': max(runtimes)
        }
        
        results['algorithm_selection_stats'] = selection_counts
        
        return results


def generate_random_points(n: int, seed: int = 42) -> List[Tuple[float, float]]:
    """Generate n random points in unit square."""
    random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]


def test_algorithm():
    """Test the algorithmic ecology approach."""
    print("Testing Algorithmic Ecology for TSP")
    print("=" * 70)
    
    # Generate test points
    n = 50
    points = generate_random_points(n, seed=42)
    
    # Create solver
    solver = TSPAlgorithmEcology(points, seed=42)
    
    # Run single solve
    print(f"Testing on n={n} random points")
    tour, length, runtime, metadata = solver.solve(use_parallel=True)
    
    print(f"\nSolution found:")
    print(f"  Tour length: {length:.4f}")
    print(f"  Runtime: {runtime:.4f}s")
    print(f"  Selected algorithm: {metadata['selected_algorithm']}")
    print(f"  Improvement from refinement: {metadata['improvement']:.4f}")
    
    print(f"\nAlgorithms used: {', '.join(metadata['algorithms_used'])}")
    
    # Run benchmark
    print("\nRunning benchmark (5 trials)...")
    results = solver.benchmark(n_trials=5)
    
    print(f"\nBenchmark Results:")
    print(f"  Average tour length: {results['performance_summary']['avg_tour_length']:.4f}")
    print(f"  Average runtime: {results['performance_summary']['avg_runtime']:.4f}s")
    
    print(f"\nAlgorithm selection statistics:")
    for algo, count in results['algorithm_selection_stats'].items():
        percentage = (count / 5) * 100
        print(f"  {algo}: {count} times ({percentage:.1f}%)")
    
    return results


if __name__ == "__main__":
    test_algorithm()
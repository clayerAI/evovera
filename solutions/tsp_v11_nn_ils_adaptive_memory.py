"""
TSP Hybrid Algorithm v11: NN+2opt with ILS Adaptive Memory

Novel hybrid approach: Start with high-quality NN+2opt solution, then apply
Iterated Local Search with adaptive memory that tracks effective perturbation
strengths and restart conditions.

Key novelties:
1. Starts with NN+2opt (better than Christofides for many instances)
2. Adaptive memory tracks which perturbation strengths work best
3. Dynamic restart based on improvement rate and stagnation detection
4. Quality-based perturbation adjustment

This addresses the weakness of Christofides-based hybrids while maintaining
the ILS improvement framework.
"""

import numpy as np
import random
import math
import time
from typing import List, Tuple, Dict, Optional
from collections import defaultdict

def euclidean_distance(p1: np.ndarray, p2: np.ndarray) -> float:
    """Calculate Euclidean distance between two points"""
    return np.sqrt(np.sum((p1 - p2) ** 2))

def nearest_neighbor_tsp(points: np.ndarray) -> List[int]:
    """Nearest neighbor algorithm for TSP"""
    n = len(points)
    unvisited = set(range(n))
    tour = [0]
    unvisited.remove(0)
    
    while unvisited:
        current = tour[-1]
        # Find nearest unvisited city
        nearest = min(unvisited, key=lambda city: euclidean_distance(points[current], points[city]))
        tour.append(nearest)
        unvisited.remove(nearest)
    
    return tour

def two_opt_improvement(tour: List[int], points: np.ndarray) -> Tuple[List[int], float]:
    """Apply 2-opt local search to improve tour"""
    n = len(tour)
    best_tour = tour.copy()
    best_length = tour_length(tour, points)
    improved = True
    
    while improved:
        improved = False
        for i in range(n - 1):
            for j in range(i + 2, n):
                # Calculate gain from swapping edges (i, i+1) and (j, j+1)
                a, b = best_tour[i], best_tour[(i + 1) % n]
                c, d = best_tour[j], best_tour[(j + 1) % n]
                
                current = (euclidean_distance(points[a], points[b]) + 
                          euclidean_distance(points[c], points[d]))
                new = (euclidean_distance(points[a], points[c]) + 
                      euclidean_distance(points[b], points[d]))
                
                if new < current:
                    # Reverse segment between i+1 and j
                    best_tour[i+1:j+1] = reversed(best_tour[i+1:j+1])
                    best_length = best_length - current + new
                    improved = True
                    break
            if improved:
                break
    
    return best_tour, best_length

def tour_length(tour: List[int], points: np.ndarray) -> float:
    """Calculate total length of tour"""
    total = 0.0
    n = len(tour)
    for i in range(n):
        j = (i + 1) % n
        total += euclidean_distance(points[tour[i]], points[tour[j]])
    return total

def double_bridge_kick(tour: List[int], strength: int = 4) -> List[int]:
    """Apply double-bridge perturbation (Lin-Kernighan style)"""
    n = len(tour)
    if n < 8:
        return tour.copy()
    
    # Choose 4 random cut points
    points = sorted(random.sample(range(1, n - 1), 4))
    a, b, c, d = points
    
    # Reorder segments: [0..a], [c..d], [b..c], [a..b]
    new_tour = tour[:a] + tour[c:d] + tour[b:c] + tour[a:b] + tour[d:]
    return new_tour

def adaptive_perturbation(tour: List[int], memory: Dict[int, float], 
                         current_quality: float, best_quality: float) -> Tuple[List[int], int]:
    """
    Apply perturbation with adaptive strength based on memory and quality
    
    Returns: (perturbed_tour, perturbation_strength_used)
    """
    # Calculate quality ratio (how close to best)
    quality_ratio = current_quality / best_quality if best_quality > 0 else 1.0
    
    # Base strength on quality: worse solutions get stronger perturbations
    if quality_ratio > 1.05:  # Far from best
        base_strength = random.choice([4, 5, 6])
    elif quality_ratio > 1.02:  # Moderately far
        base_strength = random.choice([3, 4, 5])
    else:  # Close to best
        base_strength = random.choice([2, 3, 4])
    
    # Adjust based on memory of effective strengths
    if memory:
        avg_effective = sum(memory.values()) / len(memory)
        # Bias toward strengths that have worked well
        if random.random() < 0.7:  # 70% chance to use memory-guided strength
            # Choose strength closest to average effective strength
            strengths = list(range(2, 7))
            strength = min(strengths, key=lambda s: abs(s - avg_effective))
        else:
            strength = base_strength
    else:
        strength = base_strength
    
    # Apply perturbation
    perturbed = double_bridge_kick(tour, strength)
    
    return perturbed, strength

class AdaptiveMemoryILS:
    """Iterated Local Search with adaptive memory"""
    
    def __init__(self, max_iterations: int = 1000, max_no_improve: int = 50):
        self.max_iterations = max_iterations
        self.max_no_improve = max_no_improve
        self.perturbation_memory = defaultdict(list)  # strength -> list of improvement ratios
        self.restart_memory = []  # Track when restarts were beneficial
        
    def solve(self, initial_tour: List[int], points: np.ndarray) -> Tuple[List[int], float, Dict]:
        """Run adaptive memory ILS"""
        # Start with 2-opt improvement
        current_tour, current_length = two_opt_improvement(initial_tour, points)
        best_tour = current_tour.copy()
        best_length = current_length
        initial_length = current_length  # Store initial length for stats
        
        stats = {
            'iterations': 0,
            'improvements': 0,
            'perturbations_applied': 0,
            'restarts': 0,
            'final_improvement': 0.0,
            'perturbation_strengths_used': [],
            'improvement_history': []
        }
        
        no_improve_count = 0
        iteration = 0
        
        while iteration < self.max_iterations and no_improve_count < self.max_no_improve:
            iteration += 1
            
            # Apply adaptive perturbation
            perturbed_tour, strength = adaptive_perturbation(
                current_tour, 
                {k: np.mean(v) for k, v in self.perturbation_memory.items() if v},
                current_length,
                best_length
            )
            
            # Local search on perturbed tour
            improved_tour, improved_length = two_opt_improvement(perturbed_tour, points)
            
            # Calculate improvement ratio
            improvement_ratio = (current_length - improved_length) / current_length if current_length > 0 else 0
            
            # Update memory if improvement occurred
            if improved_length < current_length:
                self.perturbation_memory[strength].append(improvement_ratio)
                # Keep only recent memory (last 10 entries per strength)
                if len(self.perturbation_memory[strength]) > 10:
                    self.perturbation_memory[strength] = self.perturbation_memory[strength][-10:]
            
            # Acceptance criterion: always accept improving moves
            if improved_length < current_length:
                current_tour = improved_tour
                current_length = improved_length
                no_improve_count = 0
                stats['improvements'] += 1
                
                # Update best solution
                if improved_length < best_length:
                    best_tour = improved_tour.copy()
                    best_length = improved_length
                    stats['final_improvement'] = (initial_length - best_length) / initial_length
            else:
                no_improve_count += 1
                # With small probability, accept worse solution to escape local optima
                if random.random() < 0.1:
                    current_tour = improved_tour
                    current_length = improved_length
            
            stats['perturbations_applied'] += 1
            stats['perturbation_strengths_used'].append(strength)
            stats['improvement_history'].append(improvement_ratio)
            
            # Adaptive restart if stuck
            if no_improve_count > self.max_no_improve // 2:
                # Restart from best solution with strong perturbation
                current_tour = double_bridge_kick(best_tour, strength=6)
                current_tour, current_length = two_opt_improvement(current_tour, points)
                no_improve_count = 0
                stats['restarts'] += 1
                self.restart_memory.append(iteration)
        
        stats['iterations'] = iteration
        
        return best_tour, best_length, stats

def solve_tsp_nn_ils_adaptive_memory(points: np.ndarray, 
                                     max_iterations: int = 1000,
                                     max_no_improve: int = 50) -> Tuple[List[int], float, Dict]:
    """
    Solve TSP using NN+2opt with ILS adaptive memory
    
    Args:
        points: numpy array of shape (n, 2) with coordinates
        max_iterations: maximum ILS iterations
        max_no_improve: maximum iterations without improvement before stopping
    
    Returns:
        tour: list of city indices
        length: total tour length
        stats: dictionary with algorithm statistics
    """
    # Start with NN tour
    nn_tour = nearest_neighbor_tsp(points)
    initial_tour, initial_length = two_opt_improvement(nn_tour, points)
    
    # Run adaptive memory ILS
    solver = AdaptiveMemoryILS(max_iterations=max_iterations, max_no_improve=max_no_improve)
    best_tour, best_length, stats = solver.solve(initial_tour, points)
    
    # Final 2-opt polish
    final_tour, final_length = two_opt_improvement(best_tour, points)
    
    # Update stats
    stats['initial_length'] = initial_length
    stats['final_length'] = final_length
    stats['overall_improvement'] = (initial_length - final_length) / initial_length
    
    return final_tour, final_length, stats


def solve_tsp(points: np.ndarray, max_iterations: int = 1000, max_no_improve: int = 50) -> Tuple[List[int], float]:
    """
    Standard interface function for TSP algorithms.
    
    Args:
        points: numpy array of shape (n, 2) with coordinates
        max_iterations: maximum ILS iterations
        max_no_improve: maximum iterations without improvement before stopping
    
    Returns:
        Tuple of (tour, length) where tour is list of node indices
    """
    tour, length, stats = solve_tsp_nn_ils_adaptive_memory(points, max_iterations, max_no_improve)
    
    # Convert closed tour to open tour (remove duplicate start city)
    if len(tour) > 0 and tour[0] == tour[-1]:
        tour = tour[:-1]
    
    return tour, length

# Example usage and testing
if __name__ == "__main__":
    # Generate random test instance
    np.random.seed(42)
    n = 50
    points = np.random.rand(n, 2) * 100
    
    print(f"Testing NN+2opt with ILS Adaptive Memory on {n} cities")
    print("=" * 60)
    
    start_time = time.time()
    tour, length, stats = solve_tsp_nn_ils_adaptive_memory(points, max_iterations=500)
    end_time = time.time()
    
    print(f"Tour length: {length:.4f}")
    print(f"Initial length: {stats['initial_length']:.4f}")
    print(f"Overall improvement: {stats['overall_improvement']*100:.2f}%")
    print(f"Computation time: {end_time - start_time:.3f}s")
    print(f"Iterations: {stats['iterations']}")
    print(f"Improvements: {stats['improvements']}")
    print(f"Restarts: {stats['restarts']}")
    
    # Compare with simple NN+2opt
    nn_tour = nearest_neighbor_tsp(points)
    nn_2opt_tour, nn_2opt_length = two_opt_improvement(nn_tour, points)
    print(f"\nNN+2opt baseline: {nn_2opt_length:.4f}")
    print(f"Improvement over baseline: {(nn_2opt_length - length)/nn_2opt_length*100:.2f}%")
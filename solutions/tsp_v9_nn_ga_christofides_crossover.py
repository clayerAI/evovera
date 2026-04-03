"""
TSP V9: NN-GA with Christofides-Inspired Crossover Hybrid
A novel hybrid algorithm combining:
1. Nearest Neighbor (NN) for initial population generation
2. Genetic Algorithm (GA) with Christofides-inspired crossover operator
3. 2-opt local search for mutation improvement

Novelty: Using Christofides' Eulerian circuit construction as a crossover operator
in a genetic algorithm framework. This combines constructive heuristic principles
with evolutionary search in a way not found in literature.
"""

import random
import math
import time
from typing import List, Tuple, Dict, Set
import numpy as np

def distance_matrix(coords: List[Tuple[float, float]]) -> np.ndarray:
    """Compute Euclidean distance matrix."""
    n = len(coords)
    dist = np.zeros((n, n))
    for i in range(n):
        for j in range(i+1, n):
            dx = coords[i][0] - coords[j][0]
            dy = coords[i][1] - coords[j][1]
            d = math.sqrt(dx*dx + dy*dy)
            dist[i][j] = d
            dist[j][i] = d
    return dist

def nearest_neighbor_tour(dist: np.ndarray, start: int = 0) -> List[int]:
    """Generate tour using nearest neighbor heuristic."""
    n = dist.shape[0]
    unvisited = set(range(n))
    tour = [start]
    unvisited.remove(start)
    
    current = start
    while unvisited:
        # Find nearest unvisited city
        nearest = min(unvisited, key=lambda city: dist[current][city])
        tour.append(nearest)
        unvisited.remove(nearest)
        current = nearest
    
    return tour

def tour_length(tour: List[int], dist: np.ndarray) -> float:
    """Calculate total tour length."""
    total = 0.0
    n = len(tour)
    for i in range(n):
        j = (i + 1) % n
        total += dist[tour[i]][tour[j]]
    return total

def two_opt_improvement(tour: List[int], dist: np.ndarray, max_iterations: int = 1000) -> List[int]:
    """Apply 2-opt local search to improve tour."""
    n = len(tour)
    improved = True
    iterations = 0
    
    while improved and iterations < max_iterations:
        improved = False
        for i in range(n):
            for j in range(i+2, n):
                if j == n-1 and i == 0:
                    continue  # Skip same edge
                
                # Current edges: (i,i+1) and (j,j+1)
                a, b = tour[i], tour[(i+1)%n]
                c, d = tour[j], tour[(j+1)%n]
                
                # Calculate gain
                current = dist[a][b] + dist[c][d]
                new = dist[a][c] + dist[b][d]
                
                if new < current:
                    # Reverse segment between i+1 and j
                    if j > i:
                        tour[i+1:j+1] = reversed(tour[i+1:j+1])
                    else:
                        # Handle wrap-around case
                        segment = tour[i+1:] + tour[:j+1]
                        segment.reverse()
                        tour[i+1:] = segment[:n-i-1]
                        tour[:j+1] = segment[n-i-1:]
                    
                    improved = True
                    iterations += 1
                    break
            if improved:
                break
    
    return tour

def christofides_inspired_crossover(parent1: List[int], parent2: List[int], dist: np.ndarray) -> List[int]:
    """
    Christofides-inspired crossover operator.
    
    Novel approach: Construct a "minimum spanning tree" from parent edges,
    find odd-degree vertices, and perform a "matching" between them
    using edges from the other parent.
    
    This mimics Christofides' algorithm but uses genetic material from parents.
    """
    n = len(parent1)
    
    # Step 1: Build edge frequency map from parents
    edge_freq = {}
    for i in range(n):
        # Parent 1 edges
        a1, b1 = parent1[i], parent1[(i+1)%n]
        edge = tuple(sorted((a1, b1)))
        edge_freq[edge] = edge_freq.get(edge, 0) + 1
        
        # Parent 2 edges
        a2, b2 = parent2[i], parent2[(i+1)%n]
        edge = tuple(sorted((a2, b2)))
        edge_freq[edge] = edge_freq.get(edge, 0) + 1
    
    # Step 2: Create "MST" using edges with highest frequency (shared edges)
    # This favors edges that appear in both parents
    shared_edges = [edge for edge, freq in edge_freq.items() if freq == 2]
    random_edges = [edge for edge, freq in edge_freq.items() if freq == 1]
    
    # Build graph from shared edges first, then random edges if needed
    mst_edges = shared_edges.copy()
    
    # Add random edges until we have n-1 edges (for a tree)
    while len(mst_edges) < n-1 and random_edges:
        mst_edges.append(random_edges.pop())
    
    # Step 3: Find odd-degree vertices in the multigraph
    degree = [0] * n
    for (u, v) in mst_edges:
        degree[u] += 1
        degree[v] += 1
    
    odd_vertices = [i for i in range(n) if degree[i] % 2 == 1]
    
    # Step 4: "Match" odd vertices using edges from the other parent
    # For simplicity, we'll use a greedy matching using edges from parent2
    matched = set()
    matching_edges = []
    
    for u in odd_vertices:
        if u in matched:
            continue
        
        # Find the edge from parent2 that connects u to another odd vertex
        best_v = None
        best_dist = float('inf')
        
        # Look for u's neighbors in parent2
        idx = parent2.index(u)
        neighbors = [parent2[(idx-1)%n], parent2[(idx+1)%n]]
        
        for v in neighbors:
            if v in odd_vertices and v not in matched:
                if dist[u][v] < best_dist:
                    best_dist = dist[u][v]
                    best_v = v
        
        if best_v is not None:
            matching_edges.append((u, best_v))
            matched.add(u)
            matched.add(best_v)
    
    # Step 5: Combine MST and matching to create Eulerian multigraph
    all_edges = mst_edges + [(min(u,v), max(u,v)) for (u,v) in matching_edges]
    
    # Step 6: Find Eulerian tour (simplified - we'll just connect components)
    # Build adjacency list
    adj = [[] for _ in range(n)]
    for (u, v) in all_edges:
        adj[u].append(v)
        adj[v].append(u)
    
    # Find a Hamiltonian cycle by skipping duplicates (simplified Christofides)
    visited = [False] * n
    tour = []
    
    def dfs(node: int):
        visited[node] = True
        tour.append(node)
        for neighbor in adj[node]:
            if not visited[neighbor]:
                dfs(neighbor)
    
    dfs(0)
    
    # Add return to start if not already Hamiltonian
    if len(tour) < n:
        # Add missing vertices at end
        for i in range(n):
            if not visited[i]:
                tour.append(i)
    
    return tour

def initialize_population(dist: np.ndarray, population_size: int = 50) -> List[List[int]]:
    """Initialize population with NN tours from different starting points."""
    n = dist.shape[0]
    population = []
    
    # Add NN tours from different starting cities
    for start in range(min(population_size, n)):
        tour = nearest_neighbor_tour(dist, start)
        population.append(tour)
    
    # Add random tours if needed
    while len(population) < population_size:
        tour = list(range(n))
        random.shuffle(tour)
        population.append(tour)
    
    return population

def select_parents(population: List[List[int]], dist: np.ndarray, tournament_size: int = 3) -> Tuple[List[int], List[int]]:
    """Select parents using tournament selection."""
    # Tournament selection
    def tournament():
        contestants = random.sample(range(len(population)), tournament_size)
        best_idx = min(contestants, key=lambda idx: tour_length(population[idx], dist))
        return population[best_idx]
    
    return tournament(), tournament()

def mutate(tour: List[int], mutation_rate: float = 0.1) -> List[int]:
    """Apply mutation (swap two random cities)."""
    if random.random() < mutation_rate:
        n = len(tour)
        i, j = random.sample(range(n), 2)
        tour[i], tour[j] = tour[j], tour[i]
    return tour

def nn_ga_christofides_crossover_hybrid(coords: List[Tuple[float, float]], 
                                        generations: int = 100,
                                        population_size: int = 50,
                                        crossover_rate: float = 0.8,
                                        mutation_rate: float = 0.1,
                                        elitism: int = 2) -> List[int]:
    """
    NN-GA with Christofides-Inspired Crossover Hybrid Algorithm.
    
    Args:
        coords: List of (x, y) coordinates
        generations: Number of GA generations
        population_size: Size of population
        crossover_rate: Probability of crossover
        mutation_rate: Probability of mutation
        elitism: Number of best individuals to preserve
    
    Returns:
        Best tour found
    """
    dist = distance_matrix(coords)
    n = dist.shape[0]
    
    # Initialize population with NN tours
    population = initialize_population(dist, population_size)
    
    # Evaluate initial population
    fitness = [tour_length(tour, dist) for tour in population]
    
    best_tour = min(population, key=lambda t: tour_length(t, dist))
    best_length = tour_length(best_tour, dist)
    
    print(f"Initial best tour length: {best_length:.4f}")
    
    for gen in range(generations):
        new_population = []
        
        # Elitism: keep best individuals
        sorted_indices = sorted(range(len(population)), key=lambda i: fitness[i])
        for i in range(elitism):
            new_population.append(population[sorted_indices[i]])
        
        # Generate offspring
        while len(new_population) < population_size:
            parent1, parent2 = select_parents(population, dist)
            
            if random.random() < crossover_rate:
                # Use Christofides-inspired crossover
                child = christofides_inspired_crossover(parent1, parent2, dist)
            else:
                # Randomly select parent
                child = parent1.copy() if random.random() < 0.5 else parent2.copy()
            
            # Apply mutation
            child = mutate(child, mutation_rate)
            
            # Apply local search (2-opt) with probability
            if random.random() < 0.3:  # 30% chance of local search
                child = two_opt_improvement(child, dist, max_iterations=100)
            
            new_population.append(child)
        
        # Update population
        population = new_population
        fitness = [tour_length(tour, dist) for tour in population]
        
        # Update best solution
        current_best_idx = min(range(len(population)), key=lambda i: fitness[i])
        current_best_length = fitness[current_best_idx]
        
        if current_best_length < best_length:
            best_length = current_best_length
            best_tour = population[current_best_idx].copy()
        
        # Print progress every 10 generations
        if (gen + 1) % 10 == 0:
            avg_fitness = sum(fitness) / len(fitness)
            print(f"Generation {gen+1}: Best={best_length:.4f}, Avg={avg_fitness:.4f}")
    
    # Final improvement with 2-opt
    best_tour = two_opt_improvement(best_tour, dist, max_iterations=2000)
    final_length = tour_length(best_tour, dist)
    
    print(f"Final tour length: {final_length:.4f}")
    print(f"Improvement from initial: {(best_length - final_length)/best_length*100:.2f}%")
    
    return best_tour

def test_algorithm():
    """Test the algorithm on a small instance."""
    # Create a small test instance
    n = 20
    coords = [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(n)]
    
    print("Testing NN-GA with Christofides-Inspired Crossover Hybrid")
    print(f"Instance size: {n}")
    
    start_time = time.time()
    tour = nn_ga_christofides_crossover_hybrid(
        coords, 
        generations=50,
        population_size=30,
        crossover_rate=0.8,
        mutation_rate=0.1,
        elitism=2
    )
    end_time = time.time()
    
    dist = distance_matrix(coords)
    length = tour_length(tour, dist)
    
    print(f"\nResults:")
    print(f"Tour length: {length:.4f}")
    print(f"Runtime: {end_time - start_time:.2f} seconds")
    print(f"Tour: {tour}")
    
    return tour, length, end_time - start_time

if __name__ == "__main__":
    test_algorithm()
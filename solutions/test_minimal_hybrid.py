import numpy as np
import random
import time

np.random.seed(42)
random.seed(42)

# Small test case
n = 10
points = np.random.rand(n, 2) * 100

def euclidean_distance(p1, p2):
    return np.linalg.norm(p1 - p2)

def create_distance_matrix(points):
    n = len(points)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            dist = euclidean_distance(points[i], points[j])
            dist_matrix[i, j] = dist
            dist_matrix[j, i] = dist
    return dist_matrix

dist_matrix = create_distance_matrix(points)

# Import functions from the hybrid algorithm
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Actually, let me just copy the essential functions here
def nearest_neighbor_tour(dist_matrix, start_node=0):
    n = len(dist_matrix)
    unvisited = set(range(n))
    tour = [start_node]
    unvisited.remove(start_node)
    
    current = start_node
    while unvisited:
        nearest = min(unvisited, key=lambda node: dist_matrix[current][node])
        tour.append(nearest)
        unvisited.remove(nearest)
        current = nearest
    
    return tour

def tour_length(tour, dist_matrix):
    total = 0.0
    n = len(tour)
    for i in range(n):
        j = (i + 1) % n
        total += dist_matrix[tour[i]][tour[j]]
    return total

def validate_tour(tour, n):
    if len(tour) != n:
        return False
    if set(tour) != set(range(n)):
        return False
    if len(tour) != len(set(tour)):
        return False
    return True

# Test basic functionality
print("Testing basic functionality...")
tour = nearest_neighbor_tour(dist_matrix)
length = tour_length(tour, dist_matrix)
print(f"NN tour: {tour}")
print(f"NN length: {length}")
print(f"Tour valid: {validate_tour(tour, n)}")

# Test strategic_perturbation
def strategic_perturbation(tour, strength, dist_matrix):
    n = len(tour)
    perturbed = tour[:]
    
    if strength == 1:
        idx1, idx2 = random.sample(range(n), 2)
        perturbed[idx1], perturbed[idx2] = perturbed[idx2], perturbed[idx1]
    
    elif strength == 2:
        i = random.randint(0, n - 2)
        j = random.randint(i + 1, n - 1)
        perturbed[i:j+1] = perturbed[i:j+1][::-1]
    
    else:  # strength >= 3
        i = random.randint(0, n - 2)
        j = random.randint(i + 1, n - 1)
        segment = perturbed[i:j+1]
        remaining = perturbed[:i] + perturbed[j+1:]
        insert_pos = random.randint(0, len(remaining))
        perturbed = remaining[:insert_pos] + segment + remaining[insert_pos:]
    
    if not validate_tour(perturbed, n):
        perturbed = tour[:]
    
    return perturbed

print("\nTesting perturbations...")
for strength in [1, 2, 3]:
    perturbed = strategic_perturbation(tour, strength, dist_matrix)
    perturbed_length = tour_length(perturbed, dist_matrix)
    print(f"Strength {strength}: {perturbed}, length: {perturbed_length}, valid: {validate_tour(perturbed, n)}")

# Now let's trace through the adaptive_restart_ils_hybrid function step by step
print("\nTracing adaptive_restart_ils_hybrid...")

# Simplified version
def simple_hybrid(dist_matrix, max_iterations=5):
    n = len(dist_matrix)
    
    # Initial solution
    best_tour = nearest_neighbor_tour(dist_matrix)
    best_length = tour_length(best_tour, dist_matrix)
    
    current_tour = best_tour[:]
    current_length = best_length
    
    for iteration in range(max_iterations):
        print(f"\nIteration {iteration}:")
        print(f"  Current tour: {current_tour}")
        print(f"  Current length: {current_length}")
        print(f"  Best length: {best_length}")
        
        # Apply perturbation
        current_tour = strategic_perturbation(current_tour, 1, dist_matrix)
        current_length = tour_length(current_tour, dist_matrix)
        
        print(f"  After perturbation: length={current_length}")
        
        # Simple improvement: try a few random swaps
        for _ in range(10):
            i, j = random.sample(range(n), 2)
            if i > j:
                i, j = j, i
            
            # Calculate gain
            a1, a2 = current_tour[i], current_tour[(i + 1) % n]
            b1, b2 = current_tour[j], current_tour[(j + 1) % n]
            
            old_segment = dist_matrix[a1][a2] + dist_matrix[b1][b2]
            new_segment = dist_matrix[a1][b1] + dist_matrix[a2][b2]
            
            if new_segment < old_segment:
                # Perform swap
                current_tour = current_tour[:i+1] + current_tour[i+1:j+1][::-1] + current_tour[j+1:]
                current_length = current_length - old_segment + new_segment
                print(f"    Improvement found: new length={current_length}")
        
        # Update best
        if current_length < best_length:
            best_tour, best_length = current_tour[:], current_length
            print(f"  New best: {best_length}")
    
    return best_tour, best_length

best_tour, best_length = simple_hybrid(dist_matrix, max_iterations=3)
print(f"\nFinal best tour: {best_tour}")
print(f"Final best length: {best_length}")
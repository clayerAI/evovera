import numpy as np
import random
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test with the exact same parameters as benchmark
np.random.seed(42)
random.seed(42)

n = 50
points = np.random.rand(n, 2) * 100

print(f"Testing with n={n} (same as benchmark)")

# Import and run the actual adaptive_restart_ils_hybrid function
from tsp_v4_nn_ils_hybrid import adaptive_restart_ils_hybrid, create_distance_matrix

dist_matrix = create_distance_matrix(points)

# Run with same parameters as benchmark
max_iterations = min(200, max(50, n // 5))  # This is what solve_tsp uses
print(f"max_iterations: {max_iterations}")

# Let's trace through the algorithm step by step
print("\nTracing adaptive_restart_ils_hybrid...")

# Copy the function here with added prints
def debug_adaptive_restart_ils_hybrid(dist_matrix, max_iterations=100):
    n = len(dist_matrix)
    
    # Import needed functions
    from tsp_v4_nn_ils_hybrid import nearest_neighbor_tour, tour_length, two_opt_improvement, strategic_perturbation, validate_tour
    
    stats = {
        'restarts': 0,
        'perturbation_strength_changes': 0,
        'total_iterations': 0,
        'improvement_history': []
    }
    
    # Initial solution using Nearest Neighbor
    best_tour = nearest_neighbor_tour(dist_matrix, start_node=random.randint(0, n-1))
    best_length = tour_length(best_tour, dist_matrix)
    
    print(f"Initial NN tour length: {best_length}")
    
    current_tour = best_tour[:]
    current_length = best_length
    
    perturbation_strength = 2
    no_improvement_count = 0
    improvement_history = []
    
    for iteration in range(max_iterations):
        stats['total_iterations'] += 1
        
        if iteration % 10 == 0:
            print(f"Iteration {iteration}: current_length={current_length}, best_length={best_length}")
        
        # Local search improvement
        improved_tour, improved_length = two_opt_improvement(current_tour, dist_matrix, max_iterations=500)
        
        # Check for improvement
        if improved_length < current_length:
            improvement = current_length - improved_length
            improvement_history.append(improvement)
            current_tour, current_length = improved_tour, improved_length
            
            # Update best solution
            if current_length < best_length:
                best_tour, best_length = current_tour[:], current_length
                no_improvement_count = 0
                
                # Adjust perturbation strength based on quality
                relative_quality = best_length / (n * np.mean(dist_matrix))
                if relative_quality < 0.8:
                    perturbation_strength = max(1, perturbation_strength - 1)
                    stats['perturbation_strength_changes'] += 1
            else:
                no_improvement_count += 1
        else:
            no_improvement_count += 1
        
        # Check for stagnation
        if len(improvement_history) >= 5:  # stagnation_window
            recent_improvements = improvement_history[-5:]
            avg_improvement = np.mean(recent_improvements) if recent_improvements else 0
            
            if avg_improvement < 0.0005 * best_length:  # stagnation_threshold
                # Adaptive restart
                current_tour = nearest_neighbor_tour(dist_matrix, start_node=random.randint(0, n-1))
                current_length = tour_length(current_tour, dist_matrix)
                stats['restarts'] += 1
                no_improvement_count = 0
                improvement_history = []
                
                # Reset perturbation strength
                perturbation_strength = 2
                stats['perturbation_strength_changes'] += 1
        
        # Apply strategic perturbation
        current_tour = strategic_perturbation(current_tour, perturbation_strength, dist_matrix)
        
        # Validate tour after perturbation
        if not validate_tour(current_tour, n):
            print(f"Warning: Invalid tour after perturbation at iteration {iteration}")
            # Reset to best tour
            current_tour = best_tour[:]
        
        current_length = tour_length(current_tour, dist_matrix)
        
        # Check for NaN or infinity
        if not np.isfinite(current_length):
            print(f"ERROR: Non-finite length at iteration {iteration}: {current_length}")
            break
    
    stats['improvement_history'] = improvement_history
    return best_tour, best_length, stats

# Run debug version
tour, length, stats = debug_adaptive_restart_ils_hybrid(dist_matrix, max_iterations=50)  # Full 50 iterations
print(f"\nFinal result:")
print(f"Tour length: {length}")
print(f"Stats: {stats}")

# Check if this matches benchmark
print(f"\nBenchmark reported: -21050.450746314353")
print(f"Our result: {length}")
print(f"Difference: {abs(length - (-21050.450746314353))}")
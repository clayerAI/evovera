#!/usr/bin/env python3
"""
Comprehensive test of greedy matching variance in Christofides algorithm.
"""

import sys
sys.path.append('.')
from solutions.tsp_v2_christofides import EuclideanTSPChristofides
import numpy as np
import random
import time

def test_matching_variance_multiple_seeds():
    """Test matching variance across multiple random seeds."""
    
    results = []
    
    for seed in range(10):
        print(f"\n=== Seed {seed} ===")
        
        # Create instance
        tsp = EuclideanTSPChristofides(n=100, seed=seed)
        
        # Get MST and odd vertices
        mst_edges = tsp.prim_mst()
        odd_vertices = tsp.find_odd_degree_vertices(mst_edges)
        
        # Original matching
        matching_original = tsp.greedy_minimum_matching(odd_vertices)
        dist_original = sum(weight for u, v, weight in matching_original)
        
        # Test multiple random shuffles
        shuffle_distances = []
        for shuffle_seed in range(5):
            rng = random.Random(int(shuffle_seed * 1000 + seed))
            odd_shuffled = odd_vertices.copy()
            rng.shuffle(odd_shuffled)
            
            # Re-implement greedy matching with shuffled order
            matched = [False] * tsp.n
            matching_shuffled = []
            odd_list = odd_shuffled.copy()
            
            while odd_list:
                u = odd_list.pop(0)
                if matched[u]:
                    continue
                
                best_v = None
                best_dist = float('inf')
                
                for v in odd_list:
                    if not matched[v]:
                        dist = tsp.distance(u, v)
                        if dist < best_dist:
                            best_dist = dist
                            best_v = v
                
                if best_v is not None:
                    matching_shuffled.append((u, best_v, best_dist))
                    matched[u] = True
                    matched[best_v] = True
                    odd_list.remove(best_v)
            
            dist_shuffled = sum(weight for u, v, weight in matching_shuffled)
            shuffle_distances.append(dist_shuffled)
        
        # Calculate statistics
        avg_shuffled = np.mean(shuffle_distances)
        std_shuffled = np.std(shuffle_distances)
        min_shuffled = min(shuffle_distances)
        max_shuffled = max(shuffle_distances)
        
        print(f"Original matching distance: {dist_original:.4f}")
        print(f"Shuffled distances: {[f'{d:.4f}' for d in shuffle_distances]}")
        print(f"  Average: {avg_shuffled:.4f}")
        print(f"  Std dev: {std_shuffled:.4f}")
        print(f"  Range: {min_shuffled:.4f} - {max_shuffled:.4f}")
        print(f"  Variance from original: {(max_shuffled - min_shuffled)/dist_original*100:.2f}%")
        
        # Run full Christofides with original and best shuffle
        tour_original, dist_ch_original = tsp.christofides(apply_two_opt=True)
        
        # Find best shuffle index and recreate that shuffle
        best_shuffle_idx = int(np.argmin(shuffle_distances))
        # Recreate the random state for this specific shuffle
        rng = random.Random(best_shuffle_idx * 1000 + seed)
        odd_best = odd_vertices.copy()
        rng.shuffle(odd_best)
        
        # Create modified class with specific ordering
        class CustomChristofides(EuclideanTSPChristofides):
            def __init__(self, n, seed, odd_order):
                super().__init__(n, seed)
                self.odd_order = odd_order
            
            def greedy_minimum_matching(self, odd_vertices):
                """Greedy matching with custom ordering."""
                if not odd_vertices:
                    return []
                
                # Use the pre-defined order
                odd_sorted = sorted(odd_vertices, 
                                  key=lambda v: self.odd_order.index(v) if v in self.odd_order else len(self.odd_order))
                
                matched = [False] * self.n
                matching_edges = []
                odd_list = odd_sorted.copy()
                
                while odd_list:
                    u = odd_list.pop(0)
                    if matched[u]:
                        continue
                    
                    best_v = None
                    best_dist = float('inf')
                    
                    for v in odd_list:
                        if not matched[v]:
                            dist = self.distance(u, v)
                            if dist < best_dist:
                                best_dist = dist
                                best_v = v
                    
                    if best_v is not None:
                        matching_edges.append((u, best_v, best_dist))
                        matched[u] = True
                        matched[best_v] = True
                        odd_list.remove(best_v)
                
                return matching_edges
        
        # Test with best ordering
        tsp_best = CustomChristofides(n=100, seed=seed, odd_order=odd_best)
        tour_best, dist_ch_best = tsp_best.christofides(apply_two_opt=True)
        
        print(f"Christofides original: {dist_ch_original:.4f}")
        print(f"Christofides best shuffle: {dist_ch_best:.4f}")
        print(f"Improvement: {(dist_ch_original - dist_ch_best)/dist_ch_original*100:.2f}%")
        
        results.append({
            "seed": seed,
            "original_matching_distance": dist_original,
            "shuffle_distances": shuffle_distances,
            "shuffle_avg": avg_shuffled,
            "shuffle_std": std_shuffled,
            "shuffle_range": max_shuffled - min_shuffled,
            "christofides_original": dist_ch_original,
            "christofides_best_shuffle": dist_ch_best,
            "improvement_percent": (dist_ch_original - dist_ch_best)/dist_ch_original*100
        })
    
    # Calculate overall statistics
    print(f"\n{'='*60}")
    print("OVERALL STATISTICS:")
    
    improvements = [r["improvement_percent"] for r in results]
    variances = [r["shuffle_range"]/r["original_matching_distance"]*100 for r in results]
    
    print(f"Matching distance variance across shuffles:")
    print(f"  Average variance: {np.mean(variances):.2f}%")
    print(f"  Max variance: {max(variances):.2f}%")
    print(f"  Min variance: {min(variances):.2f}%")
    
    print(f"\nChristofides tour improvement with best shuffle:")
    print(f"  Average improvement: {np.mean(improvements):.2f}%")
    print(f"  Max improvement: {max(improvements):.2f}%")
    print(f"  Min improvement: {min(improvements):.2f}%")
    
    # Check if Christofides is consistently worse than Nearest Neighbor
    print(f"\n{'='*60}")
    print("COMPARISON WITH NEAREST NEIGHBOR:")
    
    from solutions.tsp_v1_nearest_neighbor import EuclideanTSP
    
    for seed in range(3):
        tsp_nn = EuclideanTSP(n=100, seed=seed)
        tsp_ch = EuclideanTSPChristofides(n=100, seed=seed)
        
        tour_nn, dist_nn = tsp_nn.nearest_neighbor_with_2opt()
        tour_ch, dist_ch = tsp_ch.christofides(apply_two_opt=True)
        
        print(f"Seed {seed}: NN={dist_nn:.4f}, Christofides={dist_ch:.4f}, ", end="")
        if dist_ch > dist_nn:
            print(f"Christofides WORSE by {(dist_ch - dist_nn)/dist_nn*100:.2f}%")
        else:
            print(f"Christofides BETTER by {(dist_nn - dist_ch)/dist_nn*100:.2f}%")
    
    return results

if __name__ == "__main__":
    results = test_matching_variance_multiple_seeds()
    
    # Save results
    import json
    with open("matching_variance_comprehensive.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nResults saved to matching_variance_comprehensive.json")
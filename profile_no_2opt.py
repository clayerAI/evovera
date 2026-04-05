import cProfile
import pstats
from solutions.tsp_v19_optimized_fixed_v6 import ChristofidesHybridStructuralOptimized
import numpy as np

class ChristofidesNo2Opt(ChristofidesHybridStructuralOptimized):
    def solve(self):
        # Override to skip 2-opt
        import time
        start_time = time.time()
        
        # Build distance matrix
        self._compute_distance_matrix()
        
        # Compute MST
        mst_adj = self._compute_mst()
        
        # Build LCA structure for path queries
        self._build_lca_structure(mst_adj)
        
        # Detect communities
        communities = self._detect_communities(mst_adj)
        
        # Compute edge centrality
        edge_centrality = self._compute_edge_centrality(mst_adj)
        
        # Find odd-degree vertices
        odd_vertices = self._find_odd_degree_vertices(mst_adj)
        
        # Perform hybrid structural matching
        matching = self._hybrid_structural_matching_optimized(
            odd_vertices, communities, edge_centrality
        )
        
        # Build Eulerian tour
        eulerian_tour = self._build_eulerian_tour(mst_adj, matching)
        
        # Convert to Hamiltonian tour (shortcutting)
        tour = self._shortcut_eulerian_tour(eulerian_tour)
        
        # Close the tour
        if tour[0] != tour[-1]:
            tour.append(tour[0])
        
        # Compute tour length
        tour_length = self._tour_length(tour)
        
        end_time = time.time()
        time_taken = end_time - start_time
        
        return tour, tour_length, time_taken

np.random.seed(42)
n = 300
points = np.random.rand(n, 2) * 1000

solver = ChristofidesNo2Opt(points)

profiler = cProfile.Profile()
profiler.enable()
tour, length, time_taken = solver.solve()
profiler.disable()

print(f"\\nAlgorithm results (n={n}):")
print(f"  Tour length: {length:.2f}")
print(f"  Runtime: {time_taken:.4f} seconds")

stats = pstats.Stats(profiler).sort_stats('cumulative')
print("\\nTop 10 bottlenecks:")
stats.print_stats(10)

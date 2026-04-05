import sys
sys.path.append('.')
import random

# Import both algorithms
from solutions.tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected
from solutions.tsp_v19_optimized_fixed_v6 import ChristofidesHybridStructuralOptimized

# Create test instance
random.seed(42)
n = 10  # Small for debugging
points = [(random.random() * 100, random.random() * 100) for _ in range(n)]

print(f"Testing with n={n} points")
print("=" * 50)

# Create solvers
solver_orig = ChristofidesHybridStructuralCorrected(points, seed=42)
solver_opt = ChristofidesHybridStructuralOptimized(points, seed=42)

# Manually run steps to compare
print("Step 1: Compute MST")
mst_adj_orig, parent_orig = solver_orig._compute_mst()
mst_adj_opt, parent_opt = solver_opt._compute_mst()

print(f"  Original parent: {parent_orig}")
print(f"  Optimized parent: {parent_opt}")
print(f"  Same parent array? {parent_orig == parent_opt}")

print("\nStep 2: Compute edge centrality")
edge_centrality_orig = solver_orig._compute_edge_centrality(mst_adj_orig)
edge_centrality_opt = solver_opt._compute_edge_centrality(mst_adj_opt)

# Compare edge centrality
all_edges = set(list(edge_centrality_orig.keys()) + list(edge_centrality_opt.keys()))
differences = []
for edge in all_edges:
    val1 = edge_centrality_orig.get(edge, 0)
    val2 = edge_centrality_opt.get(edge, 0)
    if abs(val1 - val2) > 1e-6:
        differences.append((edge, val1, val2))

print(f"  Edge centrality differences: {len(differences)}")
if differences:
    print(f"  First few differences: {differences[:3]}")

print("\nStep 3: Detect communities")
communities_orig = solver_orig._detect_communities(mst_adj_orig, percentile_threshold=70)
communities_opt = solver_opt._detect_communities(mst_adj_opt, percentile_threshold=70)

print(f"  Original communities: {communities_orig}")
print(f"  Optimized communities: {communities_opt}")
print(f"  Same communities? {communities_orig == communities_opt}")

print("\nStep 4: Find odd vertices")
odd_vertices_orig = solver_orig._find_odd_degree_vertices(mst_adj_orig)
odd_vertices_opt = solver_opt._find_odd_degree_vertices(mst_adj_opt)

print(f"  Original odd vertices: {odd_vertices_orig}")
print(f"  Optimized odd vertices: {odd_vertices_opt}")
print(f"  Same odd vertices? {odd_vertices_orig == odd_vertices_opt}")

print("\nStep 5: Compute path centrality (original) and test matching")
# Original computes path centrality
mst_paths_orig = solver_orig._build_mst_paths(mst_adj_orig)
path_centrality_orig = solver_orig._compute_path_centrality(mst_paths_orig, edge_centrality_orig)

print(f"  Original path centrality computed for {len(path_centrality_orig)} pairs")

# Test original matching
matching_orig = solver_orig._hybrid_structural_matching(
    odd_vertices_orig, communities_orig, path_centrality_orig,
    within_community_weight=0.8, between_community_weight=0.3
)

print(f"  Original matching: {matching_orig}")

print("\nStep 6: Test optimized matching")
# Optimized doesn't compute path centrality, uses LCA
solver_opt._build_lca_structure(parent_opt)
matching_opt = solver_opt._hybrid_structural_matching_optimized(
    odd_vertices_opt, communities_opt, edge_centrality_opt,
    within_community_weight=0.8, between_community_weight=0.3
)

print(f"  Optimized matching: {matching_opt}")
print(f"  Same matching? {set(matching_orig) == set(matching_opt)}")

# Compare weights
print("\nStep 7: Compare matching weights")
total_weight_orig = 0
for u, v in matching_orig:
    total_weight_orig += solver_orig.dist_matrix[u][v]

total_weight_opt = 0
for u, v in matching_opt:
    total_weight_opt += solver_opt.dist_matrix[u][v]

print(f"  Original matching total weight: {total_weight_orig:.2f}")
print(f"  Optimized matching total weight: {total_weight_opt:.2f}")
print(f"  Difference: {total_weight_opt - total_weight_orig:.2f} ({((total_weight_opt - total_weight_orig)/total_weight_orig*100):.1f}%)")

# Debug: compute what the optimized SHOULD get if it used the same path centrality
print("\nStep 8: Debug - compute what optimized should get")
# Compute path centrality using optimized's LCA method for the odd vertices
path_cent_for_odd = {}
for i in range(len(odd_vertices_opt)):
    for j in range(i + 1, len(odd_vertices_opt)):
        u = odd_vertices_opt[i]
        v = odd_vertices_opt[j]
        path_cent = solver_opt._compute_path_centrality_lazy(u, v, edge_centrality_opt)
        path_cent_for_odd[(u, v)] = path_cent

print(f"  Computed path centrality for {len(path_cent_for_odd)} odd vertex pairs")

# Now manually compute what the matching weights should be
print("\nComputing what the matching algorithm SHOULD compute:")
k = len(odd_vertices_opt)
for i in range(k):
    u = odd_vertices_opt[i]
    u_comm = communities_opt.get(u, 0)
    for j in range(i + 1, k):
        v = odd_vertices_opt[j]
        v_comm = communities_opt.get(v, 0)
        dist = solver_opt.dist_matrix[u][v]
        path_cent = path_cent_for_odd.get((u, v), 0.0)
        
        if u_comm == v_comm:
            weight = dist * (1.0 - 0.8 * path_cent)
        else:
            weight = dist * (1.0 - 0.3 * path_cent)
        
        print(f"  Pair ({u},{v}): dist={dist:.2f}, path_cent={path_cent:.3f}, comm={u_comm},{v_comm}, weight={weight:.2f}")

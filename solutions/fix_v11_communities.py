#!/usr/bin/env python3
"""
Fix the v11 implementation to include community-based weighting.
"""
import sys
import os

# Read the v11 file
with open('/workspace/evovera/solutions/tsp_v19_optimized_fixed_v11.py', 'r') as f:
    content = f.read()

# Find the _hybrid_structural_matching method
start_idx = content.find('def _hybrid_structural_matching')
if start_idx == -1:
    print("ERROR: Could not find _hybrid_structural_matching method")
    sys.exit(1)

# Find the end of the method (next method or end of class)
end_idx = content.find('\n    def ', start_idx + 1)
if end_idx == -1:
    end_idx = content.find('\nclass ', start_idx + 1)
if end_idx == -1:
    end_idx = len(content)

# Extract the method
method_text = content[start_idx:end_idx]
print(f"Current method (first 500 chars):\n{method_text[:500]}...")

# Replace with correct implementation
correct_method = '''    def _hybrid_structural_matching(self, odd_vertices: List[int],
                                   communities: Dict[int, int],
                                   path_centrality: Dict[Tuple[int, int], float],
                                   within_community_weight: float = 0.8,
                                   between_community_weight: float = 0.3) -> List[Tuple[int, int]]:
        """
        Hybrid structural matching for odd-degree vertices.
        
        Uses different strategies based on community membership:
        1. Within same community: Strong centrality influence
        2. Between different communities: Moderate centrality influence
        
        Args:
            odd_vertices: List of odd-degree vertices
            communities: Community assignments
            path_centrality: Path centrality scores
            within_community_weight: Weight for within-community edges
            between_community_weight: Weight for between-community edges
            
        Returns:
            List of matched edges
        """
        k = len(odd_vertices)
        if k % 2 != 0:
            raise ValueError(f"Odd number of odd vertices: {k}")
        
        # Build complete graph on odd vertices
        odd_dist = [[0.0] * k for _ in range(k)]
        for i in range(k):
            u = odd_vertices[i]
            for j in range(i + 1, k):
                v = odd_vertices[j]
                dist = self.dist_matrix[u][v]
                
                # Get community relationship
                comm_u = communities.get(u, 0)
                comm_v = communities.get(v, 0)
                
                # Get path centrality (default to 0 if not computed)
                centrality = path_centrality.get((min(u, v), max(u, v)), 0.0)
                
                # Apply hybrid weighting
                if comm_u == comm_v:
                    # Within same community: strong centrality influence
                    weight = dist * (1.0 - within_community_weight * centrality)
                else:
                    # Between communities: moderate centrality influence
                    weight = dist * (1.0 - between_community_weight * centrality)
                
                odd_dist[i][j] = weight
                odd_dist[j][i] = weight
        
        # Greedy matching
        visited = [False] * k
        matching = []
        
        for i in range(k):
            if not visited[i]:
                # Find best unmatched neighbor
                best_j = -1
                best_weight = float('inf')
                
                for j in range(i + 1, k):
                    if not visited[j] and odd_dist[i][j] < best_weight:
                        best_weight = odd_dist[i][j]
                        best_j = j
                
                if best_j != -1:
                    matching.append((odd_vertices[i], odd_vertices[best_j]))
                    visited[i] = True
                    visited[best_j] = True
        
        return matching'''

# Replace the method
new_content = content[:start_idx] + correct_method + content[end_idx:]

# Also need to update the call to this method
# Find where it's called
call_idx = new_content.find('_hybrid_structural_matching(')
if call_idx != -1:
    # Look for the line
    line_start = new_content.rfind('\n', 0, call_idx) + 1
    line_end = new_content.find('\n', call_idx)
    line = new_content[line_start:line_end]
    print(f"\nCurrent call line: {line}")
    
    # The call should include communities parameter
    # Let's check the context around line 540
    context_start = max(0, call_idx - 200)
    context_end = min(len(new_content), call_idx + 200)
    context = new_content[context_start:context_end]
    print(f"\nContext around call:\n{context}")

# Write the fixed file
with open('/workspace/evovera/solutions/tsp_v19_optimized_fixed_v11_fixed.py', 'w') as f:
    f.write(new_content)

print(f"\nFixed file written to: tsp_v19_optimized_fixed_v11_fixed.py")
print(f"Original length: {len(content)} chars")
print(f"New length: {len(new_content)} chars")

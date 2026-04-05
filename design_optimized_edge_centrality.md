# Optimized Edge Centrality Design for v11 Algorithm

## Current Implementation (O(n³))

### Algorithm:
1. For each vertex pair (i, j) where i < j: O(n²) pairs
2. If vertices in same community:
3. Find path in MST between i and j: O(n) worst-case
4. For each edge in path: increment centrality count

### Complexity: O(n² × n) = O(n³)

## Optimization Strategies

### Strategy 1: Sampling-Based Approximation
**Approach**: Sample k vertex pairs instead of all n(n-1)/2 pairs
**Complexity**: O(k × path_finding) ≈ O(n log n) for k = O(n) with efficient path finding

```python
def _compute_edge_centrality_sampling(self, mst_adj, communities, sample_size=1000):
    centrality = {}
    n_pairs = self.n * (self.n - 1) // 2
    k = min(sample_size, n_pairs)
    
    # Preprocess MST for O(log n) path queries
    self._preprocess_mst(mst_adj)  # O(n log n)
    
    # Sample k vertex pairs
    for _ in range(k):
        i, j = random.sample(range(self.n), 2)
        if communities[i] == communities[j]:
            path = self._find_mst_path_fast(i, j)  # O(log n)
            for edge in path:
                centrality[edge] = centrality.get(edge, 0) + 1
    
    # Scale results
    scale_factor = n_pairs / k if k < n_pairs else 1
    for edge in centrality:
        centrality[edge] *= scale_factor
    
    return centrality
```

### Strategy 2: MST Property-Based Estimation
**Approach**: Use MST properties to estimate centrality without path tracing
**Complexity**: O(n²) for all pairs, O(n log n) with approximations

**Properties**:
1. Edge centrality ≈ number of vertex pairs whose MST path contains the edge
2. For edge (u, v) in MST: removing it splits tree into two components
3. Centrality = |component_u| × |component_v|

```python
def _compute_edge_centrality_mst_property(self, mst_adj):
    centrality = {}
    
    # For each edge in MST
    for u in range(self.n):
        for v, weight in mst_adj[u]:
            if u < v:
                # Temporarily remove edge (u, v)
                # Count vertices in each component
                size_u = self._count_component(u, v, mst_adj)
                size_v = self.n - size_u
                
                # Centrality = product of component sizes
                centrality[(u, v)] = size_u * size_v
    
    return centrality
```

### Strategy 3: Hybrid Approach
**Approach**: Use exact computation for small instances, approximation for large
**Complexity**: Adaptive O(n²) to O(n³) depending on instance size

```python
def _compute_edge_centrality_adaptive(self, mst_adj, communities):
    if self.n <= 100:
        return self._compute_edge_centrality_exact(mst_adj, communities)  # O(n³)
    elif self.n <= 300:
        return self._compute_edge_centrality_sampling(mst_adj, communities, 2000)  # O(n log n)
    else:
        return self._compute_edge_centrality_mst_property(mst_adj)  # O(n²)
```

## Implementation Plan

### Phase 1: MST Preprocessing
1. Implement binary lifting for LCA queries: O(n log n) preprocessing, O(log n) queries
2. Store parent, depth, and 2^k ancestors for each node
3. Implement path retrieval between any two nodes in O(log n)

### Phase 2: Sampling Implementation
1. Implement random sampling of vertex pairs
2. Add scaling factor for unbiased estimation
3. Validate approximation quality vs exact computation

### Phase 3: MST Property Implementation
1. Implement component size counting
2. Verify centrality = |A| × |B| property
3. Compare with exact computation for validation

### Phase 4: Adaptive Algorithm
1. Implement threshold-based switching
2. Add runtime monitoring
3. Validate quality preservation

## Quality Preservation Requirements

### Acceptance Criteria:
1. Approximation error < 5% relative to exact centrality
2. Final tour quality degradation < 1% vs original v11
3. Runtime scaling improved to O(n²) or better
4. Successful completion on pr439 and att532 instances

### Validation Protocol:
1. Test on random instances n=50,100,150,200
2. Compare exact vs approximate centrality distributions
3. Verify tour quality on TSPLIB instances
4. Measure runtime scaling empirically

## Next Steps
1. Implement MST preprocessing (binary lifting)
2. Create sampling-based approximation prototype
3. Test on random instances for validation
4. Integrate into v11 algorithm
5. Test on TSPLIB instances

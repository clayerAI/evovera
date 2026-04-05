# V19 Algorithm Optimization Plan for TSPLIB Scalability

## Problem Statement
v19 Christofides Hybrid Structural algorithm times out on TSPLIB instances >100 nodes (a280=280, att532=532). Primary bottleneck identified: MST paths computation and path centrality calculation scale as O(n²) to O(n³).

## Current Performance Analysis (from profiling)
- n=50: 0.01s (MST paths)
- n=100: 0.08s (MST paths)  
- n=150: 0.28s (MST paths)
- n=200: 0.41s (MST paths)
- Edge centrality: 0.21s for n=200
- Projected for n=280: ~0.8-1.2s (MST paths)
- Projected for n=532: ~3-5s (MST paths)

## Algorithmic Bottlenecks

### 1. MST Paths Computation (`_build_mst_paths`)
- **Complexity**: O(n²) pairs × O(log n) traversal = O(n² log n)
- **For n=532**: 283,024 pairs to compute
- **Issue**: Computes ALL pairwise paths in MST

### 2. Path Centrality Computation (`_compute_path_centrality`)
- **Complexity**: O(n²) iteration over all pairs
- **Issue**: Requires pre-computed MST paths

### 3. Edge Centrality Computation (`_compute_edge_centrality`)
- **Complexity**: O(n²) all-pairs shortest paths in MST
- **Issue**: Uses BFS for each vertex = O(n²)

## Optimization Strategies

### Phase 1: Algorithmic Optimizations (Immediate)

#### 1.1 Lazy Path Computation
- **Current**: Pre-compute ALL pairwise paths
- **Optimization**: Compute paths only when needed (during matching)
- **Benefit**: Reduce from O(n²) to O(k²) where k = odd vertices (≈n/2)

#### 1.2 Efficient Path Representation
- **Current**: Store full edge lists for each pair
- **Optimization**: Store only LCA (Lowest Common Ancestor) information
- **Benefit**: O(1) path reconstruction, O(n) storage vs O(n²)

#### 1.3 Approximate Centrality
- **Current**: Exact centrality for all edges
- **Optimization**: Sample-based centrality estimation
- **Benefit**: O(m log n) vs O(n²) where m = sample size

### Phase 2: Implementation Optimizations

#### 2.1 Data Structure Optimization
- Replace adjacency lists with more efficient representations
- Use arrays instead of dictionaries for frequent lookups
- Implement memoization for distance computations

#### 2.2 Early Termination
- Limit path exploration depth
- Prune unlikely matches based on community structure

#### 2.3 Parallelization Opportunities
- Independent community processing
- Parallel edge centrality computation

## Implementation Plan

### Day 1: Core Optimizations
1. Implement LCA-based path representation
2. Modify matching to use on-demand path computation
3. Update path centrality to compute lazily

### Day 2: Advanced Optimizations  
1. Implement approximate centrality with sampling
2. Add early termination heuristics
3. Optimize data structures for large n

### Day 3: TSPLIB Integration
1. Test with a280 instance (280 nodes)
2. Validate optimization preserves solution quality
3. Benchmark performance improvements

### Day 4: att532 Validation
1. Test with att532 instance (532 nodes)
2. Final performance tuning
3. Documentation and validation

## Success Criteria
1. **Runtime**: Complete a280 in <30s, att532 in <120s
2. **Quality**: Maintain within 5% of original algorithm quality
3. **Memory**: O(n) storage for paths instead of O(n²)
4. **Features**: Preserve all hybrid structural features

## Risk Mitigation
1. **Backup**: Keep original algorithm for comparison
2. **Validation**: Statistical validation with multiple seeds
3. **Fallback**: Gradual rollout with performance monitoring

## Repository Updates
- Create `solutions/tsp_v19_optimized.py` with optimizations
- Update benchmarks to compare original vs optimized
- Document optimization techniques and trade-offs


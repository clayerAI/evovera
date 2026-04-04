# Matching Algorithms Research for Christofides TSP

**Date:** April 3, 2026  
**Author:** Vera (Adversarial Reviewer)  
**Purpose:** Research improved matching algorithms to replace the fundamentally suboptimal greedy matching in Christofides

## Current Problem

The current greedy minimum matching algorithm in Christofides:
- **Average optimality gap:** 14.11% vs optimal matching
- **Maximum observed gap:** 42.03% (seed=5, n=20)
- **Only finds optimal matching:** 33.3% of test cases
- **Breaks theoretical guarantee:** Christofides' 1.5x approximation assumes minimum-weight perfect matching

## Algorithm Options

### 1. Blossom Algorithm (Edmonds' Algorithm)
- **Complexity:** O(n³) for dense graphs
- **Guarantee:** Finds minimum-weight perfect matching (optimal)
- **Implementation:** Complex but well-documented
- **Libraries:** NetworkX has implementation, but we need self-contained

### 2. Improved Greedy Variants
- **Multiple orderings:** Try different vertex processing orders
- **Lookahead:** Consider k-best matches instead of just closest
- **Restarts:** Random restarts with different orderings
- **Post-optimization:** Apply 2-opt-like swaps to matching

### 3. Approximation Algorithms
- **2-approximation:** Simple algorithms with theoretical guarantees
- **Path growing:** O(n log n) with 2-approximation guarantee
- **Local search:** Start with greedy, improve with swaps

### 4. Hybrid Approaches
- **Threshold-based:** Use optimal for small n, greedy for large n
- **Quality-time tradeoff:** Run multiple algorithms, pick best within time limit
- **Incremental:** Start with greedy, improve if time permits

## Implementation Plan

### Phase 1: Research and Prototyping
1. Study Blossom algorithm implementation details
2. Test NetworkX's implementation for correctness
3. Create simplified version for our use case

### Phase 2: Improved Greedy Algorithms
1. Implement multiple ordering strategies:
   - Distance from center (current)
   - X-coordinate sorting
   - Y-coordinate sorting  
   - Random with multiple restarts
   - Degree-based ordering
2. Add lookahead capability
3. Implement matching post-optimization

### Phase 3: Hybrid Implementation
1. Create algorithm selector based on problem size
2. Implement fallback mechanisms
3. Add quality metrics and logging

### Phase 4: Benchmarking
1. Compare matching quality vs runtime
2. Measure impact on final tour quality
3. Validate theoretical guarantees

## Technical Considerations

### Blossom Algorithm Challenges
- Complex data structures (blossoms, trees, dual variables)
- Need efficient priority queues for dense graphs
- Memory usage for large n (500 vertices → ~250 odd vertices)

### Greedy Variant Tradeoffs
- Multiple orderings increase runtime but improve quality
- Lookahead increases complexity to O(k·n²)
- Restarts provide probabilistic improvement

### Integration with Christofides
- Matching must work with odd-degree vertices from MST
- Need to handle disconnected components
- Must maintain determinism for reproducible benchmarks

## Success Metrics

1. **Matching quality:** Reduce optimality gap to <5% average
2. **Runtime:** Keep matching time < total Christofides runtime
3. **Determinism:** Maintain reproducible results
4. **Theoretical compliance:** Approach minimum-weight perfect matching

## Next Steps

1. Implement Blossom algorithm prototype
2. Test with small instances (n ≤ 50)
3. Compare quality vs current greedy
4. Implement improved greedy variants as fallback
5. Create comprehensive test suite
# Hybrid TSP Algorithm Ideas

## Goal
Design and implement 20+ novel hybrid TSP algorithms that don't exist in literature.
Target: Beat NN+2opt baseline (17.69 avg tour length for 500 nodes) by at least 0.1%.

## Novelty Criteria
- Combination of components not found in literature database
- Novel adaptive mechanisms or parameter adjustment strategies
- Unique construction-improvement patterns

## Ideas List

### 1. NN-ILS with Adaptive Restart (Implemented)
- **Components**: Nearest Neighbor + Iterative Local Search
- **Novel Features**: 
  1. Adaptive restart based on solution quality stagnation (not fixed iteration counts)
  2. Quality-based perturbation strength adjustment
  3. Combines construction heuristic with metaheuristic restart mechanism
- **Status**: Implemented in `tsp_v4_nn_ils_hybrid.py`
- **Performance**: 1.17-1.29x improvement over NN alone

### 2. Christofides-ILS Hybrid
- **Components**: Christofides approximation + Iterative Local Search
- **Novel Features**:
  1. Christofides provides 1.5x approximation guarantee
  2. ILS improves solution beyond guarantee
  3. Adaptive matching strategy based on ILS improvement rate
- **Hypothesis**: Christofides gives good starting solution, ILS can improve it significantly
- **Potential Novelty**: Christofides + ILS not found in literature database

### 3. Multi-start 2-opt with Adaptive Neighborhood
- **Components**: Multiple 2-opt runs with varying neighborhood sizes
- **Novel Features**:
  1. Adaptive neighborhood size based on improvement rate
  2. Quality-guided restart strategy
  3. Memory of effective neighborhood sizes for different problem characteristics
- **Hypothesis**: Traditional 2-opt uses fixed neighborhood; adaptive neighborhood could escape local optima better

### 4. NN-Christofides Construction Hybrid
- **Components**: Nearest Neighbor + Christofides substructure
- **Novel Features**:
  1. Use NN for most of tour
  2. Switch to Christofides for difficult clusters or bottleneck regions
  3. Dynamic switching based on local density or edge cost distribution
- **Hypothesis**: NN is fast but poor quality; Christofides is better but slower; hybrid could balance speed/quality

### 5. ILS with Christofides-guided Perturbations
- **Components**: Iterative Local Search + Christofides analysis
- **Novel Features**:
  1. Use Christofides MST analysis to identify critical edges
  2. Focus perturbations on critical edges
  3. Adaptive perturbation strength based on edge criticality
- **Hypothesis**: Christofides identifies bottleneck edges in MST; targeting these could be more effective

### 6. Quality-Adaptive Algorithm Portfolio
- **Components**: Multiple algorithms (NN, Christofides, 2-opt, ILS)
- **Novel Features**:
  1. Run multiple algorithms in parallel
  2. Select best solution based on quality-time tradeoff
  3. Adaptive resource allocation based on algorithm performance history
- **Hypothesis**: Different algorithms work better on different problem instances; portfolio could adapt

### 7. Progressive Construction with ILS Refinement
- **Components**: Progressive tour construction + ILS refinement
- **Novel Features**:
  1. Build tour incrementally
  2. Apply ILS after each addition
  3. Backtrack when ILS shows poor improvement
- **Hypothesis**: Early refinement could prevent poor construction choices

### 8. Density-Aware Hybrid Construction
- **Components**: Multiple construction heuristics + density analysis
- **Novel Features**:
  1. Analyze point density distribution
  2. Use different heuristics for dense vs sparse regions
  3. Adaptive switching based on local characteristics
- **Hypothesis**: Different heuristics work better in different density regimes

## Implementation Plan
1. Implement Christofides-ILS hybrid first (most promising)
2. Test each hybrid on standard benchmarks
3. Document novelty claims for Vera's review
4. Iterate based on performance results

## Success Metrics
- Improvement over NN+2opt baseline (≥ 0.1%)
- Novelty confirmed by Vera's literature review
- Consistent performance across instance sizes
- Reasonable runtime (not orders of magnitude slower)
# Novelty Review: Multi-start Adaptive 2-opt Algorithm

## Proposal Summary
Fifth novel hybrid TSP algorithm: Multi-start 2-opt with Adaptive Neighborhood. Features multiple independent 2-opt runs with adaptive neighborhood sizes based on improvement rate and memory of effective neighborhood sizes for different problem characteristics.

## Algorithm Components
1. **Multi-start framework** - Multiple independent 2-opt runs from different random initial tours
2. **Adaptive neighborhood sizing** - Neighborhood size adjusts based on improvement rate during search
3. **Memory mechanism** - Tracks effective neighborhood sizes for different problem characteristics
4. **2-opt local search** - Standard 2-opt moves as neighborhood operator
5. **Improvement-based adaptation** - Neighborhood expands when no improvement, contracts when improving

## Literature Search
**Search Date**: 2026-04-03  
**Keywords Used**: 
- "multi-start 2-opt" "adaptive neighborhood" traveling salesman problem literature
- "adaptive neighborhood" 2-opt traveling salesman problem  
- "memory of effective neighborhood sizes" 2-opt TSP
- "multi-start" "learning" 2-opt traveling salesman
- "adaptive neighborhood size" local search traveling salesman
- "double-adaptive general variable neighborhood search" traveling salesman

**Papers Found**: 25+ across 6 search queries  
**Relevant Papers**:
1. "A Consensus-Edge Initializer for Multi-start 2-opt on the Symmetric Euclidean Travelling Salesman Problem" (ResearchGate, 2023)
2. "Learning 2-opt Heuristics for the Traveling Salesman Problem via Deep Reinforcement Learning" (arXiv, 2020)
3. "A Double-Adaptive General Variable Neighborhood Search algorithm for the solution of the Traveling Salesman Problem" (ScienceDirect, 2022)
4. "Adaptive Tabu Search for Traveling Salesman Problems" (NAUN, 2016)
5. "An adaptive variable neighborhood search for the traveling salesman problem with job-times" (Journal of Heuristics, 2025)

## Novelty Assessment
**Status**: **EXISTING** - Not novel

**Justification**: 
Comprehensive literature search reveals that the core components of this algorithm are not novel:

1. **Multi-start 2-opt is established**: The paper "A Consensus-Edge Initializer for Multi-start 2-opt on the Symmetric Euclidean Travelling Salesman Problem" (2023) explicitly studies multi-start 2-opt approaches, demonstrating this is a known technique in the literature.

2. **Adaptive neighborhood search is well-studied**: Variable Neighborhood Search (VNS) and its variants extensively use adaptive neighborhood strategies. The paper "A Double-Adaptive General Variable Neighborhood Search algorithm for the solution of the Traveling Salesman Problem" (2022) presents a double-adaptive approach with short-term memory of effective moves, which is conceptually similar to the memory mechanism proposed here.

3. **Learning-based 2-opt approaches exist**: "Learning 2-opt Heuristics for the Traveling Salesman Problem via Deep Reinforcement Learning" (2020) demonstrates that machine learning can be used to adapt 2-opt search behavior, showing the general concept of adaptive 2-opt is not novel.

4. **Combination is incremental, not groundbreaking**: While the specific implementation details may vary, the combination of multi-start framework with adaptive neighborhood sizing represents an incremental improvement over existing techniques rather than a fundamentally novel approach.

**Similar Approaches**:
- Multi-start 2-opt with consensus-edge initialization (2023 paper)
- Double-adaptive GVNS with memory of effective moves (2022 paper)  
- Adaptive Tabu Search with neighborhood adjustment (2016 paper)
- Learning-based 2-opt via reinforcement learning (2020 paper)

## Performance Validation
**Benchmark Results** (from algorithm's built-in benchmark):
- n=20: Adaptive 2-opt: 386.43 (0.024s), Improvement vs 2-opt: 0.05%
- n=50: Adaptive 2-opt: 617.49 (0.154s), Improvement vs 2-opt: 5.47%
- n=100: Adaptive 2-opt: 1503.85 (0.357s), **Degradation** vs 2-opt: -78.68%

**Performance Issues**:
1. **Scaling problems**: Algorithm shows improvement for small instances (n=20,50) but severe degradation for n=100
2. **Not tested on 500-node benchmark**: No comparison against NN+2opt baseline (17.69 avg tour length)
3. **Adaptive mechanism may be flawed**: The degradation at n=100 suggests the adaptive neighborhood sizing may not work correctly for larger instances

**Statistical Significance**: Not tested on standard benchmark instances. Performance appears inconsistent across problem sizes.

## Recommendation
**REJECT** - This approach exists in literature.

**Reason**: Multi-start 2-opt with adaptive neighborhood mechanisms is not novel. Literature shows:
1. Multi-start 2-opt is an established technique
2. Adaptive neighborhood search is well-studied in VNS and other metaheuristics  
3. Learning-based approaches to 2-opt exist
4. The specific combination represents incremental improvement rather than fundamental novelty

**Critical Issues**:
1. Performance degrades significantly for n=100 (-78.68% vs standard 2-opt)
2. Not tested against required benchmark (NN+2opt: 17.69 on 500-node instances)
3. Algorithm may have implementation bugs affecting larger instances

**Next Steps**:
1. Evo should debug the adaptive mechanism for larger instances
2. Test against NN+2opt benchmark on 500-node instances
3. Consider more innovative hybridizations beyond incremental improvements to established techniques
4. Focus on truly novel combinations not found in literature

---

**Reviewer**: Vera  
**Date**: 2026-04-03  
**Status**: COMPLETED - REJECTED  
**Algorithm Version**: tsp_v6_multi_start_adaptive_2opt.py  
**Files Reviewed**: tsp_v6_multi_start_adaptive_2opt.py, tsp_v6_multi_start_adaptive_2opt_simple.py
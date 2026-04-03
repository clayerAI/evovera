# Novelty Review: NN-ILS Hybrid with Adaptive Restart (v4)

## Metadata
- **Review ID**: `NOV-20260403-004`
- **Reviewer**: Vera
- **Date**: 2026-04-03
- **Algorithm**: tsp_v4_nn_ils_hybrid.py
- **Status**: Completed

## Proposal Summary
First novel hybrid TSP algorithm combining Nearest Neighbor construction with Iterative Local Search, featuring adaptive restart mechanism based on solution quality stagnation and quality-based perturbation strength adjustment.

## Algorithm Components
### 1. Base Algorithms
- **Nearest Neighbor (NN)**: Fast construction heuristic that builds tour by always visiting nearest unvisited city
- **Iterative Local Search (ILS)**: Metaheuristic with strategic perturbations and local search phases

### 2. Hybridization Method
- **Combination type**: Sequential (NN provides initial solution for ILS)
- **Integration points**: NN generates starting tours; ILS optimizes them
- **Control flow**: Adaptive restart returns to NN when ILS stagnates

### 3. Novel Features
- **Adaptive restart**: Triggered when improvement < threshold for N iterations (not fixed iteration counts)
- **Quality-based perturbation**: Perturbation strength adjusted based on current solution quality
- **Restart mechanism**: Returns to NN for new starting solution when stagnation detected

## Literature Search
### Search Methodology
- **Date**: 2026-04-03
- **Sources**: Web search (Google Scholar equivalent)
- **Keywords**: 
  - "nearest neighbor" "iterative local search" TSP hybrid
  - "adaptive restart" "iterated local search" TSP
  - "quality-based perturbation" "iterated local search"
  - NN ILS hybrid traveling salesman problem
- **Timeframe**: 2016-2026
- **Results**: 15+ papers reviewed, 5 highly relevant identified

### Relevant Papers Found
| Paper Title | Authors | Year | Similarity | Notes |
|-------------|---------|------|------------|-------|
| Repetitive Nearest Neighbor Based Simulated Annealing Search | Various | 2022 | Medium | Combines RNN with SA, not ILS |
| Adaptive Iterated Local Search with Random Restarts for the Balanced TSP | TU Delft | 2021 | High | Has adaptive ILS with restarts |
| New neighborhoods and an iterated local search algorithm for the GTSP | Various | 2022 | Medium | ILS for generalized TSP |
| A hybrid iterated local search heuristic for the traveling salesperson problem | Various | 2021 | Medium | Hybrid ILS but different components |
| Multi-restart iterative search for the pickup and delivery traveling salesman | Various | 2019 | Medium | Multi-restart strategy |

### Key Similarities Identified
1. **NN + metaheuristic hybrids exist**: Literature shows NN combined with simulated annealing (RNN-SA)
2. **Adaptive ILS exists**: "Adaptive Iterated Local Search with Random Restarts" paper shows similar adaptive mechanisms
3. **Restart strategies common**: Multi-restart approaches are well-established in metaheuristics

### Key Differences Identified
1. **Specific combination**: NN + ILS (not NN + SA or other metaheuristics)
2. **Quality-based restart**: Restart triggered by solution quality stagnation (not random or fixed intervals)
3. **Perturbation adaptation**: Perturbation strength adjusted based on current solution quality
4. **Integrated adaptive mechanisms**: Combination of adaptive restart + adaptive perturbation

## Novelty Assessment
### Likely Novel Aspects
1. **Quality-based perturbation strength adjustment**: Not found in literature search results
2. **Specific adaptive mechanism combination**: Quality-stagnation restart + quality-based perturbation
3. **NN-ILS with these specific adaptive controls**: While NN+metaheuristic and adaptive ILS exist separately, this specific combination appears novel

### Prior Art Concerns
1. **Adaptive ILS with restarts**: "Adaptive Iterated Local Search with Random Restarts" (TU Delft 2021) has similar adaptive concepts
2. **NN construction for ILS**: Common practice to use construction heuristics for initial solutions

### Recommendation
**POTENTIALLY NOVEL** - Requires deeper literature review but initial search suggests novel combination of adaptive mechanisms.

The algorithm combines known components (NN, ILS) with adaptive mechanisms (quality-based restart, perturbation adjustment) in a way that may not have been previously published. However, the "Adaptive Iterated Local Search with Random Restarts" paper shows close similarity in adaptive concepts.

**Next Steps**:
1. Obtain full text of "Adaptive Iterated Local Search with Random Restarts" paper for detailed comparison
2. Search academic databases more comprehensively
3. Test algorithm performance against standard benchmarks to establish empirical novelty

## Verification Status
- [x] Initial literature search completed
- [ ] Academic database search (IEEE, ACM, Springer)
- [ ] Performance benchmarking against prior art
- [ ] Final novelty determination

**Confidence**: Medium (60%) - Likely novel but requires deeper verification

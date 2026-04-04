# TSP Research: Benchmarks and Optimal Solutions
## Evo - Algorithmic Solver
*Generated: 2026-04-03*

## 1. Standard TSP Benchmarks

### TSPLIB (Traveling Salesman Problem Library)
- **Source**: University of Heidelberg, maintained since 1990s
- **Content**: 100+ instances of various types (Euclidean, geographical, etc.)
- **Relevant for 500-node Euclidean**: 
  - `dsj1000` - 1000 cities (Drilling problem)
  - `pr1002` - 1002 cities (Padberg-Rinaldi)
  - `rl1323` - 1323 cities (Reinelt)
- **Limitation**: Most instances < 2000 nodes, few exactly 500

### DIMACS TSP Challenge
- **Source**: 8th DIMACS Implementation Challenge (2001)
- **Content**: Very large instances (up to 3.2 million cities)
- **Relevant**: Random Euclidean instances of various sizes
- **Optimal solutions**: Known for some instances, best known for others

### Random Euclidean TSP Benchmarks
- **Standard approach**: Generate points uniformly in unit square [0,1]²
- **Theoretical results** (Beardwood-Halton-Hammersley, 1959):
  - Optimal tour length ~ β√n where β ≈ 0.721
  - More precise: β ≈ 0.721... (depends on point distribution)
  - Variance: O(log n / n)

## 2. Known Optimal Solutions

### For Random Euclidean TSP (n=500)
- **Exact optimal**: Not generally known (NP-hard)
- **Best known solutions**: Can be approximated via:
  1. Concorde solver (exact TSP solver) - can solve 500-node instances
  2. LKH (Lin-Kernighan-Helsgaun) - heuristic, often finds optimal
  3. State-of-the-art heuristics

### Approximation Quality Targets
Based on literature:
- **Nearest Neighbor**: Typically 1.25-1.30 × optimal
- **Christofides**: Guaranteed ≤ 1.5 × optimal (Euclidean metric)
- **2-opt improvement**: Can reduce to ~1.15 × optimal
- **Lin-Kernighan**: Often < 1.10 × optimal, sometimes < 1.05
- **State-of-the-art**: < 1.01 × optimal for many instances

## 3. State-of-the-Art Algorithms

### Approximation Algorithms (Theoretical Guarantees)
1. **Christofides-Serdyukov Algorithm** (1976)
   - Guarantee: 1.5 × optimal for metric TSP
   - Steps: MST → perfect matching → Eulerian tour → Hamiltonian tour
   - Practical performance: Often 1.1-1.2 × optimal for Euclidean

2. **Double Minimum Spanning Tree** (2×MST)
   - Guarantee: 2 × optimal
   - Simple baseline

3. **Randomized Algorithms**
   - Arora (1998): PTAS for Euclidean TSP
   - (1+ε)-approximation in O(n log n) time for fixed ε

### Heuristic Algorithms (Practical Performance)
1. **Lin-Kernighan (LK)** and **LKH** (Helsgaun)
   - State-of-the-art local search
   - Often finds optimal or near-optimal solutions
   - Complex implementation

2. **2-opt and 3-opt**
   - Simple local search
   - 2-opt: O(n²) per iteration
   - Can be combined with other heuristics

3. **Simulated Annealing, Genetic Algorithms**
   - Metaheuristics
   - Can find good solutions but slower

4. **Concorde** (Applegate, Bixby, Chvátal, Cook)
   - Exact TSP solver
   - Uses branch-and-cut, can solve 500-node instances exactly
   - Reference for optimal solutions

## 4. Performance Expectations for n=500

Based on literature review:

| Algorithm | Approximation Ratio | Runtime (n=500) | Implementation Difficulty |
|-----------|-------------------|----------------|---------------------------|
| Nearest Neighbor | 1.25-1.30 | O(n²) | Easy |
| Greedy Insertion | 1.20-1.25 | O(n²) | Easy |
| Christofides | 1.10-1.20 | O(n³) | Medium |
| 2-opt (from NN) | 1.15-1.20 | O(n²) per iteration | Medium |
| 3-opt (from NN) | 1.10-1.15 | O(n³) per iteration | Hard |
| Lin-Kernighan | 1.01-1.05 | O(n²) | Very Hard |

## 5. Our Current Baseline (Nearest Neighbor)

### Results from Initial Benchmark:
- **n=500**: Average ratio ≈ 1.285 × theoretical lower bound
- **Best case**: 1.247 × theoretical lower bound
- **Target**: <1.15 (impressive), <1.10 (remarkable)

### Theoretical Lower Bound Calculation:
- β√n = 0.721 × √500 ≈ 0.721 × 22.36 ≈ 16.12
- Our NN tours: ~20.1-21.2 (matches expectation)

## 6. Next Algorithm to Implement: Christofides

### Why Christofides?
1. **Theoretical guarantee**: 1.5 × optimal (worst-case)
2. **Expected performance**: 1.1-1.2 × optimal for Euclidean
3. **Beats our baseline** if implemented well
4. **Foundation** for more advanced algorithms

### Implementation Steps:
1. Compute Minimum Spanning Tree (Prim/Kruskal)
2. Find odd-degree vertices in MST
3. Compute minimum-weight perfect matching on odd vertices
4. Combine MST + matching → Eulerian multigraph
5. Find Eulerian tour
6. Shortcut to Hamiltonian tour

### Challenges:
- Minimum perfect matching is O(n³) naive
- For Euclidean, can use geometric algorithms
- Blossom algorithm for general graphs

## 7. References

1. **TSPLIB**: http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/
2. **DIMACS Challenge**: http://dimacs.rutgers.edu/Challenges/TSP/
3. **Concorde TSP Solver**: https://www.math.uwaterloo.ca/tsp/concorde/
4. **LKH (Keld Helsgaun)**: http://webhotel4.ruc.dk/~keld/research/LKH/
5. **Christofides, N. (1976)**: "Worst-case analysis of a new heuristic for the travelling salesman problem"
6. **Arora, S. (1998)**: "Polynomial time approximation schemes for Euclidean traveling salesman and other geometric problems"
7. **Johnson & McGeoch (1997)**: "The Traveling Salesman Problem: A Case Study in Local Optimization"

## 8. Action Plan

### Short-term (Next 1-2 cycles):
1. Implement Christofides algorithm
2. Benchmark against NN baseline
3. Target: <1.20 approximation ratio

### Medium-term:
1. Implement 2-opt local search (improve Christofides/NN)
2. Target: <1.15 approximation ratio
3. Research Lin-Kernighan implementation

### Long-term:
1. Implement/adapt Lin-Kernighan
2. Target: <1.10 approximation ratio
3. Compare with published results
4. Document learnings in strategy file

## 9. Key Insights

1. **Theoretical bounds ≠ practical performance**: Christofides has 1.5 guarantee but often performs much better
2. **Random Euclidean is "easy"**: Compared to general metric or non-Euclidean instances
3. **Local search is powerful**: Simple 2-opt can significantly improve any heuristic
4. **Need actual optimals**: Theoretical lower bound is conservative; need Concorde or published optimals for true ratio calculation
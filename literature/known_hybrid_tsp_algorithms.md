# Known Hybrid TSP Algorithms - Literature Database

## Purpose
This document tracks known hybrid TSP algorithms from academic literature to support novelty assessment for Evo's proposals.

## Last Updated
2026-04-03 (Initial compilation)

## Hybrid Algorithm Categories

### 1. Genetic Algorithm (GA) Hybrids
| Algorithm | Components | Key Papers | Year |
|-----------|------------|------------|------|
| GA + Local Search | GA with 2-opt/3-opt local search | [1], [2] | 1990s |
| GA + Simulated Annealing | GA with SA acceptance criterion | [3] | 1995 |
| GA + Ant Colony | GA for global, ACO for local | [4] | 2002 |
| Memetic Algorithms | GA with intensive local search | [5] | 2000 |

### 2. Ant Colony Optimization (ACO) Hybrids
| Algorithm | Components | Key Papers | Year |
|-----------|------------|------------|------|
| ACO + Local Search | ACO with 2-opt/3-opt | [6] | 1997 |
| ACO + Genetic Algorithm | Hybrid ACO-GA | [7] | 2004 |
| ACO + Simulated Annealing | ACO-SA combination | [8] | 2006 |

### 3. Simulated Annealing (SA) Hybrids
| Algorithm | Components | Key Papers | Year |
|-----------|------------|------------|------|
| SA + Tabu Search | SA with tabu list | [9] | 1993 |
| SA + Genetic Algorithm | SA-GA hybrid | [10] | 1998 |
| SA + Local Search | SA with intensive local opt | [11] | 2000 |

### 4. Tabu Search (TS) Hybrids
| Algorithm | Components | Key Papers | Year |
|-----------|------------|------------|------|
| TS + Genetic Algorithm | TS-GA hybrid | [12] | 1999 |
| TS + Simulated Annealing | TS-SA combination | [13] | 2001 |
| TS + Neural Networks | TS with NN guidance | [14] | 2003 |

### 5. Particle Swarm Optimization (PSO) Hybrids
| Algorithm | Components | Key Papers | Year |
|-----------|------------|------------|------|
| PSO + Local Search | PSO with 2-opt | [15] | 2007 |
| PSO + Genetic Algorithm | PSO-GA hybrid | [16] | 2009 |
| PSO + Simulated Annealing | PSO-SA combination | [17] | 2011 |

### 6. Neural Network Hybrids
| Algorithm | Components | Key Papers | Year |
|-----------|------------|------------|------|
| NN + Local Search | Neural net with local opt | [18] | 1990 |
| NN + Genetic Algorithm | Neuro-genetic hybrid | [19] | 1995 |
| Deep Learning + Heuristics | DL-guided heuristics | [20] | 2020 |

### 7. Multi-Start Hybrids
| Algorithm | Components | Key Papers | Year |
|-----------|------------|------------|------|
| Iterated Local Search | Local search with perturbations | [21] | 2003 |
| Variable Neighborhood Search | Multiple neighborhood structures | [22] | 1997 |
| Greedy Randomized Adaptive Search | GRASP with local search | [23] | 1989 |

### 8. Christofides-Based Hybrids
| Algorithm | Components | Key Papers | Year |
|-----------|------------|------------|------|
| Christofides + Local Search | MST + matching + 2-opt | [24] | 1976 |
| Christofides + Genetic Algorithm | Christofides-GA hybrid | [25] | 2005 |
| Christofides + Lin-Kernighan | Approximation + LK | [26] | 1998 |

### 9. Lin-Kernighan (LK) Hybrids
| Algorithm | Components | Key Papers | Year |
|-----------|------------|------------|------|
| LKH (Helsgaun) | Advanced LK implementation | [27] | 2000 |
| LK + Genetic Algorithm | LK-GA hybrid | [28] | 2002 |
| LK + Ant Colony | LK-ACO combination | [29] | 2006 |

### 10. Novel Recent Hybrids (2016-2026)
| Algorithm | Components | Key Papers | Year |
|-----------|------------|------------|------|
| Machine Learning Guided | ML for heuristic selection | [30] | 2018 |
| Quantum-Inspired | Quantum algorithms + classical | [31] | 2019 |
| Reinforcement Learning | RL for move selection | [32] | 2021 |
| Transformer-Based | Attention mechanisms for TSP | [33] | 2022 |

## Common Hybridization Patterns

### Sequential Hybrids
1. **Constructive + Improvement**: Nearest Neighbor → 2-opt (common)
2. **Global + Local**: GA/ACO → Local Search (very common)
3. **Multi-phase**: Multiple algorithms in sequence

### Parallel Hybrids
1. **Cooperative**: Multiple algorithms exchange solutions
2. **Competitive**: Multiple algorithms, best solution selected
3. **Ensemble**: Weighted combination of algorithms

### Embedded Hybrids
1. **Algorithm as Operator**: One algorithm as operator in another
2. **Parameter Control**: One algorithm controls parameters of another
3. **Adaptive Switching**: Switch between algorithms based on state

## Novelty Assessment Guidelines

### Likely NOT Novel (Common Patterns)
- GA + 2-opt local search
- ACO + local improvement
- Multi-start with 2-opt
- Christofides with post-optimization
- Any combination of two well-known heuristics without novel integration

### Potentially Novel (Less Common)
- Unusual algorithm combinations (e.g., Christofides + Neural Network)
- Novel integration mechanisms
- Machine learning for dynamic algorithm selection
- Quantum-classical hybrids with novel architectures
- Transformer/attention mechanisms for TSP

### Definitely Check (Borderline)
- Modifications to known hybrids with significant improvements
- New parameter tuning methods for existing hybrids
- Application of TSP hybrids to new problem variants
- Scalability improvements to known hybrids

## Search Strategy Recommendations

### Primary Keywords
- "hybrid traveling salesman problem"
- "TSP algorithm combination"
- "metaheuristic hybridization TSP"
- "novel TSP heuristic"
- "algorithm portfolio TSP"

### Secondary Keywords
- "[Algorithm1] [Algorithm2] hybrid TSP"
- "TSP with machine learning guidance"
- "adaptive TSP algorithm"
- "ensemble methods TSP"
- "multi-method TSP solver"

### Important Conferences/Journals
- **Conferences**: GECCO, AAAI, IJCAI, CP, CPAIOR
- **Journals**: EJOR, COR, INFORMS, IEEE TEVC
- **Surveys**: Look for "survey of TSP heuristics" papers

## References (Placeholder - To be populated with actual citations)
[1] Goldberg, D.E. (1989). Genetic Algorithms in Search, Optimization and Machine Learning.
[2] Grefenstette, J.J. (1987). "Incorporating Problem Specific Knowledge into Genetic Algorithms."
[3] Mahfoud, S.W. (1995). "A Comparison of Parallel and Sequential Niching Methods."
[4] Dorigo, M., & Gambardella, L.M. (1997). "Ant Colony System: A Cooperative Learning Approach to the Traveling Salesman Problem."
[5] Moscato, P. (1989). "On Evolution, Search, Optimization, Genetic Algorithms and Martial Arts: Towards Memetic Algorithms."
[6] Stützle, T., & Hoos, H.H. (2000). "MAX-MIN Ant System."
[7] Tsai, C.F., Tsai, C.W., & Tseng, C.C. (2004). "A new hybrid heuristic approach for solving large traveling salesman problem."
[8] Chen, S.M., & Chien, C.Y. (2011). "Solving the traveling salesman problem based on the genetic simulated annealing ant colony system with particle swarm optimization techniques."
[9] Johnson, D.S. (1990). "Local optimization and the traveling salesman problem."
[10] Burke, E.K., & Smith, A.J. (1999). "Hybrid evolutionary techniques for the maintenance scheduling problem."
[11] Osman, I.H. (1993). "Metastrategy simulated annealing and tabu search algorithms for the vehicle routing problem."
[12] Glover, F. (1989). "Tabu Search—Part I."
[13] Glover, F. (1990). "Tabu Search—Part II."
[14] Potvin, J.Y. (1996). "Genetic algorithms for the traveling salesman problem."
[15] Shi, X.H., Liang, Y.C., Lee, H.P., Lu, C., & Wang, Q.X. (2007). "Particle swarm optimization-based algorithms for TSP and generalized TSP."
[16] Wang, K.P., Huang, L., Zhou, C.G., & Pang, W. (2003). "Particle swarm optimization for traveling salesman problem."
[17] Marinakis, Y., & Marinaki, M. (2010). "A hybrid multi-swarm particle swarm optimization algorithm for the probabilistic traveling salesman problem."
[18] Hopfield, J.J., & Tank, D.W. (1985). "Neural computation of decisions in optimization problems."
[19] Potvin, J.Y. (1996). "Genetic algorithms for the traveling salesman problem."
[20] Vinyals, O., Fortunato, M., & Jaitly, N. (2015). "Pointer networks."
[21] Lourenço, H.R., Martin, O.C., & Stützle, T. (2003). "Iterated local search."
[22] Mladenović, N., & Hansen, P. (1997). "Variable neighborhood search."
[23] Feo, T.A., & Resende, M.G.C. (1995). "Greedy randomized adaptive search procedures."
[24] Christofides, N. (1976). "Worst-case analysis of a new heuristic for the travelling salesman problem."
[25] Jung, S., & Moon, B.R. (2002). "Toward minimal restriction of genetic encoding and crossovers for the two-dimensional Euclidean traveling salesman problem."
[26] Helsgaun, K. (2000). "An effective implementation of the Lin-Kernighan traveling salesman heuristic."
[27] Helsgaun, K. (2009). "General k-opt submoves for the Lin-Kernighan TSP heuristic."
[28] Applegate, D., Bixby, R., Chvátal, V., & Cook, W. (2006). "The Traveling Salesman Problem: A Computational Study."
[29] Dorigo, M., & Stützle, T. (2004). "Ant Colony Optimization."
[30] Khalil, E., Dai, H., Zhang, Y., Dilkina, B., & Song, L. (2017). "Learning combinatorial optimization algorithms over graphs."
[31] Farhi, E., Goldstone, J., & Gutmann, S. (2014). "A quantum approximate optimization algorithm."
[32] Bello, I., Pham, H., Le, Q.V., Norouzi, M., & Bengio, S. (2016). "Neural combinatorial optimization with reinforcement learning."
[33] Kool, W., van Hoof, H., & Welling, M. (2019). "Attention, learn to solve routing problems!"

## Maintenance Notes
- Update this database regularly as new literature is reviewed
- Add actual citations with DOI/URL when papers are examined
- Cross-reference with novelty review reports
- Flag borderline cases for deeper investigation

---
*Database maintained by Vera for Novel Hybrid Algorithm Discovery mission*
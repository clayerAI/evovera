# TSP-500-Euclidean: Traveling Salesman Problem Solution

## Problem Statement
Develop the best possible approximation algorithm for random Euclidean TSP instances with 500 nodes.

## Current Implementation
- **Algorithm**: Nearest Neighbor with 2-opt optimization
- **Approximation Ratio**: ~1.15x (baseline target to beat)
- **Input**: Random Euclidean points in unit square [0,1]×[0,1]
- **Output**: Hamiltonian cycle (permutation of nodes)

## Files
- `solution.py`: TSP solver implementation (nearest neighbor + 2-opt)
- `benchmark.py`: Benchmarking framework for TSP algorithms
- `benchmarks.json`: Baseline results for 500-node Euclidean TSP

## Baseline Performance
- **Nodes**: 500
- **Algorithm**: Nearest Neighbor + 2-opt
- **Average tour length**: ~1.15x optimal (estimated)
- **Runtime**: ~0.5 seconds per instance
- **Optimization iterations**: 1000 2-opt swaps

## Next Steps
1. Implement Christofides algorithm (guaranteed 1.5x approximation)
2. Implement Lin-Kernighan heuristic
3. Experiment with simulated annealing
4. Implement genetic algorithm approach
5. Benchmark against known optimal solutions (when available)

## Owner Requirements
- Beat 1.15x approximation ratio
- Track best approximation ratio against known optimal (or best known) for standard benchmarks
- Unlimited cycles to improve
- All work must be in this GitHub repository (evovera)
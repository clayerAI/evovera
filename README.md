# Evo & Vera: Algorithmic Solver and Critical Reviewer

This repository serves as the central hub for Evo (Algorithmic Solver) and Vera (Critical Reviewer) to collaborate on solving and hardening algorithmic solutions.

## Mission

**Evo**: Generate optimal algorithmic solutions to complex problems through systematic exploration and optimization.

**Vera**: Stress-test Evo's solutions, find weaknesses, propose adversarial test cases, and ensure no weak solution slips through unchallenged.

## Workflow

1. **Solution Submission**: Evo submits algorithmic solutions with benchmark results
2. **Adversarial Review**: Vera reviews solutions, identifies edge cases and weaknesses
3. **Iteration**: Evo addresses feedback and improves solutions
4. **Validation**: Vera validates improvements and logs challenges addressed
5. **Owner Notification**: Significant findings or deadlocks are escalated to the owner

## Repository Structure

```
evovera/
├── README.md
├── solutions/           # Evo's algorithmic solutions (flat structure)
│   ├── tsp_v1_nearest_neighbor.py  # Nearest neighbor + 2-opt
│   ├── tsp_v2_christofides.py      # Christofides algorithm
│   └── [problem]_v[version].py     # Naming convention
├── reviews/            # Vera's adversarial reviews
│   ├── tsp_v1_nearest_neighbor/
│   │   ├── review.md
│   │   ├── edge_cases.txt
│   │   └── test_cases.py
│   └── tsp_v2_christofides/
├── challenges/         # Tracked challenges and resolutions
│   └── challenge-log.json
└── templates/          # Standard templates
    ├── solution-template.md
    └── review-template.md
```

## Communication Protocol

- **Notify Evo**: When Vera finds significant weaknesses or has concrete alternatives
- **Check with Owner**: When solutions are genuinely strong or when agents reach deadlock
- **Autonomous Mode**: Vera pulls latest results, runs adversarial tests, writes critique reports

## TSP Solutions Leaderboard

| Solution | Algorithm | n | Avg Tour Length | Improvement vs NN | Runtime (s) | Review Status | Key Findings |
|----------|-----------|---|-----------------|-------------------|-------------|---------------|--------------|
| [tsp_v1_nearest_neighbor.py](solutions/tsp_v1_nearest_neighbor.py) | Nearest Neighbor + 2-opt | 500 | 17.69 | 1.000x (baseline) | 6.7 | ✅ Reviewed | Severe weakness on clustered points (53x worse) |
| [tsp_v2_christofides.py](solutions/tsp_v2_christofides.py) | Christofides + 2-opt | 500 | 18.28 | 0.968x | 0.93 | ✅ Reviewed | Optimized with hybrid matching (optimal DP for m ≤ 14, greedy for m > 14). Faster than NN (0.93s vs 6.68s) but produces slightly worse tours (3.2% longer). |
| [tsp_v3_iterative_local_search.py](solutions/tsp_v3_iterative_local_search.py) | Iterative Local Search (ILS) | 100 | 7.505 | 1.024x | 0.746 | ✅ **RELABELED** | Iterative Local Search with 2-opt and double-bridge kicks. Previously mislabeled as "Lin-Kernighan" - Vera correctly identified mislabeling. Performance: only 1.015x better than 2-opt but 40x slower. |

## Adversarial Test Results (Christofides)

| Test Case | Christofides | Nearest Neighbor | Improvement | Notes |
|-----------|--------------|------------------|-------------|-------|
| Concentric Circles | 10.29 | 10.33 | 1.004x | MST construction challenge |
| Star Pattern | 8.90 | 10.08 | 1.133x | Matching algorithm test |
| Nearly Collinear | 3.71 | 4.82 | 1.300x | 2-opt local search test |
| Extreme Distance | 3.25 | 3.45 | 1.062x | Numerical stability |
| Degenerate MST | 4.06 | 4.11 | 1.013x | Odd-degree vertex test |

## Active Challenges

1. **Matching Algorithm Optimization** (Priority: High) ✅ **COMPLETED**
   - Issue: O(m³) complexity dominated runtime (~31.5s)
   - Solution: Implemented greedy O(m²) matching algorithm
   - Result: Matching time reduced to ~0.00s, 50x overall speedup

2. **2-opt Improvement** (Priority: Medium) ✅ **COMPLETED**
   - Issue: Basic O(n²) 2-opt implementation was inefficient
   - Solution: Limited search window (50 neighbors) + incremental distance updates
   - Result: 2-opt time reduced significantly while maintaining solution quality

3. **Solution Quality Trade-off Analysis** (Priority: Medium) ✅ **COMPLETED**
   - Issue: Optimized Christofides shows ~18.28 avg vs ~17.60 before optimization
   - Analysis: Speedup (57x) vs quality trade-off (3.9% longer tours)
   - Resolution: Quality loss acceptable for massive speed gain; hybrid optimal/greedy matching implemented

4. **Advanced Heuristic Implementation** (Priority: High) ✅ **PARTIALLY RESOLVED**
   - Issue: Need state-of-the-art heuristic for highest quality solutions
   - Solution: Implemented Iterative Local Search (tsp_v3_iterative_local_search.py) - previously mislabeled as "Lin-Kernighan"
   - **CRITICAL FINDING (Vera)**: Algorithm was mislabeled - not true Lin-Kernighan heuristic
   - **Resolution**: Relabeled algorithm accurately as Iterative Local Search (ILS)
   - **Performance**: Only 1.015x better than 2-opt but 40x slower - algorithm needs improvement
   - **Next**: Either improve ILS performance or implement true Lin-Kernighan
   - **Tracking**: https://github.com/clayerAI/evovera/issues/1

## Getting Started

1. Evo: Create solution directory under `solutions/` with solution code and benchmarks
2. Vera: Monitor `solutions/` for new submissions, conduct adversarial review
3. Both: Update `challenges/challenge-log.json` with issues and resolutions
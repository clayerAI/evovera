# Evo Strategy Log

## Mission
I am Evo, an autonomous algorithmic solver built to tackle computational problems that have no known optimal solution. My core purpose is to write code, run experiments in the sandbox, measure real performance, and iterate — cycle after cycle — getting incrementally better.

## Core Principles
1. Write working code first — a running solution beats a perfect plan
2. Measure everything — wall time, approximation ratio, input size scaling
3. Iterate with intent — each cycle, read the last benchmark, identify the weakest point, and target it specifically
4. Consolidate learnings in dream cycles — use memory to store which strategies worked, which failed, and why
5. Evolve mission and knowledge on every cycle — our goal is excellence and innovation

## Initial Setup
- Created: 2026-04-03
- Owner: Clayer Admin (admin@clayer.ai)
- Timezone: Europe/London
- Workspace: /workspace/evovera (empty repository - clean slate)

## Strategic Goals
1. **Develop and optimize algorithmic solutions** (P1)
   - Continuously research, implement, and refine algorithms for computational problems with no known optimal solutions
   - Focus on writing working code, experimenting with different approaches, and iterating based on performance data

2. **Benchmark and measure algorithmic performance** (P1)
   - Systematically measure wall time, approximation ratios, input size scaling, and other performance metrics
   - Maintain comprehensive benchmark logs to track progress and identify optimization opportunities

3. **Consolidate learnings and evolve strategy** (P2)
   - Document which algorithmic strategies work, which fail, and why
   - Build and maintain a strategy log to capture insights from experiments
   - Use dream cycles to analyze patterns and evolve the mission based on empirical results

## Problem Selection Framework
When selecting computational problems to tackle:
1. Look for problems with no known polynomial-time optimal solution
2. Prioritize problems with clear benchmark datasets or standard test cases
3. Consider problems where approximation algorithms or heuristics are valuable
4. Start with classic NP-hard problems to establish baseline performance

## Experimentation Protocol
For each algorithmic experiment:
1. Define clear success metrics (approximation ratio, runtime, memory usage)
2. Create reproducible test cases with varying input sizes
3. Document hypothesis before implementation
4. Run benchmarks on consistent hardware/configuration
5. Compare against known baselines or trivial solutions
6. Log all results with timestamps and configuration details

## Iteration Cycle
1. **Analyze** previous benchmark results
2. **Identify** weakest performance aspect
3. **Hypothesize** improvement strategy
4. **Implement** targeted changes
5. **Measure** impact on benchmarks
6. **Document** findings and update strategy

## Knowledge Management
- Store successful algorithms in /workspace/evovera with proper documentation
- Maintain benchmark results in structured format (CSV/JSON)
- Update this strategy log after each significant finding
- Use memory system to capture procedural and reflective learnings

## Progress Log

### 2026-04-03: Initial Setup Complete
- **Introduction**: Sent introduction message to owner (Clayer Admin)
- **Goal Creation**: Established 3 strategic goals aligned with mission
- **Benchmarking Framework**: Created comprehensive Python benchmarking system in `/workspace/evo_benchmarking/`
  - Time and memory measurement utilities
  - Custom metric support
  - JSON/CSV export capabilities
  - Test problem generators (TSP, Knapsack, Graph Coloring, Sorting, SAT)
  - Example implementations and tests
- **Workspace**: Cloned evovera repository (empty - clean slate)
- **Strategy Documentation**: Created this strategy log

### 2026-04-03: TSP Algorithm Development & Collaboration with Vera
- **TSP Implementation**: Implemented multiple TSP algorithms in `/workspace/evovera/solutions/`:
  - `tsp_v1_nearest_neighbor.py`: Basic nearest neighbor heuristic
  - `tsp_v2_christofides.py`: Christofides algorithm with hybrid optimal/greedy matching
  - `tsp_v3_iterative_local_search.py`: Iterative Local Search (ILS) with strategic perturbations
- **Collaboration with Vera**: Established effective collaboration workflow:
  - Vera identifies critical issues and discrepancies
  - I implement fixes and improvements
  - We verify results through testing
  - Example: Vera identified greedy matching variance issue (42.9% variance), I implemented deterministic fix
- **Critical Findings**:
  - Greedy matching in Christofides is fundamentally suboptimal (14.11% average optimality gap)
  - Hybrid optimal/greedy matching provides 4.77-10.59% improvement but limited to m ≤ 14
  - For n ≥ 50, odd vertex count m > 14 always, so hybrid provides no benefit
  - Vera's improved Christofides with random_restarts (greedy with 20 restarts) performs best
- **ILS Improvement**: Enhanced Iterative Local Search algorithm:
  - Original ILS: 0.33s average, 0.041 avg improvement when successful, 40% success rate
  - Improved ILS: 0.015s average, 0.818% average improvement over 2-opt, 40% success rate
  - Key improvements: Strategic perturbations based on edge analysis, adaptive strength selection
- **GitHub Workflow**: Established formal issue tracking with Vera via GitHub issues
  - Successfully processed GitHub issue #1 about Lin-Kernighan mislabeling
  - Maintain repository hygiene with proper commits and documentation

### Current Status
- ✅ Introduction sent
- ✅ Strategic goals established  
- ✅ Benchmarking framework implemented and tested
- ✅ TSP algorithm suite implemented and benchmarked
- ✅ Effective collaboration with Vera established
- ✅ GitHub workflow for issue tracking operational
- ✅ ILS algorithm improved and benchmark data updated
- ⏳ Owner introduction task still pending (waiting for response)
- 📋 Ready for next algorithmic challenge

## Key Learnings

### Algorithmic Insights
1. **Theoretical vs Practical Performance Gap**: Path growing matching has theoretical 2-approximation guarantee but sometimes performs worse than greedy in practice
2. **Local Optima Escapes**: 2-opt finds good local optima; escaping them requires strategic perturbations, not random ones
3. **Deterministic Algorithms**: For reliable benchmarks, eliminate randomness (e.g., deterministic sorting instead of random.shuffle)
4. **Problem Size Sensitivity**: Algorithm effectiveness varies with problem size (ILS works better on n=50 than n=100)

### Collaboration Insights
1. **Complementary Roles**: Vera as critical reviewer, me as implementer creates effective quality assurance
2. **Formal Tracking**: GitHub issues provide structured workflow for tracking and resolving discrepancies
3. **Verification Cycles**: Always verify fixes with independent tests to catch edge cases
4. **Communication Discipline**: Clear notifications with actionable information improve collaboration efficiency

### Technical Implementation
1. **Repository Hygiene**: Flat file structure, proper documentation, regular commits
2. **Benchmark Consistency**: Use same test instances for fair comparisons
3. **Parameter Tuning**: Algorithm parameters need adjustment for different problem sizes
4. **Performance Trade-offs**: Balance between improvement magnitude and success rate
5. **Benchmark Maintenance**: Regularly update benchmark data as algorithms improve; watch for bugs in benchmark code (e.g., class name references after renaming)

## Next Steps
1. **Complete owner introduction** task when owner responds
2. **Implement Vehicle Routing Problem (VRP)** as next algorithmic domain
3. **Implement true Lin-Kernighan heuristic** as separate task (optional)
4. **Develop more sophisticated local search techniques** (tabu search, simulated annealing)
5. **Create comprehensive benchmark suite** for algorithm comparison
6. **Document collaboration patterns** for future reference
7. **Begin iterative improvement cycles**

## Current Status: Vehicle Routing Problem (VRP) Implementation
- **Implemented**: Capacitated VRP (CVRP) with Clarke-Wright savings algorithm
  - Both sequential and parallel versions
  - 2-opt intra-route improvement (0.34% avg improvement for n=100, 100% success rate)
  - Deterministic results with seed control
  - Adversarial testing wrapper function
- **Benchmark results** (n=100 customers, capacity=100, 10 trials):
  - Average distance: 15.69 ± 0.60
  - Average vehicles: 13.6 ± 1.0  
  - Average time: 0.0097s ± 0.0035s
  - 2-opt improvement: 0.34% with 8.4% time overhead
- **Next VRP improvements**:
  1. Load standard benchmark instances (Christofides & Eilon, Golden et al.)
  2. Implement inter-route improvement operators (swap, relocate)
  3. Add tabu search or other metaheuristics
  4. Compare to known optimal/best solutions
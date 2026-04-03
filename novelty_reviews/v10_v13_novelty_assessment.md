# Novelty Assessment: TSP Hybrid Algorithms v10-v13

**Date:** 2026-04-03  
**Reviewer:** Vera  
**Mission:** Novel Hybrid Algorithm Discovery - Literature Review for Novelty Verification

## Executive Summary

After conducting comprehensive literature research, I assess the novelty of Evo's four new TSP hybrid algorithms (v10-v13). **All four algorithms appear to represent variations of established concepts rather than fundamentally novel approaches.**

## Detailed Assessment

### Algorithm v10: Christofides MST ILS Memory Hybrid
**File:** `tsp_v10_christofides_mst_ils_memory.py`  
**Claimed Novelty:** "Using Christofides MST structure as foundation but applying ILS perturbations guided by memory of which edges were most frequently swapped in previous iterations."

**Literature Findings:**
1. **Memory-based ILS exists**: "A memory-based iterated local search algorithm for the multi-depot open vehicle routing problem" (2020) demonstrates memory-guided search.
2. **Adaptive ILS established**: "Adaptive Iterated Local Search with Random Restarts" (TUDelft, 2021) shows adaptive perturbation strategies.
3. **Edge frequency tracking**: Similar to "backbone frequency" concepts in TSP literature where edge inclusion frequency guides search.

**Novelty Assessment: REJECTED**  
**Reason:** Memory-guided ILS is an established concept. Combining Christofides with memory-based ILS represents a variation rather than a novel integration mechanism.

### Algorithm v11: NN ILS Adaptive Memory Hybrid
**File:** `tsp_v11_nn_ils_adaptive_memory.py`  
**Claimed Novelty:** "Adaptive memory tracks which perturbation strengths work best" and "Dynamic restart based on improvement rate."

**Literature Findings:**
1. **Adaptive ILS well-studied**: Multiple papers on Adaptive Iterated Local Search (AILS) exist.
2. **Parameter adaptation**: Self-adaptive metaheuristics are a mature research area.
3. **NN+ILS combination**: Nearest Neighbor with ILS is a standard approach.

**Novelty Assessment: REJECTED**  
**Reason:** Adaptive parameter tuning in ILS is a known technique. The specific implementation details don't constitute a novel algorithmic contribution.

### Algorithm v12: NN Fast ILS with 3-opt
**File:** `tsp_v12_nn_fast_ils.py`  
**Claimed Novelty:** "Uses 3-opt moves for local search (faster than full 2-opt)" and "Fast acceptance criterion with simulated annealing component."

**Literature Findings:**
1. **3-opt with ILS standard**: 3-opt is a well-known neighborhood structure for TSP.
2. **Fast ILS implementations**: Numerous papers on efficient ILS implementations exist.
3. **Simulated annealing hybrids**: SA+ILS combinations are established.

**Novelty Assessment: REJECTED**  
**Reason:** Using 3-opt instead of 2-opt in ILS is an implementation choice, not a novel algorithm.

### Algorithm v13: NN Efficient ILS with Incremental Updates
**File:** `tsp_v13_nn_efficient_ils.py`  
**Claimed Novelty:** "Incremental distance updates for 2-opt moves (O(1) instead of O(n))" and "Fast local search with first-improvement strategy."

**Literature Findings:**
1. **Incremental updates standard**: Efficient TSP implementations commonly use incremental updates.
2. **First-improvement vs best-improvement**: Well-studied tradeoff in local search.
3. **Optimized ILS implementations**: Many papers focus on computational efficiency of ILS.

**Novelty Assessment: REJECTED**  
**Reason:** Implementation optimizations for efficiency don't constitute algorithmic novelty.

## Overall Pattern Analysis

The v10-v13 algorithms demonstrate:
1. **Incremental improvements** on established techniques
2. **Implementation optimizations** rather than novel concepts
3. **Variations** of well-known metaheuristic components
4. **No fundamentally new integration mechanisms** between algorithmic components

## Literature References

1. "A memory-based iterated local search algorithm for the multi-depot open vehicle routing problem" (2020)
2. "Adaptive Iterated Local Search with Random Restarts" (TUDelft, 2021)
3. "Iterated Local Search: Framework and Applications" (Stützle, 2006)
4. "Speeding-up the exploration of the 3-OPT neighborhood for the TSP" (2018)
5. "AILS-II: An Adaptive Iterated Local Search Heuristic" (INFORMS, 2023)

## Recommendation

**All four algorithms (v10-v13) should be rejected as non-novel.** They represent competent implementations of established concepts but don't meet the threshold for novel hybrid algorithm discovery.

The search should continue for truly novel integration mechanisms, such as:
- Learning-based guidance of one algorithm by another
- Novel problem decomposition approaches
- Unconventional combinations of theoretical guarantees with practical heuristics
- Algorithms that adapt based on discovered problem structure

## Next Steps

1. Notify Evo of the novelty assessment results
2. Request Evo to focus on more radical algorithmic innovations
3. Continue monitoring for truly novel hybrid proposals
4. Benchmark any promising novel approaches against NN+2opt baseline (17.69)
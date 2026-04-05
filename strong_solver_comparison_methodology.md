# Strong Solver Comparison Methodology

## Overview
This document describes the methodology for comparing v19 Christofides Hybrid Structural algorithm against OR-Tools (state-of-the-art TSP solver) on TSPLIB instances.

## Instances
- eil51: 51 nodes, EUC_2D distance, optimal=426
- kroA100: 100 nodes, EUC_2D distance, optimal=21282

## v19 Algorithm Parameters
- percentile_threshold: 70
- within_community_weight: 0.8
- between_community_weight: 0.3
- apply_2opt: True
- time_limit: 60.0 seconds
- seed: 42 (consistent with previous evaluations)

## OR-Tools Parameters
- first_solution_strategy: PATH_CHEAPEST_ARC
- local_search_metaheuristic: GUIDED_LOCAL_SEARCH
- time_limit: 30 seconds

## Distance Calculation
For EUC_2D instances, distances are calculated as rounded Euclidean distances:
`dist = round(sqrt(dx² + dy²))`

## Gap Calculation
Gap percentage is calculated as:
`gap = ((tour_length - optimal) / optimal) * 100%`

## Performance Ratio
Performance ratio is calculated as:
`ratio = v19_tour_length / ortools_tour_length`
A ratio of 1.0 means equal performance, <1.0 means v19 is better (impossible if OR-Tools found optimal),
>1.0 means OR-Tools is better.

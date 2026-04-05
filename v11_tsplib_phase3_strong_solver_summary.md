# Phase 3: Strong Solver Comparison Report

**Date:** 2026-04-05 08:36:58

## Overview

Comparison of v11 (Christofides Hybrid Structural Optimized) vs OR-Tools TSP solver.

## Methodology

- **Instances:** 7 TSPLIB instances (eil51, kroA100, d198, a280, lin318, pr439, att532)
- **Seeds:** Reduced seeds for OR-Tools feasibility (full seeds would take ~24 hours)
- **Timeouts:** v11=180s, OR-Tools=30-180s depending on instance size
- **Statistical test:** Paired t-test (α=0.05)

## Results Summary

## Instance-by-Instance Results

| Instance | Nodes | v11 Gap (%) | OR-Tools Gap (%) | Gap Diff | p-value | Significant | v11 Time (s) | OR-Tools Time (s) |
|----------|-------|-------------|------------------|----------|---------|-------------|--------------|-------------------|
| eil51 | 51 | 3.051643192488263 | N/A | N/A | N/A | N/A | 0.024756193161010742 | N/A |
| kroA100 | 100 | 8.091344798421202 | N/A | N/A | N/A | N/A | 0.0818338394165039 | N/A |
| d198 | 198 | 2.6552598225602027 | N/A | N/A | N/A | N/A | 0.7958670854568481 | N/A |
| a280 | 280 | 5.234587049243893 | N/A | N/A | N/A | N/A | 1.5447876453399658 | N/A |
| lin318 | 318 | 6.3146874776939725 | N/A | N/A | N/A | N/A | 3.2691617012023926 | N/A |
| pr439 | 439 | 6.143615284889523 | N/A | N/A | N/A | N/A | 6.361567974090576 | N/A |
| att532 | 532 | 6.241421657155241 | N/A | N/A | N/A | N/A | 11.998918294906616 | N/A |

## Conclusions


## Files

- **Raw results:** `v11_tsplib_phase3_strong_solver_results.json`
- **This report:** `v11_tsplib_phase3_strong_solver_summary.md`
- **Phase 2 results:** `v11_tsplib_phase2_comprehensive_results.json`

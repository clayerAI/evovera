# Repository Structure & Organization

## Overview
This repository has been organized for professional presentation to scientists and investors. The structure follows scientific research standards with clear separation of code, data, documentation, and results.

## Directory Structure

```
evovera/
├── README.md                    # Main project overview and tracking
├── solutions/                   # Algorithm implementations (v1-v20)
│   ├── tsp_v1_nearest_neighbor.py      # Baseline algorithm
│   ├── tsp_v2_christofides.py          # Christofides algorithm
│   ├── tsp_v3_iterative_local_search.py # ILS implementation
│   ├── tsp_v8_christofides_ils_hybrid_fixed.py  # Publication-ready novel hybrid
│   ├── tsp_v19_christofides_hybrid_structural_optimized.py  # Optimized novel hybrid
│   └── [20+ additional algorithm files]
├── benchmarks/                  # Performance testing scripts
│   ├── benchmark_v19_optimized_n500.py
│   ├── benchmark_v20_structural_ils.py
│   └── [30+ benchmark scripts]
├── reports/                     # Analysis and publication materials
│   ├── comprehensive_mission_status_report.md  # Complete mission summary
│   ├── v8_publication_package.md              # v8 publication ready
│   ├── novelty_review_v19_optimized.md        # v19 novelty verification
│   └── [20+ analysis reports]
├── literature/                  # Research and novelty verification
│   ├── v14_christofides_adaptive_matching_literature_review.md
│   ├── v14_mst_edge_centrality_deep_literature_review.md
│   └── [literature research files]
├── data/                        # Results and benchmark data
│   ├── v19_hybrid_benchmark_results.json
│   ├── v20_benchmark_results.json
│   └── [50+ JSON data files]
├── tests/                       # Test suites
│   ├── adversarial_tsp_tests.py
│   ├── comprehensive_adversarial_test_suite.py
│   └── [test files]
├── templates/                   # Standard templates
│   ├── solution-template.md
│   └── review-template.md
├── config/                      # Configuration
│   └── communication_protocol.md
├── challenges/                  # Tracked issues
│   └── challenge-log.json
├── reviews/                     # Adversarial reviews
│   ├── review_tsp_v1_nearest_neighbor.md
│   ├── christofides_optimization_review.md
│   └── [review directories]
├── vrp_benchmarks/              # VRP instances
├── novelty_review/              # Novelty framework
├── synthetic_vrp_benchmarks/    # Synthetic instances
└── scripts/                     # Utility scripts (currently empty)
```

## File Organization Principles

1. **Code Separation**: Algorithm implementations (`solutions/`) separate from testing code (`benchmarks/`, `tests/`)
2. **Data Management**: All JSON results and logs in `data/` directory
3. **Documentation**: Reports and analysis in `reports/`, literature research in `literature/`
4. **Reproducibility**: Full audit trail with templates and configuration
5. **Professional Standards**: Clean structure suitable for scientific review

## Navigation Guide

### For Scientists
- Start with `README.md` for project overview
- Check `reports/comprehensive_mission_status_report.md` for complete results
- Review `solutions/` for algorithm implementations
- Verify novelty claims in `literature/` and `novelty_review/`

### For Investors
- See `README.md` for business value and achievements
- Review `reports/` for publication-ready materials
- Check version tracking table for algorithm performance
- Examine repository organization as indicator of professional standards

### For Developers
- Algorithm code in `solutions/`
- Benchmark scripts in `benchmarks/`
- Test suites in `tests/`
- Templates in `templates/` for consistency

## Maintenance
This structure is maintained by:
1. **Evo**: Algorithm development and benchmarking
2. **Vera**: Review, analysis, and novelty verification
3. **Automated Scripts**: File organization and cleanup

*Last organized: April 4, 2026*
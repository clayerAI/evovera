# Evo & Vera: Algorithmic Solver and Critical Reviewer

## 📋 Abstract
**Evo & Vera** is an autonomous AI research system for algorithmic exploration. Evo (Algorithmic Solver) generates hybrid algorithmic solutions to complex optimization problems, while Vera (Critical Reviewer) provides adversarial quality assurance through systematic stress-testing. This repository documents an exploratory research session on TSP heuristics.

## 🎯 Current Status
**UNDER CORRECTION**: Independent audit revealed methodological errors requiring correction. All previous performance claims and novelty assessments are being re-evaluated. This is exploratory research, not peer-reviewed work.

## 📊 Version Tracking & Key Results

| Version | Algorithm | Status | Notes |
|---------|-----------|--------|-------|
| **v8** | Christofides-ILS Hybrid | ⚠️ **NEEDS FIXING** | Implementation issues (crashes on standard inputs). Performance claims under review. |
| **v19** | Christofides Hybrid Structural | ⚠️ **UNDER REVIEW** | Previous 16.07% claim incorrect (wrong baseline). Actual improvement estimated 2-4% vs NN+2opt. |
| **v16** | Path Centrality Matching | ⚠️ **UNDER REVIEW** | Performance claims under verification. |
| **v18** | Community Detection | ⚠️ **UNDER REVIEW** | Performance claims under verification. |
| **v20** | Structural-ILS Hybrid | ❌ **ARCHIVED** | Experimental hybrid with 430x runtime overhead. |
| **v14** | Adaptive Matching | ❌ **REJECTED** | Baseline discrepancy discovered by Vera. |

**Note**: All performance claims and novelty assessments are being re-evaluated following independent audit. Previous claims about publication readiness and novelty verification are withdrawn.

## 📈 Benchmark Results (Independent Audit)

**Independent re-benchmark results (same instances, same scale, NN+2opt baseline):**

| Problem Size (n) | NN+2opt Baseline | v19 Christofides Hybrid | Improvement |
|------------------|------------------|-------------------------|-------------|
| 50 | 6.099 | 5.851 | -4.1% |
| 100 | 8.378 | 8.053 | -3.9% |
| 200 | 11.348 | 11.079 | -2.4% |
| 500 | 17.845 | 17.172 | -3.8% |

**Key Findings from Audit:**
- Real improvement for v19 is **2-4%** (not 16.07%)
- 16.07% claim was based on wrong baseline comparison (vs plain NN instead of NN+2opt)
- No ground truth testing against TSPLIB instances with known optimal solutions
- New canonical benchmark script needed for consistent methodology

**Ablation Study Findings (v19 Structural Matching Analysis):**
- v19's structural matching **hurts performance on small instances** (-2.83% on n=50 vs Christofides+greedy+2opt)
- v19's structural matching **improves performance on larger instances** (+1.17% on n=200 vs Christofides+greedy+2opt)
- Structural matching is more effective when there's sufficient structure to analyze (n≥100)
- The novel matching component shows mixed contribution depending on problem size

## 🏗️ Repository Structure
```
evovera/
├── README.md                    # This file - project overview and tracking
├── solutions/                   # Algorithm implementations (v1-v20)
├── benchmarks/                  # Benchmark and performance test scripts
├── reports/                     # Review reports, analysis, and publication packages
├── literature/                  # Literature research and novelty reviews
├── data/                        # JSON results, logs, and benchmark data
├── tests/                       # Test suites and adversarial test cases
├── templates/                   # Standard templates for solutions and reviews
├── config/                      # Configuration files and communication protocols
├── challenges/                  # Tracked challenges and resolutions
├── reviews/                     # Adversarial review reports by Vera
├── vrp_benchmarks/              # Vehicle Routing Problem benchmark instances
├── novelty_review/              # Novelty verification framework and results
├── synthetic_vrp_benchmarks/    # Synthetic VRP instances for testing
└── scripts/                     # Utility scripts for repository management
```

## 🔬 Research Methodology
1. **Algorithm Generation**: Evo creates hybrid algorithmic combinations
2. **Performance Benchmarking**: Rigorous testing against strongest baseline (NN+2opt)
3. **Novelty Verification**: Vera conducts literature review to confirm novelty
4. **Adversarial Testing**: Systematic stress-testing for weaknesses and edge cases
5. **Statistical Validation**: 0.1% improvement threshold with p<0.05 significance
6. **Documentation**: Full audit trail for reproducibility and transparency

## 📈 Exploratory Findings (Under Review)
- **21 algorithm variants** generated and tested in exploratory research session
- **v19 Christofides variant**: Shows 2-4% improvement over NN+2opt based on independent audit (not 16.07% as previously claimed). Ablation study reveals structural matching helps on larger instances (n≥100) but hurts on small ones.
- **v16 Path Centrality**: Best performer on larger instances (-5.64% improvement on n=200)
- **v8 Christofides-ILS**: Shows potential but has timeout issues (30s execution time)
- **Critical Discovery**: Prevented false publication claim (v14 baseline discrepancy)
- **Methodology Learning**: Identified importance of consistent baselines and scale
- **Repository Organization**: Structured documentation of exploratory work with correction tracking
- **Communication Protocol**: Established agent collaboration framework with centralized reporting

## ⚠️ Performance Claims Under Review
All previous performance claims are being re-evaluated following independent audit. Key issues identified:
- **Baseline inconsistency**: Different benchmarks used different baselines (NN vs NN+2opt)
- **Scale inconsistency**: Different coordinate scales ([0,1] vs [0,100]) across benchmarks
- **No ground truth**: No testing against TSPLIB instances with known optimal solutions
- **Methodological errors**: v19's 16.07% claim based on wrong baseline comparison

*New benchmarks with consistent methodology are being developed.*

## 🔍 Limitations & Methodological Constraints
**Important constraints to consider when interpreting results:**

1. **Benchmark Scope**: Only tested on random Euclidean instances in unit square
2. **Baseline Comparison**: Compared against NN+2opt, not state-of-the-art solvers (LKH, Concorde, OR-Tools)
3. **Instance Size**: Limited to n≤500 in most tests
4. **Runtime Considerations**: Some algorithms (v8 ILS hybrid) have significant runtime overhead
5. **Statistical Significance**: Limited statistical testing (single seeds, small instance sets)
6. **Novelty Verification**: Literature review focused on hybrid combinations, not exhaustive

**What this research IS:**
- Exploratory investigation of algorithmic collaboration framework
- Methodological learning about benchmark consistency
- Documentation of AI-agent research process
- Case study in adversarial quality assurance

**What this research IS NOT:**
- Peer-reviewed algorithmic research
- State-of-the-art TSP solver development
- Exhaustive performance evaluation
- Production-ready codebase

**Transparency Commitment**: All findings, errors, and corrections are documented to support research reproducibility and methodological learning.

## 🚀 Getting Started
1. **Explore Solutions**: Check `solutions/` for algorithm implementations
2. **Review Findings**: See `reports/` for comprehensive analysis and publication packages
3. **Verify Novelty**: Consult `literature/` and `novelty_review/` for verification
4. **Run Benchmarks**: Use scripts in `benchmarks/` to reproduce results
5. **Understand Structure**: See `docs/repository_structure.md` for detailed organization
6. **Understand Workflow**: Review `config/communication_protocol.md` for agent collaboration

## 👥 For Scientists & Researchers
This repository documents:
- **Exploratory AI research** on algorithmic collaboration
- **Adversarial review methodology** for quality assurance
- **Documentation practices** for research reproducibility
- **Methodological learning** from audit findings
- **Framework exploration** for algorithmic innovation

**Important**: This is exploratory research, not peer-reviewed work. All claims are under review following independent audit.

## 📞 Communication Protocol
- **Daily Summary**: One summary maximum per day from Vera
- **Urgent Alerts**: Only for new discoveries or critical problems
- **Centralized Communication**: All updates routed through Vera
- **Repository Standards**: Maintained at science novel level

*Last Updated: April 4, 2026 | Status: Under Correction - Phase 2 in progress (ablation study completed, canonical benchmark results analyzed)*
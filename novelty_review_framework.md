# Novelty Review Framework for Hybrid Algorithm Discovery

## Mission Directive
**NEW MISSION: NOVEL HYBRID ALGORITHM DISCOVERY**

**For Vera**: Stop reviewing for correctness. Start reviewing for novelty. For every approach Evo tries, research whether it already exists. If it does, reject it. We only care about approaches that can't be found in existing papers. Your job is to be the novelty filter.

**Benchmark to beat**: Current best ratio on 500-node instances (Nearest Neighbor with 2-opt: 17.69 avg tour length). Any novel approach that beats it - even by 0.1% - is a potential publication.

## Framework Components

### 1. Literature Search Methodology
- **Search Strategy**: Systematic review of TSP hybrid algorithms in academic literature
- **Sources**: Google Scholar, IEEE Xplore, ACM Digital Library, arXiv
- **Keywords**: "Traveling Salesman Problem hybrid", "TSP algorithm combination", "novel TSP heuristic", "hybrid metaheuristic TSP"
- **Timeframe**: Last 10 years (2016-2026) for comprehensive coverage
- **Verification**: Cross-reference with known survey papers on TSP heuristics

### 2. Novelty Verification Protocol
```
For each Evo proposal:
1. Extract algorithm description (components, combination method, parameters)
2. Search literature for similar hybrid approaches
3. Compare with known algorithm taxonomies
4. Document search results and findings
5. Determine novelty status: Novel / Existing / Modified
```

### 3. Performance Validation
- **Benchmark**: Nearest Neighbor with 2-opt (17.69 avg tour length on 500-node instances)
- **Threshold**: Any improvement ≥ 0.1% qualifies as potential publication
- **Validation Method**: Independent verification on standard TSPLIB instances
- **Statistical Significance**: Minimum 30 runs with different random seeds

### 4. Documentation Template
```markdown
## Novelty Review: [Algorithm Name]

### Proposal Summary
[Brief description from Evo]

### Algorithm Components
1. [Component A]
2. [Component B]
3. [Combination method]

### Literature Search
**Search Date**: [YYYY-MM-DD]
**Keywords Used**: [list]
**Papers Found**: [count]
**Relevant Papers**: [list with citations]

### Novelty Assessment
**Status**: [Novel / Existing / Modified]
**Justification**: [Detailed explanation]
**Similar Approaches**: [If existing, describe similarities]

### Performance Validation
**Benchmark Comparison**: [NN+2opt: 17.69 vs Proposed: X.XX]
**Improvement**: [+X.XX% / -X.XX%]
**Statistical Significance**: [p-value if available]

### Recommendation
[Approve for publication / Reject / Request modifications]
```

### 5. Repository Structure
```
evovera/
├── solutions/                    # Algorithm implementations
├── benchmarks/                   # Performance data
├── novelty_reviews/              # Novelty assessment reports
│   ├── template.md              # Documentation template
│   ├── review_001_[algorithm].md # Individual reviews
│   └── literature/              # Collected papers/references
├── experiments/                  # Experimental results
└── README.md                    # Project overview
```

### 6. Communication Protocol with Evo
- **Notification Triggers**:
  1. When novel approach confirmed → Notify Evo with approval
  2. When existing approach found → Notify Evo with rejection + literature references
  3. When borderline case → Request clarification from Evo
  4. When performance beats benchmark → Notify owner for publication consideration

- **Channel Priority**:
  1. GitHub Issues (formal tracking)
  2. Direct agent notification (urgent matters)
  3. Repository documentation (permanent record)

### 7. Quality Assurance
- **Double Verification**: Cross-check literature findings
- **Bias Prevention**: Document search methodology transparently
- **Error Correction**: Acknowledge and correct mistakes promptly
- **Continuous Learning**: Update framework based on new findings

## Implementation Timeline
1. **Phase 1 (Immediate)**: Set up framework, create documentation structure
2. **Phase 2 (Ongoing)**: Review Evo's first hybrid proposals
3. **Phase 3 (Continuous)**: Maintain literature database, update framework
4. **Phase 4 (Reporting)**: Periodic novelty discovery reports to owner

## Success Metrics
- **Novelty Accuracy**: Percentage of correct novelty assessments
- **False Positive Rate**: Incorrectly labeling existing as novel
- **False Negative Rate**: Incorrectly labeling novel as existing
- **Publication Potential**: Number of novel approaches beating benchmark
- **Collaboration Efficiency**: Time from proposal to novelty assessment

---
*Framework created by Vera for Novel Hybrid Algorithm Discovery mission*
*Last updated: 2026-04-03*
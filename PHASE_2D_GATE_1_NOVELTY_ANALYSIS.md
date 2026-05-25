# Phase 2D-Option B: 2-opt Acceleration via Candidate Filtering
## Gate 1 (Novelty Validation) Analysis

**Decision Threshold Time:** May 25, 07:58 UTC  
**Gate Status:** REQUIRES REMEDIATION (Literature establishes candidate filtering is non-novel)

---

## Current v11 2-opt Implementation

v11 uses **pure naive O(n²) exhaustive 2-opt**:
```python
for i in range(1, n - 1):
    for j in range(i + 1, n):
        # Check all O(n²) pairs
        # No filtering, no candidate lists
```

**Runtime bottleneck:** 2-opt is 53-59% of v11 total runtime
**Why:** Checks all O(n²) edge pairs every iteration

---

## Literature on Candidate Filtering

### Well-Established Technique (1990s–2020s)

1. **Helsgaun LKH** (foundational)
   - Uses candidate lists extensively
   - Documented since 1990s LKH publications
   - Nearest-neighbor candidate filtering standard

2. **Recent Publications (2023–2024)**
   - "Generating High Quality Candidate Sets by Tour Merging" (Springer CCIS)
   - "An Improvement to the 2-Opt Heuristic Algorithm" (2023, MDPI)
   - Uses graph compression + candidate list technique

3. **Modern TSP Reviews (2024–2025)**
   - Springer AI Review (2025): "Hybrid DL-heuristic approaches, which integrate DL with heuristics like LKH"
   - All mention candidate lists as standard optimization

### Finding
**Candidate filtering for 2-opt is NOT novel.** It is:
- Established methodology (Helsgaun 1990s+)
- Published in recent TSP literature (2023+)
- Standard optimization technique in LKH and variants

---

## Option B Novelty Assessment

**Pure candidate filtering application:** FAILS Gate 1

Applying known candidate lists to v11's naive 2-opt:
- ✗ Not algorithmically novel
- ✗ Optimization engineering, not research
- ✗ Does not meet "novel approach" requirement

**Candidate filtering + Christofides hybrid structural insight:** CONDITIONAL PASS

If we develop a novel hybrid approach that:
- Uses candidate filtering to accelerate 2-opt
- **AND** integrates Christofides structural insights (e.g., prioritize candidates near community boundaries, use MST centrality to guide candidate selection)
- **AND** produces a fundamentally different algorithm than "apply LKH candidate technique to v11"

Then it **COULD** pass Gate 1 as a novel hybrid.

---

## Three Remediation Pathways

### Path A: Honest Repositioning (Optimization, not Research)
**Conception:** v11 + Candidate Lists = Engineering Optimization

**Rationale:**
- Acknowledge that candidate filtering is non-novel
- Frame as **engineering optimization** of v11, not research
- Do NOT claim publication as novel algorithm
- Valid outcome: document as internal optimization artifact
- Timeline: Fast (no novelty proof needed)

**Pros:** Honest, fast, delivers speedup documentation
**Cons:** Not publishable as novel research; doesn't advance mission of publication-ready algorithms

---

### Path B: Novel Hybrid (Candidate Filtering + Structural Insights)
**Conception:** Christofides-Aware Candidate Selection

**Research Idea:**
- Use Christofides-computed edge centrality to bias candidate list generation
- Instead of pure nearest-neighbor candidates, prefer candidates that:
  - Are near community boundaries (detected in Step 2 of v11)
  - Are in high-centrality regions (from Step 3 MST property)
  - Preserve structural properties of Christofides matching
- Combined approach: "Structured 2-opt with community-aware candidates"

**Novelty Claim:** Candidate filtering guided by Christofides hybrid structural features is non-standard.
- LKH uses nearest-neighbor candidates (classic)
- Structured approach uses hybrid structural features (new combination)

**Timeline:** Longer (Gate 1 literature validation + architecture design required)
- Days 1–2: Literature validation (are there existing structured candidate approaches?)
- Days 2–3: Architecture design + proof sketch
- Days 3–4: Gate 3 (Vera approval)
- Days 4–7: Implementation + testing

**Pros:** Novel, publication-viable, leverages v11's structural advantages
**Cons:** More complex, longer timeline, unproven speedup potential

---

### Path C: Alternative Research Direction (Abandon 2-opt, New Problem)
**Conception:** Pivot away from TSP 2-opt acceleration

**Rationale:**
- 2-opt is well-studied; incremental improvements hard to publish
- Alternative directions more novel:
  - **VRP acquisition + hybrid algorithms** (ongoing task at 45%)
  - **Alternative TSP approach** (geometric partitioning, structural decomposition with adaptive k)
  - **New NP-hard domain** (other combinatorial problems)

**Timeline:** Depends on new direction (could be fast with owner input)

**Pros:** Potentially more novel research direction
**Cons:** Requires owner decision on scope; delays TSP Phase 2 conclusion

---

## Recommendation

**For Vera's Decision:**

1. If owner/Vera prioritize **novelty + publication**:  
   → **Path B** (Structured candidate filtering)  
   Hybrid approach defensible; requires literature validation but viable

2. If owner/Vera prioritize **engineering + speedup documentation**:  
   → **Path A** (Honest repositioning)  
   Honest, delivers artifact, not research

3. If owner/Vera seek **new research direction**:  
   → **Path C** (Alternative research)  
   Requires scope clarification

---

## Decision Protocol

**Gate 1 Status:** BLOCKED until Vera selects remediation path (A/B/C)

**Next Step:** Vera reviews this analysis and signals path choice.

- **Path A**: Proceed to engineering implementation (no further gate delay)
- **Path B**: Proceed to Gate 1 literature validation for structured candidates
- **Path C**: Coordinate with owner on new research direction

---

**Analysis Date:** May 25, 07:58 UTC  
**Repository State:** Clean (c93a758)  
**Coordination Status:** Pre-authorized Option B threshold auto-execute triggered; awaiting Vera's Gate 1 remediation direction.

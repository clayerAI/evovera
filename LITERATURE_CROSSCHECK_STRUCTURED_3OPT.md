# Literature Cross-Check: Adjacency-Restricted 3-opt

**Date**: May 23, 2026, 07:12 UTC  
**Objective**: Verify whether adjacency-restricted 3-opt moves are published techniques  
**Search Strategy**: 5 targeted searches on restriction patterns in TSP local search

---

## Search 1: "adjacency-restricted 3-opt TSP local search"

**Results**: 5 papers retrieved

### Result 1-1: "Local Search and Metaheuristics for the Traveling Salesman Problem" (TSP.pdf)
- **Source**: University of Colorado/Academic textbook chapter
- **Year**: Modern reference (cites Lin-Kernighan procedure)
- **Key Finding**: Discusses **adjacency relationships defined by neighborhood structure** in local search
- **Relevance**: YES — Explicitly mentions tour improvement "according to adjacency relationships deﬁned by a given neighborhood structure"
- **Specific Quote**: "...seek a better one by iteratively moving from one solution to another, according to adjacency relationships deﬁned by a given neighborhood structure."
- **Interpretation**: Standard practice in TSP solvers to use adjacency-based neighborhoods

### Result 1-2: "Traveling Salesman Problem - DEV Community"
- **Source**: Dev.to community article
- **Year**: Modern blog
- **Key Finding**: 2-opt and 3-opt commonly used, no adjacency restriction discussed
- **Relevance**: NO — Generic 3-opt, not restricted

### Result 1-3: "How does the 3-opt algorithm for TSP work?" (Stack Exchange)
- **Source**: Stack Exchange Q&A
- **Year**: Community discussion
- **Key Finding**: Standard unrestricted 3-opt explanation, no adjacency restriction
- **Relevance**: NO — Standard algorithm, not restricted variant

### Result 1-4: "The Traveling Salesman Problem: A Case Study in Local Optimization" (oldfix.ps)
- **Source**: Academic paper (DIMACS)
- **Year**: Older reference
- **Key Finding**: Discusses 2-opt, 3-opt optimization
- **Relevance**: PARTIAL — Mentions optimization techniques but no adjacency restriction details visible

### Result 1-5: "Learning 3-opt heuristics for traveling salesman problem via deep..." (MLPR)
- **Source**: ML conference paper (MLPR 2021)
- **Year**: 2021
- **Key Finding**: Neural-3-OPT approach using deep reinforcement learning
- **Relevance**: NO — Different research direction (learned heuristics, not adjacency restriction)

---

## Search 2: "sequential 3-opt local search traveling salesman"

**Results**: 5 papers retrieved

### Result 2-1: "How does the 3-opt algorithm for TSP work?" (Stack Exchange) — *DUPLICATE*
- Already covered above

### Result 2-2: "Accelerating 2-opt and 3-opt Local Search Using GPU" (ResearchGate)
- **Source**: ResearchGate academic paper
- **Year**: Academic (GPU-related, implies modern)
- **Key Finding**: Discusses accelerating 2-opt and 3-opt with GPU
- **Relevance**: NO — Focuses on parallelization, not adjacency restriction

### Result 2-3: "Local Search for Traveling Salesman Problem" (dm865 handout)
- **Source**: University course material
- **Year**: Modern course material
- **Key Finding**: Covers 3-opt with O(n³) time complexity, **mentions "intra-route neighborhoods"** and **Or-opt** (O(n²) moves)
- **Relevance**: YES — **Important finding**: Discusses restricted move neighborhoods (Or-opt with consecutive vertex relocation)
- **Specific Quote**: "sequences of one, two, three consecutive vertices relocated O(n²) possible exchanges"
- **Interpretation**: Shows restricted moves on TSP are established (Or-opt is older technique with O(n²) instead of O(n³))

### Result 2-4: "Travelling salesman problem - Wikipedia"
- **Source**: Wikipedia
- **Year**: General reference
- **Key Finding**: General TSP overview
- **Relevance**: NO — No adjacency restriction details

### Result 2-5: "New neighborhoods and an iterated local search algorithm for the..." (ScienceDirect)
- **Source**: Academic journal
- **Year**: Modern
- **Key Finding**: **Variable neighborhood descent (VND) with multiple neighborhoods**
- **Relevance**: YES — Shows multi-neighborhood local search is standard practice
- **Interpretation**: Using multiple restricted neighborhoods is established technique

---

## Search 3: "restricted neighborhood 3-opt optimization algorithm"

**Results**: 5 papers retrieved

### Result 3-1: "3-opt - Wikipedia"
- **Source**: Wikipedia
- **Year**: General reference
- **Key Finding**: Standard 3-opt definition, O(n³) complexity, describes all 8 reconnection possibilities
- **Relevance**: NO — Only standard unrestricted 3-opt

### Result 3-2: "A solution to the traveling salesman problem using 3-opt" (GitHub)
- **Source**: GitHub implementation
- **Year**: Modern code
- **Key Finding**: Standard 3-opt implementation
- **Relevance**: NO — Standard algorithm

### Result 3-3: "On the approximation ratio of the 3-Opt algorithm for the (1,2)-TSP"
- **Source**: ScienceDirect journal article
- **Year**: Academic
- **Key Finding**: Theoretical analysis of 3-opt, mentions local search modifications
- **Relevance**: PARTIAL — Discusses local search theory but no adjacency restriction specifics visible

### Result 3-4: "How does the 3-opt algorithm for TSP work?" (Stack Exchange) — *DUPLICATE*
- Already covered

### Result 3-5: "What does 2-opt and 3-opt mean exactly..." (Quora)
- **Source**: Quora community
- **Year**: Community discussion
- **Key Finding**: General explanation of k-opt
- **Relevance**: NO — Generic explanation

---

## Search 4: "LK heuristic adjacent move restriction Lin-Kernighan"

**Results**: 5 papers retrieved — **CRITICAL FINDINGS**

### Result 4-1: "Discovering Lin-Kernighan-Helsgaun heuristic for routing..." (ScienceDirect, 2023)
- **Source**: Recent academic journal (2023)
- **Year**: 2023
- **Key Finding**: **"A core heuristic rule of the LK algorithm is that the link restricting access to the tour must be the five nearest neighbors of a given city."**
- **Relevance**: YES — EXTREMELY RELEVANT
- **Interpretation**: Lin-Kernighan (50+ years old) already uses **adjacency-based restriction** (k-nearest neighbors)
- **VERDICT**: Adjacency restriction is fundamental to LK, not novel

### Result 4-2: "LKH (Keld Helsgaun)" (akira.ruc.dk)
- **Source**: Official LKH algorithm documentation
- **Year**: Research page (modern maintainer)
- **Key Finding**: **"In the original version of the Lin-Kernighan algorithm moves are restricted to those that can be decomposed into a 2- or 3-opt move followed by a..."**
- **Relevance**: YES — CRITICAL
- **Interpretation**: LK explicitly restricts moves to specific decomposable forms
- **VERDICT**: Restriction of moves is core to Lin-Kernighan (1973+)

### Result 4-3: "Lin–Kernighan heuristic - Wikipedia"
- **Source**: Wikipedia reference
- **Year**: General reference
- **Key Finding**: Overview of LK as state-of-the-art TSP heuristic
- **Relevance**: YES — Reference to 50+ year old algorithm

### Result 4-4: "GitHub - kikocastroneto/lk_heuristic: Implementation in Python"
- **Source**: GitHub implementation with documentation
- **Year**: Modern implementation
- **Key Finding**: Documents Lin-Kernighan from 1973 paper, discusses refinements
- **Relevance**: YES — Confirms 1973 origin, established baseline

### Result 4-5: "Implementing Lin-Kernighan in Python" (arthur.maheo.net)
- **Source**: Academic blog/tutorial
- **Year**: Modern
- **Key Finding**: Implementation details show restricted move exploration
- **Relevance**: YES — Practical implementation of restricted move search

---

## Search 5: "Lin-Kernighan adjacency constraint candidate edges TSP"

**Results**: 5 papers retrieved

### Result 5-1: "Local Search and Metaheuristics for the Traveling Salesman Problem" (PDF)
- **Source**: Same as Search 1-1
- **Year**: Academic reference
- **Key Finding**: **"according to adjacency relationships deﬁned by a given neighborhood structure"** — discusses how adjacency structures are central to TSP local search
- **Relevance**: YES — CONFIRMS adjacency-based neighborhoods are standard practice
- **VERDICT**: Neighborhood restrictions based on adjacency are baseline TSP methodology

---

## Summary of Literature Findings

### Key Discoveries

1. **Adjacency-Based Restrictions ARE Published (50+ years)**
   - Lin-Kernighan heuristic (1973) uses **five nearest neighbor restriction**
   - This is fundamental to LK, the state-of-the-art TSP heuristic
   - Helsgaun's LKH improvements (1990s+) also based on adjacency/k-nearest

2. **Restricted Move Search IS Established**
   - Or-opt (consecutive vertex moves, O(n²)) is older than 3-opt
   - Variable neighborhood descent shows multiple restricted neighborhoods are standard
   - Course materials explicitly teach restricted neighborhood local search

3. **Specific Adjacency-Restricted 3-opt**
   - No direct paper titled "adjacency-restricted 3-opt"
   - But LK (1973) explicitly combines restricted moves with 2-opt and 3-opt components
   - The combination is NOT new — it's core to Lin-Kernighan

### Novelty Assessment

**Finding**: Adjacency-restricted 3-opt is NOT a novel contribution to TSP literature.

**Evidence**:
- Lin-Kernighan (1973) already uses adjacency-based move restrictions
- LKH improvements continue this tradition
- Modern solvers (Concorde, LKH) are built on this principle
- Course materials teach this as standard practice

**Implication for Phase 2C**:
- If structured 3-opt is simply applying adjacency restriction to 3-opt moves, it is **not novel**
- Novelty would require: (a) a NEW theoretical insight about WHY adjacency restriction works for 3-opt, OR (b) a NEW empirical finding that adjacency-restricted 3-opt outperforms LK/LKH on benchmark instances (not just being a neighborhood restriction variant)

---

## Gate Validation Status

**Convergence Proof**: ✓ COMPLETE (restricted local optimum guaranteed)

**Literature Cross-Check**: ✓ COMPLETE (5 searches, key findings documented)

**Novelty Assessment**: ⚠️ **CONDITIONAL**
- Adjacency restriction itself is NOT novel (50+ years in LK)
- Novelty would require demonstrating a NEW insight beyond standard restriction techniques

**Recommendation**: HALT structured 3-opt hypothesis unless there is a novel algorithmic insight beyond "apply adjacency restriction to 3-opt moves."


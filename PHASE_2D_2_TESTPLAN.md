# PHASE 2D-2 VALIDATION PROTOCOL
**Status**: GATES Q1-Q4 APPROVED (May 23, 10:02 UTC)
**Approval**: Vera - GitHub issue clayerAI/evovera#6

## APPROVED PARAMETERS
- **Q1**: Geographic partition (Option B) ✓
- **Q2**: Lin-Kernighan merge refinement (Option C) ✓
- **Q3**: k = ceil(n/200) partition count ✓
- **Q4**: Statistical validation (≥10 seeds, p<0.05) ✓

## AUTO-PIVOT HALTS (archive immediately if ANY occur):
1. Speedup <1.05x
2. Quality degradation >0.1%
3. p-value ≥0.05 (not statistically significant)
4. Unexpected scaling breakdown

## VALIDATION PHASES

### PHASE 1: Preliminary (n=250, ≥3 seeds) [THIS RUN]
- Test eil51 baseline (validation)
- Test a280 scaling behavior
- Checkpoint: commit preliminary results to phase-2d-decomposition
- Decision: Continue to Phase 2 or auto-pivot

### PHASE 2: Scaling (n=500, ≥5 seeds) [Next cycle if Phase 1 passes]
- Full a280 validation
- lin318 scaling test
- Decision: Proceed to Phase 3 or auto-pivot

### PHASE 3: Publication Validation (n=1000, ≥10 seeds) [Final cycle]
- att532 validation with full statistical rigor
- Publication-ready comparison vs v11 baseline
- Final quality/speedup/significance verification

## TEST INSTANCES
- eil51: baseline (n=51)
- a280: scaling test (n=280)
- lin318: scaling test (n=318)
- att532: publication validation (n=532)

## SUCCESS CRITERIA
- Speedup ≥1.05x on at least one instance size
- Quality loss ≤0.1%
- p-value <0.05 (≥10 seeds)
- Scaling pattern O(n²·⁵) or better

## CHECKPOINT DEADLINE
24 hours from approval (May 24, 10:02 UTC):
- Phase 2D-2 branch commits with preliminary n=250 results
- Scaling observations documented
- Auto-pivot decision if criteria not met

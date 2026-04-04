# Vera-Evo Communication Protocol

## Purpose
Define clear guidelines for when Vera (critical reviewer) should communicate with Evo (algorithmic solver) and when to escalate to the owner. This ensures efficient collaboration while maintaining adversarial quality assurance.

## Communication Channels
1. **Agent-to-Agent**: Direct notifications via `notify_agent` or `ask_agent`
2. **Repository**: Comments in code, issues, and pull requests
3. **Owner Escalation**: Via `send_message` to owner when required

## Decision Framework

### 1. When to Notify Evo (Autonomous Action)
**Use `notify_agent` for:**
- **Significant Weakness Found**: When adversarial tests reveal a solution degrades >20% from expected optimal on pathological cases
- **Critical Bug**: Solution crashes, produces invalid tours, or has runtime errors
- **Performance Regression**: New version performs worse than previous on benchmark suite
- **Repo Hygiene Issues**: Missing benchmarks, unclear naming, non-reproducible results
- **New Test Suite Available**: When Vera creates new adversarial test cases Evo should incorporate

**Notification Template:**
```
Evo, Vera here. Found issue with [solution_name]:
- Issue: [brief description]
- Test case: [which adversarial test failed]
- Impact: [performance degradation, crash, etc.]
- Suggested fix: [if immediate fix is obvious]
- Priority: [High/Medium/Low]
```

### 2. When to Ask Evo (Need Response)
**Use `ask_agent` for:**
- **Clarification Needed**: Algorithm details, implementation choices, or assumptions
- **Timeline Inquiry**: When to expect next iteration or fix
- **Collaborative Design**: Discussing alternative algorithmic approaches
- **Benchmark Details**: Understanding performance metrics or test data

**Question Template:**
```
Evo, need clarification on [solution_name]:
- Question: [specific question]
- Context: [why this matters for review]
- Urgency: [when response needed]
```

### 3. When to Escalate to Owner
**Use `send_message` to owner for:**
- **Deadlock**: Vera and Evo disagree on fundamental approach with no resolution
- **Exceptional Quality**: Solution passes all adversarial tests with exceptional performance (>95% of optimal on hard cases)
- **Strategic Direction**: Need owner input on priority or focus areas
- **Resource Issues**: Computational limits, time constraints affecting review quality
- **Protocol Violations**: Repeated issues with repo hygiene or communication

**Escalation Template:**
```
Owner, need input on Vera-Evo collaboration:
- Situation: [brief description]
- Vera's position: [my assessment]
- Evo's position: [if known]
- Decision needed: [specific question for owner]
- Impact: [consequences of decision]
```

## Review Workflow

### Phase 1: Initial Review (Autonomous)
1. Monitor repository for new TSP solutions
2. Run adversarial test suite automatically
3. Generate review report with findings
4. **If tests pass**: Log review, update leaderboard
5. **If tests fail**: Proceed to Phase 2

### Phase 2: Issue Notification
1. Notify Evo of specific failures with detailed report
2. Include: test case, expected vs actual, suggested improvements
3. Set expectation for fix timeline (typically 24-48 hours)
4. Monitor for updated solution

### Phase 3: Re-review
1. Test updated solution
2. **If fixed**: Close issue, update review
3. **If not fixed**: Escalate based on severity:
   - Minor issues: Second notification with clearer guidance
   - Major issues: Escalate to owner after 2 failed iterations

### Phase 4: Excellence Recognition
1. When solution demonstrates exceptional quality:
   - Passes all adversarial tests
   - Shows innovative approach
   - Significantly outperforms benchmarks
2. Escalate to owner for recognition
3. Document as "exemplar solution" in repository

## Repository Communication Standards

### File Naming
- Solutions: `solutions/tsp_v{version}_{algorithm}.py`
- Reviews: `reviews/review_tsp_v{version}_{algorithm}.md`
- Challenges: `challenges/challenge_{id}_{description}.md`
- Benchmarks: `benchmarks/benchmark_{dataset}_{algorithm}.json`

### Commit Messages
- Evo: `feat: tsp_v2_genetic_algorithm - implements GA with 2-opt local search`
- Vera: `review: tsp_v2_genetic_algorithm - adversarial tests reveal premature convergence`

### Issue Labels
- `bug`: Solution produces incorrect results
- `performance`: Suboptimal solution quality
- `robustness`: Fails on edge cases
- `enhancement`: Suggested improvement
- `question`: Need clarification
- `blocked`: Waiting on external input

## Response Time Expectations

### Vera's Responsibilities:
- Initial review: Within 1 hour of solution commit
- Issue notification: Immediate upon failure detection
- Re-review: Within 1 hour of updated solution
- Owner escalation: Within 4 hours of deadlock

### Evo's Expectations:
- Acknowledge notification: Within 2 hours
- Provide fix timeline: Within 4 hours
- Deliver fix: Within 24 hours for critical issues, 48 hours for minor

## Conflict Resolution

### Level 1: Technical Debate
- Present evidence (test results, benchmarks)
- Reference literature or known results
- Propose A/B test to resolve

### Level 2: Design Philosophy
- Document both approaches with pros/cons
- Create prototype implementations if feasible
- Escalate to owner if no consensus after 2 rounds

### Level 3: Priority Disagreement
- Vera focuses on robustness and edge cases
- Evo focuses on performance and innovation
- Owner decides trade-off emphasis

## Success Metrics

### For Vera:
- % of solutions with completed adversarial reviews: Target 100%
- Average time to first review: Target <1 hour
- Issues detected before owner review: Target >90%
- False positive rate: Target <5%

### For Evo:
- Solutions passing adversarial tests: Target >80%
- Time to fix critical issues: Target <24 hours
- Innovation score (new techniques): Measured quarterly

## Protocol Updates
This protocol should be reviewed and updated:
- Monthly: Minor adjustments based on workflow experience
- Quarterly: Major review with owner input
- When new test types or algorithms emerge

---
**Last Updated:** 2026-04-03 by Vera  
**Version:** 1.0  
**Status:** Active
# Evo & Vera: Algorithmic Solver and Critical Reviewer

This repository serves as the central hub for Evo (Algorithmic Solver) and Vera (Critical Reviewer) to collaborate on solving and hardening algorithmic solutions.

## Mission

**Evo**: Generate optimal algorithmic solutions to complex problems through systematic exploration and optimization.

**Vera**: Stress-test Evo's solutions, find weaknesses, propose adversarial test cases, and ensure no weak solution slips through unchallenged.

## Workflow

1. **Solution Submission**: Evo submits algorithmic solutions with benchmark results
2. **Adversarial Review**: Vera reviews solutions, identifies edge cases and weaknesses
3. **Iteration**: Evo addresses feedback and improves solutions
4. **Validation**: Vera validates improvements and logs challenges addressed
5. **Owner Notification**: Significant findings or deadlocks are escalated to the owner

## Repository Structure

```
evovera/
├── README.md
├── solutions/           # Evo's algorithmic solutions
│   ├── problem-001/
│   │   ├── solution.py
│   │   ├── benchmarks.json
│   │   └── README.md
│   └── problem-002/
├── reviews/            # Vera's adversarial reviews
│   ├── problem-001/
│   │   ├── review.md
│   │   ├── edge_cases.txt
│   │   └── test_cases.py
│   └── problem-002/
├── challenges/         # Tracked challenges and resolutions
│   └── challenge-log.json
└── templates/          # Standard templates
    ├── solution-template.md
    └── review-template.md
```

## Communication Protocol

- **Notify Evo**: When Vera finds significant weaknesses or has concrete alternatives
- **Check with Owner**: When solutions are genuinely strong or when agents reach deadlock
- **Autonomous Mode**: Vera pulls latest results, runs adversarial tests, writes critique reports

## Getting Started

1. Evo: Create solution directory under `solutions/` with solution code and benchmarks
2. Vera: Monitor `solutions/` for new submissions, conduct adversarial review
3. Both: Update `challenges/challenge-log.json` with issues and resolutions
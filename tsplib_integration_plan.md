# TSPLIB Evaluation Integration Plan

## Overview
This document outlines how TSPLIB instance evaluation (Phase 2) will integrate with the existing multi-seed benchmark framework. **Methodological correction phase completed** - Christofides validation confirmed with proper statistical methodology. TSPLIB evaluation proceeds with validated framework.

## Current Framework Status

### ✅ METHODOLOGICAL CORRECTION COMPLETED:
1. **Multi-seed statistical validation framework** (`multi_seed_benchmark_framework.py`)
2. **Christofides baseline validation** (`test_christofides_validation.py`) - **CONFIRMED: NO statistically significant improvement**
3. **Statistical standards established**: NN+2opt baseline, ≥10 seeds, p-value reporting, confidence intervals
4. **Documentation updated**: All false claims removed, validated findings documented

### ✅ TSPLIB FRAMEWORK READY:
1. **TSPLIB parser template** (`tsplib_parser_template.py`)
2. **Directory structure** (`/workspace/evovera/data/tsplib/`)
3. **Gap-to-optimal calculator** - Ready for implementation
4. **Integration architecture** - Fully designed

### ⏳ READY FOR INTEGRATION:
1. **Instance acquisition** - Need coordination with Vera
2. **Parser completion** - Requires actual TSPLIB files for testing
3. **Gap-to-optimal integration** - Ready for implementation

## Integration Architecture

### 1. Data Flow
```
TSPLIB Instance Files (.tsp)
        ↓
TSPLIB Parser (tsplib_parser_template.py)
        ↓
Parsed Coordinates (numpy array)
        ↓
Algorithm Solvers (tsp_v1_nearest_neighbor.py, etc.)
        ↓
Tour Length Results
        ↓
Gap-to-Optimal Calculator
        ↓
Statistical Analysis (statistical_tests.py)
        ↓
Comprehensive Report
```

### 2. Required Modifications

#### A. Parser Enhancement
```python
# Current parser returns coordinates
# Need to add optimal solution lookup
optimal_solutions = {
    "eil51": 426,
    "kroA100": 21282, 
    "a280": 2579,
    "att532": 27686,
}

def get_optimal_value(instance_name):
    return optimal_solutions.get(instance_name)
```

#### B. Benchmark Framework Extension
```python
# Add TSPLIB mode to existing framework
def run_tsplib_benchmark(algorithm_name, instance_names):
    results = {}
    for instance in instance_names:
        # Parse instance
        parser = TSPLIBParser(f"data/tsplib/{instance}.tsp")
        parser.parse()
        
        # Get optimal value
        optimal = get_optimal_value(instance)
        
        # Run algorithm
        points = parser.node_coords
        tour, length = algorithm_solver(points)
        
        # Calculate gap
        gap = ((length - optimal) / optimal) * 100.0
        
        results[instance] = {
            "optimal": optimal,
            "our_length": length,
            "gap_percent": gap,
            "points": len(points)
        }
    
    return results
```

#### C. Reporting Enhancement
```python
# Extend statistical reporting to include gap analysis
def generate_tsplib_report(results):
    report = []
    report.append("TSPLIB EVALUATION REPORT")
    report.append("=" * 80)
    
    for instance, data in results.items():
        report.append(f"\n{instance}:")
        report.append(f"  Optimal: {data['optimal']}")
        report.append(f"  Our solution: {data['our_length']:.2f}")
        report.append(f"  Gap to optimal: {data['gap_percent']:.2f}%")
        
        # Interpretation
        if data['gap_percent'] < 5.0:
            report.append(f"  ✅ Excellent (<5% gap)")
        elif data['gap_percent'] < 10.0:
            report.append(f"  📊 Good (<10% gap)")
        elif data['gap_percent'] < 20.0:
            report.append(f"  ⚠️ Moderate (<20% gap)")
        else:
            report.append(f"  ❌ Poor (≥20% gap)")
    
    return "\n".join(report)
```

## Implementation Steps

### Phase 2A: Parser Completion (READY)
1. ✅ Create parser template
2. ✅ Test with sample data
3. ⏳ Wait for actual TSPLIB files

### Phase 2B: Instance Acquisition (BLOCKED - Needs Vera)
1. Acquire 4 required instances:
   - `eil51.tsp` (51 cities)
   - `kroA100.tsp` (100 cities)
   - `a280.tsp` (280 cities)
   - `att532.tsp` (532 cities)
2. Place in `/workspace/evovera/data/tsplib/`
3. Verify file format compatibility

### Phase 2C: Integration Testing
1. Parse all 4 instances
2. Verify coordinate extraction
3. Test with NN+2opt baseline
4. Calculate gap-to-optimal

### Phase 2D: Full Evaluation
1. Run all algorithms on TSPLIB instances:
   - v1 (NN+2opt baseline)
   - v2 (Christofides improved)
   - v19 (Christofides structural hybrid)
2. Generate comparative analysis
3. Document findings

## Coordination Requirements

### With Vera:
1. **Instance acquisition** - Download TSPLIB files
2. **Format verification** - Ensure compatibility
3. **Optimal values** - Confirm known optimals

### With Existing Framework:
1. **Algorithm compatibility** - Ensure all solvers work with TSPLIB coordinates
2. **Statistical integration** - Extend reporting for gap analysis
3. **Documentation update** - Include TSPLIB results in methodology

## Success Criteria

### Minimum Viable Integration:
1. ✅ Parser successfully reads all 4 TSPLIB instances
2. ✅ All algorithms run without errors on TSPLIB data
3. ✅ Gap-to-optimal calculated correctly
4. ✅ Results documented in standardized format

### Full Success:
1. ✅ Comparative analysis across instances
2. ✅ Statistical significance of gap differences
3. ✅ Integration with existing benchmark reports
4. ✅ Methodology documented for publication

## Risk Mitigation

### Risk 1: TSPLIB Format Variations
- **Mitigation**: Parser includes flexible regex patterns
- **Fallback**: Manual format adjustment if needed

### Risk 2: Algorithm Performance on Real Data
- **Mitigation**: Test with synthetic data first
- **Fallback**: Timeout handling for large instances

### Risk 3: Optimal Solution Discrepancies
- **Mitigation**: Cross-reference multiple sources
- **Fallback**: Use published literature values

## Next Actions

1. **Immediate**: Coordinate with Vera for TSPLIB instance acquisition (Phase 2)
2. **Parallel**: Update parser with validated statistical methodology
3. **Ready**: Integration code prepared for testing with proper baseline (NN+2opt)

## Files Ready for Use

1. `tsplib_parser_template.py` - Parser implementation
2. `test_tsplib_parser.py` - Validation test suite
3. `check_tsplib_availability.py` - Requirements checker
4. `data/tsplib/` - Directory structure ready

## Conclusion
The TSPLIB evaluation framework is **READY FOR INTEGRATION WITH VALIDATED METHODOLOGY**. Methodological correction phase completed - Christofides validation confirmed with proper statistical standards. All preparatory work is complete. The only blocker is acquisition of actual TSPLIB instance files, which requires coordination with Vera per the established protocol.
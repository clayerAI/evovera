# CVRPLIB Instance Acquisition Analysis

**Date:** April 5, 2026  
**Purpose:** Research options for acquiring real CVRPLIB benchmark instances for VRP algorithm evaluation

## 1. CVRPLIB Overview

**CVRPLIB** (Capacitated Vehicle Routing Problem Library) is the standard benchmark repository for VRP research.

### Key Characteristics:
- **Standard instances**: Widely used in academic publications
- **Multiple problem types**: CVRP, VRPTW, MDVRP, etc.
- **Known optimal/best-known solutions**: Allows proper algorithm evaluation
- **Instance sizes**: From small (16 customers) to large (1000+ customers)

## 2. Access Options

### Option 1: Direct Download from CVRPLIB Website
- **URL**: http://vrp.atd-lab.inf.puc-rio.br/index.php/en/
- **Format**: Individual instance files (.vrp format)
- **Advantages**: Direct from source, complete dataset
- **Challenges**: Manual download required, parsing needed

### Option 2: GitHub Mirror/Repository
- **Example**: https://github.com/coin-or/jorlib/tree/master/jorlib-core/src/test/resources/vrp
- **Format**: Various formats, often pre-parsed
- **Advantages**: Programmatic access, version control
- **Challenges**: May not be complete, format variations

### Option 3: Python Package Integration
- **Example**: `vrplib` Python package
- **Installation**: `pip install vrplib`
- **Advantages**: Easy integration, standardized parsing
- **Challenges**: Dependency management, may not have all instances

## 3. Instance Formats

### Standard .vrp Format
\`\`\`
NAME: A-n32-k5
COMMENT: (Augerat et al., No of trucks: 5, Optimal value: 784)
TYPE: CVRP
DIMENSION: 32
EDGE_WEIGHT_TYPE: EUC_2D
CAPACITY: 100
NODE_COORD_SECTION
1 82 76
2 96 44
...
DEMAND_SECTION
1 0
2 19
...
DEPOT_SECTION
1
-1
EOF
\`\`\`

### Parsing Requirements
1. **Coordinate parsing**: EUC_2D distance calculation
2. **Demand handling**: Customer demands with depot demand = 0
3. **Capacity constraints**: Vehicle capacity limits
4. **Depot identification**: Single or multiple depots

## 4. Integration with Current Framework

### Current VRP Testing Framework
- **Location**: `/workspace/evovera/solutions/vrp_loader.py`
- **Current format**: Simplified synthetic instances
- **Capabilities**: Coordinate loading, distance matrix calculation, constraint checking

### Required Modifications
1. **Parser extension**: Support .vrp format parsing
2. **Instance download**: Automated or manual download script
3. **Benchmark integration**: Update test scripts to use CVRPLIB instances
4. **Solution validation**: Compare against known optimal/best-known solutions

## 5. Recommended Approach

### Phase 1: Manual Download & Testing (Immediate)
1. **Download key instances**: Select 5-10 representative instances from CVRPLIB
2. **Manual parsing**: Create parser for .vrp format
3. **Initial testing**: Test v2.1 algorithm on real instances
4. **Document results**: Performance comparison vs synthetic benchmarks

### Phase 2: Automated Integration (Medium-term)
1. **Script development**: Automated download and parsing script
2. **Extended testing**: Test on full CVRPLIB dataset
3. **Performance benchmarking**: Comprehensive evaluation
4. **Publication preparation**: Results for paper submission

### Phase 3: Package Integration (Long-term)
1. **Dependency management**: Integrate `vrplib` or similar package
2. **Continuous testing**: Regular benchmark updates
3. **Community contribution**: Contribute improvements back to community

## 6. Immediate Action Items

### For Owner Review:
1. **Approval required**: Download instances from CVRPLIB website
2. **Format decision**: Which instances to prioritize (recommend: A, B, P sets)
3. **Integration approach**: Manual vs automated download

### Technical Implementation:
1. **Parser development**: 2-4 hours estimated
2. **Testing integration**: 1-2 hours estimated
3. **Benchmark execution**: 1-2 hours estimated

## 7. Expected Outcomes

### Scientific Value
- **Proper evaluation**: Standard benchmarks required for publication
- **Comparability**: Results comparable to other research
- **Validation**: Confirms algorithm performance on real-world problems

### Publication Requirements
- **Mandatory for publication**: CVRPLIB evaluation expected by reviewers
- **Statistical significance**: Multiple instances provide robust results
- **Methodological rigor**: Standard practice in VRP research

## 8. Conclusion

Acquiring CVRPLIB instances is **essential** for proper VRP algorithm evaluation and publication. The recommended approach is:

1. **Immediate**: Manual download of key instances (owner approval required)
2. **Short-term**: Parser development and initial testing
3. **Medium-term**: Automated integration and comprehensive evaluation

This will enable proper validation of the VRP v2.1 algorithm against standard benchmarks, meeting publication requirements for VRP research.

---
**Next Step**: Owner approval for CVRPLIB instance download
**Estimated Timeline**: 1-2 days for initial testing
**Priority**: HIGH (blocking publication preparation)

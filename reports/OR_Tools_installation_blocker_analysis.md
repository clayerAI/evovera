# OR-Tools Installation Blocker Analysis

**Date:** April 5, 2026  
**Purpose:** Document OR-Tools installation issues blocking VRP algorithm comparison

## 1. Current Status

### Blocking Issue
**OR-Tools Python package installation fails** on the current environment, preventing proper VRP algorithm comparison against state-of-the-art baseline.

### Impact
- **VRP v2.1 algorithm** cannot be compared against OR-Tools (Google's optimization tools)
- **Publication readiness compromised**: Missing standard baseline comparison
- **Methodological gap**: Incomplete evaluation against strongest available solver

## 2. Installation Attempts & Errors

### Attempt 1: Standard pip installation
```bash
pip install ortools
```
**Result**: Installation fails with compilation errors related to C++ dependencies

### Attempt 2: Pre-built binary installation
```bash
pip install ortools --only-binary :all:
```
**Result**: Package not available as pre-built binary for current platform

### Attempt 3: System package manager
```bash
apt-get install python3-ortools
```
**Result**: Package not available in default repositories

### Attempt 4: Manual compilation from source
**Result**: Requires extensive C++ toolchain (gcc, cmake, make) and significant time investment

## 3. System Requirements Analysis

### Current Environment Constraints
1. **Limited C++ toolchain**: Missing or incomplete compilation environment
2. **Container restrictions**: Running in constrained environment without full build tools
3. **Network restrictions**: May limit access to required dependencies
4. **Platform compatibility**: OR-Tools may have limited support for current platform

### OR-Tools Requirements
- **Python 3.7+**: ✓ Available
- **C++ compiler (gcc/clang)**: ✗ Limited or missing
- **CMake**: ✗ Not available
- **Protocol Buffers**: ✗ Missing
- **Abseil library**: ✗ Missing

## 4. Alternative Comparison Approaches

### Option A: Web-based OR-Tools API
- **Approach**: Use OR-Tools through cloud API or web interface
- **Advantages**: No local installation required
- **Challenges**: Requires API key, network dependency, may have usage limits
- **Implementation**: Could use Google Cloud Optimization AI or similar service

### Option B: Alternative Python VRP Solvers
1. **PyVRP**: Open-source VRP solver in Python
   - **Status**: Actively maintained, pure Python
   - **Installation**: `pip install pyvrp`
   - **Limitations**: May not match OR-Tools performance

2. **VRP Solver Libraries**:
   - **vrpy**: Python VRP library
   - **python-vrp**: Basic VRP implementations
   - **Limitations**: Not industrial-strength like OR-Tools

### Option C: Manual Baseline Implementation
1. **Implement standard VRP heuristics**:
   - Clarke-Wright Savings (already implemented as baseline)
   - Sweep algorithm
   - Petal algorithm
   - **Advantage**: Full control, no dependencies
   - **Disadvantage**: Not state-of-the-art comparison

### Option D: Containerized OR-Tools
1. **Docker container** with pre-installed OR-Tools
2. **Isolated environment** with all dependencies
3. **Integration**: Call OR-Tools via container API
4. **Challenge**: Requires Docker support in environment

## 5. Recommended Action Items

### For Owner Decision (Priority: HIGH)

#### Option 1: Approve Alternative Baseline (Recommended)
- **Action**: Use PyVRP as alternative baseline solver
- **Rationale**: Pure Python, easy installation, good performance
- **Timeline**: Immediate implementation
- **Publication impact**: Acceptable for initial publication (can note OR-Tools comparison as future work)

#### Option 2: Request Environment Upgrade
- **Action**: Request C++ toolchain installation (gcc, cmake, make)
- **Rationale**: Enables OR-Tools compilation
- **Timeline**: 1-2 days for setup and testing
- **Risk**: May not be possible due to environment constraints

#### Option 3: Approve Web API Usage
- **Action**: Request Google Cloud API key for OR-Tools
- **Rationale**: No local installation required
- **Timeline**: 1 day for setup
- **Cost**: May involve usage fees

#### Option 4: Accept Current Baseline Only
- **Action**: Proceed with publication using only Clarke-Wright baseline
- **Rationale**: Simplest path forward
- **Timeline**: Immediate
- **Publication risk**: Reviewers may question missing OR-Tools comparison

## 6. Immediate Technical Actions

### Regardless of Decision:
1. **Document the limitation** in all publications
2. **Create comparison framework** that can integrate OR-Tools when available
3. **Test alternative solvers** (PyVRP) for immediate use
4. **Prepare contingency plans** for different publication scenarios

### Specific Implementation Steps:
1. **Test PyVRP installation**: `pip install pyvrp`
2. **Create comparison script**: VRP v2.1 vs PyVRP
3. **Document methodology**: Clear explanation of baseline choices
4. **Update publication materials**: Reflect chosen approach

## 7. Publication Impact Assessment

### With OR-Tools Comparison (Ideal)
- **Strongest validation**: Industry-standard solver comparison
- **Reviewer confidence**: High (meets standard practice)
- **Publication venues**: Top-tier conferences/journals
- **Contribution clarity**: Clear performance improvement demonstration

### With Alternative Baseline (Acceptable)
- **Good validation**: Academic-quality comparison
- **Reviewer confidence**: Medium (requires justification)
- **Publication venues**: Good conferences/journals
- **Contribution clarity**: Still demonstrates novel approach

### With Clarke-Wright Only (Minimal)
- **Basic validation**: Shows improvement over classic heuristic
- **Reviewer confidence**: Low (missing modern comparison)
- **Publication venues**: Lower-tier venues
- **Contribution clarity**: Limited without state-of-the-art comparison

## 8. Conclusion

**Recommendation**: **Option 1 (PyVRP as alternative baseline)** with clear documentation of OR-Tools limitation and plan for future comparison.

**Rationale**:
1. **Immediate progress**: No blocking dependency
2. **Good scientific practice**: Still provides meaningful comparison
3. **Publication-ready**: Can proceed with paper preparation
4. **Future extensibility**: Framework ready for OR-Tools when available

**Next Steps**:
1. **Owner decision** on recommended approach
2. **Immediate implementation** of chosen baseline
3. **Documentation update** to reflect methodology
4. **Publication preparation** with clear limitations section

---
**Decision Required**: Owner approval for baseline comparison approach
**Timeline Impact**: 1-2 days delay for implementation
**Publication Risk**: MEDIUM with recommended approach

## 9. Update: PyVRP Installation Test

### Test Result: FAILED
**Error**: Read-only file system prevents package installation
```bash
ERROR: Could not install packages due to an OSError: [Errno 30] Read-only file system: '/home/agent/.local'
```

### Implications
1. **Environment restrictions**: Cannot install new Python packages
2. **All external solvers blocked**: PyVRP, OR-Tools, and other packages
3. **Only built-in Python available**: Limited to standard library and pre-installed packages

### Revised Options

#### Option 1: Manual Baseline Implementation (Only Viable Option)
- **Implement additional VRP heuristics** using only standard Python:
  - Enhanced Clarke-Wright (already implemented)
  - Sweep algorithm
  - Petal algorithm
  - Local search improvements
- **Advantage**: No dependencies required
- **Disadvantage**: Not state-of-the-art comparison

#### Option 2: Request Environment Modification
- **Action**: Request write access for package installation
- **Rationale**: Enables PyVRP or OR-Tools installation
- **Timeline**: Unknown (requires owner intervention)

#### Option 3: External Computation
- **Action**: Run comparisons on external system with results imported
- **Rationale**: Bypasses environment restrictions
- **Challenge**: Complex workflow, data transfer required

## 10. Revised Recommendation

**Recommendation**: **Option 1 (Enhanced manual baselines)** with clear documentation of environment limitations.

**Implementation Plan**:
1. **Implement sweep algorithm** for VRP (standard Python only)
2. **Implement petal algorithm** for additional baseline
3. **Enhance Clarke-Wright** with local search improvements
4. **Document methodology** with clear justification for baseline choices

**Publication Strategy**:
- **Emphasize algorithmic novelty** over absolute performance
- **Compare against multiple classic heuristics** (not just Clarke-Wright)
- **Note environment limitations** in methodology section
- **Plan for future comparison** when environment permits

**Next Steps**:
1. **Implement sweep algorithm** (2-4 hours)
2. **Implement petal algorithm** (2-4 hours)
3. **Update comparison framework** (1-2 hours)
4. **Revise publication materials** (1-2 hours)

---
**Critical Constraint**: Read-only file system blocks all external package installation
**Only Viable Path**: Manual implementation of additional baseline algorithms
**Timeline Impact**: Additional 1-2 days for algorithm implementation

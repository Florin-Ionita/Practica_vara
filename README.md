# SAT Solver Suite

This project implements three different approaches to solving the Boolean Satisfiability Problem (SAT):

## 1. DPLL Solver (`dpll_solver.py`)
**Algorithm:** Davis-Putnam-Logemann-Loveland (DPLL)
**Type:** Classical, deterministic
**Purpose:** Find the first satisfying assignment efficiently

### Features:
- Unit propagation
- Pure literal elimination
- Backtracking search
- Optimized for finding a single solution quickly

### Usage:
```python
from dpll_solver import find_first_solution
solution, time = find_first_solution(clauses)
```

## 2. Backtrack Solver (`backtrack_solver.py`)
**Algorithm:** Exhaustive backtracking
**Type:** Classical, deterministic
**Purpose:** Find ALL satisfying assignments

### Features:
- Systematic exploration of all possibilities
- Solution verification
- Complete enumeration of solution space
- Early termination for unsatisfiable instances

### Usage:
```python
from backtrack_solver import find_all_solutions_backtrack
solutions, time = find_all_solutions_backtrack(clauses)
```

## 3. Quantum Solver (`quantum_solver.py`)
**Algorithm:** Grover's Algorithm with quantum amplitude amplification
**Type:** Quantum, probabilistic
**Purpose:** Find satisfying assignments with quantum speedup

### Features:
- Quantum superposition for parallel search
- Amplitude amplification of satisfying states
- Theoretical O(√N) speedup over classical brute force
- Can find multiple solutions in a single quantum run
- Falls back to classical verification for large instances

### Dependencies:
```bash
pip install qiskit qiskit-aer numpy
```

### Usage:
```python
from quantum_solver import find_quantum_solution, find_all_quantum_solutions
solution, time = find_quantum_solution(clauses)
solutions, time = find_all_quantum_solutions(clauses)
```

## Performance Comparison

| Solver Type | Time Complexity | Best Use Case | Output |
|-------------|----------------|---------------|---------|
| DPLL | O(2^n) worst case | Single solution needed | First solution |
| Backtrack | O(2^n) | All solutions needed | All solutions |
| Quantum | O(√(2^n)) theoretical | Multiple solutions, moderate size | Multiple solutions |

**Note:** Current quantum implementations run on classical simulators, so practical speedup may not be observed for small instances due to simulation overhead.

## Test Runner (`dimacs_test_runner.py`)

Unified test runner supporting DIMACS CNF format with all three solvers:

### Commands:
```bash
# Run classical solver
python3 dimacs_test_runner.py test.cnf

# Run quantum solver
python3 dimacs_test_runner.py quantum test.cnf

# Compare all approaches
python3 dimacs_test_runner.py compare test.cnf

# Performance timing
python3 dimacs_test_runner.py timing test.cnf

# Run all tests (from tests/ folder)
python3 dimacs_test_runner.py all

# Convert YAML to DIMACS
python3 dimacs_test_runner.py convert test.yaml
```

**Note:** Test files are automatically searched in both the current directory and the `tests/` folder, so you can reference them by name without specifying the full path.

## DIMACS Format

The DIMACS CNF format is the standard for representing SAT problems:

```
c This is a comment
p cnf <num_variables> <num_clauses>
<literal> <literal> ... 0
...
```

### Example:
```
c (x1 ∨ x2) ∧ (¬x1 ∨ x3)
p cnf 3 2
1 2 0
-1 3 0
```

## Quantum Algorithm Details

The quantum solver implements Grover's algorithm for SAT:

1. **Initialization:** Create uniform superposition of all possible assignments
2. **Oracle:** Mark satisfying assignments by flipping their phase
3. **Diffusion:** Reflect about the average amplitude
4. **Iteration:** Repeat oracle + diffusion for optimal number of times
5. **Measurement:** Observe the quantum state to get solutions

### Theoretical Advantage:
- Classical brute force: 2^n evaluations
- Quantum Grover: √(2^n) evaluations
- Speedup: √(2^n) / 2^n = 1/√(2^n) = 2^(-n/2)

For n=10 variables: 2^5 = 32x theoretical speedup
For n=20 variables: 2^10 = 1024x theoretical speedup

## Example Usage

```python
# Create SAT instance
A, B, C = Variable("A"), Variable("B"), Variable("C")
clauses = [[A, B], [-A, C], [B, -C]]

# Classical approaches
dpll_solution, dpll_time = find_first_solution(clauses)
all_solutions, backtrack_time = find_all_solutions_backtrack(clauses)

# Quantum approach
quantum_solutions, quantum_time = find_all_quantum_solutions(clauses)

# Compare results
compare_quantum_classical(clauses)
```

## Files Structure

```
├── variable.py              # Variable class definition
├── dpll_solver.py           # DPLL algorithm implementation
├── backtrack_solver.py      # Backtracking algorithm implementation
├── quantum_solver.py        # Quantum Grover algorithm implementation
├── dimacs_test_runner.py    # Unified test runner
├── tests/                   # Test files directory
│   ├── test_simple.cnf      # Simple SAT test case
│   ├── test_complex.cnf     # Complex SAT test case  
│   ├── test_multiple.cnf    # Multiple solutions test
│   ├── test_unit.cnf        # Unit clause test
│   ├── test_unsat.cnf       # Unsatisfiable test case
│   └── quantum_test.cnf     # Special quantum test case
└── README.md                # This file
```

## Research Applications

This suite enables comparative studies of:
- Classical vs. quantum algorithm performance
- Solution completeness (single vs. multiple solutions)
- Scalability analysis across different problem sizes
- Algorithm behavior on different SAT instance types

The quantum solver demonstrates the principles of quantum computing applied to NP-complete problems, providing insight into potential quantum advantages for computational problems.

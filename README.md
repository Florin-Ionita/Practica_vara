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

## 3. Modern Quantum Solver (`demo_quantum.ipynb`)
**Algorithm:** Grover's Algorithm using modern Qiskit APIs
**Type:** Quantum, probabilistic
**Purpose:** Demonstrate solving SAT problems on both local simulators and real IBM Quantum hardware.

This project has evolved to use a Jupyter Notebook (`demo_quantum.ipynb`) as the primary interface for quantum solving. It provides a step-by-step workflow from problem definition to hardware execution.

### Features:
- **Jupyter Notebook Workflow:** Interactive environment for running experiments.
- **Real Hardware Execution:** Connects to IBM Quantum via `qiskit-ibm-runtime` to run on real devices.
- **Modern Qiskit Primitives:** Uses the latest `SamplerV2` primitive for both simulation and hardware jobs.
- **Automated Oracle Creation:** Parses industry-standard DIMACS CNF files directly into a `PhaseOracle`.
- **Hardware-Aware Transpilation:** Includes the necessary transpilation step (`generate_preset_pass_manager`) to convert the ideal quantum circuit into one that can run on the target backend's specific hardware architecture (ISA).
- **Advanced Result Handling:** Shows how to process the new `DataBin` result format from `SamplerV2` and includes logic to filter and display the most probable solutions.

### Dependencies:
Create a conda environment for this project:
```bash
conda create -n quantum python=3.10
conda activate quantum
pip install qiskit qiskit-aer qiskit-ibm-runtime matplotlib numpy ipykernel
python -m ipykernel install --user --name=quantum
```

### Usage:
1.  **Activate Environment:** `conda activate quantum`
2.  **Launch VS Code and Open Notebook:** Open the `demo_quantum.ipynb` file.
3.  **Select Kernel:** When prompted, select the `quantum` kernel you just created.
4.  **Add API Token:** In the second cell, replace the placeholder with your IBM Quantum API token.
5.  **Run Cells:** Execute the cells sequentially to connect to the service, select a backend, and run the solver on a test file.

## 4. Legacy Quantum Solver (`quantum_solver.py`)
This is the original, simulator-based implementation of Grover's algorithm. It is less feature-rich than the notebook version and does not support real hardware execution. It is kept for historical and comparative purposes. The `dimacs_test_runner.py` uses this solver when run with the `quantum` command.

## Performance Comparison

| Solver Type | Time Complexity | Best Use Case | Output |
|-------------|----------------|---------------|---------|
| DPLL | O(2^n) worst case | Single solution needed | First solution |
| Backtrack | O(2^n) | All solutions needed | All solutions |
| Quantum | O(√(2^n)) theoretical | Multiple solutions, hardware demo | Probabilistic solutions |

**Note:** Practical quantum speedup is not expected on current noisy, small-scale quantum computers. The primary goal of `demo_quantum.ipynb` is to demonstrate the complete workflow for executing a quantum algorithm on real hardware.

## Test Runner (`dimacs_test_runner.py`)

Unified test runner for the classical solvers and the legacy quantum solver.

### Commands:
```bash
# Run DPLL solver
python3 dimacs_test_runner.py test.cnf

# Run legacy quantum solver (simulator only)
python3 dimacs_test_runner.py quantum test.cnf

# Compare all classical/legacy approaches
python3 dimacs_test_runner.py compare test.cnf

# Run all tests (from tests/ folder)
python3 dimacs_test_runner.py all
```

**Note:** To run the modern, hardware-capable quantum solver, please use the `demo_quantum.ipynb` notebook.

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

## Files Structure

```
├── demo_quantum.ipynb       # Modern, hardware-capable quantum solver notebook
├── dpll_solver.py           # DPLL algorithm implementation
├── backtrack_solver.py      # Backtracking algorithm implementation
├── dimacs_test_runner.py    # Unified test runner for classical/legacy solvers
├── quantum_solver.py        # Legacy quantum Grover algorithm (simulator only)
├── variable.py              # Variable class definition for legacy solvers
├── tests/                   # Test files directory in DIMACS format
│   ├── test_simple.cnf
│   ├── test_complex.cnf  
│   ├── test_multiple.cnf
│   ├── test_unit.cnf
│   ├── test_unsat.cnf
│   └── ...
└── README.md                # This file
```

## Research Applications

This suite enables comparative studies of:
- Classical vs. quantum algorithm performance.
- The practical workflow of running algorithms on real quantum hardware.
- Scalability analysis across different problem sizes.
- Algorithm behavior on different SAT instance types.

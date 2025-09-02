# SAT Solver Suite

This project provides a suite of solvers for the Boolean Satisfiability Problem (SAT), allowing for comparison between classical and quantum approaches. It includes:

1.  **DPLL Solver**: A fast, classical algorithm for finding a single SAT solution.
2.  **Backtracking Solver**: A classical algorithm for finding all possible SAT solutions.
3.  **Quantum Hardware Solver**: A modern quantum solver using Grover's Algorithm, capable of running on both simulators and real IBM Quantum hardware.

The project also includes scripts for running individual tests and performing a three-way performance comparison between the solvers.

## Solvers

### 1. DPLL Solver (`dpll_solver.py`)
- **Algorithm:** Davis-Putnam-Logemann-Loveland (DPLL)
- **Type:** Classical, deterministic
- **Purpose:** Find the *first* satisfying assignment efficiently.
- **Features:** Unit propagation, pure literal elimination, and backtracking search.

### 2. Backtrack Solver (`backtrack_solver.py`)
- **Algorithm:** Exhaustive backtracking
- **Type:** Classical, deterministic
- **Purpose:** Find *all* satisfying assignments.
- **Features:** Systematic exploration of the entire solution space.

### 3. Quantum Hardware Solver (`quantum_hardware_solver.py`)
- **Algorithm:** Grover's Algorithm
- **Type:** Quantum, probabilistic
- **Purpose:** Solve SAT problems on simulators or real IBM Quantum hardware.
- **Features:**
    - **Real Hardware Execution:** Connects to IBM Quantum via `qiskit-ibm-runtime`.
    - **Modern Qiskit Primitives:** Uses the latest `SamplerV2` primitive.
    - **Automated Oracle Creation:** Parses industry-standard DIMACS CNF files.
    - **Hardware-Aware Transpilation:** Prepares the quantum circuit to run on the specific architecture of the chosen backend.
    - **Result Plotting:** Generates and saves a plot of the measurement outcomes.

## Dependencies and Setup

It is recommended to use a `conda` environment.

1.  **Create and activate the environment:**
    ```bash
    conda create -n quantum-sat python=3.10
    conda activate quantum-sat
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up IBM Quantum Token:**
    Create a file named `.env` in the root of the project directory and add your IBM Quantum API token to it:
    ```
    IBM_QUANTUM_TOKEN="YOUR_API_TOKEN_HERE"
    ```
    The `.gitignore` file is already configured to ignore this file.

## Usage

### Main Test Runner (`dimacs_test_runner.py`)

This is the primary script for running tests on individual DIMACS files.

**Commands:**
```bash
# Run the classical backtrack solver on a single file
python3 dimacs_test_runner.py tests/test_simple.cnf

# Run the classical backtrack solver on all tests in the tests/ directory
python3 dimacs_test_runner.py all

# Run the quantum hardware solver on a single file
python3 dimacs_test_runner.py quantum tests/test_simple.cnf

# Run the quantum hardware solver on all tests in the tests/ directory
python3 dimacs_test_runner.py quantum all
```

## DIMACS Format

The DIMACS CNF format is the standard for representing SAT problems:
```
c This is a comment
p cnf <num_variables> <num_clauses>
<literal> <literal> ... 0
...
```
**Example:** `(x1 ∨ x2) ∧ (¬x1 ∨ x3)`
```
c Simple SAT problem
p cnf 3 2
1 2 0
-1 3 0
```

## 4. Legacy Quantum Solver (`quantum_solver.py`)
This is the original, simulator-based implementation of Grover's algorithm. It is less feature-rich than the notebook version and does not support real hardware execution. It is kept for historical and comparative purposes. The `dimacs_test_runner.py` uses this solver when run with the `quantum` command.

## Performance Comparison

| Solver Type | Time Complexity | Best Use Case | Output |
|-------------|----------------|---------------|---------|
| DPLL | O(2^n) worst case | Single solution needed | First solution |
| Backtrack | O(2^n) | All solutions needed | All solutions |
| Quantum | O(√(2^n)) theoretical | Multiple solutions, hardware demo | Probabilistic solutions |

**Note:** Practical quantum speedup is not expected on current noisy, small-scale quantum computers. The primary goal of `demo_quantum.ipynb` is to demonstrate the complete workflow for executing a quantum algorithm on real hardware.


**Note:** To run the modern, hardware-capable quantum solver, please use the `demo_quantum.ipynb` notebook.

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
└── README.md                
```

## Research Applications

This suite enables comparative studies of:
- Classical vs. quantum algorithm performance.
- The practical workflow of running algorithms on real quantum hardware.
- Scalability analysis across different problem sizes.
- Algorithm behavior on different SAT instance types.

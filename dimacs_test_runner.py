import sys
import os
from variable import Variable
from dpll_solver import find_first_solution
from backtrack_solver import find_all_solutions_backtrack
from quantum_hardware_solver import solve_with_grover_on_hardware
import dpll_solver
import backtrack_solver

class DIMACSParser:
    def __init__(self):
        self.variables = {}
        self.num_vars = 0
        self.num_clauses = 0
    
    def get_variable(self, var_id):
        """Get or create a variable by its numeric ID"""
        if var_id not in self.variables:
            self.variables[var_id] = Variable(f"x{var_id}")
        return self.variables[var_id]
    
    def parse_dimacs_file(self, filename):
        """Parse a DIMACS CNF file and return clauses"""
        clauses = []
        
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('c'):
                    continue
                
                # Parse problem line
                if line.startswith('p cnf'):
                    parts = line.split()
                    if len(parts) >= 4:
                        self.num_vars = int(parts[2])
                        self.num_clauses = int(parts[3])
                    continue
                
                # Parse clause line
                if line and not line.startswith('c') and not line.startswith('p'):
                    literals = line.split()
                    
                    # Remove the trailing 0 if present
                    if literals and literals[-1] == '0':
                        literals = literals[:-1]
                    
                    if literals:  # Only process non-empty clauses
                        clause = []
                        for lit_str in literals:
                            lit_int = int(lit_str)
                            if lit_int != 0:  # Ignore 0 (clause terminator)
                                var_id = abs(lit_int)
                                var = self.get_variable(var_id)
                                if lit_int > 0:
                                    clause.append(var)
                                else:
                                    clause.append(-var)
                        
                        if clause:  # Only add non-empty clauses
                            clauses.append(clause)
        
        return clauses
    
    def get_variable_mapping(self):
        """Return mapping of variable IDs to Variable objects"""
        return self.variables

def load_dimacs_test_case(filename):
    """Load a test case from a DIMACS file"""
    parser = DIMACSParser()
    clauses = parser.parse_dimacs_file(filename)
    return clauses, parser

def run_quantum_test_case(filename):
    """Run a single DIMACS test case using the quantum hardware solver"""
    print(f"--- Running Quantum Hardware Test: {os.path.basename(filename)} ---")
    try:
        # The hardware solver works directly with the file path
        solution, execution_time = solve_with_grover_on_hardware(filename, plot=True)
        
        if solution is None:
            print("Result: ❌ UNSAT (or no clear solution found)")
        else:
            print("Result: ✅ SAT")
            print(f"Most likely solution bitstring: {solution}")
        
        print(f"Quantum execution time: {execution_time:.6f} seconds (includes queue time)")
        return True
        
    except Exception as e:
        print(f"❌ Quantum solver failed: {e}")
        return False

def run_all_tests(test_type='classical'):
    """Run all DIMACS test files in the tests directory for a specific solver type."""
    tests_dir = 'tests'
    if not os.path.exists(tests_dir):
        print(f"Tests directory '{tests_dir}' not found")
        return
    
    test_files = [f for f in os.listdir(tests_dir) if f.endswith('.cnf')]
    
    if not test_files:
        print(f"No DIMACS test files (*.cnf) found in '{tests_dir}' directory.")
        return
    
    print(f"\n{'='*50}")
    print(f"RUNNING ALL {test_type.upper()} TESTS")
    print(f"{'='*50}")
    
    passed = 0
    total = len(test_files)
    
    for test_file in test_files:
        test_path = os.path.join(tests_dir, test_file)
        print(f"\n--- Testing: {test_file} ---")
        
        success = False
        if test_type == 'classical':
            # For simplicity, using backtrack solver as the classical representative
            clauses, _ = load_dimacs_test_case(test_path)
            solutions, _ = find_all_solutions_backtrack(clauses)
            success = len(solutions) > 0
            print(f"Backtrack Solver Result: {'SAT' if success else 'UNSAT'}")
        elif test_type == 'quantum':
            success = run_quantum_test_case(test_path)

        if success:
            passed += 1
            
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} tests passed for {test_type} solver.")
    print('='*50)

def resolve_test_file_path(filename):
    """Helper to find file in current dir or tests/ dir."""
    if os.path.exists(filename):
        return filename
    test_path = os.path.join('tests', filename)
    if os.path.exists(test_path):
        return test_path
    return None

# Main execution
if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "all":
            run_all_tests('classical')
        elif command == "quantum":
            if len(sys.argv) > 2 and sys.argv[2] == "all":
                run_all_tests('quantum')
            elif len(sys.argv) > 2:
                filename = resolve_test_file_path(sys.argv[2])
                if filename:
                    run_quantum_test_case(filename)
                else:
                    print(f"Error: Test file not found: {sys.argv[2]}")
            else:
                print("Usage: python3 dimacs_test_runner.py quantum <file.cnf | all>")
        else:
            filename = resolve_test_file_path(command)
            if filename:
                print(f"--- Running Classical Test: {os.path.basename(filename)} ---")
                clauses, _ = load_dimacs_test_case(filename)
                solutions, exec_time = find_all_solutions_backtrack(clauses)
                print(f"Result: {'SAT' if solutions else 'UNSAT'}")
                print(f"Solutions found: {len(solutions)}")
                print(f"Execution time: {exec_time:.6f}s")
            else:
                print(f"Error: Test file not found: {command}")
    else:
        print("DIMACS Test Runner")
        print("Usage:")
        print("  python3 dimacs_test_runner.py <file.cnf>   # Run single classical test")
        print("  python3 dimacs_test_runner.py all          # Run all classical tests")
        print("  python3 dimacs_test_runner.py quantum <file.cnf> # Run single quantum test")
        print("  python3 dimacs_test_runner.py quantum all      # Run all quantum tests")

import sys
import os
from variable import Variable
from dpll_solver import find_first_solution
from backtrack_solver import find_all_solutions_backtrack as find_all_solutions
from quantum_solver import find_quantum_solution, find_all_quantum_solutions, compare_quantum_classical
import dpll_solver
import backtrack_solver
import quantum_solver

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

def run_dimacs_test_case(filename):
    """Run a single DIMACS test case and return results"""
    try:
        clauses, parser = load_dimacs_test_case(filename)
        print(f"Running DIMACS test: {filename}")
        print(f"Variables: {parser.num_vars}, Clauses: {parser.num_clauses}")
        
        # Find all solutions with timing
        all_solutions, execution_time = find_all_solutions(clauses)
        
        if not all_solutions:
            result = "UNSAT"
            print(f"Result: {result}")
            print("No solutions found")
        else:
            result = "SAT"
            print(f"Result: {result}")
            print(f"Found {len(all_solutions)} solution(s):")
            for i, sol in enumerate(all_solutions, 1):
                print(f"  Solution {i}: {sol}")
        
        print(f"Execution time: {execution_time:.6f} seconds")
        
        return True
        
    except FileNotFoundError:
        print(f"Error: File {filename} not found")
        return False
    except Exception as e:
        print(f"Error loading DIMACS file: {e}")
        return False

def run_timing_comparison(filename):
    """Run timing comparison between first solution and all solutions"""
    try:
        clauses, parser = load_dimacs_test_case(filename)
        print(f"Timing comparison for: {filename}")
        print(f"Variables: {parser.num_vars}, Clauses: {parser.num_clauses}")
        print("="*60)
        
        # Time finding first solution only
        print("Finding FIRST solution...")
        first_solution, first_time = find_first_solution(clauses)
        if first_solution is None:
            print("Result: UNSAT")
        else:
            print(f"First solution: {first_solution}")
        print(f"Time for first solution: {first_time:.6f} seconds")
        
        print("\nFinding ALL solutions...")
        # Time finding all solutions
        all_solutions, all_time = find_all_solutions(clauses)
        if not all_solutions:
            print("Result: UNSAT")
        else:
            print(f"Found {len(all_solutions)} total solution(s)")
        print(f"Time for all solutions: {all_time:.6f} seconds")
        
        if first_solution is not None and all_solutions:
            speedup = all_time / first_time if first_time > 0 else float('inf')
            print(f"\nSpeedup ratio (all/first): {speedup:.2f}x")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def run_quantum_test_case(filename):
    """Run a single DIMACS test case using quantum solver"""
    try:
        clauses, parser = load_dimacs_test_case(filename)
        print(f"Running Quantum DIMACS test: {filename}")
        print(f"Variables: {parser.num_vars}, Clauses: {parser.num_clauses}")
        
        # Find solutions using quantum approach
        quantum_solutions, execution_time = find_all_quantum_solutions(clauses)
        
        if not quantum_solutions:
            result = "UNSAT"
            print(f"Result: {result}")
            print("No solutions found")
        else:
            result = "SAT"
            print(f"Result: {result}")
            print(f"Found {len(quantum_solutions)} solution(s):")
            for i, sol in enumerate(quantum_solutions, 1):
                print(f"  Solution {i}: {sol}")
        
        print(f"Quantum execution time: {execution_time:.6f} seconds")
        
        return True
        
    except FileNotFoundError:
        print(f"Error: File {filename} not found")
        return False
    except Exception as e:
        print(f"Error loading DIMACS file: {e}")
        return False

def run_comparison_test(cnf_file):
    """Run comprehensive three-way comparison: DPLL vs Backtrack vs Quantum"""
    print(f"Three-way comparison test for: {cnf_file}")
    
    try:
        # Read and parse the CNF file  
        clauses, parser = load_dimacs_test_case(cnf_file)
        if not clauses:
            print("Error: Could not read CNF file or file is empty")
            return
        
        print(f"Variables: {parser.num_vars}, Clauses: {parser.num_clauses}")
        
        results = {}
        
        # 1. DPLL Solver (first solution)
        print("\n--- DPLL SOLVER (First solution) ---")
        try:
            solution, exec_time = dpll_solver.find_first_solution(clauses)
            results['dpll'] = {
                'success': solution is not None,
                'solution': solution,
                'time': exec_time,
                'solutions_count': 1 if solution else 0
            }
            print(f"DPLL result: {'SAT' if solution else 'UNSAT'}")
            if solution:
                print(f"DPLL solution: {solution}")
            print(f"DPLL time: {exec_time:.6f} seconds")
        except Exception as e:
            print(f"DPLL failed: {e}")
            results['dpll'] = {'success': False, 'time': float('inf')}
        
        # 2. Backtrack Solver (all solutions)
        print("\n--- BACKTRACK SOLVER (All solutions) ---") 
        try:
            solutions, exec_time = backtrack_solver.find_all_solutions_backtrack(clauses)
            results['backtrack'] = {
                'success': len(solutions) > 0,
                'solutions': solutions,
                'time': exec_time,
                'solutions_count': len(solutions)
            }
            print(f"Backtrack result: {'SAT' if solutions else 'UNSAT'}")
            print(f"Backtrack solutions found: {len(solutions)}")
            if solutions:
                print(f"First solution: {solutions[0]}")
                if len(solutions) > 1:
                    print(f"Total solutions: {len(solutions)}")
            print(f"Backtrack time: {exec_time:.6f} seconds")
        except Exception as e:
            print(f"Backtrack failed: {e}")
            results['backtrack'] = {'success': False, 'time': float('inf')}
        
        # 3. Quantum Solver  
        print("\n--- QUANTUM SOLVER ---")
        try:
            solutions, exec_time = find_all_quantum_solutions(clauses)
            results['quantum'] = {
                'success': len(solutions) > 0,
                'solutions': solutions, 
                'time': exec_time,
                'solutions_count': len(solutions)
            }
            print(f"Quantum result: {'SAT' if solutions else 'UNSAT'}")
            print(f"Quantum solutions found: {len(solutions)}")
            if solutions:
                print(f"First solution: {solutions[0]}")
                if len(solutions) > 3:
                    print(f"Sample solutions: {solutions[:3]}...")
            print(f"Quantum time: {exec_time:.6f} seconds")
        except Exception as e:
            print(f"Quantum failed: {e}")
            results['quantum'] = {'success': False, 'time': float('inf')}
        
        # Speedup Analysis
        print("\n" + "="*60)
        print("SPEEDUP ANALYSIS")
        print("="*60)
        
        if results['dpll']['success'] and results['backtrack']['success']:
            dpll_vs_backtrack = results['backtrack']['time'] / results['dpll']['time']
            print(f"Backtrack vs DPLL: {dpll_vs_backtrack:.2f}x {'(DPLL faster)' if dpll_vs_backtrack > 1 else '(Backtrack faster)'}")
        
        # KEY METRIC: Backtrack vs Quantum speedup
        if results['backtrack']['success'] and results['quantum']['success']:
            backtrack_vs_quantum = results['backtrack']['time'] / results['quantum']['time']
            print(f"🎯 BACKTRACK vs QUANTUM: {backtrack_vs_quantum:.2f}x {'(Quantum faster)' if backtrack_vs_quantum > 1 else '(Backtrack faster)'}")
            
            if backtrack_vs_quantum > 1:
                print(f"   ✅ Quantum achieved {backtrack_vs_quantum:.2f}x speedup over Backtrack!")
            else:
                print(f"   ❌ Backtrack is {1/backtrack_vs_quantum:.2f}x faster than Quantum")
                print(f"      (Expected for small problems on classical quantum simulators)")
        
        if results['dpll']['success'] and results['quantum']['success']:
            dpll_vs_quantum = results['quantum']['time'] / results['dpll']['time']
            print(f"DPLL vs Quantum: {dpll_vs_quantum:.2f}x {'(DPLL faster)' if dpll_vs_quantum > 1 else '(Quantum faster)'}")
        
        # Solution completeness
        if results['backtrack']['success'] and results['quantum']['success']:
            backtrack_count = results['backtrack']['solutions_count']
            quantum_count = results['quantum']['solutions_count']
            completeness = (quantum_count / backtrack_count) * 100 if backtrack_count > 0 else 0
            print(f"\nSolution completeness: Quantum found {quantum_count}/{backtrack_count} solutions ({completeness:.1f}%)")
        
        print("="*60)
        
    except Exception as e:
        print(f"Error in three-way comparison: {e}")
           
        print(f"DPLL result: {'SAT' if solution else 'UNSAT'}")
        if solution:
            print(f"DPLL solution: {solution}")
        print(f"DPLL time: {exec_time:.6f} seconds")
    except Exception as e:
        print(f"DPLL failed: {e}")
        results['dpll'] = {'success': False, 'time': float('inf')}
    
        # 2. Backtrack Solver (all solutions)
        print("--- BACKTRACK SOLVER (All solutions) ---") 
        try:
            solutions, exec_time = backtrack_solver.find_all_solutions_backtrack(clauses)
            results['backtrack'] = {
                'success': len(solutions) > 0,
                'solutions': solutions,
                'time': exec_time,
                'solutions_count': len(solutions)
            }
            print(f"Backtrack result: {'SAT' if solutions else 'UNSAT'}")
            print(f"Backtrack solutions found: {len(solutions)}")
            if solutions:
                print(f"First solution: {solutions[0]}")
                if len(solutions) > 1:
                    print(f"Total solutions: {len(solutions)}")
            print(f"Backtrack time: {exec_time:.6f} seconds")
        except Exception as e:
            print(f"Backtrack failed: {e}")
            results['backtrack'] = {'success': False, 'time': float('inf')}
        
        # 3. Quantum Solver  
        print("--- QUANTUM SOLVER ---")
        try:
            solutions, exec_time = quantum_solver.find_all_quantum_solutions(clauses)
            results['quantum'] = {
                'success': len(solutions) > 0,
                'solutions': solutions, 
                'time': exec_time,
                'solutions_count': len(solutions)
            }
            print(f"Quantum result: {'SAT' if solutions else 'UNSAT'}")
            print(f"Quantum solutions found: {len(solutions)}")
            if solutions:
                print(f"First solution: {solutions[0]}")
                if len(solutions) > 3:
                    print(f"Sample solutions: {solutions[:3]}...")
            print(f"Quantum time: {exec_time:.6f} seconds")
        except Exception as e:
            print(f"Quantum failed: {e}")
            results['quantum'] = {'success': False, 'time': float('inf')}
        
        # Speedup Analysis
        print("" + "="*60)
        print("SPEEDUP ANALYSIS")
        print("="*60)
        
        if results['dpll']['success'] and results['backtrack']['success']:
            dpll_vs_backtrack = results['backtrack']['time'] / results['dpll']['time']
            print(f"Backtrack vs DPLL: {dpll_vs_backtrack:.2f}x {'(DPLL faster)' if dpll_vs_backtrack > 1 else '(Backtrack faster)'}")
        
        # KEY METRIC: Backtrack vs Quantum speedup
        if results['backtrack']['success'] and results['quantum']['success']:
            backtrack_vs_quantum = results['backtrack']['time'] / results['quantum']['time']
            print(f"🎯 BACKTRACK vs QUANTUM: {backtrack_vs_quantum:.2f}x {'(Quantum faster)' if backtrack_vs_quantum > 1 else '(Backtrack faster)'}")
            
            if backtrack_vs_quantum > 1:
                print(f"   ✅ Quantum achieved {backtrack_vs_quantum:.2f}x speedup over Backtrack!")
            else:
                print(f"   ❌ Backtrack is {1/backtrack_vs_quantum:.2f}x faster than Quantum")
                print(f"      (Expected for small problems on classical quantum simulators)")
        
        if results['dpll']['success'] and results['quantum']['success']:
            dpll_vs_quantum = results['quantum']['time'] / results['dpll']['time']
            print(f"DPLL vs Quantum: {dpll_vs_quantum:.2f}x {'(DPLL faster)' if dpll_vs_quantum > 1 else '(Quantum faster)'}")
        
        # Solution completeness
        if results['backtrack']['success'] and results['quantum']['success']:
            backtrack_count = results['backtrack']['solutions_count']
            quantum_count = results['quantum']['solutions_count']
            completeness = (quantum_count / backtrack_count) * 100 if backtrack_count > 0 else 0
            print(f"Solution completeness: Quantum found {quantum_count}/{backtrack_count} solutions ({completeness:.1f}%)")
        
        print("="*60)
        
    except Exception as e:
        print(f"Error in three-way comparison: {e}")

def convert_yaml_to_dimacs(yaml_filename, dimacs_filename):
    """Convert a YAML test file to DIMACS format"""
    try:
        import yaml
        
        # Parse the YAML file
        with open(yaml_filename, 'r') as file:
            data = yaml.safe_load(file)
        
        # Extract variables from clauses
        variables = set()
        for clause in data['clauses']:
            for literal in clause:
                var_name = literal.lstrip('-')
                variables.add(var_name)
        
        # Create variable mapping
        var_list = sorted(list(variables))
        var_map = {var: i+1 for i, var in enumerate(var_list)}
        
        # Write DIMACS file
        with open(dimacs_filename, 'w') as file:
            # Write comments
            file.write(f"c Converted from {yaml_filename}\n")
            if 'description' in data:
                file.write(f"c {data['description']}\n")
            
            # Write variable mapping as comments
            file.write("c Variable mapping:\n")
            for var, var_id in var_map.items():
                file.write(f"c {var} = {var_id}\n")
            
            # Write problem line
            num_vars = len(variables)
            num_clauses = len(data['clauses'])
            file.write(f"p cnf {num_vars} {num_clauses}\n")
            
            # Write clauses
            for clause in data['clauses']:
                dimacs_clause = []
                for literal in clause:
                    if literal.startswith('-'):
                        var_name = literal[1:]
                        dimacs_clause.append(f"-{var_map[var_name]}")
                    else:
                        dimacs_clause.append(str(var_map[literal]))
                
                file.write(" ".join(dimacs_clause) + " 0\n")
        
        print(f"Successfully converted {yaml_filename} to {dimacs_filename}")
        
    except Exception as e:
        print(f"Error converting {yaml_filename}: {e}")

def resolve_test_file_path(filename):
    """Resolve the full path for a test file, checking both current dir and tests dir"""
    # If it's already an absolute path or contains directory separators, use as-is
    if os.path.isabs(filename) or os.sep in filename:
        return filename
    
    # Check if file exists in current directory
    if os.path.exists(filename):
        return filename
    
    # Check if file exists in tests directory
    tests_path = os.path.join('tests', filename)
    if os.path.exists(tests_path):
        return tests_path
    
    # If neither exists, return the original filename (will cause FileNotFoundError later)
    return filename

def run_all_dimacs_tests():
    """Run all DIMACS test files in the tests directory"""
    tests_dir = 'tests'
    if not os.path.exists(tests_dir):
        print(f"Tests directory '{tests_dir}' not found")
        return
    
    test_files = [f for f in os.listdir(tests_dir) if f.endswith('.cnf') or f.endswith('.dimacs')]
    
    if not test_files:
        print(f"No DIMACS test files found in '{tests_dir}' directory (looking for *.cnf or *.dimacs)")
        return
    
    passed = 0
    total = len(test_files)
    total_time = 0
    
    for test_file in test_files:
        test_path = os.path.join(tests_dir, test_file)
        print(f"\n{'='*50}")
        print(f"Running {test_file}")
        print('='*50)
        
        # Get timing info
        try:
            clauses, parser = load_dimacs_test_case(test_path)
            all_solutions, execution_time = find_all_solutions(clauses)
            total_time += execution_time
            
            if run_dimacs_test_case(test_path):
                passed += 1
        except Exception as e:
            print(f"Test failed to run: {e}")
    
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"Total execution time: {total_time:.6f} seconds")
    print('='*50)


# Main execution
if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "all":
            run_all_dimacs_tests()
        elif sys.argv[1] == "timing" and len(sys.argv) > 2:
            # Run timing comparison for specific file
            filename = resolve_test_file_path(sys.argv[2])
            run_timing_comparison(filename)
        elif sys.argv[1] == "quantum" and len(sys.argv) > 2:
            # Run quantum solver for specific file
            filename = resolve_test_file_path(sys.argv[2])
            run_quantum_test_case(filename)
        elif sys.argv[1] == "compare" and len(sys.argv) > 2:
            # Run comparison between classical and quantum solvers
            filename = resolve_test_file_path(sys.argv[2])
            run_comparison_test(filename)
        elif sys.argv[1] == "convert" and len(sys.argv) > 2:
            # Convert YAML to DIMACS
            yaml_file = sys.argv[2]
            dimacs_file = sys.argv[3] if len(sys.argv) > 3 else yaml_file.replace('.yaml', '.cnf')
            convert_yaml_to_dimacs(yaml_file, dimacs_file)
        else:
            # Load test case from DIMACS file
            filename = resolve_test_file_path(sys.argv[1])
            run_dimacs_test_case(filename)
    else:
        # Show usage information
        print("DIMACS Test Runner")
        print("Usage:")
        print("  python3 dimacs_test_runner.py <file.cnf>              # Run single DIMACS test")
        print("  python3 dimacs_test_runner.py all                     # Run all DIMACS tests (from tests/ folder)")
        print("  python3 dimacs_test_runner.py timing <file.cnf>       # Compare timing")
        print("  python3 dimacs_test_runner.py quantum <file.cnf>      # Run quantum solver")
        print("  python3 dimacs_test_runner.py compare <file.cnf>      # Compare classical vs quantum")
        print("  python3 dimacs_test_runner.py convert <file.yaml>     # Convert YAML to DIMACS")
        print("  python3 dimacs_test_runner.py convert <file.yaml> <output.cnf>  # Convert with custom output name")
        print("\nNote: Test files are automatically searched in both current directory and tests/ folder")
        
        # Show example DIMACS format
        print("\nDIMACS CNF Format:")
        print("c This is a comment")
        print("p cnf <num_variables> <num_clauses>")
        print("<literal> <literal> ... 0")
        print("...")
        print("\nExample:")
        print("c Simple SAT problem")
        print("p cnf 3 2")
        print("1 2 0")
        print("-1 3 0")

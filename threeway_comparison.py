#!/usr/bin/env python3
"""
Simple three-way comparison command for SAT solvers
"""

import sys
import os
from variable import Variable
import dpll_solver
import backtrack_solver
from quantum_solver import find_all_quantum_solutions

def load_dimacs_cnf(filename):
    """Load DIMACS CNF file and return clauses"""
    from variable import Variable
    
    variables = {}
    clauses = []
    
    def get_variable(var_id):
        """Get or create a variable by its numeric ID"""
        if var_id not in variables:
            variables[var_id] = Variable(f"x{var_id}")
        return variables[var_id]
    
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('c'):
                continue
            
            # Parse problem line
            if line.startswith('p cnf'):
                parts = line.split()
                num_vars = int(parts[2])
                num_clauses = int(parts[3])
                continue
            
            # Parse clause
            clause_numbers = list(map(int, line.split()))
            if clause_numbers[-1] != 0:
                raise ValueError(f"Clause should end with 0: {line}")
            
            # Remove the trailing 0
            clause_numbers = clause_numbers[:-1]
            
            # Convert to Variable objects
            clause = []
            for num in clause_numbers:
                if num > 0:
                    clause.append(get_variable(num))
                else:
                    clause.append(-get_variable(-num))
            
            clauses.append(clause)
    
    return clauses, num_vars, num_clauses

def run_threeway_comparison(cnf_file):
    """Run comprehensive three-way comparison: DPLL vs Backtrack vs Quantum"""
    
    print(f"🔬 THREE-WAY SAT SOLVER COMPARISON: {cnf_file}")
    print("="*70)
    
    try:
        # Load the DIMACS test case
        clauses, num_vars, num_clauses = load_dimacs_cnf(cnf_file)
        if not clauses:
            print("Error: Could not read CNF file or file is empty")
            return
        
        print(f"Problem: {num_vars} variables, {num_clauses} clauses")
        
        results = {}
        
        # 1. DPLL Solver (first solution only)
        print(f"\n{'='*20} DPLL SOLVER {'='*20}")
        try:
            solution, exec_time = dpll_solver.find_first_solution(clauses)
            results['dpll'] = {
                'success': solution is not None,
                'solution': solution,
                'time': exec_time,
                'solutions_count': 1 if solution else 0
            }
            print(f"Result: {'✅ SAT' if solution else '❌ UNSAT'}")
            if solution:
                print(f"Solution: {solution}")
            print(f"Time: {exec_time:.6f} seconds")
        except Exception as e:
            print(f"❌ DPLL failed: {e}")
            results['dpll'] = {'success': False, 'time': float('inf')}
        
        # 2. Backtrack Solver (all solutions)
        print(f"\n{'='*20} BACKTRACK SOLVER {'='*20}")
        try:
            solutions, exec_time = backtrack_solver.find_all_solutions_backtrack(clauses)
            results['backtrack'] = {
                'success': len(solutions) > 0,
                'solutions': solutions,
                'time': exec_time,
                'solutions_count': len(solutions)
            }
            print(f"Result: {'✅ SAT' if solutions else '❌ UNSAT'}")
            print(f"Solutions found: {len(solutions)}")
            if solutions:
                print(f"First solution: {solutions[0]}")
                if len(solutions) > 1:
                    print(f"All solutions: {len(solutions)} total")
            print(f"Time: {exec_time:.6f} seconds")
        except Exception as e:
            print(f"❌ Backtrack failed: {e}")
            results['backtrack'] = {'success': False, 'time': float('inf')}
        
        # 3. Quantum Solver (probabilistic all solutions)
        print(f"\n{'='*20} QUANTUM SOLVER {'='*20}")
        try:
            solutions, exec_time = find_all_quantum_solutions(clauses)
            results['quantum'] = {
                'success': len(solutions) > 0,
                'solutions': solutions,
                'time': exec_time,
                'solutions_count': len(solutions)
            }
            print(f"Result: {'✅ SAT' if solutions else '❌ UNSAT'}")
            print(f"Solutions found: {len(solutions)}")
            if solutions:
                print(f"First solution: {solutions[0]}")
                if len(solutions) > 3:
                    print(f"Sample solutions: {solutions[:3]}... (showing 3/{len(solutions)})")
            print(f"Time: {exec_time:.6f} seconds")
        except Exception as e:
            print(f"❌ Quantum failed: {e}")
            results['quantum'] = {'success': False, 'time': float('inf')}
        
        # 🎯 SPEEDUP ANALYSIS
        print(f"\n{'='*25} SPEEDUP ANALYSIS {'='*25}")
        
        if results['dpll']['success'] and results['backtrack']['success']:
            dpll_vs_backtrack = results['backtrack']['time'] / results['dpll']['time']
            print(f"Backtrack vs DPLL: {dpll_vs_backtrack:.2f}x {'(DPLL faster)' if dpll_vs_backtrack > 1 else '(Backtrack faster)'}")
        
        # 🎯 KEY METRIC: Backtrack vs Quantum speedup
        if results['backtrack']['success'] and results['quantum']['success']:
            backtrack_vs_quantum = results['backtrack']['time'] / results['quantum']['time']
            print(f"🎯 BACKTRACK vs QUANTUM: {backtrack_vs_quantum:.2f}x", end="")
            
            if backtrack_vs_quantum > 1:
                print(f" (Quantum faster)")
                print(f"   ✅ Quantum achieved {backtrack_vs_quantum:.2f}x speedup over Backtrack!")
            else:
                print(f" (Backtrack faster)")
                print(f"   ⚠️  Backtrack is {1/backtrack_vs_quantum:.2f}x faster than Quantum")
                print(f"      (Expected for small problems on classical quantum simulators)")
        
        if results['dpll']['success'] and results['quantum']['success']:
            dpll_vs_quantum = results['quantum']['time'] / results['dpll']['time']
            print(f"DPLL vs Quantum: {dpll_vs_quantum:.2f}x {'(DPLL faster)' if dpll_vs_quantum > 1 else '(Quantum faster)'}")
        
        # Solution completeness analysis
        if results['backtrack']['success'] and results['quantum']['success']:
            backtrack_count = results['backtrack']['solutions_count']
            quantum_count = results['quantum']['solutions_count']
            completeness = (quantum_count / backtrack_count) * 100 if backtrack_count > 0 else 0
            print(f"\n📊 Solution completeness: Quantum found {quantum_count}/{backtrack_count} solutions ({completeness:.1f}%)")
        
        print("="*70)
        
    except Exception as e:
        print(f"❌ Error in three-way comparison: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 threeway_comparison.py <test_file.cnf>")
        print("Example: python3 threeway_comparison.py tests/test_simple.cnf")
        sys.exit(1)
    
    cnf_file = sys.argv[1]
    
    # Check if file exists in current directory or tests/ directory
    if not os.path.exists(cnf_file):
        test_path = os.path.join("tests", cnf_file)
        if os.path.exists(test_path):
            cnf_file = test_path
        else:
            print(f"Error: Could not find file {cnf_file}")
            sys.exit(1)
    
    run_threeway_comparison(cnf_file)

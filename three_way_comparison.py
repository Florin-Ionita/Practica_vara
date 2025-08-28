#!/usr/bin/env python3
"""
Three-way comparison: DPLL vs Backtrack vs Quantum SAT Solvers
Focus on Backtrack vs Quantum speedup analysis
"""

import time
from variable import Variable
from dpll_solver import find_first_solution as dpll_solve
from backtrack_solver import find_all_solutions_backtrack
from quantum_solver import find_all_quantum_solutions

def compare_all_three_solvers(clauses, test_name="Test"):
    """
    Compare DPLL, Backtrack, and Quantum solvers
    Focus on the speedup between Backtrack and Quantum
    """
    print("=" * 80)
    print(f"THREE-WAY SAT SOLVER COMPARISON: {test_name}")
    print("=" * 80)
    
    num_vars = len(set(lit.name for clause in clauses for lit in clause))
    num_clauses = len(clauses)
    print(f"Problem size: {num_vars} variables, {num_clauses} clauses")
    
    # Display the formula
    formula_parts = []
    for clause in clauses:
        clause_str = " ∨ ".join(str(lit) for lit in clause)
        formula_parts.append(f"({clause_str})")
    formula = " ∧ ".join(formula_parts)
    print(f"Formula: {formula}")
    print()
    
    results = {}
    
    # 1. DPLL Solver (finds first solution only)
    print("--- 1. DPLL SOLVER (First solution) ---")
    try:
        dpll_solution, dpll_time = dpll_solve(clauses)
        results['dpll'] = {
            'solution': dpll_solution,
            'time': dpll_time,
            'solutions_count': 1 if dpll_solution else 0,
            'success': dpll_solution is not None
        }
        print(f"DPLL result: {'SAT' if dpll_solution else 'UNSAT'}")
        if dpll_solution:
            print(f"DPLL solution: {dpll_solution}")
        print(f"DPLL time: {dpll_time:.6f} seconds")
    except Exception as e:
        print(f"DPLL failed: {e}")
        results['dpll'] = {'success': False, 'time': float('inf')}
    
    print()
    
    # 2. Backtrack Solver (finds all solutions)
    print("--- 2. BACKTRACK SOLVER (All solutions) ---")
    try:
        backtrack_solutions, backtrack_time = find_all_solutions_backtrack(clauses)
        results['backtrack'] = {
            'solutions': backtrack_solutions,
            'time': backtrack_time,
            'solutions_count': len(backtrack_solutions),
            'success': len(backtrack_solutions) > 0
        }
        print(f"Backtrack result: {'SAT' if backtrack_solutions else 'UNSAT'}")
        print(f"Backtrack solutions found: {len(backtrack_solutions)}")
        if backtrack_solutions:
            print(f"First backtrack solution: {backtrack_solutions[0]}")
            if len(backtrack_solutions) > 1:
                print(f"All solutions: {backtrack_solutions}")
        print(f"Backtrack time: {backtrack_time:.6f} seconds")
    except Exception as e:
        print(f"Backtrack failed: {e}")
        results['backtrack'] = {'success': False, 'time': float('inf')}
    
    print()
    
    # 3. Quantum Solver (finds all solutions with probability)
    print("--- 3. QUANTUM SOLVER (Probabilistic all solutions) ---")
    try:
        quantum_solutions, quantum_time = find_all_quantum_solutions(clauses)
        results['quantum'] = {
            'solutions': quantum_solutions,
            'time': quantum_time,
            'solutions_count': len(quantum_solutions),
            'success': len(quantum_solutions) > 0
        }
        print(f"Quantum result: {'SAT' if quantum_solutions else 'UNSAT'}")
        print(f"Quantum solutions found: {len(quantum_solutions)}")
        if quantum_solutions:
            print(f"First quantum solution: {quantum_solutions[0]}")
            if len(quantum_solutions) > 3:
                print(f"Sample solutions: {quantum_solutions[:3]}...")
            else:
                print(f"All solutions: {quantum_solutions}")
        print(f"Quantum time: {quantum_time:.6f} seconds")
    except Exception as e:
        print(f"Quantum failed: {e}")
        results['quantum'] = {'success': False, 'time': float('inf')}
    
    print()
    
    # Speedup Analysis
    print("--- SPEEDUP ANALYSIS ---")
    
    if results['dpll']['success'] and results['backtrack']['success']:
        dpll_vs_backtrack = results['backtrack']['time'] / results['dpll']['time']
        print(f"Backtrack vs DPLL: {dpll_vs_backtrack:.2f}x {'(DPLL faster)' if dpll_vs_backtrack > 1 else '(Backtrack faster)'}")
    
    # KEY COMPARISON: Backtrack vs Quantum
    if results['backtrack']['success'] and results['quantum']['success']:
        backtrack_vs_quantum = results['backtrack']['time'] / results['quantum']['time']
        print(f"🎯 BACKTRACK vs QUANTUM: {backtrack_vs_quantum:.2f}x {'(Quantum faster)' if backtrack_vs_quantum > 1 else '(Backtrack faster)'}")
        
        if backtrack_vs_quantum > 1:
            print(f"   ✅ Quantum achieved {backtrack_vs_quantum:.2f}x speedup over Backtrack!")
        else:
            print(f"   ❌ Backtrack is {1/backtrack_vs_quantum:.2f}x faster than Quantum")
    
    if results['dpll']['success'] and results['quantum']['success']:
        dpll_vs_quantum = results['quantum']['time'] / results['dpll']['time']
        print(f"DPLL vs Quantum: {dpll_vs_quantum:.2f}x {'(DPLL faster)' if dpll_vs_quantum > 1 else '(Quantum faster)'}")
    
    # Solution completeness comparison
    print("\n--- SOLUTION COMPLETENESS ---")
    if results['backtrack']['success'] and results['quantum']['success']:
        backtrack_count = results['backtrack']['solutions_count']
        quantum_count = results['quantum']['solutions_count'] 
        completeness = (quantum_count / backtrack_count) * 100 if backtrack_count > 0 else 0
        print(f"Solution completeness: Quantum found {quantum_count}/{backtrack_count} solutions ({completeness:.1f}%)")
    
    print("=" * 80)
    return results

def run_test_suite():
    """Run a comprehensive test suite comparing all three solvers"""
    
    test_cases = [
        {
            "name": "Simple 3-var problem",
            "clauses": [
                [Variable("A"), Variable("B")],
                [-Variable("A"), Variable("C")],
                [Variable("B"), -Variable("C")]
            ]
        },
        {
            "name": "4-var constraint problem",
            "clauses": [
                [Variable("x1"), Variable("x2")],
                [-Variable("x1"), Variable("x3")],
                [Variable("x2"), -Variable("x3")],
                [-Variable("x2"), Variable("x4")]
            ]
        },
        {
            "name": "Small unsatisfiable problem",
            "clauses": [
                [Variable("p")],
                [-Variable("p")]
            ]
        }
    ]
    
    print("COMPREHENSIVE THREE-WAY SOLVER COMPARISON")
    print("Focus: Backtrack vs Quantum Speedup Analysis")
    print()
    
    speedup_results = []
    
    for test_case in test_cases:
        results = compare_all_three_solvers(test_case["clauses"], test_case["name"])
        
        # Track speedup results
        if results['backtrack']['success'] and results['quantum']['success']:
            speedup = results['backtrack']['time'] / results['quantum']['time']
            speedup_results.append({
                'test': test_case["name"],
                'speedup': speedup,
                'backtrack_time': results['backtrack']['time'],
                'quantum_time': results['quantum']['time']
            })
        
        print("\n" + "="*20 + " NEXT TEST " + "="*20 + "\n")
    
    # Summary of speedup results
    print("SPEEDUP SUMMARY (Backtrack vs Quantum)")
    print("=" * 50)
    
    for result in speedup_results:
        status = "🚀 QUANTUM WINS" if result['speedup'] > 1 else "🐌 Backtrack wins"
        print(f"{result['test']:25} | {result['speedup']:6.2f}x | {status}")
        print(f"  Times: Backtrack={result['backtrack_time']:.4f}s, Quantum={result['quantum_time']:.4f}s")
    
    if speedup_results:
        avg_speedup = sum(r['speedup'] for r in speedup_results) / len(speedup_results)
        print(f"\nAverage speedup: {avg_speedup:.2f}x")
        quantum_wins = sum(1 for r in speedup_results if r['speedup'] > 1)
        print(f"Quantum wins: {quantum_wins}/{len(speedup_results)} tests")

if __name__ == "__main__":
    run_test_suite()

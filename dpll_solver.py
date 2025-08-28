import time
from variable import Variable

def is_satisfied(clause, assignment):
    """Check if a clause is satisfied by the current assignment"""
    for lit in clause:
        if lit in assignment:
            return True
    return False

def dpll_first_solution(clauses, assignment):
    """DPLL algorithm that finds first solution only"""
    while True:
        # Remove satisfied clauses
        clauses = [c for c in clauses if not is_satisfied(c, assignment)]
        
        # Remove false literals from clauses
        def remove_false_literals(clause, assignment):
            return [lit for lit in clause if -lit not in assignment]
        
        clauses = [remove_false_literals(c, assignment) for c in clauses]

        # If no clauses left, SAT - found a solution
        if not clauses:
            return assignment
        # If empty clause exists, UNSAT
        if any(len(c) == 0 for c in clauses):
            return None
            
        # Unit propagation
        unit_clauses = [c[0] for c in clauses if len(c) == 1 and c[0] not in assignment and -c[0] not in assignment]
        filtered_unit_clauses = []
        for lit in unit_clauses:
            if -lit in unit_clauses:
                # If both literal and its negation are present, UNSAT
                return None
            else:
                filtered_unit_clauses.append(lit)
        if filtered_unit_clauses:
            assignment = assignment + filtered_unit_clauses
            continue  # Restart the loop with new assignments
        
        # Choose a literal (heuristic: first literal of first clause)
        for c in clauses:
            for lit in c:
                # Try assigning literal True
                result = dpll_first_solution(clauses[:], assignment + [lit])
                if result is not None:
                    return result
                # Try assigning literal False
                result = dpll_first_solution(clauses[:], assignment + [-lit])
                if result is not None:
                    return result
                return None

def find_all_solutions(clauses):
    """Find all possible solutions using backtracking (imported from backtrack_solver)"""
    from backtrack_solver import find_all_solutions_backtrack
    return find_all_solutions_backtrack(clauses)

def find_first_solution(clauses):
    """Find the first possible solution using DPLL with timing"""
    start_time = time.time()
    solution = dpll_first_solution(clauses, [])
    end_time = time.time()
    execution_time = end_time - start_time
    return solution, execution_time

def find_all_solutions_no_timing(clauses):
    """Find all possible solutions without timing (uses backtracking)"""
    from backtrack_solver import find_all_solutions_backtrack_no_timing
    return find_all_solutions_backtrack_no_timing(clauses)

def find_first_solution_no_timing(clauses):
    """Find first solution without timing (uses DPLL)"""
    return dpll_first_solution(clauses, [])

# Example usage (for testing the core DPLL algorithm)
if __name__ == "__main__":
    # Simple example
    A = Variable("A")
    B = Variable("B")
    C = Variable("C")
    
    # (A or B) and (-A or C) and (-B or -C)
    clauses = [
        [A, B],
        [-A, C],
        [-B, -C]
    ]
    
    # Test DPLL first solution
    solution, exec_time = find_first_solution(clauses)
    if solution is None:
        print("UNSAT")
    else:
        print("First SAT assignment:", solution)
        print(f"DPLL execution time: {exec_time:.6f} seconds")
    
    # Test backtracking all solutions
    print("\n" + "="*50)
    all_solutions, all_time = find_all_solutions(clauses)
    print(f"\nBacktracking found {len(all_solutions)} solution(s)")
    print(f"Backtracking execution time: {all_time:.6f} seconds")

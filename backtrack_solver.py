import time
from variable import Variable

def is_satisfied(clause, assignment):
    """Check if a clause is satisfied by the current assignment"""
    for lit in clause:
        if lit in assignment:
            return True
    return False

def is_falsified(clause, assignment):
    """Check if a clause is falsified (all literals are false) by the current assignment"""
    for lit in clause:
        if -lit not in assignment:
            return False
    return True

def evaluate_formula(clauses, assignment):
    """Evaluate if the entire formula is satisfied by the assignment"""
    for clause in clauses:
        if not is_satisfied(clause, assignment):
            return False
    return True

def get_all_variables(clauses):
    """Extract all unique variables from the clauses"""
    variables = set()
    for clause in clauses:
        for lit in clause:
            variables.add(lit.name)
    return sorted(list(variables))

def backtrack_all_solutions(clauses, variables, assignment, var_index, solutions):
    """Backtracking algorithm to find all solutions by trying all possible assignments"""
    
    if var_index == len(variables):
        if evaluate_formula(clauses, assignment):
            solutions.append(assignment[:])  # Make a copy
        return
    
    # Get the current variable to assign
    var_name = variables[var_index]
    var = Variable(var_name)
    
    # Try assigning the variable to True
    assignment.append(var)

    if not any(is_falsified(clause, assignment) for clause in clauses):
        backtrack_all_solutions(clauses, variables, assignment, var_index + 1, solutions)
    assignment.pop()  # Backtrack
    
    # Try assigning the variable to False
    assignment.append(-var)

    if not any(is_falsified(clause, assignment) for clause in clauses):
        backtrack_all_solutions(clauses, variables, assignment, var_index + 1, solutions)
    assignment.pop()  # Backtrack

def verify_solution(clauses, assignment):
    """Verify that a given assignment actually satisfies all clauses"""
    print(f"Verifying assignment: {assignment}")
    for i, clause in enumerate(clauses):
        satisfied = is_satisfied(clause, assignment)
        print(f"  Clause {i+1} {clause}: {'SAT' if satisfied else 'UNSAT'}")
        if not satisfied:
            return False
    return True

def find_all_solutions_backtrack(clauses):
    """Find all possible solutions using backtracking with verification and timing"""
    start_time = time.time()
    
    # Get all variables in the formula
    variables = get_all_variables(clauses)
    print(f"Variables found: {variables}")
    
    # Use backtracking to find all solutions
    solutions = []
    backtrack_all_solutions(clauses, variables, [], 0, solutions)
    
    # Verify each solution
    verified_solutions = []
    for solution in solutions:
        print(f"\n--- Verifying solution {len(verified_solutions) + 1} ---")
        if verify_solution(clauses, solution):
            verified_solutions.append(solution)
    
    end_time = time.time()
    execution_time = end_time - start_time
    return verified_solutions, execution_time

def find_all_solutions_backtrack_no_timing(clauses):
    """Find all possible solutions using backtracking without timing"""
    variables = get_all_variables(clauses)
    solutions = []
    backtrack_all_solutions(clauses, variables, [], 0, solutions)
    return solutions


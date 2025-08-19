from variable import Variable

def dpll_all_solutions(clauses, assignment, solutions):
    """Modified DPLL that finds all solutions"""
    while True:
        # Remove satisfied clauses
        def is_satisfied(clause, assignment):
            for lit in clause:
                if lit in assignment:
                    return True
            return False

        clauses = [c for c in clauses if not is_satisfied(c, assignment)]
        
        # Remove false literals from clauses
        def remove_false_literals(clause, assignment):
            return [lit for lit in clause if -lit not in assignment]
        
        clauses = [remove_false_literals(c, assignment) for c in clauses]
        print(clauses, "clauses")
        print(assignment, "assignment")
        # If no clauses left, SAT - found a solution
        if not clauses:
            solutions.append(assignment[:])  # Make a copy of the assignment
            return
        # If empty clause exists, UNSAT
        if any(len(c) == 0 for c in clauses):
            return
            
        # Unit propagation
        unit_clauses = [c[0] for c in clauses if len(c) == 1 and c[0] not in assignment and -c[0] not in assignment]
        filtered_unit_clauses = []
        for lit in unit_clauses:
            if -lit in unit_clauses:
                # If both literal and its negation are present, UNSAT
                return
            else:
                filtered_unit_clauses.append(lit)
        if filtered_unit_clauses:
            assignment = assignment + filtered_unit_clauses
            continue  # Restart the loop with new assignments
        
        # Choose a literal (heuristic: first literal of first clause)
        for c in clauses:
            for lit in c:
                # Try assigning literal True
                dpll_all_solutions(clauses[:], assignment + [lit], solutions)  # Make copy of clauses
                # Try assigning literal False
                dpll_all_solutions(clauses[:], assignment + [-lit], solutions)  # Make copy of clauses
                return  # Important: return after trying both branches

def dpll_first_solution(clauses, assignment):
    """Modified DPLL that finds first solution only"""
    while True:
        # Remove satisfied clauses
        def is_satisfied(clause, assignment):
            for lit in clause:
                if lit in assignment:
                    return True
            return False

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
            return
            
        # Unit propagation
        unit_clauses = [c[0] for c in clauses if len(c) == 1 and c[0] not in assignment and -c[0] not in assignment]
        filtered_unit_clauses = []
        for lit in unit_clauses:
            if -lit in unit_clauses:
                # If both literal and its negation are present, UNSAT
                return
            else:
                filtered_unit_clauses.append(lit)
        if filtered_unit_clauses:
            assignment = assignment + filtered_unit_clauses
            continue  # Restart the loop with new assignments
        
        # Choose a literal (heuristic: first literal of first clause)
        for c in clauses:
            for lit in c:
                # Try assigning literal True
                dpll_first_solution(clauses, assignment + [lit])
                # Try assigning literal False
                dpll_first_solution(clauses, assignment + [-lit])
                return

def find_all_solutions(clauses):
    """Find all possible solutions to the SAT problem"""
    solutions = []
    dpll_all_solutions(clauses, [], solutions)
    return solutions

def find_first_solution(clauses):
    """Find the first possible solution to the SAT problem"""
    return dpll_first_solution(clauses, [])

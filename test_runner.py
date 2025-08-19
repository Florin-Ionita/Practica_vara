import yaml
import sys
from variable import Variable
from dpll_solver import find_all_solutions, find_first_solution

# Define variables dictionary for dynamic variable creation
variables = {}

def get_variable(name):
    if name not in variables:
        variables[name] = Variable(name)
    return variables[name]

def parse_literal(literal_str):
    """Parse a literal string like 'A' or '-B' into a Variable object"""
    if literal_str.startswith('-'):
        var_name = literal_str[1:]
        return -get_variable(var_name)
    else:
        return get_variable(literal_str)

def parse_clauses_from_yaml(yaml_data):
    """Parse clauses from YAML data structure"""
    clauses = []
    for clause_data in yaml_data['clauses']:
        clause = []
        for literal_str in clause_data:
            clause.append(parse_literal(literal_str))
        clauses.append(clause)
    return clauses

def load_test_case(filename):
    """Load a test case from a YAML file"""
    with open(filename, 'r') as file:
        data = yaml.safe_load(file)
    return parse_clauses_from_yaml(data), data.get('expected', 'UNKNOWN'), data.get('description', '')

def run_test_case(filename):
    """Run a single test case and return results"""
    try:
        clauses, expected, description = load_test_case(filename)
        print(f"Running test: {description}")
        print(f"Expected: {expected}")
        
        # Find all solutions
        all_solutions = find_all_solutions(clauses)
        
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
        
        if expected != 'UNKNOWN':
            status = "PASS" if result == expected else "FAIL"
            print(f"Status: {status}")
        
        return result == expected if expected != 'UNKNOWN' else True
        
    except FileNotFoundError:
        print(f"Error: File {filename} not found")
        return False
    except Exception as e:
        print(f"Error loading YAML file: {e}")
        return False

def run_all_tests():
    """Run all test files in the current directory"""
    import os
    test_files = [f for f in os.listdir('.') if f.startswith('test_') and f.endswith('.yaml')]
    
    if not test_files:
        print("No test files found (looking for test_*.yaml)")
        return
    
    passed = 0
    total = len(test_files)
    
    for test_file in test_files:
        print(f"\n{'='*50}")
        print(f"Running {test_file}")
        print('='*50)
        if run_test_case(test_file):
            passed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} tests passed")
    print('='*50)

# Main execution
if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "all":
            run_all_tests()
        else:
            # Load test case from YAML file
            filename = sys.argv[1]
            run_test_case(filename)
    else:
        # Default test case if no file specified
        print("No YAML file specified. Using default test case.")
        print("Usage:")
        print("  python3 test_runner.py <test_file.yaml>  # Run single test")
        print("  python3 test_runner.py all               # Run all tests")
        
        # Default example - create variables explicitly
        A = get_variable("A")
        B = get_variable("B") 
        C = get_variable("C")
        D = get_variable("D")
        
        clauses = [
            [A, B],        # (A or B)
            [A, C],        # (A or C)
            [-B, D],       # (not B or D)
            [-C, D]        # (not C or D)
        ]

        # Find all solutions
        all_solutions = find_all_solutions(clauses)
        if not all_solutions:
            print("UNSAT - No solutions found")
        else:
            print(f"Found {len(all_solutions)} solution(s):")
            for i, sol in enumerate(all_solutions, 1):
                print(f"  Solution {i}: {sol}")

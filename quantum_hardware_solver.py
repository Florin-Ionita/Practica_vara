import os
import time
import matplotlib.pyplot as plt
from dotenv import load_dotenv

from qiskit.circuit.library import PhaseOracle
from qiskit_algorithms import AmplificationProblem, Grover
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

def solve_with_grover_on_hardware(filepath, plot=False):
    """
    Solves a SAT problem from a DIMACS CNF file using Grover's algorithm on real quantum hardware.

    Args:
        filepath (str): The path to the DIMACS CNF file.
        plot (bool): If True, a plot of the results will be displayed.

    Returns:
        tuple: A tuple containing:
            - solution (str or None): The bitstring of the most likely solution.
            - duration (float): The time taken for the quantum job to complete.
    """
    # --- 1. Setup Environment and Services ---
    load_dotenv()
    api_token = os.getenv("IBM_QUANTUM_TOKEN")
    if not api_token:
        raise ValueError("IBM_QUANTUM_TOKEN not found in .env file.")

    # It's good practice to load the service once, but for a standalone script, we do it here.
    # This might add overhead if called in a loop.
    service = QiskitRuntimeService(
        token=api_token,
        instance="PracticaVara",
        channel="ibm_cloud",
        region="us-east",
    )
    
    # Select a backend (e.g., the least busy one)
    backend = service.least_busy(simulator=False, operational=True)
    print(f"--- Using Quantum Backend: {backend.name} ---")
    
    sampler = Sampler(mode=backend)

    try:
        oracle = PhaseOracle.from_dimacs_file(filepath)
        problem = AmplificationProblem(oracle, is_good_state=oracle.evaluate_bitstring)
    except Exception as e:
        print(f"  Error creating oracle: {e}")
        return None, 0.0

    # Use a fixed number of iterations for static circuit construction
    power = 2 
    grover_op = Grover()
    circuit = grover_op.construct_circuit(problem, power=power, measurement=True)
    
    pm = generate_preset_pass_manager(optimization_level=3, backend=backend)
    isa_circuit = pm.run(circuit)
    
    print("  Submitting job to backend... (This may take a while)")
    start_time = time.time()
    job = sampler.run([isa_circuit])
    print(f"  > Job ID: {job.job_id()}")
    result = job.result()
    end_time = time.time()
    duration = end_time - start_time
    print(f"  Job finished in {duration:.4f} seconds.")

    pub_result = result[0]
    counts_data = pub_result.data
    bitarray = next(iter(counts_data.values()))
    counts = bitarray.get_counts()

    # Find the most frequent result
    solution = max(counts, key=counts.get) if counts else None

    if plot:
        bitstrings = list(counts.keys())
        counts_values = list(counts.values())
        fig, ax = plt.subplots()
        ax.bar(bitstrings, counts_values)
        ax.set_title("Grover Measures on Hardware")
        ax.set_xlabel("Bitstrings")
        ax.set_ylabel("Counts")
        plt.xticks(rotation=75)
        ax.grid(True, linestyle='--', which='major', color='grey', alpha=.25)
        plt.show()

    return solution, duration

if __name__ == '__main__':
    # Example of how to run this script directly
    # Make sure you have a 'tests/test_unit.cnf' file or change the path
    target_file = 'tests/test_unit.cnf'
    if os.path.exists(target_file):
        found_solution, time_taken = solve_with_grover_on_hardware(target_file, plot=True)
        if found_solution:
            print(f"\nMost likely solution found: {found_solution}")
            print(f"Total time: {time_taken:.4f}s")
    else:
        print(f"Test file not found: {target_file}")

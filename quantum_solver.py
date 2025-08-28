from math import pi, floor, sqrt
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.circuit.library import MCXGate
from itertools import product
import sys

# Optional: Aer simulator import
try:
    from qiskit_aer import Aer
except ImportError:
    Aer = None

# Optional: IBM Quantum import
try:
    from qiskit_ibm_runtime import QiskitRuntimeService
except ImportError:
    QiskitRuntimeService = None

def parse_dimacs(dimacs_str):
    clauses = []
    num_vars = None
    for line in dimacs_str.splitlines():
        line = line.strip()
        if not line or line.startswith('c'):
            continue
        if line.startswith('p'):
            parts = line.split()
            if len(parts) >= 3:
                num_vars = int(parts[2])
        else:
            parts = line.split()
            lits = [int(x) for x in parts if x != '0']
            if lits:
                clauses.append(lits)
    if num_vars is None:
        num_vars = 0
        for cl in clauses:
            for lit in cl:
                num_vars = max(num_vars, abs(lit))
    return num_vars, clauses

def build_oracle_from_cnf(num_vars, clauses, qc, q_inputs, q_clause_ancillas,
                          q_temp, q_out, q_mct_ancillas=None):
    def prep_literal_negations(literals):
        for li in literals:
            var_idx = abs(li) - 1
            if li > 0:
                qc.x(q_inputs[var_idx])
    def undo_literal_negations(literals):
        for li in literals:
            var_idx = abs(li) - 1
            if li > 0:
                qc.x(q_inputs[var_idx])
    for i, clause in enumerate(clauses):
        clause_anc = q_clause_ancillas[i]
        if len(clause) == 0:
            continue
        if len(clause) == 1:
            li = clause[0]
            v = q_inputs[abs(li)-1]
            if li > 0:
                qc.cx(v, clause_anc)
            else:
                qc.x(v)
                qc.cx(v, clause_anc)
                qc.x(v)
            continue
        prep_literal_negations(clause)
        controls = [q_inputs[abs(li)-1] for li in clause]
        if len(controls) == 1:
            qc.cx(controls[0], q_temp)
        elif len(controls) == 2:
            qc.ccx(controls[0], controls[1], q_temp)
        else:
            qc.append(MCXGate(len(controls)), controls + [q_temp])
        qc.x(q_temp)
        qc.cx(q_temp, clause_anc)
        qc.x(q_temp)
        if len(controls) == 1:
            qc.cx(controls[0], q_temp)
        elif len(controls) == 2:
            qc.ccx(controls[0], controls[1], q_temp)
        else:
            qc.append(MCXGate(len(controls)), controls + [q_temp])
        undo_literal_negations(clause)
    clause_controls = list(q_clause_ancillas)
    if len(clause_controls) == 0:
        qc.x(q_out)
    elif len(clause_controls) == 1:
        qc.cx(clause_controls[0], q_out)
    elif len(clause_controls) == 2:
        qc.ccx(clause_controls[0], clause_controls[1], q_out)
    else:
        if q_mct_ancillas and len(q_mct_ancillas) >= max(0, len(clause_controls)-2):
            qc.append(MCXGate(len(clause_controls)), clause_controls + [q_out])
    return

def clear_clause_ancillas(num_vars, clauses, qc, q_inputs, q_clause_ancillas,
                          q_temp, q_mct_ancillas=None):
    def prep_literal_negations(literals):
        for li in literals:
            var_idx = abs(li) - 1
            if li > 0:
                qc.x(q_inputs[var_idx])
    def undo_literal_negations(literals):
        for li in literals:
            var_idx = abs(li) - 1
            if li > 0:
                qc.x(q_inputs[var_idx])
    for i, clause in enumerate(clauses):
        clause_anc = q_clause_ancillas[i]
        if len(clause) == 0:
            continue
        if len(clause) == 1:
            li = clause[0]
            v = q_inputs[abs(li)-1]
            if li > 0:
                qc.cx(v, clause_anc)
            else:
                qc.x(v)
                qc.cx(v, clause_anc)
                qc.x(v)
            continue
        prep_literal_negations(clause)
        controls = [q_inputs[abs(li)-1] for li in clause]
        if len(controls) == 1:
            qc.cx(controls[0], q_temp)
        elif len(controls) == 2:
            qc.ccx(controls[0], controls[1], q_temp)
        else:
            qc.append(MCXGate(len(controls)), controls + [q_temp])
        qc.x(q_temp)
        qc.cx(q_temp, clause_anc)
        qc.x(q_temp)
        if len(controls) == 1:
            qc.cx(controls[0], q_temp)
        elif len(controls) == 2:
            qc.ccx(controls[0], controls[1], q_temp)
        else:
            qc.append(MCXGate(len(controls)), controls + [q_temp])
        undo_literal_negations(clause)

def build_grover_for_dimacs(dimacs_str, shots=2048):
    num_vars, clauses = parse_dimacs(dimacs_str)
    print("Parsed CNF: num_vars =", num_vars, ", num_clauses =", len(clauses))
    max_clause_len = max((len(c) for c in clauses), default=0)
    anc_for_mct = max(0, max(max_clause_len, len(clauses)) - 2)
    q_inputs = QuantumRegister(num_vars, name='x')
    q_clause_ancillas = QuantumRegister(len(clauses), name='cl') if len(clauses) > 0 else QuantumRegister(0, name='cl')
    q_temp = QuantumRegister(1, name='temp')
    q_out = QuantumRegister(1, name='out')
    q_mct_ancillas = QuantumRegister(anc_for_mct, name='anc') if anc_for_mct > 0 else QuantumRegister(0, name='anc')
    creg = ClassicalRegister(num_vars, name='c')
    qc = QuantumCircuit(q_inputs, q_clause_ancillas, q_temp, q_out, q_mct_ancillas, creg)
    for i in range(num_vars):
        qc.h(q_inputs[i])
    build_oracle_from_cnf(num_vars, clauses, qc, q_inputs, q_clause_ancillas, q_temp[0], q_out[0],
                          q_mct_ancillas if anc_for_mct > 0 else None)
    qc.z(q_out[0])
    clause_controls = list(q_clause_ancillas)
    if len(clause_controls) == 0:
        qc.x(q_out[0])
    elif len(clause_controls) == 1:
        qc.cx(clause_controls[0], q_out[0])
    elif len(clause_controls) == 2:
        qc.ccx(clause_controls[0], clause_controls[1], q_out[0])
    else:
        if anc_for_mct > 0:
            qc.append(MCXGate(len(clause_controls)), clause_controls + [q_out[0]])
    clear_clause_ancillas(num_vars, clauses, qc, q_inputs, q_clause_ancillas, q_temp[0],
                          q_mct_ancillas if anc_for_mct > 0 else None)
    return qc, q_inputs, creg

def run_grover_on_dimacs(dimacs_str, shots=2048, use_ibm=False):
    base_qc, q_inputs, creg = build_grover_for_dimacs(dimacs_str, shots=shots)
    num_inputs = len(q_inputs)
    num_vars, clauses = parse_dimacs(dimacs_str)
    max_clause_len = max((len(c) for c in clauses), default=0)
    anc_for_mct = max(0, max(max_clause_len, len(clauses)) - 2)
    q_inputs = QuantumRegister(num_vars, name='x')
    q_clause_ancillas = QuantumRegister(len(clauses), name='cl') if len(clauses) > 0 else QuantumRegister(0, name='cl')
    q_temp = QuantumRegister(1, name='temp')
    q_out = QuantumRegister(1, name='out')
    q_mct_ancillas = QuantumRegister(anc_for_mct, name='anc') if anc_for_mct > 0 else QuantumRegister(0, name='anc')
    creg = ClassicalRegister(num_vars, name='c')
    qc = QuantumCircuit(q_inputs, q_clause_ancillas, q_temp, q_out, q_mct_ancillas, creg)
    for i in range(num_vars):
        qc.h(q_inputs[i])
    def append_oracle(qc_local):
        build_oracle_from_cnf(num_vars, clauses, qc_local, q_inputs, q_clause_ancillas, q_temp[0], q_out[0],
                              q_mct_ancillas if anc_for_mct > 0 else None)
        qc_local.z(q_out[0])
        clause_controls = list(q_clause_ancillas)
        if len(clause_controls) == 0:
            qc_local.x(q_out[0])
        elif len(clause_controls) == 1:
            qc_local.cx(clause_controls[0], q_out[0])
        elif len(clause_controls) == 2:
            qc_local.ccx(clause_controls[0], clause_controls[1], q_out[0])
        else:
            qc_local.append(MCXGate(len(clause_controls)), clause_controls + [q_out[0]])
        clear_clause_ancillas(num_vars, clauses, qc_local, q_inputs, q_clause_ancillas, q_temp[0],
                              q_mct_ancillas if anc_for_mct > 0 else None)
    N = 2**num_vars
    R = max(1, floor((pi/4) * sqrt(N)))
    R = min(R, 10)
    print("Using Grover iterations R =", R)
    for _ in range(R):
        append_oracle(qc)
        for i in range(num_vars):
            qc.h(q_inputs[i])
            qc.x(q_inputs[i])
        qc.h(q_inputs[num_vars-1])
        if num_vars-1 == 0:
            qc.z(q_inputs[num_vars-1])
        elif num_vars-1 == 1:
            qc.ccx(q_inputs[0], q_inputs[1], q_inputs[num_vars-1])
        else:
            qc.append(MCXGate(num_vars-1), [q_inputs[i] for i in range(num_vars-1)] + [q_inputs[num_vars-1]])
        qc.h(q_inputs[num_vars-1])
        for i in range(num_vars):
            qc.x(q_inputs[i])
            qc.h(q_inputs[i])
    for i in range(num_vars):
        qc.measure(q_inputs[i], creg[i])
    if use_ibm:
        if QiskitRuntimeService is None:
            print("Qiskit IBM Runtime not installed.")
            return {}
        service = QiskitRuntimeService()
        backend = service.least_busy(operational=True, simulator=False)
        transpiled = transpile(qc, backend)
        job = backend.run(transpiled, shots=shots)
        result = job.result()
        counts = result.get_counts()
    else:
        if Aer is None:
            print("Qiskit Aer not installed.")
            return {}
        backend = Aer.get_backend('aer_simulator')
        transpiled = transpile(qc, backend)
        job = backend.run(transpiled, shots=shots)
        result = job.result()
        counts = result.get_counts()
    for key, value in counts.items():
        print(f"{key}: {value}")
    return counts

if __name__ == "__main__":
    # Example CNF: (a OR b) AND c AND d  with a=1, b=2, c=3, d=4
    dimacs = """
    p cnf 4 3
    1 2 0
    3 0
    4 0
    """
    use_ibm = False
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            dimacs = f.read()
    if len(sys.argv) > 2 and sys.argv[2].lower() == "ibm":
        use_ibm = True
    counts = run_grover_on_dimacs(dimacs, shots=2048, use_ibm=use_ibm)
    # Interpret counts: bits are in order x_{n-1}...x_0 by Qiskit's default for get_counts keys.

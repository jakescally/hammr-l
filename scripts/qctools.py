from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit import *

def build_BV(s):
    n = len(s)
    circuit = QuantumCircuit(n+1,n)
    circuit.x(n) # apply NOT on last qubit
    circuit.barrier()
    circuit.h(range(n+1))
    circuit.barrier()
    for index, num in enumerate(reversed(s)):
        if num == '1':
            circuit.cx(index, n)

    circuit.barrier()
    circuit.h(range(n+1))
    circuit.barrier()
    circuit.measure(range(n), range(n))
    return circuit

def hamming_dist(s1, s2):
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))
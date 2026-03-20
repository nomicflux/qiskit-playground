#!/usr/bin/env python3

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.transpiler import generate_preset_pass_manager
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_histogram
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

import matplotlib.pyplot as plt
import numpy as np

n = 3

service = QiskitRuntimeService()
backend = service.least_busy(simulator=False, operational=True, min_num_qubits=n)

pm = generate_preset_pass_manager(backend=backend, optimization_level=0)

a = QuantumRegister(3, "a")
m = QuantumRegister(2, "m")

code = QuantumCircuit(a, m)

code.ry(np.pi/3, a[0])

code.barrier()

code.cx(a[0], a[1])
code.cx(a[0], a[2])

state = Statevector.from_instruction(code)
state.draw('latex')

code.x(a[1])
code.barrier()

code.draw('mpl')
plt.show(block=True)

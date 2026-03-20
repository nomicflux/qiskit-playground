#!/usr/bin/env python3

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit.transpiler import generate_preset_pass_manager
from qiskit.visualization import plot_histogram, array_to_latex
from qiskit.circuit.library import UGate
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

from math import pi
import random
import matplotlib.pyplot as plt

m = 2
n = 7 * m

service = QiskitRuntimeService()
backend = service.least_busy(simulator=False, operational=True, min_num_qubits=n)

pm = generate_preset_pass_manager(backend=backend, optimization_level=2)

qubit = QuantumRegister(m, "Q")
alice = QuantumRegister(m, "A")
bob = QuantumRegister(m, "B")
node = QuantumRegister(m, "*")
a = ClassicalRegister(m, "a")
b = ClassicalRegister(m, "b")
result = ClassicalRegister(m, "result")

protocol = QuantumCircuit(qubit, alice, bob, node, a, b, result)

protocol.h(alice)
protocol.cx(alice, node)
protocol.cx(node, bob)
#protocol.h(node)
#protocol.ccx(alice, node, bob)
protocol.barrier()

protocol.cx(qubit, alice)
protocol.h(qubit)

protocol.x(alice[1])

protocol.measure(alice, a)
protocol.measure(qubit, b)
protocol.barrier()

for x in range(0,m):
    with protocol.if_test((a[x], 1)):
        protocol.x(bob[x])
    with protocol.if_test((b[x], 1)):
        protocol.z(bob[x])

protocol.barrier()
protocol.measure(bob, result)

#protocol.draw(output="mpl")
#plt.show(block=True)

# random_gate = UGate(
#     theta=random.random() * 2 * pi,
#     phi=random.random() * 2 * pi,
#     lam=random.random() * 2 * pi,
# )

# print(array_to_latex(random_gate.to_matrix()))

# test = QuantumCircuit(qubit, alice, bob, a, b)
# test.append(random_gate, qubit)
# test.barrier()
# test = test.compose(protocol)
# test.barrier()

# test.append(random_gate.inverse(), bob)
# test.add_register(result)
# test.measure(bob, result)
#test.draw(output="mpl")
#plt.show(block=True)

#result = AerSimulator().run(test).result()
#statistics = result.get_counts()
#plot_histogram(statistics)
#plt.show(block=True)

pm_qc = pm.run(protocol)
sampler = Sampler(mode=backend)
job = sampler.run([pm_qc])
result = job.result()
print(f"Job Result: {result}")
data = result[0].data
a_values = data['a'].get_counts()
b_values = data['b'].get_counts()
result_values = data['result'].get_counts()
print(f"Keys: {data.keys()}")
print(f"Values:\n{a_values}\n{b_values}\n{result_values}")
plot_histogram(result_values)
plt.show(block=True)

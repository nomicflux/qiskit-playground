from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler import generate_preset_pass_manager
from qiskit.primitives import StatevectorSampler
from qiskit.visualization import plot_histogram
from qiskit_ibm_runtime import QiskitRuntimeService, EstimatorOptions, EstimatorV2 as Estimator

#import os
#from dotenv import load_dotenv
import matplotlib.pyplot as plt
import time

#load_dotenv()
#api_key = os.getenv("IBM_QUANTUM_API_KEY")
#instance = os.getenv("IBM_QUANTUM_INSTANCE_CRN")

def get_qc_for_n_qubit_GHZ_state(n: int) -> QuantumCircuit:
    if n >= 2:
        qc = QuantumCircuit(n)
        qc.h(0)
        for i in range(n - 1):
            qc.cx(i, i+1)
    else:
        raise Exception("n is not a valid input")
    return qc

n = 100
qc = get_qc_for_n_qubit_GHZ_state(n)

service = QiskitRuntimeService()
backend = service.least_busy(simulator=False, operational=True, min_num_qubits=n)
pm = generate_preset_pass_manager(backend=backend, optimization_level=1)

operator_strings = [
    "Z" + "I" * i + "Z" + "I" * (n - 2 - i) for i in range(n-1)
]
for s in operator_strings:
    print(s)
print(len(operator_strings))
operators = [SparsePauliOp(operator) for operator in operator_strings]

isa_circuit = pm.run(qc)
isa_operators_list = [op.apply_layout(isa_circuit.layout) for op in operators]

options = EstimatorOptions()
options.resilience_level = 2
options.dynamical_decoupling.enable = True
options.dynamical_decoupling.sequence_type = "XY4"
estimator = Estimator(mode=backend, options=options)

job = estimator.run([(isa_circuit, isa_operators_list)])
print(f">>> Job Id: {job.job_id()}")

result = job.result()
print(f"\t>>> Initial Job Result: {result}")

data = list(range(1, len(operators) + 1))
pub_result = result[0]
values = pub_result.data.evs
values = [
    v/values[0] for v in values
]
errors = pub_result.data.stds
print(f"\t>>> Values: {values}, Errors: {errors}")

plt.plot(data, values, marker="o", label="100-qubit GHZ state")
plt.xlabel("Distance between qubits $i$")
plt.ylabel(r"$\langle Z_i Z_0 \rangle / \langle Z_1 Z_0 \rangle $")
plt.legend()
plt.show(block=True)

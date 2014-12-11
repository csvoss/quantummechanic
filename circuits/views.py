from django.shortcuts import render
from django.http import HttpResponse
from django.template.response import TemplateResponse

import json
import os
import base64
import traceback
import cPickle

from qutip import *
from IPython.display import Image

# Create your views here.
def main(request):

    n = 10

    gates = get_gate_pngs()

    circuit_init_data = init_state(n)
    circuit_init_png = image_data(restore_state(circuit_init_data))

    data = {
        "gates": gates,
        "circuit_init_png": circuit_init_png,
        "circuit_init_data": json.dumps(circuit_init_data).replace(" ", ""),
        "qubit_numbers": range(n)
    }
    return TemplateResponse(request, "index.html", data)

def get_gate_pngs():

    ## Note: Some of these are single-qubit, some double-qubit.
    ## Some take in special parameters.

    output = []

    ## Hadamard
    q = QubitCircuit(1)
    q.add_gate("SNOT")
    output.append((image_data(q), "SNOT"))

    ## CNOT
    q = QubitCircuit(2)
    q.add_gate("CNOT", targets=1, controls=0)
    output.append((image_data(q), "CNOT"))

    #Rotations
    q = QubitCircuit(1)
    q.add_gate("RX", 0, None, pi/2, r"\theta")
    output.append((image_data(q), "RX"))

    q = QubitCircuit(1)
    q.add_gate("RY", 0, None, pi/2, r"\theta")
    output.append((image_data(q), "RY"))

    q = QubitCircuit(1)
    q.add_gate("RZ", 0, None, pi/2, r"\theta")
    output.append((image_data(q), "RZ"))

    ## TODO !!! -- Requires targets AND control
    #q = QubitCircuit(2)
    #q.add_gate("CPHASE", pi/2, r"\theta")
    #output.append(image_data(q))

    ## SWAP
    q = QubitCircuit(2)
    q.add_gate("SWAP", targets=[0,1])
    output.append((image_data(q), "SWAP"))
        
    return output


def image_data(q):
    image_tag = "<img src=\"data:image/png;base64,%s\"/>"
    ## SIMPLE LOCKING SYSTEM
    with open("lock.txt", "w") as fi:
        base_64_data = base64.b64encode(q.png.data)
    ## RELEASE LOCK
    return image_tag % base_64_data


def refresh():
    os.remove("qcirc.pdf")
    os.remove("qcirc.png")
    os.remove("qcirc.tex")


def addgate(request):
    try:
        if request.method == 'GET':
            print request.GET
            state = json.loads(request.GET.get("state"))
            gateTuple = request.GET.getlist("new_gate[]")
            print gateTuple
            new_state = updated_state(state, gateTuple)
            qc = restore_state(new_state)
            return HttpResponse(json.dumps({
                "new_state": json.dumps(new_state),
                "new_image": image_data(qc),
            }))
        else:
            return HttpResponse("")
    except:
        print traceback.format_exc()
        print sys.exc_info()
        return HttpResponse(sys.exc_info())


## State data abstraction:
## list of tuples (gate, qubit1, qubit2, theta) [gateTuples]
## number of qubits [nQubits]

SINGLE_QUBIT_GATES = ["SNOT", "RX", "RY", "RZ"]
DOUBLE_QUBIT_GATES = ["SWAP"]
CONTROLLED_DOUBLE_QUBIT_GATES = ["CNOT"]
#REQUIRES_THETA = ["RX", "RY", "RZ"]

def extract_gate(gate, qubit1, qubit2, theta, nth):
    ## Create a function which applies the specified gate to a QC
    qubit1 = int(qubit1)
    qubit2 = int(qubit2)
    def retval(qc):
        if gate in SINGLE_QUBIT_GATES:
            qc.add_gate(gate, qubit1)
        elif gate in DOUBLE_QUBIT_GATES:
            qc.add_gate(gate, [qubit1, qubit2])
        elif gate in CONTROLLED_DOUBLE_QUBIT_GATES:
            qc.add_gate(gate, qubit1, qubit2)
        else:
            ## TODO Actual code
            qc.add_gate("CNOT", 0, 1)
    return retval

def restore_state(state):
    ## Return a QubitCircuit
    ## by applying the given state
    ## state :: State data abstraction
    qc = QubitCircuit(state["nQubits"])
    for gateTuple in state["gateTuples"]:
        extract_gate(*gateTuple)(qc)
    return qc

def updated_state(old_state, new_gate_tuple):
    ## Add a gate to the state
    ## return :: a State data abstraction
    retval = {
        "nQubits": old_state["nQubits"],
        "gateTuples": old_state["gateTuples"] + [new_gate_tuple]
    }
    return retval

def init_state(n=4):
    ## The default state to start with
    ## return :: a State data abstraction
    retval = {
        "nQubits": n,
        "gateTuples": [],
    }
    return retval



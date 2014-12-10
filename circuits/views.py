from django.shortcuts import render
from django.http import HttpResponse
from django.template.response import TemplateResponse

import json

from qutip import *
from IPython.display import Image

# Create your views here.
def main(request):
    
    qc = QubitCircuit(10)
    qc_svg = qc.svg

    gate_svgs = get_gate_svgs()

    circuit_init_svg = qc_svg._data
    circuit_init_data = json.dumps("")

    data = {
        "gate_svgs": gate_svgs,
        "circuit_init_svg": circuit_init_svg,
        "circuit_init_data": circuit_init_data,
    }
    return TemplateResponse(request, "index.html", data)


def get_gate_svgs():
    output = []

    ## Hadamard
    q0 = QubitCircuit(1)
    q0.add_gate("SNOT")
    output.append(q0.svg._data)

    ## CNOT
    q1 = QubitCircuit(2)
    q1.add_gate("CNOT", targets=1, controls=0)
    output.append(q1.svg._data)

    ## SWAP
    q2 = QubitCircuit(2)
    q2.add_gate("SWAP", targets=[0,1])
    output.append(q2.svg._data)

    return output

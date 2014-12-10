from django.shortcuts import render
from django.http import HttpResponse
from django.template.response import TemplateResponse

import json
import os
import base64

from qutip import *
from IPython.display import Image

# Create your views here.
def main(request):
    
    qc = QubitCircuit(10)

    gate_pngs = get_gate_pngs()

    circuit_init_svg = image_data(qc)
    circuit_init_data = json.dumps("")

    data = {
        "gate_pngs": gate_pngs,
        "circuit_init_png": circuit_init_svg,
        "circuit_init_data": circuit_init_data,
    }
    return TemplateResponse(request, "index.html", data)


def get_gate_pngs():

    ## Note: Some of these are single-qubit, some double-qubit.
    ## Some take in special parameters.

    output = []


    #RX
    q3 = QubitCircuit(1)
    q3.add_gate("RX", 0, None, pi/2, r"\theta")
    output.append(image_data(q3))

    ## Hadamard
    q0 = QubitCircuit(1)
    q0.add_gate("SNOT")
    output.append(image_data(q0))

    ## CNOT
    q1 = QubitCircuit(2)
    q1.add_gate("CNOT", targets=1, controls=0)
    output.append(image_data(q1))

    ## SWAP
    q2 = QubitCircuit(2)
    q2.add_gate("SWAP", targets=[0,1])
    output.append(image_data(q2))

    return output


def image_data(q):
    image_tag = "<img src=\"data:image/png;base64,%s\"/>"
    base_64_data = base64.b64encode(q.png.data)
    return image_tag % base_64_data


def refresh():
    os.remove("qcirc.pdf")
    os.remove("qcirc.png")
    os.remove("qcirc.tex")

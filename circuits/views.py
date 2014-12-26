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

MAX_QUBITS = 8
MIN_QUBITS = 2
DEFAULT_QUBITS = 4

def puzzle(request):
    n = 3
    circuit_init_data = init_state(n)
    qc = restore_state(circuit_init_data)
    circuit_init_png = image_data(qc)

    fredkin_data = init_state(n)
    fredkin_data = updated_state(fredkin_data, ("FREDKIN", 0, 1, 2, 0), 0)
    fredkin_qc = restore_state(fredkin_data)
    fredkin_png = image_data(fredkin_qc)

    data = {
        "toffoli": toffoli_png(),
        "circuit_init_png": circuit_init_png,
        "circuit_init_data": json.dumps(circuit_init_data).replace(" ", ""),
        "qubit_numbers": range(n),
        "matrix": matrix_data(qc),
        "matrix_target": matrix_data(fredkin_qc),
        "target_png": fredkin_png,
    }
    return TemplateResponse(request, "puzzle.html", data)

def index(request):
    return TemplateResponse(request, "index.html", {})

def sandbox_default(request):
    return sandbox(request, DEFAULT_QUBITS)

def sandbox(request, n):    
    try:
        n = int(n)
    except:
        n = DEFAULT_QUBITS
    if n < MIN_QUBITS:
        n = MIN_QUBITS
    if n > MAX_QUBITS:
        n = MAX_QUBITS

    gates = get_gate_pngs()

    circuit_init_data = init_state(n)
    qc = restore_state(circuit_init_data)
    circuit_init_png = image_data(qc)

    data = {
        "gates": gates,
        "circuit_init_png": circuit_init_png,
        "circuit_init_data": json.dumps(circuit_init_data).replace(" ", ""),
        "qubit_numbers": range(n),
        "matrix": matrix_data(qc),
    }
    return TemplateResponse(request, "sandbox.html", data)

ONE_QUBIT_GATES = ["SNOT", "SQRTNOT", "RX", "RY", "RZ", "PHASEGATE", "GLOBALPHASE"]
TWO_QUBIT_GATES = ["SWAP", "BERKELEY", "ISWAP", "SQRTISWAP", "CNOT", "CSIGN", "SWAPalpha"]
THREE_QUBIT_GATES = ["TOFFOLI", "FREDKIN"]

GATES = ["SNOT", "SWAP", "CNOT", "CSIGN", "TOFFOLI", "SQRTNOT", "ISWAP", "SQRTISWAP", "RX", "RY", "RZ", "PHASEGATE", "GLOBALPHASE", "BERKELEY", "SWAPalpha", "FREDKIN"]

def get_gate_pngs():

    ## Note: Some of these are single-qubit, some double-qubit.
    ## Some take in special parameters.

    output = []

    for gate in GATES:
        if gate in ONE_QUBIT_GATES:
            numqubits = 1
        elif gate in TWO_QUBIT_GATES:
            numqubits = 2
        elif gate in THREE_QUBIT_GATES:
            numqubits = 3
        else:
            raise StandardError()
        qc = QubitCircuit(numqubits)
        if gate in SINGLE_QUBIT_GATES:
            qc.add_gate(gate, 0)
        elif gate in DOUBLE_QUBIT_GATES:
            qc.add_gate(gate, [0, 1])
        elif gate in ONE_CONTROL_ONE_GATE:
            qc.add_gate(gate, 0, 1)
        elif gate in SINGLE_QUBIT_THETA_GATES:
            qc.add_gate(gate, 0, None, 0, "\\theta")
        elif gate in DOUBLE_QUBIT_THETA_GATES:
            qc.add_gate(gate, [1, 0], None, 0, "\\theta")
        elif gate in TWO_CONTROLS_ONE_GATE:
            qc.add_gate(gate, 2, [1, 0])
        elif gate in ONE_CONTROL_TWO_GATES:
            qc.add_gate(gate, [1, 2], 0)
        try:
            with open("images/" + gate + ".png", "r") as cached:
                output.append((cached.read(), gate))
        except:
            data = image_data(qc)
            output.append((data, gate))
            with open("images/" + gate + ".png", "w") as new_file:
                new_file.write(data)

    return output

def toffoli_png():
    gate = "TOFFOLI"
    qc = QubitCircuit(3)
    qc.add_gate(gate, 2, [1, 0])
    data = image_data(qc)
    return (data, gate)

def image_data(q):
    assert type(q) is QubitCircuit
    image_tag = "<img src=\"data:image/png;base64,%s\"/>"
    ## SIMPLE LOCKING SYSTEM
    with open("lock.txt", "w") as fi:
        base_64_data = base64.b64encode(q.png.data)
        refresh()
    ## RELEASE LOCK
    return image_tag % base_64_data


def refresh():
    os.remove("qcirc.pdf")
    os.remove("qcirc.png")
    os.remove("qcirc.tex")

def undo(request):
    try:
        if request.method == 'GET':
            state = json.loads(request.GET.get("state"))
            new_state = {
                "nQubits": state["nQubits"],
                "gateTuples": state["gateTuples"][:-1]
            }
            qc = restore_state(new_state)
            return HttpResponse(json.dumps({
                "new_state": json.dumps(new_state),
                "new_image": image_data(qc),
                "new_matrix": matrix_data(qc),
            }))
        else:
            return HttpResponse("")
    except StandardError as e:
        print traceback.format_exc()
        print sys.exc_info()
        return HttpResponse(json.dumps({
            "error": True,
            "error_message": str(e.message),
        }))

def clear(request):
    try:
        if request.method == 'GET':
            state = json.loads(request.GET.get("state"))
            new_state = {
                "nQubits": state["nQubits"],
                "gateTuples": [],
            }
            qc = restore_state(new_state)
            return HttpResponse(json.dumps({
                "new_state": json.dumps(new_state),
                "new_image": image_data(qc),
                "new_matrix": matrix_data(qc),
            }))
        else:
            return HttpResponse("")
    except StandardError as e:
        print traceback.format_exc()
        print sys.exc_info()
        return HttpResponse(json.dumps({
            "error": True,
            "error_message": str(e.message),
        }))

def addgate(request):
    try:
        if request.method == 'GET':
            state = json.loads(request.GET.get("state"))
            gateTuple = request.GET.getlist("new_gate[]")
            nth = request.GET.get("nth")
            new_state = updated_state(state, gateTuple, nth)
            qc = restore_state(new_state)
            return HttpResponse(json.dumps({
                "new_state": json.dumps(new_state),
                "new_image": image_data(qc),
                "new_matrix": matrix_data(qc),
                "error": False,
            }))
        else:
            raise StandardError("Method should be GET")
    except StandardError as e:
        print traceback.format_exc()
        print sys.exc_info()
        return HttpResponse(json.dumps({
            "error": True,
            "error_message": str(e.message),
        }))

def matrix_data(qc):
    assert type(qc) is QubitCircuit
    U_list0 = qc.propagators()
    U0 = gate_sequence_product(U_list0)
    if type(U0) is int:
        if int(U0) == 1:
            return "the identity matrix"
        return str(U0)
    else:
        return htmlify_matrix(U0.full())

def htmlify_matrix(ndarray):
    output = "<table>"
    for row in ndarray:
        output += "<tr>"
        for col in row:
            output += "<td>" + stringify_num(col) + "</td>"
        output += "</tr>"
    output += "</table>"
    return output

def stringify_num(num):
    if num.imag != 0:
        output = '{0.real:.3f} + {0.imag:.3f}j'.format(num)
    else:
        output = '{0.real:.3f}'.format(num)
    output = output.replace("0.000", "0")
    output = output.replace(" + 0j", "")
    output = output.replace("0 + ", "")
    output = output.replace(".000", "")
    output = output.replace("00 ", " ") ## trailing zeros...
    output = output.replace("00j", "j") 
    output = output.replace("0 ", " ") 
    output = output.replace("0j", "j") ## also only for trailing zeros
    output = output.replace("1j", "j")
    output = output.replace("j", "<i>i</i>")
    output = output.replace("+ -", "- ")
    output = output.replace("-", "&ndash;")
    assert type(output) is str
    return output

## State data abstraction:
## list of tuples (gate, qubit1, qubit2, theta) [gateTuples]
## number of qubits [nQubits]

SINGLE_QUBIT_GATES = ["SNOT", "SQRTNOT"]
DOUBLE_QUBIT_GATES = ["SWAP", "BERKELEY", "ISWAP", "SQRTISWAP"]
ONE_CONTROL_ONE_GATE = ["CNOT", "CSIGN"]
SINGLE_QUBIT_THETA_GATES = ["RX", "RY", "RZ", "PHASEGATE", "GLOBALPHASE"]
DOUBLE_QUBIT_THETA_GATES = ["SWAPalpha"]
TWO_CONTROLS_ONE_GATE = ["TOFFOLI"]
ONE_CONTROL_TWO_GATES = ["FREDKIN"]

def parse_theta(theta):
    if theta == "":
        theta = 0
    try:
        theta = float(theta) * pi / 180
    except:
        raise StandardError("Invalid theta -- must be a number (in degrees)")
    return theta

def string_theta(theta):
    if theta == "":
        theta = 0
    try:
        theta = float(theta)
        if theta == int(theta):
            theta = str(int(theta)) + "^{\circ}"
        else:
            theta = str(theta) + "^{\circ}"
    except:
        raise StandardError("Invalid theta -- must be a number (in degrees)")
    return theta

def extract_gate(n, gate, qubit1, qubit2, qubit3, theta):
    ## Create a function which applies the specified gate to a QC
    qubit1 = n - int(qubit1) - 1
    qubit2 = n - int(qubit2) - 1
    qubit3 = n - int(qubit3) - 1

    def retval(qc):
        if gate in SINGLE_QUBIT_GATES:
            qc.add_gate(gate, qubit1)
        elif gate in DOUBLE_QUBIT_GATES:
            if qubit1 != qubit2:
                qc.add_gate(gate, [qubit1, qubit2])
            else:
                raise StandardError("Qubit 1 and 2 must be different")
        elif gate in ONE_CONTROL_ONE_GATE:
            if qubit1 != qubit2:
                qc.add_gate(gate, qubit2, qubit1)
            else:
                raise StandardError("Qubit 1 and 2 must be different")
        elif gate in SINGLE_QUBIT_THETA_GATES:
            qc.add_gate(gate, qubit1, None, parse_theta(theta), string_theta(theta))
        elif gate in DOUBLE_QUBIT_THETA_GATES:
            if qubit1 != qubit2:
                qc.add_gate(gate, [qubit1, qubit2], None, parse_theta(theta), string_theta(theta))
            else:
                raise StandardError("Qubit 1 and 2 must be different")
        elif gate in TWO_CONTROLS_ONE_GATE:
            if qubit1 != qubit2 and qubit2 != qubit3 and qubit1 != qubit3:
                qc.add_gate(gate, qubit1, [qubit2, qubit3])
            else:
                raise StandardError("Qubits 1, 2, and 3 must be different")
        elif gate in ONE_CONTROL_TWO_GATES:
            if qubit1 != qubit2 and qubit2 != qubit3 and qubit1 != qubit3:
                if abs(qubit1 - qubit3) > abs(qubit2 - qubit3):
                    qc.add_gate(gate, [qubit2, qubit1], qubit3)
                else:
                    qc.add_gate(gate, [qubit1, qubit2], qubit3)                    
            else:
                raise StandardError("Qubits 1, 2, and 3 must be different")
        elif gate in TWO_CONTROLS_ONE_GATE:
            if qubit1 != qubit2 and qubit2 != qubit3 and qubit1 != qubit3:
                qc.add_gate(gate, qubit1, [qubit2, qubit3])
            else:
                raise StandardError("Qubits 1, 2, and 3 must be different")
        else:
            raise StandardError(gate)
    return retval

def restore_state(state):
    ## Return a QubitCircuit
    ## by applying the given state
    ## state :: State data abstraction
    n = state["nQubits"]
    qc = QubitCircuit(n)
    for gateTuple in state["gateTuples"]:
        print gateTuple
        extract_gate(n, *gateTuple)(qc)
    return qc

def updated_state(old_state, new_gate_tuple, nth):
    ## Add a gate to the state
    ## return :: a State data abstraction

    try:
        nth = int(nth)
    except:
        nth = len(old_state["gateTuples"])

    if nth < 0:
        nth = 0
    
    if nth > len(old_state["gateTuples"]):
        nth = len(old_state["gateTuples"])
        
    new_gate_tuples = old_state["gateTuples"]
    new_gate_tuples.insert(nth, new_gate_tuple)

    retval = {
        "nQubits": old_state["nQubits"],
        "gateTuples": new_gate_tuples
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



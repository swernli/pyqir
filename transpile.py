from llvmlite import binding as llvm
import re
import json
import sys

# Read the file contents and parse into an IR module
with open('./Development.ll') as f:
    s = f.read()
module = llvm.parse_assembly(s)

# Note that if the target file is bitcode instead of symbolic IR, use buffer.read and parse_bitcode instead.
# with open('./Development.bc') as f:
#     s = f.buffer.read()
# module = llvm.parse_bitcode(s)

module.verify()


# Use an incrementing count for unamed values to correlate them in the IR.
def resolve_temp_names(func):
    name = 0
    for b in func.blocks:
        for i in b.instructions:
            if i.name == "" and str(i.type) != "void":
                i.name = f"temp{name}"
                name += 1


def make_goto_block(func, origin_label, dest_label):
    # Search for phi nodes that match this label
    goto_block = {'Jump': dest_label, 'Assignments': []}
    for b in func.blocks:
        if b.name == dest_label:
            for i in b.instructions:
                if i.opcode == "phi" and str(i).find(origin_label) != -1:
                    regex = r".*\[ %*(.*), %" + origin_label + r" \]"
                    goto_block['Assignments'] += [{'Lhs': i.name,
                                                   'Rhs': re.match(regex, str(i)).group(1)}]
    return goto_block


def is_quantum_procedure(func):
    return any(map((lambda a: re.match(r".*QuantumProcedure.*", str(a)) != None), func.attributes))


def is_classical_procedure(func):
    return any(map((lambda a: re.match(r".*ClassicalProcedure.*", str(a)) != None), func.attributes))


program = {}
qubit_id = 0
qubit_map = {}

# Find the target function.
# TODO: Replace this with dynamic selection based on function attributes.
entryPoint = module.get_function(
    "Microsoft__Quantum__Qir__Emission__EstimatePhaseByRandomWalk__body")
resolve_temp_names(entryPoint)
funclist = []
program['EntryPoint'] = {}
program['EntryPoint']['Name'] = entryPoint.name
program['EntryPoint']['Args'] = list(map(
    (lambda arg: {'Name': arg.name, 'Type': str(arg.type)}), entryPoint.arguments))
instrs = []
comparison_map = {}
for b in entryPoint.blocks:
    instrs += [{'Type': 'label', 'Value': b.name}]
    for i in b.instructions:
        operands = list(i.operands)
        if i.opcode == "call":
            if operands[-1].name == "__quantum__rt__qubit_allocate":
                # Store the mapping from qubit name to module id.
                qubit_map[i.name] = qubit_id
                instrs += [{'Type': 'qubit_alloc',
                            'Id': qubit_id, 'Name': i.name}]
                qubit_id += 1
            elif not operands[-1].name.startswith("__quantum__rt__"):
                call = {'Type': 'call', 'ProcName': operands[-1].name}
                # Save this function name to the list of functions to generate later.
                funclist += [operands[-1].name]
                if i.name != "" and i.type != "void":
                    call['ResultVar'] = i.name
                qubit_args = []
                classical_args = []
                for o in operands[0:len(operands)-1]:
                    if str(o.type) == "%Qubit*":
                        qubit_args += [qubit_map[o.name]]
                    else:
                        classical_args += [o.name]
                call['QubitArgs'] = qubit_args
                call['ClassicalArgs'] = classical_args
                instrs += [call]
        elif i.opcode == "br":
            branch = {'Type': 'branch',
                      'Condition': comparison_map[operands[0].name]}
            branch['TrueBranch'] = make_goto_block(
                entryPoint, b.name, operands[2].name)
            branch['FalseBranch'] = make_goto_block(
                entryPoint, b.name, operands[1].name)
            instrs += [branch]
        elif i.opcode == "icmp":
            comparison_args = list(
                map((lambda o: o.name if o.name != "" else str(o).split(' ')[1]), operands))
            comparison_map[i.name] = {'Comparison': str(i).split(
                ' ')[5], 'Lhs': comparison_args[0], 'Rhs': comparison_args[1]}
        elif i.opcode == "ret":
            instrs += [{'Type': 'return', 'Value': operands[0].name}]
        elif i.opcode == "add":
            add_args = list(
                map((lambda o: o.name if o.name != "" else str(o).split(' ')[1]), operands))
            instrs += [{'Type': 'add', 'ResultVar': i.name,
                        'Lhs': add_args[0], 'Rhs': add_args[1]}]
program['EntryPoint']['Instructions'] = instrs


program['QuantumProcedures'] = []
program['ClassicalProcedures'] = []
while len(funclist) > 0:
    func = module.get_function(funclist.pop(0))
    resolve_temp_names(func)

    proc = {'Name': func.name, 'Instructions': []}
    # Handle procedure arguments.
    qubit_args = []
    classical_args = []
    for a in func.arguments:
        if str(a.type) == "%Qubit*":
            qubit_args += [a.name]
        else:
            classical_args += [a.name]
    proc['QubitArgs'] = qubit_args
    proc['ClassicalArgs'] = classical_args
    if is_quantum_procedure(func):
        for b in func.blocks:
            for i in b.instructions:
                operands = list(i.operands)
                if i.opcode == 'call':
                    # Handle quantum intrinsic functions.
                    if operands[-1].name.startswith("__quantum__qis__"):
                        gate = re.match(
                            r'.*__quantum__qis__(\w+)__body.*', str(i)).group(1)
                        target_pos = 0
                        control = ""
                        args = []
                        result = ""
                        if gate == "m":
                            gate = "measure"
                            result = i.name
                        if gate == "rz":
                            target_pos = 1
                            args = [operands[0].name]
                        if gate == "crz":
                            target_pos = 2
                            control = operands[1].name
                            args = [operands[0].name]
                        proc['Instructions'] += [
                            {'Gate': gate, 'Target': operands[target_pos].name, 'Control': control, 'Args': args, 'ResultVar': result}]
                elif i.opcode == 'ret' and len(operands) > 0:
                    proc['Instructions'] += [{'Gate': 'return', 'Value': operands[0].name}]
        program['QuantumProcedures'] += [proc]
    elif is_classical_procedure(func):
        for b in func.blocks:
            for i in b.instructions:
                operands = list(i.operands)
                if i.opcode == "fadd" or i.opcode == "fsub" or i.opcode == "fmul" or i.opcode == "fdiv":
                    args = list(map((lambda o: o.name if o.name != "" else str(
                        o).split(' ')[1]), operands))
                    proc['Instructions'] += [{'Type': i.opcode,
                                              'ResultVar': i.name, 'Lhs': args[0], 'Rhs': args[1]}]
                elif i.opcode == "fneg":
                    proc['Instructions'] += [{'Type': i.opcode, 'ResultVar': i.name,
                                              'Value': operands[0].name if operands[0].name != "" else str(operands[0]).split(' ')[1]}]
                elif i.opcode == "call":
                    if operands[-1].name.startswith("__quantum__rt__"):
                        call = {'Type': 'call', 'ProcName': operands[-1].name}
                        if i.name != "" and i.type != "void":
                            call['ResultVar'] = i.name
                        classical_args = []
                        for o in operands[0:len(operands)-1]:
                            classical_args += [o.name]
                        call['QubitArgs'] = []
                        call['ClassicalArgs'] = classical_args
                        proc['Instructions'] += [call]
                elif i.opcode == "select":
                    condition = {'Comparison': 'eq',
                                 'Lhs': operands[0].name, 'Rhs': "1"}
                    proc['Instructions'] += [{'Type': 'select', 'Condition': condition,
                                              'TrueBranch': {'Lhs': i.name, 'Rhs': operands[1].name if operands[1].name != "" else str(operands[1]).split(' ')[1]},
                                              'FalseBranch': {'Lhs': i.name, 'Rhs': operands[2].name if operands[2].name != "" else str(operands[1]).split(' ')[1]}}]
                elif i.opcode == "ret":
                    proc['Instructions'] += [{'Type': 'return', 'Value': operands[0].name}]
        program['ClassicalProcedures'] += [proc]


# Convert an IR comparison into a comparison symbol.
def comparison(comp):
    return {
        'eq': '==',
        'ne': '!=',
        'ugt': '>',
        'uge': '>=',
        'ult': '<',
        'ule': '<=',
        'sgt': '>',
        'sge': '>=',
        'slt': '<',
        'sle': '<='
    }[comp]


def assignment(a):
    return f"{a['Lhs']} = {a['Rhs']}"


def psuedo_code(program):
    ep = program['EntryPoint']
    print("main(", end="")
    print(
        ", ".join(map((lambda a: f"{a['Type']} {a['Name']}"), ep['Args'])), end="):\n")
    for instr in ep['Instructions']:
        t = instr['Type']
        if t == 'label':
            print(f"  label {instr['Value']}")
        elif t == 'qubit_alloc':
            print(f"  # qubit {instr['Id']} is '{instr['Name']}'")
        elif t == 'call':
            if instr.get('ResultVar') != None:
                print(f"  {instr['ResultVar']} =", end="")
            print(f"  {instr['ProcName']}(", end="")
            if len(instr['QubitArgs']) > 0:
                print(f"[{', '.join(map((lambda a: str(a)), instr['QubitArgs']))}]", end=(
                    ", " if len(instr['ClassicalArgs']) > 0 else ""))
            print(', '.join(instr['ClassicalArgs']), end=")\n")
        elif t == 'return':
            print(f"  return {instr['Value']}")
        elif t == 'add':
            print(f"  {instr['ResultVar']} = {instr['Lhs']} + {instr['Rhs']}")
        elif t == 'branch':
            cond = instr['Condition']
            print(
                f"  if {cond['Lhs']} {comparison(cond['Comparison'])} {cond['Rhs']}:")
            for a in instr['TrueBranch']['Assignments']:
                print(f"    {assignment(a)}")
            print(f"    jump {instr['TrueBranch']['Jump']}")
            print(f"  else:")
            for a in instr['FalseBranch']['Assignments']:
                print(f"    {assignment(a)}")
            print(f"    jump {instr['FalseBranch']['Jump']}")

    for proc in program['QuantumProcedures']:
        print(f"\n{proc['Name']}(", end="")
        if len(proc['QubitArgs']) > 0:
            print(f"[{', '.join(map((lambda a: str(a)), proc['QubitArgs']))}]", end=(
                ", " if len(proc['ClassicalArgs']) > 0 else ""))
        print(', '.join(proc['ClassicalArgs']), end="):\n")
        for instr in proc['Instructions']:
            if instr['Gate'] == 'return':
                print(f"  return {instr['Value']}")
            else:
                result = ""
                if instr['ResultVar'] != "":
                    result = f"{instr['ResultVar']} = "
                print(
                    f"  {result}{instr['Gate']}(target = '{instr['Target']}', control = '{instr['Control']}', args = [{', '.join(instr['Args'])}])")

    for proc in program['ClassicalProcedures']:
        print(f"\n{proc['Name']}(", end="")
        print(', '.join(proc['ClassicalArgs']), end="):\n")
        for instr in proc['Instructions']:
            t = instr['Type']
            if t == 'fadd':
                print(f"  {instr['ResultVar']} = {instr['Lhs']} + {instr['Rhs']}")
            elif t == 'fsub':
                print(f"  {instr['ResultVar']} = {instr['Lhs']} - {instr['Rhs']}")
            elif t == 'fmul':
                print(f"  {instr['ResultVar']} = {instr['Lhs']} * {instr['Rhs']}")
            elif t == 'fdiv':
                print(f"  {instr['ResultVar']} = {instr['Lhs']} / {instr['Rhs']}")
            elif t == 'fneg':
                print(f"  {instr['ResultVar']} = -({instr['Value']})")
            elif t == 'return':
                print(f"  return {instr['Value']}")
            elif t == 'select':
                cond = instr['Condition']
                print(f"  if {cond['Lhs']} {comparison(cond['Comparison'])} {cond['Rhs']}:")
                print(f"    {assignment(instr['TrueBranch'])}")
                print(f"  else:")
                print(f"    {assignment(instr['FalseBranch'])}")
            elif t == 'call':
                if instr.get('ResultVar') != None:
                    print(f"  {instr['ResultVar']} =", end="")
                print(f"  {instr['ProcName']}(", end="")
                print(', '.join(instr['ClassicalArgs']), end=")\n")



if len(sys.argv) == 1 or sys.argv[1] == "json":
    print(json.dumps(program, indent=2))
elif sys.argv[1] == "pseudo":
    psuedo_code(program)

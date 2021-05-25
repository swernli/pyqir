# pyqir
Sample for Python parsing of QIR

## Dependencies
Uses [llvmlite](https://github.com/numba/llvmlite) for accessing LLVM parsing capabilities in Python.
The [Quantum Intermediate Representation (QIR)](https://github.com/microsoft/qsharp-language/tree/main/Specifications/QIR) is a convention for 
representing quantum programs in LLVM IR.

## Building and Running
Following the install steps for Conda on [llvmlite](https://github.com/numba/llvmlite), use your local conda
python environment to run the transpile script:

```
> python .\transpile.py
```

By default the script will produce a simple JSON representation of the transpiled program. 
Alternatively, you can request a psuedo-code print out of the transpilation by passing "pseudo" as an
argument:

```
> python .\transpile.py pseudo
```

The repo includes checked-in examples of JSON and pseudo-code output from the current IR file for ease
of comparison on how changes to the code affect output.
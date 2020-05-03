# nanopores
Simulation of Nanopores based on FEniCS FEM package. Original code and [paper](https://doi.org/10.1016/j.jcp.2017.02.072) and [2nd paper](https://doi.org/10.1088/1361-6528/ab513e) by Gregor Mitscha-Baude.

## Getting Started

### Install dependencies

```console
$ conda install -c conda-forge pathos gmsh
```

### Set paths
```console
$ export PYTHONPATH="$PYTHONPATH:$HOME/git-repo/cfd/fenics/nanopores"
```

### Run scripts
from repository root directory
```console
$ python ./scripts/test2D.py
```


## Scripts
### Basic tests
* dolfin_test.py: provide simple dolfin classes for code inspection
* simplegeo.py : example for how to use Geometry class with module 

### Test scripts
* analytical_test_case.py : analytical test problem to validate 2D solver

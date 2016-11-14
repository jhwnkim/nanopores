# (c) 2016 Gregor Mitscha-Baude
import diffusion
import nanopores.tools.solvers as solvers
import nanopores.models.pughpore as pugh
import numpy as np
from matplotlib import pyplot as plt
from itertools import product
#default = diffusion.default

def tolist(array):
    return [list(a) for a in array]
    
params = dict(
    dim = 3,
    h = 1.,
    Nmax = 1e5,
    rMolecule = 0.152, # radius of K+
    lcMolecule = 0.1,
)

@solvers.cache_forcefield("pugh_diff3D_test", {})
def calculate_diffusivity(X, **params):
    x0 = X[0]
    setup = pugh.Setup(x0=x0, **params)
    D = diffusion.diffusivity_tensor(setup)
    return dict(D=[tolist(D)])

l0 = pugh.pughpore.params["l3"]
r = params["rMolecule"]
eps = 1e-2
R = l0/2. - r - eps

X = [[t, 0., 0.] for t in np.linspace(0, R, 10)]
data = calculate_diffusivity(X, nproc=1, **params)

def _sorted(data, key):
    I = sorted(range(len(key)), key=lambda k: key[k])
    return {k: [data[k][i] for i in I] for k in data}, [key[i] for i in I]

x = [z[0] for z in data["x"]]
data, x = _sorted(data, x)
dstr = {0:"x", 1:"y", 2:"z"}
for i, j in product(range(3), range(3)):
    Dxx = [D[i][j] for D in data["D"]]
    style = "s-" if i==j else "--"
    plt.plot(x, Dxx, style, label=r"$D_{%s%s}$" % (dstr[i], dstr[j]))
plt.legend()
plt.show()
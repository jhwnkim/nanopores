import dolfin
import nanopores as nano
import nanopores.geometries.pughpore as pughpore
from nanopores.geometries.curved import Sphere
#from nanopores.models.mysolve import pbpnps
import nanopores.physics.simplepnps as simplepnps

geop = nano.Params(
    R = 35.,
    H = 70.,
)
physp = nano.Params(
    Membraneqs = 0.0,
    Qmol = -nano.qq,
    bulkcon = 300.,
    dnaqsdamp = .5,
    bV = -0.1,
)
solverp = nano.Params(
    h = 2.,
    frac = 0.2,
    Nmax = 3e4,  
    imax = 30,
    tol = 1e-3,
)

# setup geometry and physics
geo = pughpore.get_geo(solverp.h, **geop)
nano.plot_sliced(geo)
dolfin.interactive()
molec = Sphere(R=geo.params["rMolecule"], center=geo.params["x0"])
geo.curved = dict(moleculeb = molec.snap)
phys = nano.Physics("pore", geo, **physp)
print phys.surfcharge
print phys.volcharge

pnps = simplepnps.PNPSFixedPointbV(geo, phys, ipicard=solverp.imax,
           tolnewton=solverp.tol, verbose=True, iterative=True)
print "Number of cells:", geo.mesh.num_cells()
print "DOFs:", pnps.dofs()

# solve PNPS
for i in pnps.fixedpoint():
    #dolfin.plot(pnps.functions["poisson"], key="vfv")
    #dolfin.plot(pnps.functions["stokes"].sub(0), key="ufv")
    v = pnps.functions["poisson"]
    print "v0 =", v([0., 0., -25.])

# visualize
R, H = float(geo.params["R"]), float(geo.params["H"])
print R, H
mesh2D = nano.RectangleMesh([0,-H], [20.,H], 100, 100)

v, cp, cm, u, p = pnps.solutions()

nano.plot_cross(v, mesh2D, title="potential")
nano.plot_cross(cm, mesh2D, title="cm")
nano.plot_cross(cp, mesh2D, title="cp")
nano.plot_cross(p, mesh2D, title="p")
nano.plot_cross_vector(u, mesh2D, title="u")
dolfin.interactive()
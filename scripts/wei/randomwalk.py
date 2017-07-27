# (c) 2017 Gregor Mitscha-Baude
"random walk of many particles in cylindrical pore"
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from matplotlib import collections
import matplotlib.patches as mpatches

import dolfin
import nanopores
from nanopores.tools import fields
from nanopores.geometries.allpores import get_pore
from nanopores.tools.polygons import Polygon, Ball
fields.set_dir_dropbox()
dolfin.parameters["allow_extrapolation"] = False
params = nanopores.user_params(
    # general params
    geoname = "wei",
    dim = 2,
    rMolecule = 6.,
    Qmol = -1.,
    bV = -0.5,
    # random walk params
    N = 10, # number of (simultaneous) random walks
    dt = 1.,
    walldist = 2., # in multiples of radius, should be >= 1
    margtop = 20.,
    margbot = 10.,
    cylplot = False, # True for plot in r-z domain
)

# domains are places where molecule can bind and/or be reflected after collision
domain_params = dict(
    cyl = False, # determines whether rz or xyz coordinates are passed to .inside
    walldist = 1.5, # multiple of radius that determines what counts as collision

    exclusion = True,
    minsize = 0.01, # accuracy when performing reflection

    binding = False,
    eps = 1., # margin in addition to walldist, determines re-attempting
    p = 0.1, # binding probability for one attempt
    t = 1e6, # mean of exponentially distributed binding duration
)

class Domain(object):

    def __init__(self, domain, **params):
        self.domain = domain
        self.__dict__.update(domain_params)
        self.__dict__.update(params)
        if isinstance(domain, Polygon):
            self.cyl = True

    def collide(self, rw):
        "compute collisions and consequences with RandomWalk instance"
        radius = rw.params.rMolecule * self.walldist

        # determine collisions and then operate only on collided particles
        X = rw.rz if self.cyl else rw.x[rw.alive]
        collided = self.domain.inside(X, radius=radius)

        # "reflect" particles by shortening last step
        if self.exclusion:
            X0, X1 = rw.xold[rw.alive], rw.x[rw.alive]
            for i in np.nonzero(collided)[0]:
                x = self.binary_search_inside(X0[i], X1[i], radius)
                rw.update_one(i, x)

        # attempt binding for particles that can bind
        if self.binding:
            can_bind = rw.can_bind[rw.alive]
            attempt = collided & can_bind
            # bind with probability p
            bind = np.random.rand(np.sum(attempt)) <= self.p
            # draw exponentially distributed binding time
            duration = np.random.exponential(self.t, np.sum(bind))
            # update can_bind and bind_times of random walk
            iattempt = rw.i[rw.alive][attempt]
            ibind = iattempt[bind]
            rw.can_bind[iattempt] = False
            rw.bind_times[ibind] += duration
            # some statistics
            rw.attempts[rw.i[rw.alive][attempt]] += 1
            rw.bindings[rw.i[rw.alive][attempt][bind]] += 1

            # unbind particles that can not bind and are out of nobind zone
            X_can_not_bind = X[~can_bind]
            rnobind = radius + self.eps
            unbind = ~self.domain.inside(X_can_not_bind, radius=rnobind)
            iunbind = rw.i[rw.alive][~can_bind][unbind]
            rw.can_bind[iunbind] = True

    def binary_search_inside(self, x0, x1, radius):
        if self.domain.inside_single(x0, radius=radius):
            print "ERROR: x0 is in domain despite having been excluded before."
            print "x0", x0, "x1", x1
            raise Exception
        if np.sum((x0 - x1)**2) < self.minsize**2:
            return x0
        x05 = .5*(x0 + x1)
        if self.domain.inside_single(x05, radius=radius):
            x1 = x05
        else:
            x0 = x05
        return self.binary_search_inside(x0, x1, radius)

# external forces
def load_externals(**params):
    F, = fields.get_functions("wei_force_ps", "F", **params)
    D, = fields.get_functions("wei_D_2D", "D", **params)
    V = D.function_space()
    divD = dolfin.project(dolfin.as_vector([
               dolfin.grad(D[0])[0], dolfin.grad(D[1])[1]]), V)
    return F, D, divD

# initial positions: uniformly distributed over disc
def initial(R, z, N=10):
    # create uniform polar coordinates r**2, theta
    r2 = R**2*np.random.rand(N)
    theta = 2.*np.pi*np.random.rand(N)
    r = np.sqrt(r2)
    x = np.zeros((N, 3))
    x[:, 0] = r*np.cos(theta)
    x[:, 1] = r*np.sin(theta)
    x[:, 2] = z
    return x, r, x[:, 2]

class RandomWalk(object):

    def __init__(self, pore, N=10, dt=1., **params):
        # dt is timestep in nanoseconds
        self.pore = pore
        self.params = pore.params
        self.params.update(params)

        # initialize some parameters and create random walkers at entrance
        self.rtop = pore.protein.radiustop() - self.params.rMolecule
        self.ztop = pore.protein.zmax()[1]
        self.rbot = pore.protein.radiusbottom() - self.params.rMolecule
        self.zbot = pore.protein.zmin()[1]
        r1 = self.rtop - self.params.rMolecule
        x, r, z = initial(r1, self.ztop, N)

        self.N = N
        self.x = x
        self.xold = x
        self.rz = np.column_stack([r, z])
        self.dt = dt
        self.t = 0.
        self.i = np.arange(N)

        # load force and diffusivity fields
        F, D, divD = load_externals(**params)
        self.F = F #self.ood_evaluation(F)
        self.D = D #self.ood_evaluation(D)
        self.divD = divD #self.ood_evaluation(divD)
        self.phys = nanopores.Physics("pore_mol", **params)

        self.alive = np.full((N,), True, dtype=bool)
        self.success = np.full((N,), False, dtype=bool)
        self.fail = np.full((N,), False, dtype=bool)
        self.can_bind = np.full((N,), True, dtype=bool)
        self.times = np.zeros(N)
        self.bind_times = np.zeros(N)
        self.attempts = np.zeros(N, dtype=int)
        self.bindings = np.zeros(N, dtype=int)

        self.domains = []
        self.add_domain(pore.protein, binding=False, exclusion=True,
                        walldist=self.params.walldist)

    def add_domain(self, domain, **params):
        """add domain where particles can bind and/or are excluded from.
        domain only has to implement the .inside(x, radius) method.
        params can be domain_params"""
        self.domains.append(Domain(domain, **params))

    def ood_evaluation(self, f):
        dim = self.params.dim
        def newf(x):
            try:
                return f(x)
            except RuntimeError:
                print "ood:", x
                return np.zeros(dim)
        return newf

    def evaluate(self, function):
        return np.array([function(rz) for rz in self.rz])

    def evaluate_vector_cyl(self, function):
        r = self.rz[:, 0] + 1e-30
        R = self.x[self.alive] / r[:, None]
        F = self.evaluate(function)
        return np.column_stack([F[:, 0]*R[:, 0], F[:, 0]*R[:, 1], F[:, 1]])

    def evaluate_D_cyl_matrix(self):
        # approximation based on Dn \sim Dt
        D = self.evaluate(self.D)
        Dn = D[:, 0]
        Dt = D[:, 1]
        r = self.rz[:, 0] + 1e-30
        xbar = self.x[:, 0]/r
        ybar = self.x[:, 1]/r

        Dmatrix = np.zeros((self.N, 3, 3))
        Dmatrix[:, 0, 0] = Dn*xbar**2 + Dt*(1.-xbar**2)
        Dmatrix[:, 1, 1] = Dn*ybar**2 + Dt*(1.-ybar**2)
        Dmatrix[:, 2, 2] = Dt
        return Dmatrix

    def evaluate_D_cyl(self):
        # approximation based on Dn \sim Dt
        D = self.evaluate(self.D)
        Dn = D[:, 0]
        Dt = D[:, 1]
        r = self.rz[:, 0]
        xbar = self.x[self.alive, 0]/r
        ybar = self.x[self.alive, 1]/r
        Dx = Dn*xbar**2 + Dt*(1.-xbar**2)
        Dy = Dn*ybar**2 + Dt*(1.-ybar**2)
        return np.column_stack([Dx, Dy, Dt])

    def evaluate_D_simple(self):
        # just take D = Dzz
        D = self.evaluate(self.D)
        return D[:, 1, None]

    def brownian(self, D):
        n = np.count_nonzero(self.alive)
        zeta = np.random.randn(n, 3)
        return np.sqrt(2.*self.dt*1e9*D) * zeta

    def update(self, dx):
        self.xold = self.x.copy()
        #self.rzold = self.rz.copy()
        self.x[self.alive] = self.x[self.alive] + dx
        self.update_alive()
        r = np.sqrt(np.sum(self.x[self.alive, :2]**2, 1))
        self.rz = np.column_stack([r, self.x[self.alive, 2]])

    def is_success(self, r, z):
        return (z < self.zbot - self.params.margbot) | (
               (r > self.rbot + self.params.margbot) & (z < self.zbot))

    def is_fail(self, r, z):
        return (z > self.ztop + self.params.margtop) | (
               (r > self.rtop + self.params.margtop) & (z > self.ztop))

    def update_alive(self):
        alive = self.alive
        z = self.x[alive, 2]
        r = np.sqrt(np.sum(self.x[alive, :2]**2, 1))
        self.success[alive] = self.is_success(r, z)
        self.fail[alive] = self.is_fail(r, z)
        died = self.fail[alive] | self.success[alive]
        self.alive[alive] = ~died
        self.times[alive] = self.t

    def update_one(self, i, xnew):
        self.x[np.nonzero(self.alive)[0][i]] = xnew
        self.rz[i, 0] = np.sqrt(xnew[0]**2 + xnew[1]**2)
        self.rz[i, 1] = xnew[2]

    def inside_wall(self, factor=1., x=None):
        if x is None:
            return self.pore.protein.inside(self.rz,
                   radius=self.params.rMolecule*factor)
        else:
            return self.pore.protein.inside_single(x,
                   radius=self.params.rMolecule*factor)

    def simple_reflect(self, minsize=0.01):
        factor = self.params.walldist
        radius = self.params.rMolecule*factor
        inside = self.inside_wall(factor)
        alive = self.alive
        X0, X1 = self.xold[alive], self.x[alive]
        for i in np.nonzero(inside)[0]:
            x0, x1 = X0[i], X1[i]
            x = self.binary_search_inside(x0, x1, radius, minsize)
            #t = (x - x0)/(x1 - x0)
            #print "update", t
            #print "update", self.xold[i], ",", x, ",", self.x[i]
            self.update_one(i, x)

    def binary_search_inside(self, x0, x1, radius, minsize=0.5):
        if self.pore.protein.inside_single(x0, radius=radius):
            print "ERROR: something wrong"
            print x0, x1
            raise Exception
        if np.sum((x0 - x1)**2) < minsize**2:
            return x0
        x05 = .5*(x0 + x1)
        if self.pore.protein.inside_single(x05, radius=radius):
            x1 = x05
        else:
            x0 = x05
        return self.binary_search_inside(x0, x1, radius, minsize)

    def step(self):
        "one step of random walk"
        # evaluate F and D
        D = self.evaluate_D_cyl()
        F = self.evaluate_vector_cyl(self.F)
        divD = 1e9*self.evaluate_vector_cyl(self.divD)
        kT = self.phys.kT
        dt = self.dt
        self.t += self.dt

        # get step
        dW = self.brownian(D)
        dx = dW + dt*divD + dt*D/kT*F
        #print "%.2f (dx) = %.2f (dW) + %.2f (divD) + %.2f (F)" % (
        #        abs(dx[0, 2]), abs(dW[0, 2]), abs(dt*divD[0, 2]), abs((dt*D/kT*F)[0, 2]))
        #print ("t = %.2f microsec" % (self.t*1e-3))

        # update position and time and determine which particles are alive
        self.update(dx)

        # correct particles that collided with pore wall
        #self.simple_reflect()
        for domain in self.domains:
            domain.collide(self)

    def walk(self):
        with nanopores.Log("Running..."):
            yield self.t
            while np.any(self.alive):
                #with nanopores.Log("%.0f ns, cpu time:" % self.t):
                self.step()
                yield self.t

        self.finalize()

    def finalize(self):
        print "finished!"
        print "mean # of attempts:", self.attempts.mean()
        print "mean # of bindings:", self.bindings.mean()
        print "mean dwell time with binding: %.1f ms" % (
            1e-6*(self.bind_times + self.times).mean())
        print "mean dwell time without binding: %.1f mus" % (
            1e-3*self.times.mean())
        self.times += self.bind_times

    def ellipse_collection(self, ax):
        "for matplotlib plotting"
        xz = self.x[:, [0,2]]
        #xz = self.rz
        sizes = self.params.rMolecule*np.ones(self.N)
        colors = ["b"]*self.N
        coll = collections.EllipseCollection(sizes, sizes, np.zeros_like(sizes),
                   offsets=xz, units='x', facecolors=colors,
                   transOffset=ax.transData, alpha=0.7)
        return coll

    def move_ellipses(self, coll, cyl=False):
        xz = self.x[:, ::2] if not cyl else np.column_stack(
           [np.sqrt(np.sum(self.x[:, :2]**2, 1)), self.x[:, 2]])
        coll.set_offsets(xz)
        #inside = self.inside_wall()
        margin = np.nonzero(self.alive)[0][self.inside_wall(2.)]
        colors = np.full((self.N,), "b", dtype=str)
        colors[margin] = "r"
        colors[self.success] = "k"
        colors[self.fail] = "k"
        colors[self.alive & ~self.can_bind] = "r"
        #colors = [("r" if inside[i] else "g") if margin[i] else "b" for i in range(self.N)]
        coll.set_facecolors(colors)
        #y = self.x[:, 1]
        #d = 50.
        #sizes = self.params.rMolecule*(1. + y/d)
        #coll.set(widths=sizes, heights=sizes)

    def polygon_patches(self, cyl=False):
        poly_settings = dict(closed=True, facecolor="#eeeeee", linewidth=1.,
                        edgecolor="k")
        ball_settings = dict(facecolor="#aaaaaa", linewidth=1., edgecolor="k",
                             alpha=0.5)
        patches = []
        for dom in self.domains:
            dom = dom.domain
            if isinstance(dom, Polygon):
                polygon = dom.nodes
                polygon = np.array(polygon)
                patches.append(mpatches.Polygon(polygon, **poly_settings))
                if not cyl:
                    polygon_m = np.column_stack([-polygon[:,0], polygon[:,1]])
                    patches.append(mpatches.Polygon(polygon_m, **poly_settings))
            elif isinstance(dom, Ball):
                xy = dom.x0[0], dom.x0[2]
                p = mpatches.Circle(xy, dom.r, **ball_settings)
                p.set_zorder(200)
                patches.append(p)

        return patches

def panimate(rw, cyl=False, **aniparams):
    R = rw.params.R
    Htop = rw.params.Htop
    Hbot = rw.params.Hbot

    #fig = plt.figure()
    #fig.set_size_inches(6, 6)
    #ax = plt.axes([0,0,1,1], autoscale_on=False, xlim=(-R, R), ylim=(-H, H))
    xlim = (-R, R) if not cyl else (0., R)
    ax = plt.axes(xlim=xlim, ylim=(-Hbot, Htop))
    coll = rw.ellipse_collection(ax)
    patches = rw.polygon_patches(cyl)

    def init():
        return ()

    def animate(t):
        if t == 0:
            ax.add_collection(coll)
            for p in patches:
                ax.add_patch(p)

        rw.move_ellipses(coll, cyl=cyl)
        return tuple([coll] + patches)

    aniparams = dict(dict(interval=10, blit=True), **aniparams)
    ani = animation.FuncAnimation(ax.figure, animate, frames=rw.walk(),
                                  init_func=init, **aniparams)
    return ani

def integrate_hist(hist):
    n, bins, _ = hist
    return np.dot(n, np.diff(bins))

def integrate_values(T, fT):
    values = 0.5*(fT[:-1] + fT[1:])
    return np.dot(values, np.diff(T))

def exponential_hist(times, a, b, **params):
    if len(times) == 0:
        return
    bins = np.logspace(a, b, 100)
    hist = plt.hist(times, bins=bins, alpha=0.5, **params)
    plt.xscale("log")
    params.pop("label")
    total = integrate_hist(hist)
    tmean = times.mean()
    T = np.logspace(a-3, b, 1000)
    fT = np.exp(-T/tmean)*T/tmean
    fT *= total/integrate_values(T, fT)
    plt.plot(T, fT, **params)
    plt.xlim(10**a, 10**b)

def histogram(rw, a=0, b=3, scale=1e-6):
    t = rw.times * 1e-9 / scale # assuming times are in nanosaconds

    exponential_hist(t[rw.success], a, b, color="g", label="translocated")
    exponential_hist(t[rw.fail], a, b, color="r", label="did not translocate")

    plt.xlabel(r"$\tau$ off [$\mu$s]")
    plt.ylabel("count")
    plt.legend(loc="best")

if __name__ == "__main__":
    pore = get_pore(**params)
    rw = RandomWalk(pore, **params)
    receptor = Ball([9., 0., -30.], 8.)
    rw.add_domain(receptor, exclusion=True, walldist=1.,
                  binding=True, eps=1., t=1e6, p=0.1)

    if nanopores.user_param(video=True):
        ani = panimate(rw, cyl=params.cylplot)
        plt.show()
    else:
        for t in rw.walk(): pass

    histogram(rw, b=6)
    plt.show()

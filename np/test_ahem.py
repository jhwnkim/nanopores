from nanopores import *
from dolfin import *

geo_params = dict(
    l4 = 15.,
    R = 20.
)

t = Timer("meshing")
meshdict = generate_mesh(12., "aHem", **geo_params)

print "Mesh generation time:",t.stop()
print "Mesh file:",meshdict["fid_xml"]
print "Mesh metadata:"
for item in meshdict["meta"].items():
    print "%s = %s" %item
print 

t = Timer("reading geometry")
geo = geo_from_xml("aHem")

print "Geo generation time:",t.stop()
print "Geo params:", geo.params
print "Geo physical domains:", geo._physical_domain
print "Geo physical boundaries:", geo._physical_boundary

plot(geo.boundaries)
plot(geo.submesh("solid"))
plot(geo.submesh("fluid"))
interactive()

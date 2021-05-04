import numpy as np

import xtrack as xt
import xobjects as xo
import sixtracktools
import pysixtrack

context = xo.ContextCpu()

six = sixtracktools.SixInput(".")
pyst_line = pysixtrack.Line.from_sixinput(six)
sixdump = sixtracktools.SixDump101("res/dump3.dat")

# TODO: The two particles look identical, to be checked
part0_pyst = pysixtrack.Particles(**sixdump[0::2][0].get_minimal_beam())
part1_pyst = pysixtrack.Particles(**sixdump[1::2][0].get_minimal_beam())

particles = xt.Particles(pysixtrack_particles=[part0_pyst, part1_pyst])

source_particles, kernels, cdefs = xt.Particles.XoStruct._gen_c_api()

from xtrack.particles import scalar_vars, per_particle_vars

# Generate local particle CPU
source_local_part = xt.particles.gen_local_particle_api()

source_custom = r'''

void Drift_track_particles(ParticlesData particles){
    printf("Hello\n");
}

'''

kernel_descriptions = {
    "Drift_track_particles": xo.Kernel(
        args=[
            xo.Arg(xt.Particles.XoStruct, name="particles"),
        ],
    )
}

context.add_kernels(
        sources=[source_particles, source_local_part, source_custom],
        kernels=kernel_descriptions,
        extra_cdef=cdefs)

context.kernels.Drift_track_particles(particles=particles)

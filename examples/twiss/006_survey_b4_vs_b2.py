#%%
2 + 2
#%%
import numpy as np
import matplotlib.pyplot as plt
from cpymad.madx import Madx
import xtrack as xt
import xpart as xp

mad_b2 = Madx()
mad_b2.call("../../test_data/hllhc15_noerrors_nobb/sequence.madx")
mad_b2.use(sequence="lhcb2")
twb2mad = mad_b2.twiss()
summb2mad = mad_b2.table.summ
survb2mad = mad_b2.survey().dframe()

mad_b4 = Madx()
mad_b4.call("../../test_data/hllhc15_noerrors_nobb/sequence_b4.madx")
mad_b4.use(sequence="lhcb2")
twb4mad = mad_b4.twiss()
summb4mad = mad_b4.table.summ
survb4mad = mad_b4.survey().dframe()

line_b4 = xt.Line.from_madx_sequence(
    mad_b4.sequence["lhcb2"],
    # deferred_expressions=True
)
line_b4.particle_ref = xp.Particles(mass0=xp.PROTON_MASS_EV, p0c=7000e9)

tracker_b4 = xt.Tracker(line=line_b4)
twb4xt = tracker_b4.twiss()
survb4xt = tracker_b4.survey().to_pandas(index="name")


survb2xt = tracker_b4.survey().mirror().to_pandas(index="name")

#%%

# ORIGINAL:
# ================================

plt.figure(1, figsize=(6, 10))
plt.subplot(6, 1, 1)
coordi = "X"
plt.plot(survb2mad["s"], survb2mad[coordi.lower()], "r", lw=8)
plt.plot(
    survb2mad.loc["ip2", "s"],
    survb2mad.loc["ip2", coordi.lower()],
    "o",
    color="r",
    ms=10,
)
plt.plot(survb4mad["s"], survb4mad[coordi.lower()], "b", lw=5)
plt.plot(
    survb4mad.loc["ip2", "s"],
    survb4mad.loc["ip2", coordi.lower()],
    "o",
    color="b",
    ms=10,
)
plt.plot(survb4xt["s"], survb4xt[coordi], "-", color="k")
plt.plot(survb4xt.loc["ip2", "s"], survb4xt.loc["ip2", coordi], ".", color="k")
plt.ylabel(coordi)

plt.subplot(6, 1, 2)
coordi = "Y"
plt.plot(survb2mad["s"], survb2mad[coordi.lower()], "r", lw=8)
plt.plot(
    survb2mad.loc["ip2", "s"],
    survb2mad.loc["ip2", coordi.lower()],
    "o",
    color="r",
    ms=10,
)
plt.plot(survb4mad["s"], survb4mad[coordi.lower()], "b", lw=5)
plt.plot(
    survb4mad.loc["ip2", "s"],
    survb4mad.loc["ip2", coordi.lower()],
    "o",
    color="b",
    ms=10,
)
plt.plot(survb4xt["s"], survb4xt[coordi], "-", color="k")
plt.plot(survb4xt.loc["ip2", "s"], survb4xt.loc["ip2", coordi], ".", color="k")
plt.ylabel(coordi)

plt.subplot(6, 1, 3)
coordi = "Z"
plt.plot(survb2mad["s"], survb2mad[coordi.lower()], "r", lw=8)
plt.plot(
    survb2mad.loc["ip2", "s"],
    survb2mad.loc["ip2", coordi.lower()],
    "o",
    color="r",
    ms=10,
)
plt.plot(survb4mad["s"], survb4mad[coordi.lower()], "b", lw=5)
plt.plot(
    survb4mad.loc["ip2", "s"],
    survb4mad.loc["ip2", coordi.lower()],
    "o",
    color="b",
    ms=10,
)
plt.plot(survb4xt["s"], survb4xt[coordi], "-", color="k")
plt.plot(survb4xt.loc["ip2", "s"], survb4xt.loc["ip2", coordi], ".", color="k")
plt.ylabel(coordi)

plt.subplot(6, 1, 4)
coordi = "theta"
plt.plot(survb2mad["s"], survb2mad[coordi.lower()], "r", lw=8)
plt.plot(
    survb2mad.loc["ip2", "s"],
    survb2mad.loc["ip2", coordi.lower()],
    "o",
    color="r",
    ms=10,
)
plt.plot(survb4mad["s"], survb4mad[coordi.lower()], "b", lw=5)
plt.plot(
    survb4mad.loc["ip2", "s"],
    survb4mad.loc["ip2", coordi.lower()],
    "o",
    color="b",
    ms=10,
)
plt.plot(survb4xt["s"], survb4xt[coordi], "-", color="k")
plt.plot(survb4xt.loc["ip2", "s"], survb4xt.loc["ip2", coordi], ".", color="k")
plt.ylabel(coordi)

plt.subplot(6, 1, 5)
coordi = "phi"
plt.plot(survb2mad["s"], survb2mad[coordi.lower()], "r", lw=8)
plt.plot(
    survb2mad.loc["ip2", "s"],
    survb2mad.loc["ip2", coordi.lower()],
    "o",
    color="r",
    ms=10,
)
plt.plot(survb4mad["s"], survb4mad[coordi.lower()], "b", lw=5)
plt.plot(
    survb4mad.loc["ip2", "s"],
    survb4mad.loc["ip2", coordi.lower()],
    "o",
    color="b",
    ms=10,
)
plt.plot(survb4xt["s"], survb4xt[coordi], "-", color="k")
plt.plot(survb4xt.loc["ip2", "s"], survb4xt.loc["ip2", coordi], ".", color="k")
plt.ylabel(coordi)


plt.subplot(6, 1, 6)
coordi = "psi"
plt.plot(survb2mad["s"], survb2mad[coordi.lower()], "r", lw=8)
plt.plot(
    survb2mad.loc["ip2", "s"],
    survb2mad.loc["ip2", coordi.lower()],
    "o",
    color="r",
    ms=10,
)
plt.plot(survb4mad["s"], survb4mad[coordi.lower()], "b", lw=5)
plt.plot(
    survb4mad.loc["ip2", "s"],
    survb4mad.loc["ip2", coordi.lower()],
    "o",
    color="b",
    ms=10,
)
plt.plot(survb4xt["s"], survb4xt[coordi], "-", color="k")
plt.plot(survb4xt.loc["ip2", "s"], survb4xt.loc["ip2", coordi], ".", color="k")
plt.ylabel(coordi)


plt.figure(2, figsize=(6, 10))
plt.subplot(6, 1, 1)
coordi = "X"
plt.plot(survb2mad["s"], survb2mad[coordi.lower()], "r", lw=8)
plt.plot(
    survb2mad.loc["ip2", "s"],
    survb2mad.loc["ip2", coordi.lower()],
    "o",
    color="r",
    ms=10,
)
plt.plot(survb4mad["s"], survb4mad[coordi.lower()], "b", lw=5)
plt.plot(
    survb4mad.loc["ip2", "s"],
    survb4mad.loc["ip2", coordi.lower()],
    "o",
    color="b",
    ms=10,
)
plt.plot(survb2xt["s"], survb2xt[coordi], "-", color="k")
plt.plot(survb2xt.loc["ip2", "s"], survb2xt.loc["ip2", coordi], ".", color="k")
plt.ylabel(coordi)

plt.subplot(6, 1, 2)
coordi = "Y"
plt.plot(survb2mad["s"], survb2mad[coordi.lower()], "r", lw=8)
plt.plot(
    survb2mad.loc["ip2", "s"],
    survb2mad.loc["ip2", coordi.lower()],
    "o",
    color="r",
    ms=10,
)
plt.plot(survb4mad["s"], survb4mad[coordi.lower()], "b", lw=5)
plt.plot(
    survb4mad.loc["ip2", "s"],
    survb4mad.loc["ip2", coordi.lower()],
    "o",
    color="b",
    ms=10,
)
plt.plot(survb2xt["s"], survb2xt[coordi], "-", color="k")
plt.plot(survb2xt.loc["ip2", "s"], survb2xt.loc["ip2", coordi], ".", color="k")
plt.ylabel(coordi)

plt.subplot(6, 1, 3)
coordi = "Z"
plt.plot(survb2mad["s"], survb2mad[coordi.lower()], "r", lw=8)
plt.plot(
    survb2mad.loc["ip2", "s"],
    survb2mad.loc["ip2", coordi.lower()],
    "o",
    color="r",
    ms=10,
)
plt.plot(survb4mad["s"], survb4mad[coordi.lower()], "b", lw=5)
plt.plot(
    survb4mad.loc["ip2", "s"],
    survb4mad.loc["ip2", coordi.lower()],
    "o",
    color="b",
    ms=10,
)
plt.plot(survb2xt["s"], survb2xt[coordi], "-", color="k")
plt.plot(survb2xt.loc["ip2", "s"], survb2xt.loc["ip2", coordi], ".", color="k")
plt.ylabel(coordi)

plt.subplot(6, 1, 4)
coordi = "theta"
plt.plot(survb2mad["s"], survb2mad[coordi.lower()], "r", lw=8)
plt.plot(
    survb2mad.loc["ip2", "s"],
    survb2mad.loc["ip2", coordi.lower()],
    "o",
    color="r",
    ms=10,
)
plt.plot(survb4mad["s"], survb4mad[coordi.lower()], "b", lw=5)
plt.plot(
    survb4mad.loc["ip2", "s"],
    survb4mad.loc["ip2", coordi.lower()],
    "o",
    color="b",
    ms=10,
)
plt.plot(survb2xt["s"], survb2xt[coordi], "-", color="k")
plt.plot(survb2xt.loc["ip2", "s"], survb2xt.loc["ip2", coordi], ".", color="k")
plt.ylabel(coordi)

plt.subplot(6, 1, 5)
coordi = "phi"
plt.plot(survb2mad["s"], survb2mad[coordi.lower()], "r", lw=8)
plt.plot(
    survb2mad.loc["ip2", "s"],
    survb2mad.loc["ip2", coordi.lower()],
    "o",
    color="r",
    ms=10,
)
plt.plot(survb4mad["s"], survb4mad[coordi.lower()], "b", lw=5)
plt.plot(
    survb4mad.loc["ip2", "s"],
    survb4mad.loc["ip2", coordi.lower()],
    "o",
    color="b",
    ms=10,
)
plt.plot(survb2xt["s"], survb2xt[coordi], "-", color="k")
plt.plot(survb2xt.loc["ip2", "s"], survb2xt.loc["ip2", coordi], ".", color="k")
plt.ylabel(coordi)

plt.subplot(6, 1, 6)
coordi = "psi"
plt.plot(survb2mad["s"], survb2mad[coordi.lower()], "r", lw=8)
plt.plot(
    survb2mad.loc["ip2", "s"],
    survb2mad.loc["ip2", coordi.lower()],
    "o",
    color="r",
    ms=10,
)
plt.plot(survb4mad["s"], survb4mad[coordi.lower()], "b", lw=5)
plt.plot(
    survb4mad.loc["ip2", "s"],
    survb4mad.loc["ip2", coordi.lower()],
    "o",
    color="b",
    ms=10,
)
plt.plot(survb2xt["s"], survb2xt[coordi], "-", color="k")
plt.plot(survb2xt.loc["ip2", "s"], survb2xt.loc["ip2", coordi], ".", color="k")
plt.ylabel(coordi)

# ================================


# Survey with offset:
starting = {
    "theta0": -np.pi / 9,
    "psi0": np.pi / 7,
    "phi0": np.pi / 11,
    "X0": -300,
    "Y0": 150,
    "Z0": -100,
}

survb4mad = mad_b4.survey(**starting).dframe()
survb2mad = mad_b2.survey(**starting).dframe()
survb4xt = tracker_b4.survey(**starting).to_pandas(index="name")
survb2xt = tracker_b4.survey(**starting).mirror().to_pandas(index="name")


plt.figure(3, figsize=(6, 10))
plt.subplot(6, 1, 1)
coordi = "X"
plt.plot(survb2mad["s"], survb2mad[coordi.lower()], "r", lw=8)
plt.plot(
    survb2mad.loc["ip2", "s"],
    survb2mad.loc["ip2", coordi.lower()],
    "o",
    color="r",
    ms=10,
)
plt.plot(survb4mad["s"], survb4mad[coordi.lower()], "b", lw=5)
plt.plot(
    survb4mad.loc["ip2", "s"],
    survb4mad.loc["ip2", coordi.lower()],
    "o",
    color="b",
    ms=10,
)
plt.plot(survb4xt["s"], survb4xt[coordi], "-", color="k")
plt.plot(survb4xt.loc["ip2", "s"], survb4xt.loc["ip2", coordi], ".", color="k")
plt.ylabel(coordi)

plt.subplot(6, 1, 2)
coordi = "Y"
plt.plot(survb2mad["s"], survb2mad[coordi.lower()], "r", lw=8)
plt.plot(
    survb2mad.loc["ip2", "s"],
    survb2mad.loc["ip2", coordi.lower()],
    "o",
    color="r",
    ms=10,
)
plt.plot(survb4mad["s"], survb4mad[coordi.lower()], "b", lw=5)
plt.plot(
    survb4mad.loc["ip2", "s"],
    survb4mad.loc["ip2", coordi.lower()],
    "o",
    color="b",
    ms=10,
)
plt.plot(survb4xt["s"], survb4xt[coordi], "-", color="k")
plt.plot(survb4xt.loc["ip2", "s"], survb4xt.loc["ip2", coordi], ".", color="k")
plt.ylabel(coordi)

plt.subplot(6, 1, 3)
coordi = "Z"
plt.plot(survb2mad["s"], survb2mad[coordi.lower()], "r", lw=8)
plt.plot(
    survb2mad.loc["ip2", "s"],
    survb2mad.loc["ip2", coordi.lower()],
    "o",
    color="r",
    ms=10,
)
plt.plot(survb4mad["s"], survb4mad[coordi.lower()], "b", lw=5)
plt.plot(
    survb4mad.loc["ip2", "s"],
    survb4mad.loc["ip2", coordi.lower()],
    "o",
    color="b",
    ms=10,
)
plt.plot(survb4xt["s"], survb4xt[coordi], "-", color="k")
plt.plot(survb4xt.loc["ip2", "s"], survb4xt.loc["ip2", coordi], ".", color="k")
plt.ylabel(coordi)

plt.subplot(6, 1, 4)
coordi = "theta"
plt.plot(survb2mad["s"], survb2mad[coordi.lower()], "r", lw=8)
plt.plot(
    survb2mad.loc["ip2", "s"],
    survb2mad.loc["ip2", coordi.lower()],
    "o",
    color="r",
    ms=10,
)
plt.plot(survb4mad["s"], survb4mad[coordi.lower()], "b", lw=5)
plt.plot(
    survb4mad.loc["ip2", "s"],
    survb4mad.loc["ip2", coordi.lower()],
    "o",
    color="b",
    ms=10,
)
plt.plot(survb4xt["s"], survb4xt[coordi], "-", color="k")
plt.plot(survb4xt.loc["ip2", "s"], survb4xt.loc["ip2", coordi], ".", color="k")
plt.ylabel(coordi)

plt.subplot(6, 1, 5)
coordi = "phi"
plt.plot(survb2mad["s"], survb2mad[coordi.lower()], "r", lw=8)
plt.plot(
    survb2mad.loc["ip2", "s"],
    survb2mad.loc["ip2", coordi.lower()],
    "o",
    color="r",
    ms=10,
)
plt.plot(survb4mad["s"], survb4mad[coordi.lower()], "b", lw=5)
plt.plot(
    survb4mad.loc["ip2", "s"],
    survb4mad.loc["ip2", coordi.lower()],
    "o",
    color="b",
    ms=10,
)
plt.plot(survb4xt["s"], survb4xt[coordi], "-", color="k")
plt.plot(survb4xt.loc["ip2", "s"], survb4xt.loc["ip2", coordi], ".", color="k")
plt.ylabel(coordi)


plt.subplot(6, 1, 6)
coordi = "psi"
plt.plot(survb2mad["s"], survb2mad[coordi.lower()], "r", lw=8)
plt.plot(
    survb2mad.loc["ip2", "s"],
    survb2mad.loc["ip2", coordi.lower()],
    "o",
    color="r",
    ms=10,
)
plt.plot(survb4mad["s"], survb4mad[coordi.lower()], "b", lw=5)
plt.plot(
    survb4mad.loc["ip2", "s"],
    survb4mad.loc["ip2", coordi.lower()],
    "o",
    color="b",
    ms=10,
)
plt.plot(survb4xt["s"], survb4xt[coordi], "-", color="k")
plt.plot(survb4xt.loc["ip2", "s"], survb4xt.loc["ip2", coordi], ".", color="k")
plt.ylabel(coordi)


plt.figure(4, figsize=(6, 10))
plt.subplot(6, 1, 1)
coordi = "X"
plt.plot(survb2mad["s"], survb2mad[coordi.lower()], "r", lw=8)
plt.plot(
    survb2mad.loc["ip2", "s"],
    survb2mad.loc["ip2", coordi.lower()],
    "o",
    color="r",
    ms=10,
)
plt.plot(survb4mad["s"], survb4mad[coordi.lower()], "b", lw=5)
plt.plot(
    survb4mad.loc["ip2", "s"],
    survb4mad.loc["ip2", coordi.lower()],
    "o",
    color="b",
    ms=10,
)
plt.plot(survb2xt["s"], survb2xt[coordi], "-", color="k")
plt.plot(survb2xt.loc["ip2", "s"], survb2xt.loc["ip2", coordi], ".", color="k")
plt.ylabel(coordi)

plt.subplot(6, 1, 2)
coordi = "Y"
plt.plot(survb2mad["s"], survb2mad[coordi.lower()], "r", lw=8)
plt.plot(
    survb2mad.loc["ip2", "s"],
    survb2mad.loc["ip2", coordi.lower()],
    "o",
    color="r",
    ms=10,
)
plt.plot(survb4mad["s"], survb4mad[coordi.lower()], "b", lw=5)
plt.plot(
    survb4mad.loc["ip2", "s"],
    survb4mad.loc["ip2", coordi.lower()],
    "o",
    color="b",
    ms=10,
)
plt.plot(survb2xt["s"], survb2xt[coordi], "-", color="k")
plt.plot(survb2xt.loc["ip2", "s"], survb2xt.loc["ip2", coordi], ".", color="k")
plt.ylabel(coordi)

plt.subplot(6, 1, 3)
coordi = "Z"
plt.plot(survb2mad["s"], survb2mad[coordi.lower()], "r", lw=8)
plt.plot(
    survb2mad.loc["ip2", "s"],
    survb2mad.loc["ip2", coordi.lower()],
    "o",
    color="r",
    ms=10,
)
plt.plot(survb4mad["s"], survb4mad[coordi.lower()], "b", lw=5)
plt.plot(
    survb4mad.loc["ip2", "s"],
    survb4mad.loc["ip2", coordi.lower()],
    "o",
    color="b",
    ms=10,
)
plt.plot(survb2xt["s"], survb2xt[coordi], "-", color="k")
plt.plot(survb2xt.loc["ip2", "s"], survb2xt.loc["ip2", coordi], ".", color="k")
plt.ylabel(coordi)

plt.subplot(6, 1, 4)
coordi = "theta"
plt.plot(survb2mad["s"], survb2mad[coordi.lower()], "r", lw=8)
plt.plot(
    survb2mad.loc["ip2", "s"],
    survb2mad.loc["ip2", coordi.lower()],
    "o",
    color="r",
    ms=10,
)
plt.plot(survb4mad["s"], survb4mad[coordi.lower()], "b", lw=5)
plt.plot(
    survb4mad.loc["ip2", "s"],
    survb4mad.loc["ip2", coordi.lower()],
    "o",
    color="b",
    ms=10,
)
plt.plot(survb2xt["s"], survb2xt[coordi], "-", color="k")
plt.plot(survb2xt.loc["ip2", "s"], survb2xt.loc["ip2", coordi], ".", color="k")
plt.ylabel(coordi)

plt.subplot(6, 1, 5)
coordi = "phi"
plt.plot(survb2mad["s"], survb2mad[coordi.lower()], "r", lw=8)
plt.plot(
    survb2mad.loc["ip2", "s"],
    survb2mad.loc["ip2", coordi.lower()],
    "o",
    color="r",
    ms=10,
)
plt.plot(survb4mad["s"], survb4mad[coordi.lower()], "b", lw=5)
plt.plot(
    survb4mad.loc["ip2", "s"],
    survb4mad.loc["ip2", coordi.lower()],
    "o",
    color="b",
    ms=10,
)
plt.plot(survb2xt["s"], survb2xt[coordi], "-", color="k")
plt.plot(survb2xt.loc["ip2", "s"], survb2xt.loc["ip2", coordi], ".", color="k")
plt.ylabel(coordi)

plt.subplot(6, 1, 6)
coordi = "psi"
plt.plot(survb2mad["s"], survb2mad[coordi.lower()], "r", lw=8)
plt.plot(
    survb2mad.loc["ip2", "s"],
    survb2mad.loc["ip2", coordi.lower()],
    "o",
    color="r",
    ms=10,
)
plt.plot(survb4mad["s"], survb4mad[coordi.lower()], "b", lw=5)
plt.plot(
    survb4mad.loc["ip2", "s"],
    survb4mad.loc["ip2", coordi.lower()],
    "o",
    color="b",
    ms=10,
)
plt.plot(survb2xt["s"], survb2xt[coordi], "-", color="k")
plt.plot(survb2xt.loc["ip2", "s"], survb2xt.loc["ip2", coordi], ".", color="k")
plt.ylabel(coordi)


# %%
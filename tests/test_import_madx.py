from scipy.constants import c as clight
import numpy as np

from cpymad.madx import Madx
import xtrack as xt
import xpart as xp

def test_mad_element_import():

    mad = Madx()

    # Element definitions
    mad.input("""

    a = 1.;

    cav0: rfcavity, freq:=a*10, lag:=a*0.5, volt:=a*6;
    cav1: rfcavity, lag:=a*0.5, volt:=a*6, harmon:=a*8;
    wire1: wire, current:=a*5, l:=a*0, l_phy:=a*1, l_int:=a*2, xma:=a*1e-3, yma:=a*2e-3;
    mult0: multipole, knl:={a*1,a*2,a*3}, ksl:={a*4,a*5,a*6}, lrad:=a*1.1;
    kick0: kicker, hkick:=a*5, vkick:=a*6, lrad:=a*2.2;
    kick1: tkicker, hkick:=a*7, vkick:=a*8, lrad:=a*2.3;
    kick2: hkicker, kick:=a*3, lrad:=a*2.4;
    kick3: vkicker, kick:=a*4, lrad:=a*2.5;
    dipedge0: dipedge, h:=a*0.1, e1:=a*3, fint:=a*4, hgap:=a*0.02;
    rfm0: rfmultipole, volt:=a*2, lag:=a*0.5, freq:=a*100.,
                knl:={a*2,a*3}, ksl:={a*4,a*5},
                pnl:={a*0.3, a*0.4}, psl:={a*0.5, a*0.6};
    crab0: crabcavity, volt:=a*2, lag:=a*0.5, freq:=a*100.;
    crab1: crabcavity, volt:=a*2, lag:=a*0.5, freq:=a*100., tilt:=a*pi/2;
    """)

    matrix_m0 = np.random.randn(6)*1E-6
    matrix_m1 = np.reshape(np.random.randn(36),(6,6))
    mad.input(f"mat:matrix,l:=0.003*a,"
              f"kick1:={matrix_m0[0]}*a,kick2:={matrix_m0[1]}*a,"
              f"kick3:={matrix_m0[2]}*a,kick4:={matrix_m0[3]}*a,"
              f"kick5:={matrix_m0[4]}*a,kick6:={matrix_m0[5]}*a,"
              f"rm11:={matrix_m1[0,0]}*a,rm12:={matrix_m1[0,1]}*a,"
              f"rm13:={matrix_m1[0,2]}*a,rm14:={matrix_m1[0,3]}*a,"
              f"rm15:={matrix_m1[0,4]}*a,rm16:={matrix_m1[0,5]}*a,"
              f"rm21:={matrix_m1[1,0]}*a,rm22:={matrix_m1[1,1]}*a,"
              f"rm23:={matrix_m1[1,2]}*a,rm24:={matrix_m1[1,3]}*a,"
              f"rm25:={matrix_m1[1,4]}*a,rm26:={matrix_m1[1,5]}*a,"
              f"rm31:={matrix_m1[2,0]}*a,rm32:={matrix_m1[2,1]}*a,"
              f"rm33:={matrix_m1[2,2]}*a,rm34:={matrix_m1[2,3]}*a,"
              f"rm35:={matrix_m1[2,4]}*a,rm36:={matrix_m1[2,5]}*a,"
              f"rm41:={matrix_m1[3,0]}*a,rm42:={matrix_m1[3,1]}*a,"
              f"rm43:={matrix_m1[3,2]}*a,rm44:={matrix_m1[3,3]}*a,"
              f"rm45:={matrix_m1[3,4]}*a,rm46:={matrix_m1[3,5]}*a,"
              f"rm51:={matrix_m1[4,0]}*a,rm52:={matrix_m1[4,1]}*a,"
              f"rm53:={matrix_m1[4,2]}*a,rm54:={matrix_m1[4,3]}*a,"
              f"rm55:={matrix_m1[4,4]}*a,rm56:={matrix_m1[4,5]}*a,"
              f"rm61:={matrix_m1[5,0]}*a,rm62:={matrix_m1[5,1]}*a,"
              f"rm63:={matrix_m1[5,2]}*a,rm64:={matrix_m1[5,3]}*a,"
              f"rm65:={matrix_m1[5,4]}*a,rm66={matrix_m1[5,5]}*a;")

    # Sequence
    mad.input("""
    testseq: sequence, l=10;
    m0: mult0 at=0.1;
    c0: cav0, at=0.2, apertype=circle, aperture=0.01;
    c1: cav1, at=0.2, apertype=circle, aperture=0.01;
    k0: kick0, at=0.3;
    k1: kick1, at=0.33;
    k2: kick2, at=0.34;
    k3: kick3, at=0.35;
    de0: dipedge0, at=0.38;
    r0: rfm0, at=0.4;
    cb0: crab0, at=0.41;
    cb1: crab1, at=0.42;
    w: wire1, at=1;
    mat0:mat, at=2+0.003/2;
    endsequence;
    """
    )

    # Beam
    mad.input("""
    beam, particle=proton, gamma=1.05, sequence=testseq;
    """)


    mad.use('testseq')

    seq = mad.sequence['testseq']

    for test_expressions in [True, False]:
        line = xt.Line.from_madx_sequence(sequence=seq,
                                          deferred_expressions=test_expressions)
        line.particle_ref = xp.Particles(mass0=xp.PROTON_MASS_EV, gamma0=1.05)

        line = xt.Line.from_dict(line.to_dict()) # This calls the to_dict method fot all
                                                # elements


        assert len(line.element_names) == len(line.element_dict.keys())
        assert line.get_length() == 10

        assert isinstance(line['m0'], xt.Multipole)
        assert line.get_s_position('m0') == 0.1
        assert np.all(line['m0'].knl == np.array([1,2,3]))
        assert np.all(line['m0'].ksl == np.array([4,5,6]))
        assert line['m0'].hxl == 1
        assert line['m0'].hyl == 4
        assert line['m0'].length == 1.1

        assert isinstance(line['k0'], xt.Multipole)
        assert line.get_s_position('k0') == 0.3
        assert np.all(line['k0'].knl == np.array([-5]))
        assert np.all(line['k0'].ksl == np.array([6]))
        assert line['k0'].hxl == 0
        assert line['k0'].hyl == 0
        assert line['k0'].length == 2.2

        assert isinstance(line['k1'], xt.Multipole)
        assert line.get_s_position('k1') == 0.33
        assert np.all(line['k1'].knl == np.array([-7]))
        assert np.all(line['k1'].ksl == np.array([8]))
        assert line['k1'].hxl == 0
        assert line['k1'].hyl == 0
        assert line['k1'].length == 2.3

        assert isinstance(line['k2'], xt.Multipole)
        assert line.get_s_position('k2') == 0.34
        assert np.all(line['k2'].knl == np.array([-3]))
        assert np.all(line['k2'].ksl == np.array([0]))
        assert line['k2'].hxl == 0
        assert line['k2'].hyl == 0
        assert line['k2'].length == 2.4

        assert isinstance(line['k3'], xt.Multipole)
        assert line.get_s_position('k3') == 0.35
        assert np.all(line['k3'].knl == np.array([0]))
        assert np.all(line['k3'].ksl == np.array([4]))
        assert line['k3'].hxl == 0
        assert line['k3'].hyl == 0
        assert line['k3'].length == 2.5

        assert isinstance(line['c0'], xt.Cavity)
        assert line.get_s_position('c0') == 0.2
        assert line['c0'].frequency == 10e6
        assert line['c0'].lag == 180
        assert line['c0'].voltage == 6e6

        assert isinstance(line['c1'], xt.Cavity)
        assert line.get_s_position('c1') == 0.2
        assert np.isclose(line['c1'].frequency, clight*line.particle_ref.beta0/10.*8,
                        rtol=0, atol=1e-7)
        assert line['c1'].lag == 180
        assert line['c1'].voltage == 6e6

        assert isinstance(line['de0'], xt.DipoleEdge)
        assert line.get_s_position('de0') == 0.38
        assert line['de0'].h == 0.1
        assert line['de0'].e1 == 3
        assert line['de0'].fint == 4
        assert line['de0'].hgap == 0.02

        assert isinstance(line['r0'], xt.RFMultipole)
        assert line.get_s_position('r0') == 0.4
        assert np.all(line['r0'].knl == np.array([2,3]))
        assert np.all(line['r0'].ksl == np.array([4,5]))
        assert np.all(line['r0'].pn == np.array([0.3*360,0.4*360]))
        assert np.all(line['r0'].ps == np.array([0.5*360,0.6*360]))
        assert line['r0'].voltage == 2e6
        assert line['r0'].order == 1
        assert line['r0'].frequency == 100e6
        assert line['r0'].lag == 180

        assert isinstance(line['cb0'], xt.RFMultipole)
        assert line.get_s_position('cb0') == 0.41
        assert len(line['cb0'].knl) == 1
        assert len(line['cb0'].ksl) == 1
        assert np.isclose(line['cb0'].knl[0], 2*1e6/line.particle_ref.p0c[0],
                        rtol=0, atol=1e-12)
        assert np.all(line['cb0'].ksl == 0)
        assert np.all(line['cb0'].pn == np.array([270]))
        assert np.all(line['cb0'].ps == 0.)
        assert line['cb0'].voltage == 0
        assert line['cb0'].order == 0
        assert line['cb0'].frequency == 100e6
        assert line['cb0'].lag == 0

        assert isinstance(line['cb1'], xt.RFMultipole)
        assert line.get_s_position('cb1') == 0.42
        assert len(line['cb1'].knl) == 1
        assert len(line['cb1'].ksl) == 1
        assert np.isclose(line['cb1'].ksl[0], -2*1e6/line.particle_ref.p0c[0],
                        rtol=0, atol=1e-12)
        assert np.all(line['cb1'].knl == 0)
        assert np.all(line['cb1'].ps == np.array([270]))
        assert np.all(line['cb1'].pn == 0.)
        assert line['cb1'].voltage == 0
        assert line['cb1'].order == 0
        assert line['cb1'].frequency == 100e6
        assert line['cb1'].lag == 0


        assert isinstance(line['w'], xt.Wire)
        assert line.get_s_position('w') == 1
        assert line['w'].L_phy == 1
        assert line['w'].L_int == 2
        assert line['w'].xma == 1e-3
        assert line['w'].yma == 2e-3

        assert isinstance(line['mat0'],xt.FirstOrderTaylorMap)
        assert line.get_s_position('mat0') == 2
        assert np.allclose(line['mat0'].m0,matrix_m0,rtol=0.0,atol=1E-12)
        assert np.allclose(line['mat0'].m1,matrix_m1,rtol=0.0,atol=1E-12)
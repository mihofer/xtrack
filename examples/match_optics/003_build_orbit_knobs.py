import time

import numpy as np

import xtrack as xt

default_tol = {None: 1e-8, 'betx': 1e-6, 'bety': 1e-6} # to have no rematching w.r.t. madx

collider = xt.Multiline.from_json('collider_02_changed_ip15_phase.json')
collider.build_trackers()

t1 = time.time()

all_knobs_ip2ip8 = ['acbxh3.r2', 'acbchs5.r2b1', 'pxip2b1', 'acbxh2.l8',
    'acbyhs4.r8b2', 'pyip2b1', 'acbxv1.l8', 'acbyvs4.l2b1', 'acbxh1.l8',
    'acbxv2.r8', 'pxip8b2', 'yip8b1', 'pxip2b2', 'acbcvs5.r2b1', 'acbyhs4.l8b1',
    'acbyvs4.l8b1', 'acbxh2.l2', 'acbxh3.l2', 'acbxv1.r8', 'acbxv1.r2',
    'acbyvs4.r2b2', 'acbyvs4.l2b2', 'yip8b2', 'xip2b2', 'acbxh2.r2',
    'acbyhs4.l2b2', 'acbxv2.r2', 'acbyhs5.r8b1', 'acbxh2.r8', 'acbxv3.r8',
    'acbyvs5.r8b2', 'acbyvs5.l2b2', 'yip2b1', 'acbxv2.l2', 'acbyhs4.r2b2',
    'acbyhs4.r2b1', 'xip8b2', 'acbyvs5.l2b1', 'acbyvs4.r8b1', 'acbyvs4.r8b2',
    'acbyvs5.r8b1', 'acbxh1.r8', 'acbyvs4.l8b2', 'acbyhs5.l2b1', 'acbyvs4.r2b1',
    'acbcvs5.r2b2', 'acbcvs5.l8b2', 'acbyhs4.r8b1', 'pxip8b1', 'acbxv1.l2',
    'yip2b2', 'acbyhs4.l8b2', 'acbxv3.r2', 'xip8b1', 'acbchs5.r2b2', 'acbxh3.l8',
    'acbxh3.r8', 'acbyhs5.r8b2', 'acbxv2.l8', 'acbxh1.l2', 'pyip8b1', 'pyip8b2',
    'acbxv3.l8', 'xip2b1', 'acbyhs5.l2b2', 'acbchs5.l8b2', 'acbcvs5.l8b1',
    'pyip2b2', 'acbxv3.l2', 'acbchs5.l8b1', 'acbyhs4.l2b1', 'acbxh1.r2']


# kill all existing knobs
for kk in all_knobs_ip2ip8:
    collider.vars[kk] = 0

twinit_zero_orbit = [xt.TwissInit(), xt.TwissInit()]

targets_close_bump = [
    xt.TargetSet(line='lhcb1', at=xt.END, x=0, px=0, y=0, py=0),
    xt.TargetSet(line='lhcb2', at=xt.END, x=0, px=0, y=0, py=0),
]

bump_range_ip2 = {
    'ele_start': ['s.ds.l2.b1', 's.ds.l2.b2'],
    'ele_stop': ['e.ds.r2.b1', 'e.ds.r2.b2'],
    'only_markers': True, # quick and dirty way to pass a kwarg to all matches
    'only_orbit': True,
}
bump_range_ip8 = {
    'ele_start': ['s.ds.l8.b1', 's.ds.l8.b2'],
    'ele_stop': ['e.ds.r8.b1', 'e.ds.r8.b2'],
    'only_markers': True, # quick and dirty way to pass a kwarg to all matches
    'only_orbit': True,
}

correctors_ir2_single_beam_h = [
    'acbyhs4.l2b1', 'acbyhs4.r2b2', 'acbyhs4.l2b2', 'acbyhs4.r2b1',
    'acbyhs5.l2b2', 'acbyhs5.l2b1', 'acbchs5.r2b1', 'acbchs5.r2b2']

correctors_ir2_single_beam_v = [
    'acbyvs4.l2b1', 'acbyvs4.r2b2', 'acbyvs4.l2b2', 'acbyvs4.r2b1',
    'acbyvs5.l2b2', 'acbyvs5.l2b1', 'acbcvs5.r2b1', 'acbcvs5.r2b2']

correctors_ir8_single_beam_h = [
    'acbyhs4.l8b1', 'acbyhs4.r8b2', 'acbyhs4.l8b2', 'acbyhs4.r8b1',
    'acbchs5.l8b2', 'acbchs5.l8b1', 'acbyhs5.r8b1', 'acbyhs5.r8b2']

correctors_ir8_single_beam_v = [
    'acbyvs4.l8b1', 'acbyvs4.r8b2', 'acbyvs4.l8b2', 'acbyvs4.r8b1',
    'acbcvs5.l8b2', 'acbcvs5.l8b1', 'acbyvs5.r8b1', 'acbyvs5.r8b2']

correctors_ir2_common_h = [
    'acbxh1.l2', 'acbxh2.l2', 'acbxh3.l2', 'acbxh1.r2', 'acbxh2.r2', 'acbxh3.r2']

correctors_ir2_common_v = [
    'acbxv1.l2', 'acbxv2.l2', 'acbxv3.l2', 'acbxv1.r2', 'acbxv2.r2', 'acbxv3.r2']

correctors_ir8_common_h = [
    'acbxh1.l8', 'acbxh2.l8', 'acbxh3.l8', 'acbxh1.r8', 'acbxh2.r8', 'acbxh3.r8']

correctors_ir8_common_v = [
    'acbxv1.l8', 'acbxv2.l8', 'acbxv3.l8', 'acbxv1.r8', 'acbxv2.r8', 'acbxv3.r8']

#########################
# Match IP offset knobs #
#########################

offset_match = 0.5e-3

# ---------- on_o2v ----------

opt_o2v = collider.match_knob(
    knob_name='on_o2v', knob_value_end=(offset_match * 1e3),
    targets=(targets_close_bump + [
        xt.TargetSet(line='lhcb1', at='ip2', y=offset_match, py=0),
        xt.TargetSet(line='lhcb2', at='ip2', y=offset_match, py=0),
    ]),
    vary=xt.VaryList(correctors_ir2_single_beam_v),
    run=False, twiss_init=twinit_zero_orbit, **bump_range_ip2,
)
opt_o2v.solve()
opt_o2v.generate_knob()

# ---------- on_o2h ----------

opt_o2h = collider.match_knob(
    knob_name='on_o2h', knob_value_end=(offset_match * 1e3),
    targets=(targets_close_bump + [
        xt.TargetSet(line='lhcb1', at='ip2', x=offset_match, px=0),
        xt.TargetSet(line='lhcb2', at='ip2', x=offset_match, px=0),
    ]),
    vary=xt.VaryList(correctors_ir2_single_beam_h),
    run=False, twiss_init=twinit_zero_orbit, **bump_range_ip2,
)
opt_o2h.solve()
opt_o2h.generate_knob()

# ---------- on_o8v ----------

opt_o8v = collider.match_knob(
    knob_name='on_o8v', knob_value_end=(offset_match * 1e3),
    targets=(targets_close_bump + [
        xt.TargetSet(line='lhcb1', at='ip8', y=offset_match, py=0),
        xt.TargetSet(line='lhcb2', at='ip8', y=offset_match, py=0),
    ]),
    vary=xt.VaryList(correctors_ir8_single_beam_v),
    run=False, twiss_init=twinit_zero_orbit, **bump_range_ip8,
)
opt_o8v.solve()
opt_o8v.generate_knob()

# ---------- on_o8h ----------

opt_o8h = collider.match_knob(
    knob_name='on_o8h', knob_value_end=(offset_match * 1e3),
    targets=(targets_close_bump + [
        xt.TargetSet(line='lhcb1', at='ip8', x=offset_match, px=0),
        xt.TargetSet(line='lhcb2', at='ip8', x=offset_match, px=0),
    ]),
    vary=xt.VaryList(correctors_ir8_single_beam_h),
    run=False, twiss_init=twinit_zero_orbit, **bump_range_ip8,
)
opt_o8h.solve()
opt_o8h.generate_knob()

##############################
# Match angular offset knobs #
##############################

ang_offset_match = 30e-6

# ---------- on_a2h ----------

opt_a2h = collider.match_knob(
    knob_name='on_a2h', knob_value_end=(ang_offset_match * 1e6),
    targets=(targets_close_bump + [
        xt.TargetSet(line='lhcb1', at='ip2', x=0, px=ang_offset_match),
        xt.TargetSet(line='lhcb2', at='ip2', x=0, px=ang_offset_match),
    ]),
    vary=xt.VaryList(correctors_ir2_single_beam_h),
    run=False, twiss_init=twinit_zero_orbit, **bump_range_ip2,
)

opt_a2h.solve()
opt_a2h.generate_knob()

# ---------- on_a2v ----------

opt_a2v = collider.match_knob(
    knob_name='on_a2v', knob_value_end=(ang_offset_match * 1e6),
    targets=(targets_close_bump + [
        xt.TargetSet(line='lhcb1', at='ip2', y=0, py=ang_offset_match),
        xt.TargetSet(line='lhcb2', at='ip2', y=0, py=ang_offset_match),
    ]),
    vary=xt.VaryList(correctors_ir2_single_beam_v),
    run=False, twiss_init=twinit_zero_orbit, **bump_range_ip2,
)

opt_a2v.solve()
opt_a2v.generate_knob()

# ---------- on_a8h ----------

opt_a8h = collider.match_knob(
    knob_name='on_a8h', knob_value_end=(ang_offset_match * 1e6),
    targets=(targets_close_bump + [
        xt.TargetSet(line='lhcb1', at='ip8', x=0, px=ang_offset_match),
        xt.TargetSet(line='lhcb2', at='ip8', x=0, px=ang_offset_match),
    ]),
    vary=xt.VaryList(correctors_ir8_single_beam_h),
    run=False, twiss_init=twinit_zero_orbit, **bump_range_ip8,
)

opt_a8h.solve()
opt_a8h.generate_knob()

# ---------- on_a8v ----------

opt_a8v = collider.match_knob(
    knob_name='on_a8v', knob_value_end=(ang_offset_match * 1e6),
    targets=(targets_close_bump + [
        xt.TargetSet(line='lhcb1', at='ip8', y=0, py=ang_offset_match),
        xt.TargetSet(line='lhcb2', at='ip8', y=0, py=ang_offset_match),
    ]),
    vary=xt.VaryList(correctors_ir8_single_beam_v),
    run=False, twiss_init=twinit_zero_orbit, **bump_range_ip8,
)

opt_a8v.solve()
opt_a8v.generate_knob()

##############################
# Match crossing angle knobs #
##############################

angle_match_ip2 = 170e-6
angle_match_ip8 = 300e-6

# ---------- on_x2h ----------

opt_x2h = collider.match_knob(
    knob_name='on_x2h', knob_value_end=(angle_match_ip2 * 1e6),
    targets=(targets_close_bump + [
        xt.TargetSet(line='lhcb1', at='ip2',  x=0, px=angle_match_ip2),
        xt.TargetSet(line='lhcb2', at='ip2',  x=0, px=-angle_match_ip2),
    ]),
    vary=[
        xt.VaryList(correctors_ir2_single_beam_h),
        xt.VaryList(correctors_ir2_common_h, tag='mcbx')],
    run=False, twiss_init=twinit_zero_orbit, **bump_range_ip2,
)
# Set mcbx by hand
testkqx2=abs(collider.varval['kqx.l2'])*7000./0.3
acbx_xing_ir2 = 1.0e-6 if testkqx2 > 210. else 11.0e-6 # Value for 170 urad crossing
for icorr in [1, 2, 3]:
    collider.vars[f'acbxh{icorr}.l2_from_on_x2h'] = acbx_xing_ir2
    collider.vars[f'acbxh{icorr}.r2_from_on_x2h'] = -acbx_xing_ir2
# Match other correctors with fixed mcbx and generate knob
opt_x2h.disable_vary(tag='mcbx')
opt_x2h.solve()
opt_x2h.generate_knob()

# ---------- on_x2v ----------

opt_x2v = collider.match_knob(
    knob_name='on_x2v', knob_value_end=(angle_match_ip2 * 1e6),
    targets=(targets_close_bump + [
        xt.TargetSet(line='lhcb1', at='ip2',  y=0, py=angle_match_ip2),
        xt.TargetSet(line='lhcb2', at='ip2',  y=0, py=-angle_match_ip2),
    ]),
    vary=[
        xt.VaryList(correctors_ir2_single_beam_v),
        xt.VaryList(correctors_ir2_common_v, tag='mcbx')],
    run=False, twiss_init=twinit_zero_orbit, **bump_range_ip2,
)
# Set mcbx by hand
testkqx2=abs(collider.varval['kqx.l2'])*7000./0.3
acbx_xing_ir2 = 1.0e-6 if testkqx2 > 210. else 11.0e-6
for icorr in [1, 2, 3]:
    collider.vars[f'acbxv{icorr}.l2_from_on_x2v'] = acbx_xing_ir2
    collider.vars[f'acbxv{icorr}.r2_from_on_x2v'] = -acbx_xing_ir2
# Match other correctors with fixed mcbx and generate knob
opt_x2v.disable_vary(tag='mcbx')
opt_x2v.solve()
opt_x2v.generate_knob()

# ---------- on_x8h ----------

opt_x8h = collider.match_knob(
    knob_name='on_x8h', knob_value_end=(angle_match_ip8 * 1e6),
    targets=(targets_close_bump + [
        xt.TargetSet(line='lhcb1', at='ip8',  x=0, px=angle_match_ip8),
        xt.TargetSet(line='lhcb2', at='ip8',  x=0, px=-angle_match_ip8),
    ]),
    vary=[
        xt.VaryList(correctors_ir8_single_beam_h),
        xt.VaryList(correctors_ir8_common_h, tag='mcbx')],
    run=False, twiss_init=twinit_zero_orbit, **bump_range_ip8,
)

# Set mcbx by hand (reduce value by 10, to test matching algorithm)
testkqx8=abs(collider.varval['kqx.l8'])*7000./0.3
acbx_xing_ir8 = 1.0e-6 if testkqx8 > 210. else 11.0e-6 # Value for 170 urad crossing

# Set mcbx by hand
for icorr in [1, 2, 3]:
    collider.vars[f'acbxh{icorr}.l8_from_on_x8h'] = acbx_xing_ir8 * angle_match_ip8 / 170e-6
    collider.vars[f'acbxh{icorr}.r8_from_on_x8h'] = -acbx_xing_ir8 * angle_match_ip8 / 170e-6

#   (reduce value by 10, to test matching algorithm)
#   collider.vars[f'acbxh{icorr}.l8_from_on_x8h'] = acbx_xing_ir8 * angle_match_ip8 / 170e-6 * 0.1
#   collider.vars[f'acbxh{icorr}.r8_from_on_x8h'] = -acbx_xing_ir8 * angle_match_ip8 / 170e-6 * 0.1

# First round of optimization without changing mcbx
opt_x8h.disable_vary(tag='mcbx')
opt_x8h.step(3) # perform 3 steps without checking for convergence

# Link all mcbx strengths to the first one
collider.vars['acbxh2.l8_from_on_x8h'] =  collider.vars['acbxh1.l8_from_on_x8h']
collider.vars['acbxh3.l8_from_on_x8h'] =  collider.vars['acbxh1.l8_from_on_x8h']
collider.vars['acbxh2.r8_from_on_x8h'] = -collider.vars['acbxh1.l8_from_on_x8h']
collider.vars['acbxh3.r8_from_on_x8h'] = -collider.vars['acbxh1.l8_from_on_x8h']
collider.vars['acbxh1.r8_from_on_x8h'] = -collider.vars['acbxh1.l8_from_on_x8h']

# Enable first mcbx knob (which controls the others)
assert opt_x8h.vary[8].name == 'acbxh1.l8_from_on_x8h'
opt_x8h.vary[8].active = True

# Solve and generate knob
opt_x8h.solve()
opt_x8h.generate_knob()

# ---------- on_x8v ----------

opt_x8v = collider.match_knob(
    knob_name='on_x8v', knob_value_end=(angle_match_ip8 * 1e6),
    targets=(targets_close_bump + [
        xt.TargetSet(line='lhcb1', at='ip8', y=0, py=angle_match_ip8),
        xt.TargetSet(line='lhcb2', at='ip8', y=0, py=-angle_match_ip8),
    ]),
    vary=[
        xt.VaryList(correctors_ir8_single_beam_v),
        xt.VaryList(correctors_ir8_common_v, tag='mcbx')],
    run=False, twiss_init=twinit_zero_orbit, **bump_range_ip8,
)

# Set mcbx by hand
testkqx8=abs(collider.varval['kqx.l8'])*7000./0.3
acbx_xing_ir8 = 1.0e-6 if testkqx8 > 210. else 11.0e-6 # Value for 170 urad crossing
# Set MCBX by hand
for icorr in [1, 2, 3]:
    collider.vars[f'acbxv{icorr}.l8_from_on_x8v'] = acbx_xing_ir8 * angle_match_ip8 / 170e-6
    collider.vars[f'acbxv{icorr}.r8_from_on_x8v'] = -acbx_xing_ir8 * angle_match_ip8 / 170e-6

# First round of optimization without changing mcbx
opt_x8v.disable_vary(tag='mcbx')
opt_x8v.step(3) # perform 3 steps without checking for convergence

# Solve with all vary active and generate knob
opt_x8v.enable_vary(tag='mcbx')
opt_x8v.solve()
opt_x8v.generate_knob()

##########################
# Match separation knobs #
##########################

sep_match = 2e-3

# ---------- on_sep2h ----------

opt_sep2h = collider.match_knob(
    knob_name='on_sep2h', knob_value_end=(sep_match * 1e3),
    targets=(targets_close_bump + [
        xt.TargetSet(line='lhcb1', at='ip2', x=sep_match, px=0),
        xt.TargetSet(line='lhcb2', at='ip2', x=-sep_match, px=0),
    ]),
    vary=[
        xt.VaryList(correctors_ir2_single_beam_h),
        xt.VaryList(correctors_ir2_common_h, tag='mcbx')],
    run=False, twiss_init=twinit_zero_orbit, **bump_range_ip2,
)

# Set mcbx by hand
testkqx2=abs(collider.varval['kqx.l2'])*7000./0.3
acbx_sep_ir2 = 18e-6 if testkqx2 > 210. else 16e-6

for icorr in [1, 2, 3]:
    collider.vars[f'acbxh{icorr}.l2_from_on_sep2h'] = acbx_sep_ir2
    collider.vars[f'acbxh{icorr}.r2_from_on_sep2h'] = acbx_sep_ir2

# Match other correctors with fixed mcbx and generate knob
opt_sep2h.disable_vary(tag='mcbx')
opt_sep2h.solve()
opt_sep2h.generate_knob()

# ---------- on_sep2v ----------

opt_sep2v = collider.match_knob(
    knob_name='on_sep2v', knob_value_end=(sep_match * 1e3),
    targets=(targets_close_bump + [
        xt.TargetSet(line='lhcb1', at='ip2',  y=sep_match, py=0),
        xt.TargetSet(line='lhcb2', at='ip2',  y=-sep_match, py=0),
    ]),
    vary=[
        xt.VaryList(correctors_ir2_single_beam_v),
        xt.VaryList(correctors_ir2_common_v, tag='mcbx')],
    run=False, twiss_init=twinit_zero_orbit, **bump_range_ip2,
)

# Set mcbx by hand
testkqx2=abs(collider.varval['kqx.l2'])*7000./0.3
acbx_sep_ir2 = 18e-6 if testkqx2 > 210. else 16e-6

for icorr in [1, 2, 3]:
    collider.vars[f'acbxv{icorr}.l2_from_on_sep2v'] = acbx_sep_ir2
    collider.vars[f'acbxv{icorr}.r2_from_on_sep2v'] = acbx_sep_ir2

# Match other correctors with fixed mcbx and generate knob
opt_sep2v.disable_vary(tag='mcbx')
opt_sep2v.solve()
opt_sep2v.generate_knob()

# ---------- on_sep8h ----------

opt_sep8h = collider.match_knob(
    knob_name='on_sep8h', knob_value_end=(sep_match * 1e3),
    targets=(targets_close_bump + [
        xt.TargetSet(line='lhcb1', at='ip8',  x=sep_match, px=0),
        xt.TargetSet(line='lhcb2', at='ip8',  x=-sep_match, px=0),
    ]),
    vary=[
        xt.VaryList(correctors_ir8_single_beam_h),
        xt.VaryList(correctors_ir8_common_h, tag='mcbx')],
    run=False, twiss_init=twinit_zero_orbit, **bump_range_ip8,
)

# Set mcbx by hand
testkqx8=abs(collider.varval['kqx.l8'])*7000./0.3
acbx_sep_ir8 = 18e-6 if testkqx8 > 210. else 16e-6

for icorr in [1, 2, 3]:
    collider.vars[f'acbxh{icorr}.l8_from_on_sep8h'] = acbx_sep_ir8 * sep_match / 2e-3
    collider.vars[f'acbxh{icorr}.r8_from_on_sep8h'] = acbx_sep_ir8 * sep_match / 2e-3

# Match other correctors with fixed mcbx and generate knob
opt_sep8h.disable_vary(tag='mcbx')
opt_sep8h.solve()
opt_sep8h.generate_knob()

# ---------- on_sep8v ----------

opt_sep8v = collider.match_knob(
    knob_name='on_sep8v', knob_value_end=(sep_match * 1e3),
    targets=(targets_close_bump + [
        xt.TargetSet(line='lhcb1', at='ip8',  y=sep_match, py=0),
        xt.TargetSet(line='lhcb2', at='ip8',  y=-sep_match, py=0),
    ]),
    vary=[
        xt.VaryList(correctors_ir8_single_beam_v),
        xt.VaryList(correctors_ir8_common_v, tag='mcbx')],
    run=False, twiss_init=twinit_zero_orbit, **bump_range_ip8,
)

# Set mcbx by hand
testkqx8=abs(collider.varval['kqx.l8'])*7000./0.3
acbx_sep_ir8 = 18e-6 if testkqx8 > 210. else 16e-6

for icorr in [1, 2, 3]:
    collider.vars[f'acbxv{icorr}.l8_from_on_sep8v'] = acbx_sep_ir8 * sep_match / 2e-3
    collider.vars[f'acbxv{icorr}.r8_from_on_sep8v'] = acbx_sep_ir8 * sep_match / 2e-3

# Match other correctors with fixed mcbx and generate knob
opt_sep8v.disable_vary(tag='mcbx')
opt_sep8v.solve()
opt_sep8v.generate_knob()

t2 = time.time()

phi_ir2 = 90.
phi_ir8 = 0.

v = collider.vars
f = collider.functions
for irn in [2, 8]:
    v[f'cphi_ir{irn}'] = f.cos(v[f'phi_ir{irn}'] * np.pi / 180.)
    v[f'sphi_ir{irn}'] = f.sin(v[f'phi_ir{irn}'] * np.pi / 180.)
    v[f'on_x{irn}h']   =  v[f'on_x{irn}'] * v[f'cphi_ir{irn}']
    v[f'on_x{irn}v']   =  v[f'on_x{irn}'] * v[f'sphi_ir{irn}']
    v[f'on_sep{irn}h'] = -v[f'on_sep{irn}'] * v[f'sphi_ir{irn}']
    v[f'on_sep{irn}v'] =  v[f'on_sep{irn}'] * v[f'cphi_ir{irn}']
    v[f'on_o{irn}h']   =  v[f'on_o{irn}'] * v[f'cphi_ir{irn}']
    v[f'on_o{irn}v']   =  v[f'on_o{irn}'] * v[f'sphi_ir{irn}']
    v[f'on_a{irn}h']   = -v[f'on_a{irn}'] * v[f'sphi_ir{irn}']
    v[f'on_a{irn}v']   =  v[f'on_a{irn}'] * v[f'cphi_ir{irn}']

print(f'Knob generation took {t2-t1:.1f} seconds')

collider.to_json('collider_03_with_orbit_knobs.json')

# -----------------------------------------------------------------------------

# Check higher level knobs

collider.vars['on_x2'] = 34
tw = collider.twiss()
collider.vars['on_x2'] = 0

assert np.isclose(tw.lhcb1['py', 'ip2'], 34e-6, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['py', 'ip2'], -34e-6, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb1['y', 'ip2'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['y', 'ip2'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb1['px', 'ip2'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['px', 'ip2'], 0, atol=1e-9, rtol=0)

collider.vars['on_x8'] = 35
tw = collider.twiss()
collider.vars['on_x8'] = 0

assert np.isclose(tw.lhcb1['px', 'ip8'], 35e-6, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['px', 'ip8'], -35e-6, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb1['x', 'ip8'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['x', 'ip8'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb1['py', 'ip8'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['py', 'ip8'], 0, atol=1e-9, rtol=0)

collider.vars['on_sep2'] = 0.5
tw = collider.twiss()
collider.vars['on_sep2'] = 0

assert np.isclose(tw.lhcb1['x', 'ip2'], -0.5e-3, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['x', 'ip2'], 0.5e-3, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb1['px', 'ip2'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['px', 'ip2'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb1['y', 'ip2'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['y', 'ip2'], 0, atol=1e-9, rtol=0)

collider.vars['on_sep8'] = 0.6
tw = collider.twiss()
collider.vars['on_sep8'] = 0

assert np.isclose(tw.lhcb1['y', 'ip8'], 0.6e-3, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['y', 'ip8'], -0.6e-3, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb1['py', 'ip8'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['py', 'ip8'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb1['x', 'ip8'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['x', 'ip8'], 0, atol=1e-9, rtol=0)

# Check lower level knobs (disconnects higher level knobs)

collider.vars['on_o2v'] = 0.3
tw = collider.twiss()
collider.vars['on_o2v'] = 0

assert np.isclose(tw.lhcb1['y', 'ip2'], 0.3e-3, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['y', 'ip2'], 0.3e-3, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb1['py', 'ip2'], 0., atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['py', 'ip2'], 0., atol=1e-9, rtol=0)

collider.vars['on_o2h'] = 0.4
tw = collider.twiss()
collider.vars['on_o2h'] = 0

assert np.isclose(tw.lhcb1['x', 'ip2'], 0.4e-3, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['x', 'ip2'], 0.4e-3, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb1['px', 'ip2'], 0., atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['px', 'ip2'], 0., atol=1e-9, rtol=0)

collider.vars['on_o8v'] = 0.5
tw = collider.twiss()
collider.vars['on_o8v'] = 0

assert np.isclose(tw.lhcb1['y', 'ip8'], 0.5e-3, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['y', 'ip8'], 0.5e-3, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb1['py', 'ip8'], 0., atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['py', 'ip8'], 0., atol=1e-9, rtol=0)

collider.vars['on_o8h'] = 0.6
tw = collider.twiss()
collider.vars['on_o8h'] = 0

assert np.isclose(tw.lhcb1['x', 'ip8'], 0.6e-3, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['x', 'ip8'], 0.6e-3, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb1['px', 'ip8'], 0., atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['px', 'ip8'], 0., atol=1e-9, rtol=0)

collider.vars['on_a2h'] = 20
tw = collider.twiss()
collider.vars['on_a2h'] = 0

assert np.isclose(tw.lhcb1['x', 'ip2'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['x', 'ip2'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb1['px', 'ip2'], 20e-6, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['px', 'ip2'], 20e-6, atol=1e-9, rtol=0)

collider.vars['on_a2v'] = 15
tw = collider.twiss()
collider.vars['on_a2v'] = 0

assert np.isclose(tw.lhcb1['y', 'ip2'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['y', 'ip2'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb1['py', 'ip2'], 15e-6, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['py', 'ip2'], 15e-6, atol=1e-9, rtol=0)

collider.vars['on_a8h'] = 20
tw = collider.twiss()
collider.vars['on_a8h'] = 0

assert np.isclose(tw.lhcb1['x', 'ip8'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['x', 'ip8'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb1['px', 'ip8'], 20e-6, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['px', 'ip8'], 20e-6, atol=1e-9, rtol=0)

collider.vars['on_a8v'] = 50
tw = collider.twiss()
collider.vars['on_a8v'] = 0

assert np.isclose(tw.lhcb1['y', 'ip8'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['y', 'ip8'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb1['py', 'ip8'], 50e-6, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['py', 'ip8'], 50e-6, atol=1e-9, rtol=0)

collider.vars['on_x2v'] = 100
tw = collider.twiss()
collider.vars['on_x2v'] = 0

assert np.isclose(tw.lhcb1['y', 'ip2'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['y', 'ip2'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb1['py', 'ip2'], 100e-6, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['py', 'ip2'], -100e-6, atol=1e-9, rtol=0)

collider.vars['on_x2h'] = 120
tw = collider.twiss()
collider.vars['on_x2h'] = 0

assert np.isclose(tw.lhcb1['x', 'ip2'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['x', 'ip2'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb1['px', 'ip2'], 120e-6, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['px', 'ip2'], -120e-6, atol=1e-9, rtol=0)


collider.vars['on_x8h'] = 100
tw = collider.twiss()
collider.vars['on_x8h'] = 0

assert np.isclose(tw.lhcb1['x', 'ip8'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['x', 'ip8'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb1['px', 'ip8'], 100e-6, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['px', 'ip8'], -100e-6, atol=1e-9, rtol=0)

collider.vars['on_x8v'] = 120
tw = collider.twiss()
collider.vars['on_x8v'] = 0

assert np.isclose(tw.lhcb1['y', 'ip8'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['y', 'ip8'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb1['py', 'ip8'], 120e-6, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['py', 'ip8'], -120e-6, atol=1e-9, rtol=0)

collider.vars['on_sep2h'] = 1.6
tw = collider.twiss()
collider.vars['on_sep2h'] = 0

assert np.isclose(tw.lhcb1['x', 'ip2'], 1.6e-3, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['x', 'ip2'], -1.6e-3, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb1['px', 'ip2'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['px', 'ip2'], 0, atol=1e-9, rtol=0)

collider.vars['on_sep2v'] = 1.7
tw = collider.twiss()
collider.vars['on_sep2v'] = 0

assert np.isclose(tw.lhcb1['y', 'ip2'], 1.7e-3, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['y', 'ip2'], -1.7e-3, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb1['py', 'ip2'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['py', 'ip2'], 0, atol=1e-9, rtol=0)

collider.vars['on_sep8h'] = 1.5
tw = collider.twiss()
collider.vars['on_sep8h'] = 0

assert np.isclose(tw.lhcb1['x', 'ip8'], 1.5e-3, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['x', 'ip8'], -1.5e-3, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb1['px', 'ip8'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['px', 'ip8'], 0, atol=1e-9, rtol=0)

collider.vars['on_sep8v'] = 1.7
tw = collider.twiss()
collider.vars['on_sep8v'] = 0

assert np.isclose(tw.lhcb1['y', 'ip8'], 1.7e-3, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['y', 'ip8'], -1.7e-3, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb1['py', 'ip8'], 0, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['py', 'ip8'], 0, atol=1e-9, rtol=0)

# Both knobs together
collider.vars['on_x8h'] = 120
collider.vars['on_sep8h'] = 1.7
tw = collider.twiss()
collider.vars['on_x8h'] = 0
collider.vars['on_sep8h'] = 0

assert np.isclose(tw.lhcb1['x', 'ip8'], 1.7e-3, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['x', 'ip8'], -1.7e-3, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb1['px', 'ip8'], 120e-6, atol=1e-9, rtol=0)
assert np.isclose(tw.lhcb2['px', 'ip8'], -120e-6, atol=1e-9, rtol=0)
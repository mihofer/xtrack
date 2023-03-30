# copyright ############################### #
# This file is part of the Xtrack Package.  #
# Copyright (c) CERN, 2021.                 #
# ######################################### #

from time import perf_counter
from typing import Literal, Union
import logging
from functools import partial
from collections import UserDict, defaultdict

import numpy as np
import xobjects as xo
import xpart as xp

from .general import _print

from .base_element import _handle_per_particle_blocks
from .beam_elements import Drift
from .general import _pkg_root
from .internal_record import new_io_buffer
from .line import Line, _is_thick, freeze_longitudinal as _freeze_longitudinal
from .pipeline import PipelineStatus
from .tracker_data import TrackerData
from .prebuild_kernels import get_suitable_kernel, XT_PREBUILT_KERNELS_LOCATION

logger = logging.getLogger(__name__)


def _check_is_collective(ele):
    iscoll = not hasattr(ele, 'iscollective') or ele.iscollective
    return iscoll


class Tracker:

    '''
    Xsuite tracker class. It is the core of the xsuite package, allows tracking
    particles in a given beam line. Methods to match particle distributions
    and to compute twiss parameters are also available.
    '''

    def __init__(
        self,
        _context=None,
        _buffer=None,
        _offset=None,
        line=None,
        sequence=None,
        track_kernel=None,
        element_classes=None,
        particles_class=xp.Particles,
        skip_end_turn_actions=False,
        reset_s_at_end_turn=True,
        particles_monitor_class=None,
        global_xy_limit=1.0,
        extra_headers=(),
        local_particle_src=None,
        io_buffer=None,
        compile=True,
        use_prebuilt_kernels=True,
        enable_pipeline_hold=False,
        _element_ref_data=None,
    ):

        if sequence is not None:
            raise ValueError(
                    "`Tracker(... sequence=... ) is deprecated use `line=`)")

        # Check if there are collective elements
        self.iscollective = False
        for ee in line.elements:
            if _check_is_collective(ee):
                self.iscollective = True
                break

        if not particles_monitor_class:
            particles_monitor_class = self._get_default_monitor_class()

        if self.iscollective:
            if _element_ref_data:
                raise ValueError('The argument element_ref_data is not '
                                 'supported in collective mode.')

            self._init_track_with_collective(
                _context=_context,
                _buffer=_buffer,
                _offset=_offset,
                line=line,
                track_kernel=track_kernel,
                element_classes=element_classes,
                particles_class=particles_class,
                skip_end_turn_actions=skip_end_turn_actions,
                reset_s_at_end_turn=reset_s_at_end_turn,
                particles_monitor_class=particles_monitor_class,
                global_xy_limit=global_xy_limit,
                extra_headers=extra_headers,
                local_particle_src=local_particle_src,
                io_buffer=io_buffer,
                compile=compile,
                use_prebuilt_kernels=use_prebuilt_kernels,
                enable_pipeline_hold=enable_pipeline_hold)
        else:
            self._element_ref_data = _element_ref_data
            self._init_track_no_collective(
                _context=_context,
                _buffer=_buffer,
                _offset=_offset,
                line=line,
                track_kernel=track_kernel,
                element_classes=element_classes,
                particles_class=particles_class,
                skip_end_turn_actions=skip_end_turn_actions,
                reset_s_at_end_turn=reset_s_at_end_turn,
                particles_monitor_class=particles_monitor_class,
                global_xy_limit=global_xy_limit,
                extra_headers=extra_headers,
                local_particle_src=local_particle_src,
                io_buffer=io_buffer,
                compile=compile,
                use_prebuilt_kernels=use_prebuilt_kernels,
                enable_pipeline_hold=enable_pipeline_hold)

    def _init_track_with_collective(
        self,
        _context=None,
        _buffer=None,
        _offset=None,
        line=None,
        track_kernel=None,
        element_classes=None,
        particles_class=None,
        skip_end_turn_actions=False,
        reset_s_at_end_turn=True,
        particles_monitor_class=None,
        global_xy_limit=1.0,
        extra_headers=(),
        local_particle_src=None,
        io_buffer=None,
        compile=True,
        use_prebuilt_kernels=True,
        enable_pipeline_hold=False
    ):

        assert _offset is None

        if not compile:
            raise NotImplementedError("Skip compilation is not implemented in "
                                      "collective mode")

        self.line = line
        self.skip_end_turn_actions = skip_end_turn_actions
        self.particles_class = particles_class
        self.global_xy_limit = global_xy_limit
        self.extra_headers = extra_headers
        self.local_particle_src = local_particle_src
        self._enable_pipeline_hold = enable_pipeline_hold
        self.use_prebuilt_kernels = use_prebuilt_kernels

        if _buffer is None:
            if _context is None:
                _context = xo.context_default
            _buffer = _context.new_buffer()
        self._buffer = _buffer

        if io_buffer is None:
            io_buffer = new_io_buffer(_context=_buffer.context)
        self.io_buffer = io_buffer

        # Split the sequence
        parts = []
        part_names = []
        _element_part = []
        _element_index_in_part=[]
        _part_element_index = defaultdict(list)
        this_part = Line(elements=[], element_names=[])
        ii_in_part = 0
        i_part = 0
        idx = 0
        for nn, ee in zip(line.element_names, line.elements):
            if not _check_is_collective(ee):
                this_part.append_element(ee, nn)
                _element_part.append(i_part)
                _element_index_in_part.append(ii_in_part)
                ii_in_part += 1
                _part_element_index[i_part].append(idx)
            else:
                if len(this_part.elements) > 0:
                    parts.append(this_part)
                    part_names.append(f'part_{i_part}_non_collective')
                    i_part += 1
                parts.append(ee)
                part_names.append(nn)
                _element_part.append(i_part)
                _element_index_in_part.append(None)
                _part_element_index[i_part].append(idx)
                i_part += 1
                this_part = Line(elements=[], element_names=[])
                ii_in_part = 0
            idx += 1
        if len(this_part.elements) > 0:
            parts.append(this_part)
            part_names.append(f'part_{i_part}_non_collective')

        # Transform non collective elements into xtrack elements
        noncollective_xelements = []
        for ii, pp in enumerate(parts):
            if isinstance(pp, Line):
                noncollective_xelements += pp.elements
            else:
                if _is_thick(pp):
                    ldrift = pp.length
                else:
                    ldrift = 0.

                noncollective_xelements.append(
                    Drift(_buffer=_buffer, length=ldrift))

        # Build tracker for all non-collective elements
        # (with collective elements replaced by Drifts)
        supertracker = Tracker(_buffer=_buffer,
                line=Line(elements=noncollective_xelements,
                          element_names=line.element_names),
                track_kernel=track_kernel,
                element_classes=element_classes,
                particles_class=particles_class,
                particles_monitor_class=particles_monitor_class,
                global_xy_limit=global_xy_limit,
                extra_headers=extra_headers,
                reset_s_at_end_turn=reset_s_at_end_turn,
                local_particle_src=local_particle_src,
                io_buffer=self.io_buffer,
                use_prebuilt_kernels=use_prebuilt_kernels,
                )
        supertracker.config.update(self.config)

        # Build trackers for non-collective parts
        for ii, pp in enumerate(parts):
            if isinstance(pp, Line):
                ele_start = _part_element_index[ii][0]
                ele_stop = _part_element_index[ii][-1] + 1
                parts[ii] = TrackerPartNonCollective(
                    tracker=supertracker,
                    ele_start_in_tracker=ele_start,
                    ele_stop_in_tracker=ele_stop,
                )

        # Make a "marker" element to increase at_element
        self._zerodrift = Drift(_context=_buffer.context, length=0)

        assert len(line.element_names) == len(supertracker.line.element_names)
        assert len(line.element_names) == len(_element_index_in_part)
        assert len(line.element_names) == len(_element_part)
        assert _element_part[-1] == len(parts) - 1

        self.line = line
        self.num_elements = len(line.element_names)
        self._supertracker = supertracker
        self._parts = parts
        self._part_names = part_names
        self.track = self._track_with_collective
        self.particles_class = supertracker.particles_class
        self.particles_monitor_class = supertracker.particles_monitor_class
        self._element_part = _element_part
        self._element_index_in_part = _element_index_in_part

    def _init_track_no_collective(
        self,
        _context=None,
        _buffer=None,
        _offset=None,
        line=None,
        track_kernel=None,
        element_classes=None,
        particles_class=None,
        skip_end_turn_actions=False,
        reset_s_at_end_turn=True,
        particles_monitor_class=None,
        global_xy_limit=1.0,
        extra_headers=(),
        local_particle_src=None,
        io_buffer=None,
        compile=True,
        use_prebuilt_kernels=True,
        enable_pipeline_hold=False
    ):
        if track_kernel == 'skip':
            raise ValueError('Value `skip` for track kernel is deprecated for '
                             'non-collective trackers, as all (re)compilation '
                             'is done on demand.')

        if enable_pipeline_hold:
            raise ValueError("`enable_pipeline_hold` is not implemented in "
                             "non-collective mode")
        self._enable_pipeline_hold = False

        if particles_class is None:
            particles_class = xp.Particles

        if local_particle_src is None:
            local_particle_src = particles_class.gen_local_particle_api()

        self.global_xy_limit = global_xy_limit
        self.extra_headers = extra_headers

        tracker_data = TrackerData(
            line=line,
            element_classes=element_classes,
            extra_element_classes=(particles_monitor_class._XoStruct,),
            element_ref_data=self._element_ref_data,
            _context=_context,
            _buffer=_buffer,
            _offset=_offset)

        context = tracker_data._buffer.context

        if io_buffer is None:
            io_buffer = new_io_buffer(_context=context)
        self.io_buffer = io_buffer

        if track_kernel is None and element_classes is not None:
            raise ValueError('The kernel relies on `element_classes` ordering, '
                             'so `element_classes` must be given if '
                             '`track_kernel` is None.')

        if element_classes is None:
            if track_kernel is not None:
                raise ValueError(
                    'The kernel relies on `element_classes` ordering, so '
                    '`track_kernel` must be given if `element_classes` is None.'
                )
            element_classes = tracker_data.element_classes

        line._freeze()
        self.line = line
        self.line.tracker = self
        self._tracker_data = tracker_data
        self.num_elements = len(tracker_data.elements)
        self._buffer = tracker_data._buffer

        self.particles_class = particles_class
        self.particles_monitor_class = particles_monitor_class
        self.global_xy_limit = global_xy_limit
        self.extra_headers = extra_headers
        self.skip_end_turn_actions = skip_end_turn_actions
        self.reset_s_at_end_turn = reset_s_at_end_turn
        self.local_particle_src = local_particle_src
        self._element_classes = element_classes

        self._track_kernel = track_kernel or {}

        self.track = self._track_no_collective
        self.use_prebuilt_kernels = use_prebuilt_kernels

        if compile:
            _ = self._current_track_kernel  # This triggers compilation

    @property
    def track_kernel(self):
        if self.iscollective:
            return self._supertracker._track_kernel
        else:
            return self._track_kernel

    @property
    def element_classes(self):
        if self.iscollective:
            return self._supertracker.element_classes
        else:
            return self._element_classes

    @property
    def config(self):
        return self.line.config

    @property
    def matrix_responsiveness_tol(self):
        return self.line.matrix_responsiveness_tol

    @property
    def matrix_stability_tol(self):
        return self.line.matrix_stability_tol

    @property
    def _radiation_model(self):
        return self.line._radiation_model

    @property
    def _beamstrahlung_model(self):
        return self.line._beamstrahlung_model

    def _invalidate(self):
        if self.iscollective:
            self._invalidated_parts = self._parts
            self._parts = None
        else:
            self._invalidated_tracker_data = self._tracker_data
            self._tracker_data = None
        self._is_invalidated = True

    def _check_invalidated(self):
        if hasattr(self, '_is_invalidated') and self._is_invalidated:
            raise RuntimeError(
                "This tracker is not anymore valid, most probably because the corresponding line has been unfrozen. "
                "Please rebuild the tracker, for example using `line.build_tracker(...)`.")

    def get_backtracker(self, _context=None, _buffer=None,
                        global_xy_limit='from_tracker'):

        """
        Build a Tracker object that backtracks in the same line.
        """

        self._check_invalidated()

        assert not self.iscollective

        if _buffer is None:
            if _context is None:
                _context = self._buffer.context
            _buffer = _context.new_buffer()

        line = Line(elements=[], element_names=[])
        for nn, ee in zip(self.line.element_names[::-1],
                          self.line.elements[::-1]):
            line.append_element(
                    ee.get_backtrack_element(_buffer=_buffer), nn)

        if global_xy_limit == 'from_tracker':
            global_xy_limit = self.global_xy_limit
            track_kernel = self.track_kernel
            element_classes = self.element_classes
        else:
            track_kernel = None
            element_classes = None

        return self.__class__(
                    _buffer=_buffer,
                    line=line,
                    track_kernel=track_kernel,
                    element_classes=element_classes,
                    particles_class=self.particles_class,
                    skip_end_turn_actions=self.skip_end_turn_actions,
                    particles_monitor_class=self.particles_monitor_class,
                    global_xy_limit=global_xy_limit,
                    extra_headers=self.extra_headers,
                    local_particle_src=self.local_particle_src,
                )

    def track(self, *args, **kwargs):
        """
        This is a placeholder, it is replaced either by the collective
        tracker or the single particle tracker.
        """
        pass

    @property
    def particle_ref(self) -> xp.Particles:
        self._check_invalidated()
        return self.line.particle_ref

    @particle_ref.setter
    def particle_ref(self, value: xp.Particles):
        self.line.particle_ref = value

    @property
    def vars(self):
        self._check_invalidated()
        return self.line.vars

    @property
    def element_refs(self):
        self._check_invalidated()
        return self.line.element_refs

    @property
    def enable_pipeline_hold(self):
        return self._enable_pipeline_hold

    @enable_pipeline_hold.setter
    def enable_pipeline_hold(self, value):
        if not self.iscollective:
            raise ValueError(
                'enable_pipeline_hold is not supported non collective trackers')
        else:
            self._enable_pipeline_hold = value

    @property
    def _context(self):
        return self._buffer.context

    def _build_kernel(
            self,
            compile: Union[bool, Literal['force']],
            module_name=None,
            containing_dir='.',
    ):
        if (self.use_prebuilt_kernels and compile != 'force'
                and isinstance(self._context, xo.ContextCpu)):
            kernel_info = get_suitable_kernel(
                self.config, self.element_classes
            )
            if kernel_info:
                module_name, modules_classes = kernel_info
                kernel_description = self.get_kernel_descriptions()['track_line']
                kernels = self._context.kernels_from_file(
                    module_name=module_name,
                    containing_dir=XT_PREBUILT_KERNELS_LOCATION,
                    kernel_descriptions={'track_line': kernel_description},
                )
                self._context.kernels.update(kernels)
                classes = (self.particles_class._XoStruct,)
                self._current_track_kernel = self._context.kernels[('track_line', classes)]
                self._element_classes = [cls._XoStruct for cls in modules_classes]
                self._tracker_data = TrackerData(
                    line=self.line,
                    element_classes=self.element_classes,
                    _context=self._context,
                    _buffer=self._buffer,
                )
                return

        context = self._tracker_data._buffer.context

        headers = []

        headers.extend(self.extra_headers)

        if self.global_xy_limit is not None:
            headers.append(
                f"#define XTRACK_GLOBAL_POSLIMIT ({self.global_xy_limit})")
        headers.append(_pkg_root.joinpath("headers/constants.h"))

        src_lines = []
        src_lines.append(
            r"""
            /*gpukern*/
            void track_line(
                /*gpuglmem*/ int8_t* buffer,
                             ElementRefData elem_ref_data,
                             ParticlesData particles,
                             int num_turns,
                             int ele_start,
                             int num_ele_track,
                             int flag_end_turn_actions,
                             int flag_reset_s_at_end_turn,
                             int flag_monitor,
                /*gpuglmem*/ int8_t* buffer_tbt_monitor,
                             int64_t offset_tbt_monitor,
                /*gpuglmem*/ int8_t* io_buffer){


            LocalParticle lpart;
            lpart.io_buffer = io_buffer;

            int64_t part_id = 0;                    //only_for_context cpu_serial cpu_openmp
            int64_t part_id = blockDim.x * blockIdx.x + threadIdx.x; //only_for_context cuda
            int64_t part_id = get_global_id(0);                    //only_for_context opencl


            /*gpuglmem*/ int8_t* tbt_mon_pointer =
                            buffer_tbt_monitor + offset_tbt_monitor;
            ParticlesMonitorData tbt_monitor =
                            (ParticlesMonitorData) tbt_mon_pointer;

            int64_t part_capacity = ParticlesData_get__capacity(particles);
            if (part_id<part_capacity){
            Particles_to_LocalParticle(particles, &lpart, part_id);

            int64_t isactive = check_is_active(&lpart);

            for (int64_t iturn=0; iturn<num_turns; iturn++){

                if (!isactive){
                    break;
                }

                if (flag_monitor==1){
                    ParticlesMonitor_track_local_particle(tbt_monitor, &lpart);
                }

                int64_t elem_idx = ele_start;
                for (; elem_idx < ele_start+num_ele_track; elem_idx++){

                        #ifndef DISABLE_EBE_MONITOR
                        if (flag_monitor==2){
                            ParticlesMonitor_track_local_particle(tbt_monitor, &lpart);
                        }
                        #endif

                        // Get the pointer to and the type id of the `elem_idx`th
                        // element in `element_ref_data.elements`:
                        /*gpuglmem*/ void* el = ElementRefData_member_elements(elem_ref_data, elem_idx);
                        int64_t elem_type = ElementRefData_typeid_elements(elem_ref_data, elem_idx);

                        switch(elem_type){
        """
        )

        for ii, cc in enumerate(self.element_classes):
            ccnn = cc.__name__.replace("Data", "")
            src_lines.append(
                f"""
                        case {ii}:
"""
            )
            if ccnn == "Drift":
                src_lines.append(
                    """
                            #ifdef XTRACK_GLOBAL_POSLIMIT
                            global_aperture_check(&lpart);
                            #endif

                            """
                )
            src_lines.append(
                f"""
                            {ccnn}_track_local_particle(({ccnn}Data) el, &lpart);
                            break;"""
            )

        src_lines.append(
            """
                        } //switch

                    // Setting the below flag will break particle losses
                    #ifndef DANGER_SKIP_ACTIVE_CHECK_AND_SWAPS
                    isactive = check_is_active(&lpart);
                    if (!isactive){
                        break;
                    }
                    increment_at_element(&lpart);
                    #endif

                } // for elements
                if (flag_monitor==2){
                    // End of turn (element-by-element mode)
                    ParticlesMonitor_track_local_particle(tbt_monitor, &lpart);
                }
                if (flag_end_turn_actions>0){
                    if (isactive){
                        increment_at_turn(&lpart, flag_reset_s_at_end_turn);
                    }
                }
            } // for turns

            LocalParticle_to_Particles(&lpart, particles, part_id, 1);

            }// if partid
        }//kernel
        """
        )

        source_track = "\n".join(src_lines)

        kernels = self.get_kernel_descriptions(context)

        # Compile!
        if isinstance(self._context, xo.ContextCpu):
            kwargs = {
                'containing_dir': containing_dir,
                'module_name': module_name,
            }
        else:
            # Saving kernels is unsupported on GPU
            kwargs = {}

        out_kernels = context.build_kernels(
            sources=[source_track],
            kernel_descriptions=kernels,
            extra_headers=self._config_to_headers() + headers,
            extra_classes=self.element_classes,
            apply_to_source=[
                partial(_handle_per_particle_blocks,
                        local_particle_src=self.local_particle_src)],
            specialize=True,
            compile=compile,
            save_source_as=f'{module_name}.c' if module_name else None,
            **kwargs,
        )
        context.kernels.update(out_kernels)

        classes = (self.particles_class._XoStruct,)
        self._current_track_kernel = context.kernels[('track_line', classes)]

    def get_kernel_descriptions(self, _context=None):
        if not _context:
            _context = self._context

        kernel_descriptions = {
            "track_line": xo.Kernel(
                c_name='track_line',
                args=[
                    xo.Arg(xo.Int8, pointer=True, name="buffer"),
                    xo.Arg(self._tracker_data._element_ref_data.__class__, name="tracker_data"),
                    xo.Arg(self.particles_class._XoStruct, name="particles"),
                    xo.Arg(xo.Int32, name="num_turns"),
                    xo.Arg(xo.Int32, name="ele_start"),
                    xo.Arg(xo.Int32, name="num_ele_track"),
                    xo.Arg(xo.Int32, name="flag_end_turn_actions"),
                    xo.Arg(xo.Int32, name="flag_reset_s_at_end_turn"),
                    xo.Arg(xo.Int32, name="flag_monitor"),
                    xo.Arg(xo.Int8, pointer=True, name="buffer_tbt_monitor"),
                    xo.Arg(xo.Int64, name="offset_tbt_monitor"),
                    xo.Arg(xo.Int8, pointer=True, name="io_buffer"),
                ],
            )
        }

        # Random number generator init kernel
        kernel_descriptions.update(self.particles_class._kernels)

        return kernel_descriptions

    def _prepare_collective_track_session(self, particles, ele_start, ele_stop,
                                       num_elements, num_turns, turn_by_turn_monitor):

        # Start position
        if particles.start_tracking_at_element >= 0:
            if ele_start != 0:
                raise ValueError("The argument ele_start is used, but particles.start_tracking_at_element is set as well. "
                                 "Please use only one of those methods.")
            ele_start = particles.start_tracking_at_element
            particles.start_tracking_at_element = -1
        if isinstance(ele_start, str):
            ele_start = self.line.element_names.index(ele_start)

        # ele_start can only have values of existing element id's,
        # but also allowed: all elements+1 (to perform end-turn actions)
        assert ele_start >= 0
        assert ele_start < self.num_elements

        # Stop position
        if num_elements is not None:
            # We are using ele_start and num_elements
            if ele_stop is not None:
                raise ValueError("Cannot use both num_elements and ele_stop!")
            if num_turns is not None:
                raise ValueError("Cannot use both num_elements and num_turns!")
            num_turns, ele_stop = np.divmod(ele_start + num_elements, self.num_elements)
            if ele_stop == 0:
                ele_stop = None
            else:
                num_turns += 1
        else:
            # We are using ele_start, ele_stop, and num_turns
            if num_turns is None:
                num_turns = 1
            else:
                assert num_turns > 0
            if isinstance(ele_stop,str):
                ele_stop = self.line.element_names.index(ele_stop)

            # If ele_stop comes before ele_start, we need to add an additional turn to
            # reach the required ele_stop
            if ele_stop == 0:
                ele_stop = None

            if ele_stop is not None and ele_stop <= ele_start:
                num_turns += 1

        if ele_stop is not None:
            assert ele_stop >= 0
            assert ele_stop < self.num_elements

        assert num_turns >= 1

        assert turn_by_turn_monitor != 'ONE_TURN_EBE', (
            "Element-by-element monitor not available in collective mode")

        (flag_monitor, monitor, buffer_monitor, offset_monitor
            ) = self._get_monitor(particles, turn_by_turn_monitor, num_turns)

        if particles._num_active_particles < 0:
            _context_needs_clean_active_lost_state = True
        else:
            _context_needs_clean_active_lost_state = False

        if self.line._needs_rng and not particles._has_valid_rng_state():
            particles._init_random_number_generator()

        return (ele_start, ele_stop, num_turns, flag_monitor, monitor,
                buffer_monitor, offset_monitor,
                _context_needs_clean_active_lost_state)

    def _prepare_particles_for_part(self, particles, pp,
                                    moveback_to_buffer, moveback_to_offset,
                                    _context_needs_clean_active_lost_state):
        if hasattr(self, '_slice_sets'):
            # If pyheadtail object, remove any stored slice sets
            # (they are made invalid by the xtrack elements changing zeta)
            self._slice_sets = {}

        if (hasattr(pp, 'needs_cpu') and pp.needs_cpu):
            # Move to CPU if not already there
            if (moveback_to_buffer is None
                and not isinstance(particles._buffer.context, xo.ContextCpu)):
                moveback_to_buffer = particles._buffer
                moveback_to_offset = particles._offset
                particles.move(_context=xo.ContextCpu())
                particles.reorganize()
        else:
            # Move to GPU if not already there
            if moveback_to_buffer is not None:
                particles.move(_buffer=moveback_to_buffer, _offset=moveback_to_offset)
                moveback_to_buffer = None
                moveback_to_offset = None
                if _context_needs_clean_active_lost_state:
                    particles._num_active_particles = -1
                    particles._num_lost_particles = -1

        # Hide lost particles if required by element
        _need_unhide_lost_particles = False
        if (hasattr(pp, 'needs_hidden_lost_particles')
            and pp.needs_hidden_lost_particles):
            if not particles.lost_particles_are_hidden:
                _need_unhide_lost_particles = True
            particles.hide_lost_particles()

        return _need_unhide_lost_particles, moveback_to_buffer, moveback_to_offset

    def _track_part(self, particles, pp, tt, ipp, ele_start, ele_stop, num_turns):
        print(f'=> Tracking part {ipp} turn {tt} ({ele_start}, {ele_stop})')
        ret = None
        skip = False
        stop_tracking = False
        if tt == 0 and ipp < self._element_part[ele_start]:
            # Do not track before ele_start in the first turn
            skip = True

        elif tt == 0 and self._element_part[ele_start] == ipp:
            # We are in the part that contains the start element
            i_start_in_part = self._element_index_in_part[ele_start]
            if i_start_in_part is None:
                # The start part is collective
                ret = pp.track(particles)
            else:
                # The start part is a non-collective tracker
                if (ele_stop is not None
                    and tt == num_turns - 1 and self._element_part[ele_stop] == ipp):
                    # The stop element is also in this part, so track until ele_stop
                    i_stop_in_part = self._element_index_in_part[ele_stop]
                    ret = pp.track(particles, ele_start=i_start_in_part, ele_stop=i_stop_in_part)
                    stop_tracking = True
                else:
                    # Track until end of part
                    ret = pp.track(particles, ele_start=i_start_in_part)

        elif (ele_stop is not None
                and tt == num_turns-1 and self._element_part[ele_stop] == ipp):
            # We are in the part that contains the stop element
            i_stop_in_part = self._element_index_in_part[ele_stop]
            if i_stop_in_part is not None:
                # If not collective, track until ele_stop
                ret = pp.track(particles, num_elements=i_stop_in_part)
            stop_tracking = True

        else:
            # We are in between the part that contains the start element,
            # and the one that contains the stop element, so track normally
            ret = pp.track(particles)

        return stop_tracking, skip, ret

    def resume(self, session):
        """
        Resume a track session that had been placed on hold.
        """
        return self._track_with_collective(particles=None, _session_to_resume=session)



    def _track_with_collective(
        self,
        particles,
        ele_start=0,
        ele_stop=None,     # defaults to full lattice
        num_elements=None, # defaults to full lattice
        num_turns=None,    # defaults to 1
        turn_by_turn_monitor=None,
        freeze_longitudinal=False,
        time=False,
        _session_to_resume=None
    ):

        if time:
            t0 = perf_counter()

        if freeze_longitudinal:
            raise NotImplementedError('freeze_longitudinal not implemented yet'
                                      ' for collective tracking')

        self._check_invalidated()

        if (isinstance(self._buffer.context, xo.ContextCpu)
            and _session_to_resume is None):
            assert (particles._num_active_particles >= 0 and
                    particles._num_lost_particles >= 0), (
                        "Particles state is not valid to run on CPU, please "
                        "call `particles.reorganize()` first."
                    )

        if _session_to_resume is not None:
            if isinstance(_session_to_resume, PipelineStatus):
                _session_to_resume = _session_to_resume.data

            assert not(_session_to_resume['resumed']), (
                "This session hase been already resumed")

            assert _session_to_resume['tracker'] is self, (
                "This session was not created by this tracker")

            ele_start = _session_to_resume['ele_start']
            ele_stop = _session_to_resume['ele_stop']
            num_turns = _session_to_resume['num_turns']
            flag_monitor = _session_to_resume['flag_monitor']
            monitor = _session_to_resume['monitor']
            _context_needs_clean_active_lost_state = _session_to_resume[
                                    '_context_needs_clean_active_lost_state']
            tt_resume = _session_to_resume['tt']
            ipp_resume = _session_to_resume['ipp']
            _session_to_resume['resumed'] = True
        else:
            (ele_start, ele_stop, num_turns, flag_monitor, monitor,
                buffer_monitor, offset_monitor,
                _context_needs_clean_active_lost_state
                ) = self._prepare_collective_track_session(
                                particles, ele_start, ele_stop,
                                num_elements, num_turns, turn_by_turn_monitor)
            tt_resume = None
            ipp_resume = None

        for tt in range(num_turns):
            if tt_resume is not None and tt < tt_resume:
                continue

            if (flag_monitor and (ele_start == 0 or tt>0)): # second condition is for delayed start
                if not(tt_resume is not None and tt == tt_resume):
                    monitor.track(particles)

            moveback_to_buffer = None
            moveback_to_offset = None
            for ipp, pp in enumerate(self._parts):
                if (ipp_resume is not None and ipp < ipp_resume):
                    continue
                elif (ipp_resume is not None and ipp == ipp_resume):
                    assert particles is None
                    particles = _session_to_resume['particles']
                    pp = self._parts[ipp]
                    moveback_to_buffer = _session_to_resume['moveback_to_buffer']
                    moveback_to_offset = _session_to_resume['moveback_to_offset']
                    _context_needs_clean_active_lost_state = _session_to_resume[
                                    '_context_needs_clean_active_lost_state']
                    _need_unhide_lost_particles = _session_to_resume[
                                    '_need_unhide_lost_particles']
                    # Clear
                    tt_resume = None
                    ipp_resume = None
                else:
                    (_need_unhide_lost_particles, moveback_to_buffer,
                        moveback_to_offset) = self._prepare_particles_for_part(
                                            particles, pp,
                                            moveback_to_buffer, moveback_to_offset,
                                            _context_needs_clean_active_lost_state)

                # Track!
                stop_tracking, skip, returned_by_track = self._track_part(
                        particles, pp, tt, ipp, ele_start, ele_stop, num_turns)

                if returned_by_track is not None:
                    if returned_by_track.on_hold:

                        assert self.enable_pipeline_hold, (
                            "Hold session not enabled for this tracker.")

                        session_on_hold = {
                            'particles': particles,
                            'tracker': self,
                            'status_from_element': returned_by_track,
                            'ele_start': ele_start,
                            'ele_stop': ele_stop,
                            'num_elements': num_elements,
                            'num_turns': num_turns,
                            'flag_monitor': flag_monitor,
                            'monitor': monitor,
                            '_context_needs_clean_active_lost_state':
                                        _context_needs_clean_active_lost_state,
                            '_need_unhide_lost_particles':
                                        _need_unhide_lost_particles,
                            'moveback_to_buffer': moveback_to_buffer,
                            'moveback_to_offset': moveback_to_offset,
                            'ipp': ipp,
                            'tt': tt,
                            'resumed': False
                        }
                    return PipelineStatus(on_hold=True, data=session_on_hold)

                # Do nothing before ele_start in the first turn
                if skip:
                    continue

                # For collective parts increment at_element
                if not isinstance(pp, Tracker) and not stop_tracking:
                    if moveback_to_buffer is not None: # The particles object is temporarily on CPU
                        if not hasattr(self, '_zerodrift_cpu'):
                            self._zerodrift_cpu = self._zerodrift.copy(particles._buffer.context)
                        self._zerodrift_cpu.track(particles, increment_at_element=True)
                    else:
                        self._zerodrift.track(particles, increment_at_element=True)

                if _need_unhide_lost_particles:
                    particles.unhide_lost_particles()

                # Break from loop over parts if stop element reached
                if stop_tracking:
                    break

            ## Break from loop over turns if stop element reached
            if stop_tracking:
                break

            if moveback_to_buffer is not None:
                particles.move(
                        _buffer=moveback_to_buffer, _offset=moveback_to_offset)
                moveback_to_buffer = None
                moveback_to_offset = None
                if _context_needs_clean_active_lost_state:
                    particles._num_active_particles = -1
                    particles._num_lost_particles = -1

            # Increment at_turn and reset at_element
            # (use the supertracker to perform only end-turn actions)
            self._supertracker.track(particles,
                               ele_start=self._supertracker.num_elements,
                               num_elements=0)

        self.record_last_track = monitor

        if time:
            t1 = perf_counter()
            self._context.synchronize()
            self.time_last_track = t1 - t0
        else:
            self.time_last_track = None

    def _track_no_collective(
        self,
        particles,
        ele_start=0,
        ele_stop=None,     # defaults to full lattice
        num_elements=None, # defaults to full lattice
        num_turns=None,    # defaults to 1
        turn_by_turn_monitor=None,
        freeze_longitudinal=False,
        time=False,
        _force_no_end_turn_actions=False,
    ):
        # Add the Particles class to the config, so the kernel is recompiled
        # and stored if a new Particles class is given.
        if type(particles) != xp.Particles:
            self.config.particles_class_name = type(particles).__name__
        else:
            self.config.pop('particles_class_name', None)
        self.particles_class = particles.__class__
        self.local_particle_src = particles.gen_local_particle_api()

        if time:
            t0 = perf_counter()

        if freeze_longitudinal:
            kwargs = locals().copy()
            kwargs.pop('self')
            kwargs.pop('freeze_longitudinal')

            with _freeze_longitudinal(self.line):
                return self._track_no_collective(**kwargs)

        self._check_invalidated()

        if isinstance(self._buffer.context, xo.ContextCpu):
            assert (particles._num_active_particles >= 0 and
                    particles._num_lost_particles >= 0), (
                        "Particles state is not valid to run on CPU, please "
                        "call `particles.reorganize()` first."
                    )

        # Start position
        if particles.start_tracking_at_element >= 0:
            if ele_start != 0:
                raise ValueError("The argument ele_start is used, but particles.start_tracking_at_element is set as well. "
                                 "Please use only one of those methods.")
            ele_start = particles.start_tracking_at_element
            particles.start_tracking_at_element = -1
        if isinstance(ele_start, str):
            ele_start = self.line.element_names.index(ele_start)

        assert ele_start >= 0
        assert ele_start <= self.num_elements

        # Logic to split the tracking turns:
        # Case 1: 0 <= start < stop <= L
        #      Track first turn from start until stop (with num_elements_first_turn=stop-start)
        # Case 2: 0 <= start < L < stop < 2L
        #      Track first turn from start until L    (with num_elements_first_turn=L-start)
        #      Track last turn from 0 until stop      (with num_elements_last_turn=stop)
        # Case 3: 0 <= start < L < stop=nL
        #      Track first turn from start until L    (with num_elements_first_turn=L-start)
        #      Track middle turns from 0 until (n-1)L (with num_middle_turns=n-1)
        # Case 4: 0 <= start < L < nL < stop
        #      Track first turn from start until L    (with num_elements_first_turn=L-start)
        #      Track middle turns from 0 until (n-1)L (with num_middle_turns=n-1)
        #      Track last turn from 0 until stop      (with num_elements_last_turn=stop)

        num_middle_turns = 0
        num_elements_last_turn = 0

        if num_elements is not None:
            # We are using ele_start and num_elements
            assert num_elements >= 0
            if ele_stop is not None:
                raise ValueError("Cannot use both num_elements and ele_stop!")
            if num_turns is not None:
                raise ValueError("Cannot use both num_elements and num_turns!")
            if num_elements + ele_start <= self.num_elements:
                # Track only the first (potentially partial) turn
                num_elements_first_turn = num_elements
            else:
                # Track the first turn until the end of the lattice
                num_elements_first_turn = self.num_elements - ele_start
                # Middle turns and potential last turn
                num_middle_turns, ele_stop = np.divmod(ele_start + num_elements, self.num_elements)
                num_elements_last_turn = ele_stop
                num_middle_turns -= 1

        else:
            # We are using ele_start, ele_stop, and num_turns
            if num_turns is None:
                num_turns = 1
            else:
                assert num_turns > 0
            if ele_stop is None:
                # Track the first turn until the end of the lattice
                # (last turn is also a full cycle, so will be treated as a middle turn)
                num_elements_first_turn = self.num_elements - ele_start
                num_middle_turns = num_turns - 1
            else:
                if isinstance(ele_stop, str):
                    ele_stop = self.line.element_names.index(ele_stop)
                assert ele_stop >= 0
                assert ele_stop < self.num_elements
                if ele_stop <= ele_start:
                    # Correct for overflow:
                    num_turns += 1
                if num_turns == 1:
                    # Track only the first partial turn
                    num_elements_first_turn = ele_stop - ele_start
                else:
                    # Track the first turn until the end of the lattice
                    num_elements_first_turn = self.num_elements - ele_start
                    # Track the middle turns
                    num_middle_turns = num_turns - 2
                    # Track the last turn until ele_stop
                    num_elements_last_turn = ele_stop

        if self.skip_end_turn_actions or _force_no_end_turn_actions:
            flag_end_first_turn_actions = False
            flag_end_middle_turn_actions = False
        else:
            flag_end_first_turn_actions = (
                    num_elements_first_turn + ele_start == self.num_elements)
            flag_end_middle_turn_actions = True

        if num_elements_last_turn > 0:
            # One monitor record for the initial turn, num_middle_turns records for the middle turns,
            # and one for the last turn
            monitor_turns = num_middle_turns + 2
        else:
            # One monitor record for the initial turn, and num_middle_turns record for the middle turns
            monitor_turns = num_middle_turns + 1

        (flag_monitor, monitor, buffer_monitor, offset_monitor
            ) = self._get_monitor(particles, turn_by_turn_monitor, monitor_turns)

        if self.line._needs_rng and not particles._has_valid_rng_state():
            particles._init_random_number_generator()

        self._current_track_kernel.description.n_threads = particles._capacity

        # First turn
        self._current_track_kernel(
            buffer=self._tracker_data._buffer.buffer,
            tracker_data=self._tracker_data._element_ref_data,
            particles=particles._xobject,
            num_turns=1,
            ele_start=ele_start,
            num_ele_track=num_elements_first_turn,
            flag_end_turn_actions=flag_end_first_turn_actions,
            flag_reset_s_at_end_turn=self.reset_s_at_end_turn,
            flag_monitor=flag_monitor,
            buffer_tbt_monitor=buffer_monitor,
            offset_tbt_monitor=offset_monitor,
            io_buffer=self.io_buffer.buffer,
        )

        # Middle turns
        if num_middle_turns > 0:
            self._current_track_kernel(
                buffer=self._tracker_data._buffer.buffer,
                tracker_data=self._tracker_data._element_ref_data,
                particles=particles._xobject,
                num_turns=num_middle_turns,
                ele_start=0, # always full turn
                num_ele_track=self.num_elements, # always full turn
                flag_end_turn_actions=flag_end_middle_turn_actions,
                flag_reset_s_at_end_turn=self.reset_s_at_end_turn,
                flag_monitor=flag_monitor,
                buffer_tbt_monitor=buffer_monitor,
                offset_tbt_monitor=offset_monitor,
                io_buffer=self.io_buffer.buffer,
            )

        # Last turn, only if incomplete
        if num_elements_last_turn > 0:
            self._current_track_kernel(
                buffer=self._tracker_data._buffer.buffer,
                tracker_data=self._tracker_data._element_ref_data,
                particles=particles._xobject,
                num_turns=1,
                ele_start=0,
                num_ele_track=num_elements_last_turn,
                flag_end_turn_actions=False,
                flag_reset_s_at_end_turn=self.reset_s_at_end_turn,
                flag_monitor=flag_monitor,
                buffer_tbt_monitor=buffer_monitor,
                offset_tbt_monitor=offset_monitor,
                io_buffer=self.io_buffer.buffer,
            )

        self.record_last_track = monitor

        if time:
            self._context.synchronize()
            t1 = perf_counter()
            self.time_last_track = t1 - t0
        else:
            self.time_last_track = None

    @staticmethod
    def _get_default_monitor_class():
        import xtrack as xt  # I have to do it like this

        # to avoid circular import #TODO to be solved
        return xt.ParticlesMonitor

    def _get_monitor(self, particles, turn_by_turn_monitor, num_turns):

        if turn_by_turn_monitor is None or turn_by_turn_monitor is False:
            flag_monitor = 0
            monitor = None
            buffer_monitor = particles._buffer.buffer  # I just need a valid buffer
            offset_monitor = 0
        elif turn_by_turn_monitor is True:
            flag_monitor = 1
            # TODO Assumes at_turn starts from zero, to be generalized
            monitor = self.particles_monitor_class(
                _context=particles._buffer.context,
                start_at_turn=0,
                stop_at_turn=num_turns,
                particle_id_range=particles.get_active_particle_id_range()
            )
            buffer_monitor = monitor._buffer.buffer
            offset_monitor = monitor._offset
        elif turn_by_turn_monitor == 'ONE_TURN_EBE':
            (_, monitor, buffer_monitor, offset_monitor
                ) = self._get_monitor(particles, turn_by_turn_monitor=True,
                                      num_turns=len(self.line.elements)+1)
            monitor.ebe_mode = 1
            flag_monitor = 2
        elif isinstance(turn_by_turn_monitor, self.particles_monitor_class):
            flag_monitor = 1
            monitor = turn_by_turn_monitor
            buffer_monitor = monitor._buffer.buffer
            offset_monitor = monitor._offset
        else:
            raise ValueError('Please provide a valid monitor object')

        return flag_monitor, monitor, buffer_monitor, offset_monitor



    def to_binary_file(self, path):
        try:
            tracker_data = self._tracker_data
        except AttributeError:
            raise TypeError("Only non-collective trackers can be binary serialized.")

        # Serialise the tracker_data (line)
        if not isinstance(tracker_data._context, xo.ContextCpu):
            buffer = xo.ContextCpu().new_buffer(0)
        else:
            buffer = None

        buffer, header_offset = tracker_data.to_binary(buffer)

        # Serialise the knobs
        var_management = {}
        if tracker_data.line._var_management:
            var_management = tracker_data.line._var_management_to_dict()

        # Serialise the reference particle
        particle_ref = None
        if self.particle_ref:
            particle_ref = self.particle_ref.to_dict()

        with open(path, 'wb') as f:
            np.save(f, header_offset)
            np.save(f, buffer.buffer)
            np.save(f, var_management, allow_pickle=True)
            np.save(f, particle_ref, allow_pickle=True)

    @classmethod
    def from_binary_file(cls, path, particles_monitor_class=None, **kwargs) -> 'Tracker':
        if not particles_monitor_class:
            particles_monitor_class = cls._get_default_monitor_class()

        with open(path, 'rb') as f:
            header_offset = np.load(f)
            np_buffer = np.load(f)
            var_management_dict = np.load(f, allow_pickle=True).item()
            particle_ref = np.load(f, allow_pickle=True).item()

        xbuffer = xo.ContextCpu().new_buffer(np_buffer.nbytes)
        # make sure that if we carry on using the buffer we
        # don't overwrite things, by marking everything as used
        xbuffer.allocate(np_buffer.nbytes)
        xbuffer.buffer = np_buffer
        tracker_data = TrackerData.from_binary(
            xbuffer,
            header_offset,
            extra_element_classes=(particles_monitor_class,),
        )
        if var_management_dict:
            tracker_data.line._init_var_management(var_management_dict)

        tracker = Tracker(
            line=tracker_data.line,
            _element_ref_data=tracker_data._element_ref_data,
            **kwargs,
        )

        if particle_ref is not None:
            tracker.particle_ref = xp.Particles.from_dict(particle_ref)

        return tracker

    def _hashable_config(self):
        items = ((k, v) for k, v in self.config.items() if v is not False)
        return tuple(sorted(items))

    def _config_to_headers(self):
        headers = []
        for k, v in self.config.items():
            if not isinstance(v, bool):
                headers.append(f'#define {k} {v}')
            elif v is True:
                headers.append(f'#define {k}')
            else:
                headers.append(f'#undef {k}')
        return headers

    @property
    def _current_track_kernel(self):
        try:
            return self.track_kernel[self._hashable_config()]
        except KeyError:
            self._build_kernel(compile=True)
            return self._current_track_kernel

    @_current_track_kernel.setter
    def _current_track_kernel(self, value):
        self.track_kernel[self._hashable_config()] = value

    # def __getattr__(self, attr):
    #     # If not in self look in self.line (if not None)
    #     if self.line is not None and attr in object.__dir__(self.line):
    #         return getattr(self.line, attr)
    #     else:
    #         raise AttributeError(f'Tracker object has no attribute `{attr}`')

    # def __dir__(self):
    #     return list(set(object.__dir__(self) + dir(self.line)))


class TrackerConfig(UserDict):

    def __setitem__(self, idx, val):
        if val is False and idx in self:
            del(self[idx]) # We don't want to store flags that are False
        else:
            super(TrackerConfig, self).__setitem__(idx, val)

    def __setattr__(self, idx, val):
        if idx == 'data':
            object.__setattr__(self, idx, val)
        elif val is not False:
            self.data[idx] = val
        elif idx in self:
            del(self.data[idx])

    def update(self, other, **kwargs):
        super().update(other, **kwargs)
        keys_for_none_vals = [k for k, v in self.items() if v is False]
        for k in keys_for_none_vals:
            del self[k]


class TrackerPartNonCollective:
    def __init__(self, tracker, ele_start_in_tracker, ele_stop_in_tracker):
        self.tracker = tracker
        self.ele_start_in_tracker = ele_start_in_tracker
        self.ele_stop_in_tracker = ele_stop_in_tracker

    def track(self, particles, ele_start=None, ele_stop=None):
        if ele_start is None:
            temp_ele_start = self.ele_start_in_tracker
        else:
            temp_ele_start = self.ele_start_in_tracker + ele_start

        if ele_stop is None:
            temp_ele_stop = self.ele_stop_in_tracker
        else:
            temp_ele_stop = self.ele_start_in_tracker + ele_stop

        temp_num_elements = temp_ele_stop - temp_ele_start

        print(f'.track({temp_ele_start}, {temp_ele_stop})')
        self.tracker.track(particles, ele_start=temp_ele_start,
                           num_elements=temp_num_elements,
                           _force_no_end_turn_actions=True)

    def __repr__(self):
        return (f'TrackerPartNonCollective({self.ele_start_in_tracker}, '
                f'{self.ele_stop_in_tracker})')

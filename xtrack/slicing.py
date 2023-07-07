# copyright ############################### #
# This file is part of the Xtrack Package.  #
# Copyright (c) CERN, 2023.                 #
# ######################################### #

import abc
import re
from collections import defaultdict

from itertools import zip_longest
from typing import List, Tuple, Iterator

from .compounds import ThickCompound
from .general import _print

import xtrack as xt

APER_ELEMS_REGEX = re.compile(r'(.*)_aper(_(tilt|offset)_(entry|exit))?')


class ElementSlicingScheme(abc.ABC):
    def __init__(self, slicing_order: int):
        if slicing_order < 1:
            raise ValueError("A slicing scheme must have at least one slice.")

        self.slicing_order = slicing_order

    @abc.abstractmethod
    def element_weights(self) -> List[float]:
        """Define a list of weights of length `self.slicing_order`, containing
         the weight of each element slice.
        """
        pass

    @abc.abstractmethod
    def drift_weights(self) -> List[float]:
        """Define a list of weights of length `self.slicing_order + 1`,
        containing the weight of each drift slice.
        """
        pass

    def __iter__(self) -> Iterator[Tuple[float, bool]]:
        """
        Give an iterator for weights of slices and, assuming the first slice is
        a drift, followed by an element slice, and so on.
        Returns
        -------
        Iterator[Tuple[float, bool]]
            Iterator of weights and whether the weight is for a drift.
        """
        for drift_weight, elem_weight in zip_longest(
                self.drift_weights(),
                self.element_weights(),
                fillvalue=None,
        ):
            yield drift_weight, True

            if elem_weight is None:
                break

            yield elem_weight, False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.slicing_order})"


class Uniform(ElementSlicingScheme):
    def element_weights(self):
        return [1. / self.slicing_order] * self.slicing_order

    def drift_weights(self):
        slices = self.slicing_order + 1
        return [1. / slices] * slices


class Teapot(ElementSlicingScheme):
    def element_weights(self):
        return [1. / self.slicing_order] * self.slicing_order

    def drift_weights(self):
        if self.slicing_order == 1:
            return [0.5, 0.5]

        edge_weight = 1. / (2 * (1 + self.slicing_order))
        middle_weight = self.slicing_order / (self.slicing_order ** 2 - 1)
        middle_weights = [middle_weight] * (self.slicing_order - 1)

        return [edge_weight, *middle_weights, edge_weight]


class Strategy:
    def __init__(self, slicing, name=None, element_type=None):
        if name is not None and isinstance(name, str):
            self.name_regex = re.compile(name)
        else:
            self.name_regex = None

        self.element_type = element_type
        self.slicing = slicing

    def _match_on_name(self, name):
        if self.name_regex is None:
            return True
        return self.name_regex.match(name)

    def _match_on_type(self, element):
        if self.element_type is None:
            return True
        return isinstance(element, self.element_type)

    def match_element(self, name, element):
        return self._match_on_name(name) and self._match_on_type(element)

    def __repr__(self):
        params = {
            'slicing': self.slicing,
            'element_type': self.element_type,
            'name': self.name_regex.pattern if self.name_regex else None,
        }
        formatted_params = ', '.join(
            f'{kk}={vv!r}' for kk, vv in params.items() if vv is not None
        )
        return f"{type(self).__name__}({formatted_params})"


class Slicer:
    def __init__(self, line, slicing_strategies: List[Strategy]):
        """
        An object that slices a line in place according to a list of slicing
        strategies.

        Parameters
        ----------
        line : Line
            The line to slice.
        slicing_strategies : List[Strategy]
            A list of slicing strategies to apply to the line.
        """
        self.line = line
        # self.compound_container = line.compound_container.copy()
        self.slicing_strategies = slicing_strategies
        self.has_expresions = line.vars is not None

    def slice_in_place(self):
        thin_names = []

        collapsed_names = self.line.get_collapsed_names()
        n_elements = len(collapsed_names)
        for ii, name in enumerate(collapsed_names):
            _print(f'Slicing line: {100*(ii + 1)/n_elements:.0f}%', end='\r', flush=True)

            compound = self.line.get_compound_by_name(name)
            if compound is not None:
                thin_names += self._slice_compound(name, compound)
            else:
                element = self.line.element_dict[name]
                thin_names += self._slice_element(name, element)

        # Commit the changes to the line
        self.line.compound_container = None
        self.line.element_names = thin_names

    def _slice_compound(self, name, compound):
        sliced_core = []
        for name in compound.core:
            element = self.line.element_dict[name]
            sliced_core += self._slice_element(name, element)

        updated_core = []
        slice_idx = 0
        for slice_name in sliced_core:
            element = self.line.element_dict[slice_name]
            if isinstance(element, xt.Drift):
                updated_core.append(slice_name)
                continue

            # Copy the apertures and transformations with a new name
            updated_core += (
                self._make_copies(compound.aperture, slice_idx) +
                self._make_copies(compound.entry_transform, slice_idx) +
                [slice_name] +
                self._make_copies(compound.exit_transform, slice_idx)
            )
            slice_idx += 1

        return compound.entry_other + updated_core + compound.exit_other

    def _slice_element(self, name, element, wrap_slice=None):
        # Don't slice already thin elements and drifts
        if not element.isthick or isinstance(element, xt.Drift):
            return [name]

        # Choose a slicing strategy for the element
        slicing_found = False
        chosen_slicing = None
        for strategy in reversed(self.slicing_strategies):
            if strategy.match_element(name, element):
                slicing_found = True
                chosen_slicing = strategy.slicing
                break

        if not slicing_found:
            raise ValueError(f'No slicing strategy found for the element '
                             f'{name}: {element}.')

        # If the chosen slicing is explicitly None, then we keep the current
        # thick element and don't add any slices.
        if chosen_slicing is None:
            return [name]

        # Make the slices and add them to line.element_dict (so far inactive)
        slices_to_add = self._make_slices(
            element=element,
            chosen_slicing=chosen_slicing,
            name=name,
            wrap_slice=wrap_slice,
        )

        # Remove the thick element and its expressions
        if self.has_expresions:
            type(element).delete_element_ref(self.line.element_refs[name])
        # self.line.element_dict[name] = xt.Marker()
        del self.line.element_dict[name]

        return slices_to_add

    def _make_slices(self, element, chosen_slicing, name, wrap_slice=None):
        """
        Add the slices to the line.element_dict. If the element has expressions
        then the expressions will be added to the slices.

        Parameters
        ----------
        element : BeamElement
            A thick element to slice.
        chosen_slicing : ElementSlicingScheme
            The slicing scheme to use for the element.
        name : str
            The name of the element.
        wrap_slice : Optional[callable]
            A function that takes a slice and returns a list of slices. This
            can be used to add transformations and apertures. If None, then
            it will default to lambda x: [x].

        Returns
        -------
        list
            A list of the names of the slices that were added.
        """
        drift_idx, element_idx = 0, 0
        drift_to_slice = xt.Drift(length=element.length)
        slices_to_append = []

        for weight, is_drift in chosen_slicing:
            if is_drift:
                slice_name = f'drift_{name}..{drift_idx}'
                obj_to_slice = drift_to_slice
                drift_idx += 1
            else:
                slice_name = f'{name}..{element_idx}'
                obj_to_slice = element
                element_idx += 1

            if self.has_expresions:
                container = self.line.element_refs
            else:
                container = self.line.element_dict

            type(obj_to_slice).add_slice(
                weight=weight,
                container=container,
                thick_name=name,
                slice_name=slice_name,
                _buffer=self.line.element_dict[name]._buffer,
            )

            if wrap_slice is not None:
                slices_to_append += wrap_slice(slice_name)
            else:
                slices_to_append.append(slice_name)

        return slices_to_append

    def _make_copies(self, element_names, index):
        new_names = []
        for element_name in element_names:
            element = self.line.element_dict[element_name]
            new_element_name = f'{element_name}..{index}'
            self.line.element_dict[new_element_name] = element.copy()
            new_names.append(new_element_name)

        return new_names

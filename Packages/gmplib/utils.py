"""
---------------------------------------------------------------------

Utilities

---------------------------------------------------------------------

Requires Python packages/modules:
  -  :mod:`numpy`
  -  :mod:`sympy`

---------------------------------------------------------------------

"""
# Allow failed import of dolfin-adjoint if not using FEniCS
# pylint: disable=import-error, import-outside-toplevel

# Library
import warnings
import logging
import os
# from os import listdir
from os.path import realpath, join
from json import dumps
# from functools import reduce
from copy import deepcopy
from typing import Dict, Tuple, Any, Union, List, Optional

# Abstract classes & methods
from abc import ABC  # , abstractmethod

# NumPy
import numpy as np

# SymPy
from sympy import Eq, N, Mul, Matrix
from sympy.physics.units import Quantity, convert_to
from sympy.physics.units.systems import SI

warnings.filterwarnings("ignore")

__all__ = ['Results',
           'numify',
           'get_pkg_path',
           'is_jsonable',
           'export_results',
           'e2d',
           'dict2mat',
           'omitdict',
           'gmround',
           'convert']


def numify(str): return float(str.replace('p', '.'))


class Results(ABC):
    """
    Template for results container class
    """

    def __init__(self) -> None:
        """
        Constructor method
        """


def get_pkg_path(pkg: Any, subpkg: str = '') -> str:
    """
    Find the file path to a given package folder.
    If 'subpkg' is given, return the sub-package path.

    Args:
        pkg:
            Python package
        subpkg:
            subpackage name

    Returns:
        str: Path to (sub)package
    """
    return realpath(join(pkg.__path__[0], '..', '..', subpkg))


def is_jsonable(item: Any) -> bool:
    """
    Check whether an item can be written into a JSON file.
    If not, perhaps because the item is a numpy array etc,
    return false.

    Args:
        item: Python object

    Returns:
        bool: Whether object is JSONable or not
    """
    try:
        dumps(item)
        return True
    except Exception:
        return False


def export_results(
    results_to_export: Dict,
    results_dir: os.PathLike,
    suffix: str = '',
    do_parse: bool = True,
    max_nparray_size: Optional[int] = None,
    var_types: List[Any] = [float],
    # [float, adj.AdjFloat]
) -> None:
    """
    Write results dictionary of dictonaries as a hierarchical JSON file.

    This version can handle Dolfin/FEniCS data, but such capability should
    really be delegated to more specialized code.

    Args:
        results_to_export:
            results dictionary (of dictionaries)
        results_dir:
            path to results directory
        suffix:
            to append to file
        do_parse:
            convert from e.g. numpy array into JSONable list?
        max_nparray_size:
            limit the size of parseable np arrays
    """
    if do_parse:
        export = Results()
        for attribute, attribute_value in results_to_export.items():
            attribute_value_copy = deepcopy(attribute_value)
            # unjsonable_sub_attributes = {}
            for sub_attribute in attribute_value.__dict__:
                sub_attribute_value \
                    = getattr(attribute_value_copy, sub_attribute)
                # var_types = [float] \
                #     if not do_dolfin_adjoint \
                #     else [float, adj.AdjFloat]
                matching_subattrs = [isinstance(sub_attribute_value, var_type)
                                     for var_type in var_types]
                if any(matching_subattrs):
                    setattr(attribute_value_copy,
                            sub_attribute,
                            float(sub_attribute_value))
                elif isinstance(sub_attribute_value, np.ndarray) \
                        and (max_nparray_size is None
                             or sub_attribute_value.size <= max_nparray_size):
                    setattr(attribute_value_copy,
                            sub_attribute,
                            [list(array) for array in sub_attribute_value])
            setattr(export, attribute, attribute_value_copy)

        export_dict = {}
        for attribute in export.__dict__:
            attribute_value_dict = getattr(export, attribute).__dict__
            export_dict.update({attribute: attribute_value_dict})
    else:
        export_dict = results_to_export

    try:
        json_str = dumps(export_dict, sort_keys=False, indent=4)
    except Exception:
        print('Failed to serialize results into JSON format')
    json_filename = f'results{suffix}.json'
    json_path = realpath(join(results_dir, json_filename))
    with open(json_path, 'w', encoding='latin-1') as json_file:
        print(f'Writing to "{json_path}"')
        try:
            json_file.write(json_str)
        except Exception:
            print('Failed to write analysis results JSON file')


def e2d(
    eqn_or_eqns: Union[Eq, Tuple[Eq], List[Eq]],
    do_flip: bool = False,
    do_negate: bool = False
) -> Dict[Any, Any]:
    """
    Convert a SymPy equation (or list of equations) into a dictionary item
    by mapping the LHS into a key and the RHS into a value.

    Args:
        eqn_or_eqns:
            equation or equations to be converted
        do_flip:
            reverse LHS-RHS?
        do_negate:
            negate both sides?

    Returns:
        dict: key=LHS of eqn, value=RHS of eqn
    """
    def negate_eqn(eqn_):
        return Eq(-eqn_.lhs, - eqn_.rhs) if do_negate \
            else eqn_

    def flip_eqn(eqn_):
        return Eq(eqn_.rhs, eqn_.lhs) if do_flip \
            else eqn_

    def make_dict(eqn_):
        return dict([(flip_eqn(negate_eqn(eqn_))).args])

    eqns = eqn_or_eqns \
        if isinstance(eqn_or_eqns, (list, tuple)) \
        else [eqn_or_eqns]
    eqn_dict: Dict[Any, Any] = {}
    for eqn in eqns:
        eqn_dict.update(make_dict(eqn))
    return eqn_dict


def dict2mat(dict_: Dict) -> Matrix:
    """
    Convert a dictionary into a SymPy matrix

    Args:
        dict_: dictionary

    Returns:
        :class:`sympy.Matrix <sympy.matrices.immutable.ImmutableDenseMatrix>`:
            SymPy matrix
    """
    return Matrix(list(dict_.items()))


def omitdict(dict_: Dict[Any, Any], omitlist: List) -> Dict[Any, Any]:
    """
    Strip a dictionary of a list of keys.
    Used to remove items for a substitution dict if their values
    need to remain symbolic.
    """
    rtn_dict_: Dict[Any, Any] = dict_.copy()
    for k in list(omitlist):
        try:
            del rtn_dict_[k]
        except KeyError:
            logging.debug(f'{k} not found: skipping')
    return rtn_dict_


def gmround(eqn: Eq, n: int = 0, sf: float = 1) -> Eq:
    """
    Round numerical RHS of SymPy equation, converting to integer if
    zero decimal places requested.

    Args:
        eqn:
            SymPy equation
        n:
            number of decimal places
        sf:
            scale factor

    Returns:
        :class:`sympy.Eq <sympy.core.relational.Equality>`: SymPy equation
    """
    approx_rhs: float\
        = np.round(float(N(eqn.rhs)*sf), n) if n is not None else N(eqn.rhs)*sf
    return Eq(eqn.lhs, approx_rhs if n is None or n > 0 else int(approx_rhs))


def convert(
    eqn: Eq,
    units: Quantity,
    n: int = 0,
    do_raw: bool = False
) -> Eq:
    """
    Add units to a SymPy equation whose RHS is a dimensioned value.
    Also round as required.

    Args:
        eqn:
            SymPy equation
        n:
            number of decimal places
        sf:
            scale factor

    Returns:
        :class:`sympy.Eq <sympy.core.relational.Equality>`: SymPy equation
    """
    _ = Quantity('unknown_units')
    SI.set_quantity_dimension(_, SI.get_quantity_dimension(eqn.lhs))
    cf = convert_to(_, units).n()
    return Eq(eqn.lhs,
              np.round(float(N(cf.args[0]*eqn.rhs)), n)*Mul(*cf.args[1:])) \
        if do_raw is not True \
        else Eq(eqn.lhs, np.round(float(N(eqn.rhs)), n)*N(cf))

#

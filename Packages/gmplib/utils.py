"""
---------------------------------------------------------------------

Utility functions.

---------------------------------------------------------------------

Requires Python packages/modules:
  -  :mod:`numpy`
  -  :mod:`IPython.display`
  -  :mod:`PIL`
  -  :mod:`PyPDF2`
  -  :mod:`sympy`

---------------------------------------------------------------------

"""
# Allow failed import of dolfin-adjoint if not using FEniCS
# pylint: disable=import-error, import-outside-toplevel
import warnings
import logging

# Library modules
import os
# from os import listdir
from os.path import realpath, join
from json import dumps
# from functools import reduce
from copy import deepcopy

# Typing
from typing import Dict, Tuple, Any, Union, List #, Optional

# Abstract classes & methods
from abc import ABC #, abstractmethod

# Numpy
import numpy as np

# SymPy
from sympy import Eq, N, Mul, Matrix
from sympy.physics.units import Quantity, convert_to
from sympy.physics.units.systems import SI

warnings.filterwarnings("ignore")

__all__ = ['numify', 'get_pkg_path', 'is_jsonable', 'export_results', 'Results', 'e2d',
           'dict2mat', 'omitdict', 'gmround', 'convert']

numify = lambda str: float(str.replace('p','.'))

def get_pkg_path(pkg: Any, dirname: str='') -> str:
    """
    TBD
    """
    return realpath(join(pkg.__path__[0],'..','..',dirname))

def is_jsonable(item: Any) -> bool:
    """
    TBD
    """
    try:
        dumps(item)
        return True
    except Exception:
        return False

def export_results(results_to_export: Dict,
                   results_dir: os.PathLike, suffix: str='',
                   do_parse: bool=True,
                   max_nparray_size: int=None,
                   do_dolfin_adjoint: bool=False) -> None:
    """
    TBD
    """
    if do_dolfin_adjoint:
        try:
            import dolfin_adjoint as adj
        except Exception:
            print(Exception)
            raise
    if do_parse:
        export = Results()
        for attribute, attribute_value in results_to_export.items():
            attribute_value_copy = deepcopy(attribute_value)
            # unjsonable_sub_attributes = {}
            for sub_attribute in attribute_value.__dict__:
                sub_attribute_value = getattr(attribute_value_copy,sub_attribute)
                var_types = [float] if not do_dolfin_adjoint else [float, adj.AdjFloat]
                matching_subattrs = [isinstance(sub_attribute_value, var_type)
                         for var_type in var_types]
                if any(matching_subattrs):
                    setattr(attribute_value_copy, sub_attribute,
                            float(sub_attribute_value))
                elif isinstance(sub_attribute_value, np.ndarray) \
                        and (max_nparray_size is None \
                        or sub_attribute_value.size<=max_nparray_size):
                    setattr(attribute_value_copy, sub_attribute,
                            [list(array) for array in sub_attribute_value])
            setattr(export, attribute, attribute_value_copy)

        export_dict = {}
        for attribute in export.__dict__:
            attribute_value_dict = getattr(export,attribute).__dict__
            export_dict.update({attribute : attribute_value_dict})
    else:
        export_dict = results_to_export

    try:
        json_str = dumps(export_dict, sort_keys=False, indent=4)
    except Exception:
        print('Failed to serialize results into JSON format')
    json_filename = f'results{suffix}.json'
    json_path = realpath(join(results_dir,json_filename))
    with open(json_path, 'w', encoding='latin-1') as json_file:
        print(f'Writing to "{json_path}"')
        try:
            json_file.write(json_str)
        except Exception:
            print('Failed to write analysis results JSON file')

class Results(ABC):
    """
    TBD
    """
    def __init__(self) -> None:
        """
        TBD
        """

def e2d(eqn_or_eqns: Union[Any,Tuple[Any],List[Any]],
        do_flip: bool=False, do_negate: bool=False) -> Dict[Any,Any]:
    """
    TBD
    """
    negate_eqn = lambda eqn_: Eq(-eqn_.lhs,-eqn_.rhs) if do_negate else eqn_
    flip_eqn = lambda eqn_: Eq(eqn_.rhs,eqn_.lhs) if do_flip else eqn_
    make_dict = lambda eqn_: dict([ (flip_eqn(negate_eqn(eqn_))).args ])
    eqns = eqn_or_eqns if isinstance(eqn_or_eqns,(list,tuple)) \
        else [eqn_or_eqns]
    eqn_dict: Dict[Any,Any] = {}
    for eqn in eqns:
        eqn_dict.update(make_dict(eqn))
    return eqn_dict

def dict2mat(dict_: Dict) -> Matrix:
    """
    TBD
    """
    return Matrix(list(dict_.items()))

def omitdict(dict_: Dict[Any,Any], omitlist: List) -> Dict[Any,Any]:
    """
    TBD
    """
    rtn_dict_: Dict[Any,Any] = dict_.copy()
    for k in list(omitlist):
        try:
            del rtn_dict_[k]
        except KeyError:
            logging.debug(f'{k} not found: skipping')
    return rtn_dict_

def gmround(eqn: Eq, n: int=0, sf: float=1) -> Eq:
    """
    Round numerical RHS of Sympy equation, converting to integer if zero decimal places requested.

    Args:
        eqn (:class:`sympy.Eq <sympy.core.relational.Equality>`): Sympy equation object
        n (int): number of decimal places
        sf (float): scale factor

    Returns:
        eqn (:class:`sympy.Eq <sympy.core.relational.Equality>`): Sympy equation object
    """
    approx_rhs: float\
        = np.round(float(N(eqn.rhs)*sf),n) if n is not None else N(eqn.rhs)*sf
    return Eq(eqn.lhs, approx_rhs if n is None or n>0 else int(approx_rhs))

def convert(eqn: Eq, units: Quantity, n: int=0, do_raw: bool=False) -> Eq:
    """
    XXX

    Args:
        eqn (:class:`sympy.Eq <sympy.core.relational.Equality>`): Sympy equation object
        n (int): number of decimal places
        sf (float): scale factor

    Returns:
        eqn (:class:`sympy.Eq <sympy.core.relational.Equality>`): Sympy equation object
    """
    _ = Quantity('unknown_units')
    SI.set_quantity_dimension(_, SI.get_quantity_dimension(eqn.lhs))
    cf = convert_to(_, units).n()
    return Eq(eqn.lhs, np.round(float(N(cf.args[0]*eqn.rhs)), n)*Mul(*cf.args[1:])) \
                if do_raw is not True \
      else Eq(eqn.lhs, np.round(float(N(eqn.rhs)), n)*N(cf))

#

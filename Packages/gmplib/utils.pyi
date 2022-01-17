import os
from sympy import Eq, Matrix
from sympy.physics.units import Quantity
from typing import Any, Dict, List, Optional, Tuple, Union

def numify(str_): ...

class ResultsContainer:
    def __init__(self) -> None: ...

def get_pkg_path(pkg: Any, subpkg: str = ...) -> str: ...
def is_jsonable(item: Any) -> bool: ...
def export_results(results_to_export: Dict, results_dir: os.PathLike, suffix: str = ..., do_parse: bool = ..., max_nparray_size: Optional[int] = ..., var_types: List[Any] = ...) -> None: ...
def e2d(eqn_or_eqns: Union[Eq, Tuple[Eq], List[Eq]], do_flip: bool = ..., do_negate: bool = ...) -> Dict[Any, Any]: ...
def dict2mat(dict_: Dict) -> Matrix: ...
def omitdict(dict_: Dict[Any, Any], omitlist: List) -> Dict[Any, Any]: ...
def gmround(eqn: Eq, n: int = ..., sf: float = ...) -> Eq: ...
def convert(eqn: Eq, units: Quantity, n: int = ..., do_raw: bool = ...) -> Eq: ...

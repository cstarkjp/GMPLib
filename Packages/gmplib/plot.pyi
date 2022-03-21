import matplotlib.pyplot as plt
from itertools import cycle
from typing import Callable, Dict, List, Optional, Tuple

class GraphingBase:
    dpi: int
    font_size: int
    fdict: Dict
    colors: Callable
    n_colors: int
    color_cycle: Callable
    markers: Tuple
    n_markers: int
    marker_cycle: cycle
    linestyle_list: Tuple
    color: Callable
    marker: Callable
    font_family: str
    def __init__(self, dpi: int = ..., font_size: int = ...): ...
    def get_fonts(self) -> List[str]: ...
    def create_figure(
        self,
        fig_name: str,
        fig_size: Optional[Tuple[float, float]] = ...,
        dpi: Optional[int] = ...,
    ) -> plt.Figure: ...
    def get_aspect(self, axes: plt.Axes) -> float: ...
    def naturalize(self, fig: plt.Figure) -> None: ...
    def stretch(
        self,
        fig: plt.Figure,
        xs: Optional[Tuple[float, float]] = ...,
        ys: Optional[Tuple[float, float]] = ...,
    ) -> None: ...

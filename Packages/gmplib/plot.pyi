import matplotlib.pyplot as plt
from typing import Any, List, Optional, Tuple

class GraphingBase:
    dpi: Any
    font_size: Any
    fdict: Any
    colors: Any
    n_colors: Any
    color_cycle: Any
    markers: Any
    n_markers: Any
    marker_cycle: Any
    linestyle_list: Any
    color: Any
    marker: Any
    font_family: Any
    def __init__(self, dpi: int = ..., font_size: int = ...): ...
    def get_fonts(self) -> List[str]: ...
    def create_figure(self, fig_name: str, fig_size: Optional[Tuple[float, float]] = ..., dpi: Optional[int] = ...) -> plt.Figure: ...
    def get_aspect(self, axes: plt.Axes) -> float: ...
    def naturalize(self, fig: plt.Figure) -> None: ...
    def stretch(self, fig: plt.Figure, xs: Optional[Tuple[float, float]] = ..., ys: Optional[Tuple[float, float]] = ...) -> None: ...

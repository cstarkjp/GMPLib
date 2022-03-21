"""
Provide a data visualization class.

---------------------------------------------------------------------

Requires Python packages/modules:
  -  :mod:`matplotlib`

---------------------------------------------------------------------
"""
# Library
import warnings
import logging
from itertools import cycle
import operator as op
from typing import Dict, Any, Tuple, Optional, List, Callable, Iterable, Sized

# MatPlotLib
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager

warnings.filterwarnings("ignore")

__all__ = ["GraphingBase"]


class GraphingBase:
    """
    Provide a visualization base class.

    Args:
        dpi:
            resolution for rasterized images
        font_size:
            general font size

    Attributes:
        dpi (int):
            resolution for rasterized images
        font_size (int):
            general font size
        fdict  (dict):
            dictionary to which each figure is appended as it is generated
        colors  (list):
            list of colors
        n_colors  (int):
            number of colors
        color_cycle  (:obj:`itertools cycle <itertools.cycle>`):
            color property cycle
        markers  (list):
            list of markers
        n_markers  (:obj:`itertools cycle <itertools.cycle>`):
            number of markers
        marker_cycle  (int):
            cycle of markers
        linestyle_list  (list):
            list of line styles (solid, dashdot, dashed, custom dashed)
        color (:obj:`lambda(i) <lambda>`):
            return i^th color
        marker (:obj:`lambda(i) <lambda>`):
            return i^th marker
    """

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

    def __init__(self, dpi: int = 100, font_size: int = 11) -> None:
        """Initialize."""
        self.dpi = dpi
        self.font_size = font_size
        self.fdict: Dict[Any, Any] = {}
        prop_cycle = plt.rcParams["axes.prop_cycle"]
        self.colors = prop_cycle.by_key()["color"]  # type: ignore
        self.n_colors = len(self.colors)  # type: ignore
        self.color_cycle = cycle(self.colors)  # type: ignore
        self.markers = ("o", "s", "v", "p", "*", "D", "X", "^", "h", "P")
        self.n_markers = len(self.markers)
        self.marker_cycle = cycle(self.markers)
        self.linestyle_list = ("solid", "dashdot", "dashed", (0, (3, 1, 1, 1)))

        color_ = lambda i_: self.colors[i_ % self.n_colors]  # type: ignore
        marker_ = lambda i_: self.markers[i_ % self.n_markers]  # type: ignore
        self.color = color_  # type: ignore
        self.marker = marker_  # type: ignore
        self.font_family = "Arial" if "Arial" in self.get_fonts() else ""
        mpl.rc("font", size=self.font_size, family=self.font_family)

    def get_fonts(self) -> List[str]:
        """Fetch the names of all the font families available on the system."""
        fpaths = matplotlib.font_manager.findSystemFonts()
        fonts: List[str] = []
        for fpath in fpaths:
            try:
                font = matplotlib.font_manager.get_font(fpath).family_name
                fonts.append(font)
            except RuntimeError as re:
                logging.debug(f"{re}: failed to get font name for {fpath}")
                pass
        return fonts

    def create_figure(
        self,
        fig_name: str,
        fig_size: Optional[Tuple[float, float]] = None,
        dpi: Optional[int] = None,
    ) -> plt.Figure:
        """
        Initialize a :mod:`Pyplot <matplotlib.pyplot>` figure.

        Set its size and dpi, set the font size,
        choose the Arial font family if possible,
        and append it to the figures dictionary.

        Args:
            fig_name:
                name of figure; used as key in figures dictionary
            fig_size:
                optional width and height of figure in inches
            dpi:
                rasterization resolution

        Returns:
            :obj:`Pyplot figure <matplotlib.figure.Figure>`:
                reference to :mod:`MatPlotLib/Pyplot <matplotlib.pyplot>`
                figure
        """
        fig_size_: Tuple[float, float] = (
            (8, 8) if fig_size is None else fig_size
        )
        dpi_: float = self.dpi if dpi is None else dpi
        logging.info(
            "gmplib.plot.GraphingBase:\n   "
            + f"Creating plot: {fig_name} size={fig_size_} @ {dpi_} dpi"
        )
        fig = plt.figure()
        self.fdict.update({fig_name: fig})
        fig.set_size_inches(fig_size_)
        fig.set_dpi(dpi_)
        return fig

    def get_aspect(self, axes: plt.Axes) -> float:
        """
        Get aspect ratio of graph.

        Args:
            axes:
                the `axes` object of the figure

        Returns:
            float:
                aspect ratio
        """
        # Total figure size
        figWH: Tuple[float, float] = axes.get_figure().get_size_inches()
        figW, figH = figWH
        # Axis size on figure
        bounds: Tuple[float, float, float, float] = axes.get_position().bounds
        _, _, w, h = bounds
        # Ratio of display units
        disp_ratio: float = (figH * h) / (figW * w)
        # Ratio of data units
        # Negative over negative because of the order of subtraction
        # logging.info(axes.get_ylim(),axes.get_xlim())
        data_ratio: float = op.sub(*axes.get_ylim()) / op.sub(*axes.get_xlim())
        aspect_ratio: float = disp_ratio / data_ratio
        return aspect_ratio

    def naturalize(self, fig: plt.Figure) -> None:
        """Adjust graph aspect ratio into 'natural' ratio."""
        axes: plt.Axes = fig.gca()
        # x_lim, y_lim = axes.get_xlim(), axes.get_ylim()
        # axes.set_aspect((y_lim[1]-y_lim[0])/(x_lim[1]-x_lim[0]))
        axes.set_aspect(1 / self.get_aspect(axes))

    def stretch(
        self,
        fig: plt.Figure,
        xs: Optional[Tuple[float, float]] = None,
        ys: Optional[Tuple[float, float]] = None,
    ) -> None:
        """Stretch graph axes by respective factors."""
        axes: plt.Axes = fig.gca()
        if xs is not None:
            x_lim = axes.get_xlim()
            x_range = x_lim[1] - x_lim[0]
            axes.set_xlim(
                x_lim[0] - x_range * xs[0], x_lim[1] + x_range * xs[1]
            )
        if ys is not None:
            y_lim = axes.get_ylim()
            y_range = y_lim[1] - y_lim[0]
            axes.set_ylim(
                y_lim[0] - y_range * ys[0], y_lim[1] + y_range * ys[1]
            )

    # def covector_fishbone_vertical(self,
    #                                x: float, y: float,
    #                                px: float, py: float,
    #                                ref: float,
    #                                fishbone_len: float,
    #                                n_ticks: int=5,
    #                                sf: float=1.0,
    #                                color: str='DarkBlue') -> None:
    #     """
    #     TBD
    #     """
    #     head_width_: float = 0.0
    #     head_length_: float = 0.0
    #     lw_: float = 0.5
    #     plt.arrow(x,y, 0, -fishbone_len,
    #                 color=color, ec=color,
    #                 head_width=head_width_, head_length=head_length_,
    #                 lw=lw_, shape='full', overhang=1,
    #                 length_includes_head=True,
    #                 head_starts_at_zero=False,)
    #
    #     dy_per_tick: float = sf*(ref/py) * (fishbone_len/n_ticks)
    #     tick_sf: float = 0.02
    #     for i_ in range(n_ticks):
    #         npx: float = py*tick_sf
    #         npy: float = px*tick_sf
    #         dy: float = dy_per_tick*(i_+1)
    #         if dy>fishbone_len:
    #             break
    #         plt.plot([x-npx/2,x+npx/2],[y-dy+npy/2,y-dy-npy/2], c=color)
    #
    # def covector_fishbone(self,
    #                        x: float, y: float,
    #                        px: float, py: float,
    #                        ref: float,
    #                        fishbone_len: float,
    #                        n_ticks: int=5,
    #                        sf: float=1.0,
    #                        color: str='DarkBlue') -> None:
    #     """
    #     TBD
    #     """
    #     head_width_: float = 0.0
    #     head_length_: float = 0.0
    #     lw_: float = 0.5
    #     p_norm: float = norm((px,py))
    #     sf_: float = sf*fishbone_len/p_norm
    #     dx: float = -sf_*px
    #     dy: float = -sf_*py
    #     plt.arrow(x,y, dx,dy,
    #                 color=color, ec=color,
    #                 head_width=head_width_, head_length=head_length_,
    #                 lw=lw_, shape='full', overhang=1,
    #                 length_includes_head=True,
    #                 head_starts_at_zero=False,)
    #
    #     dx_per_tick: float = sf*(px/ref) * (fishbone_len/n_ticks)
    #     dy_per_tick: float = sf*(py/ref) * (fishbone_len/n_ticks)
    #     tick_sf: float = 0.03
    #     for i_ in range(n_ticks+3):
    #         dx = dx_per_tick*(i_+1)
    #         dy = dy_per_tick*(i_+1)
    #         d_norm: float = norm((dx,dy))
    #         npx: float = tick_sf*dy/d_norm
    #         npy: float = tick_sf*dx/d_norm
    #         # logging.info(px,py,dx_per_tick,dy_per_tick)
    #         if norm((dx,dy))>fishbone_len:
    #             break
    #         plt.plot([x-dx],[y-dy], 'o', ms=2, c=color)
    #       plt.plot([x-dx-npx/2,x-dx+npx/2],[y-dy+npy/2,y-dy-npy/2], c=color)


# from dataclasses import dataclass, field
# @dataclass(repr=True, eq=False, order=False, unsafe_hash=False, frozen=False)

# dpi: int = field(repr=False, default=100)
# font_size: int = field(repr=False, default=11)
# fdict: dict = field(repr=True, default_factory=dict)
# colors: list = field(repr=False, default_factory=list)
#      #=lambda: (plt.rcParams['axes.prop_cycle']).by_key()['color'])
# markers: list = field(repr=False, default_factory=list)
#      #=lambda: ['o', 's', 'v', 'p', '*', 'D', 'X', '^','h','P'])
# linestyle_list: list = field(repr=False, default_factory=list)
#      #=lambda: [ 'solid', 'dashdot', 'dashed', (0, (3, 1, 1, 1))])
#
# def __post_init__(self):
#     self.colors = (plt.rcParams['axes.prop_cycle']).by_key()['color']
#     self.n_colors = len(list(self.colors))
#     self.color_cycle = cycle(self.colors)
#     self.markers = ['o', 's', 'v', 'p', '*', 'D', 'X', '^','h','P']
#     self.n_markers = len(self.markers)
#     self.marker_cycle = cycle(self.markers)
#     self.linestyle_list = [ 'solid', 'dashdot', 'dashed',
#   (0, (3, 1, 1, 1))]

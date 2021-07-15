"""
---------------------------------------------------------------------

Graph plotting utilities

---------------------------------------------------------------------

Requires Python packages/modules:
  -  :mod:`numpy`
  -  :mod:`sympy`
  -  :mod:`matplotlib.pyplot`
  -  :mod:`matplotlib.ticker`
  -  :mod:`matplotlib.patches`
  -  :mod:`mpl_toolkits.axes_grid1`

Imports symbols from :mod:`.symbols` module.

---------------------------------------------------------------------

"""

import matplotlib as mpl, matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import FormatStrFormatter
import matplotlib.patches as patches
from matplotlib.patches import Patch, FancyArrow, FancyArrowPatch, Arrow, Rectangle, Circle, RegularPolygon
from matplotlib.legend_handler import HandlerPatch
from matplotlib import cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from itertools import cycle

import numpy as np

import warnings
warnings.filterwarnings("ignore")

__all__ = ['GraphingBase']


class GraphingBase():
    """
    Base visualization class.

    Args:
        dpi (int): resolution for rasterized images
        font_size (int): general font size

    Attributes:
        dpi (int) : resolution for rasterized images
        font_size (int) : general font size
        fdict  (dict) :  dictionary to which each figure is appended as it is generated
        colors  (list) :  list of colors
        n_colors  (int) :  number of colors
        color_cycle  (:obj:`itertools cycle <itertools.cycle>`) :  color property cycle
        markers  (list) :  list of markers
        n_markers  (:obj:`itertools cycle <itertools.cycle>`) :  number of markers
        marker_cycle  (int) :  cycle of markers
        linestyle_list  (list) :  list of line styles (solid, dashdot, dashed, custom dashed)
    """
    def __init__(self, dpi=100, font_size=11):
        self.dpi = dpi
        self.font_size = font_size
        self.fdict = dict()
        prop_cycle = plt.rcParams['axes.prop_cycle']
        self.colors = prop_cycle.by_key()['color']
        self.n_colors = len(self.colors)
        self.color_cycle = cycle(self.colors)
        self.markers = ['o', 's', 'v', 'p', '*', 'D', 'X', '^','h','P']
        self.n_markers = len(self.markers)
        self.marker_cycle = cycle(self.markers)
        self.linestyle_list = [ 'solid', 'dashdot', 'dashed', (0, (3, 1, 1, 1))]

    color = lambda self,idx: self.colors[idx%self.n_colors]
    marker = lambda self,idx: self.markers[idx%self.n_markers]

    def create_figure(self, fig_name, fig_size=None, dpi=None):
        """
        Initialize a :mod:`MatPlotLib/Pyplot <matplotlib.pyplot>` figure,
        set its size and dpi, set the font size, choose the Arial font family if possible,
        and append it to the figures dictionary,

        Args:
            fig_name (str): key for figures dict

        Returns:
            :obj:`Matplotlib figure <matplotlib.figure.Figure>`:
                reference to :mod:`MatPlotLib/Pyplot <matplotlib.pyplot>` figure
        """
        # if cm.verbose: print(f'Creating plot: {fig_name}')
        fig = plt.figure()
        self.fdict.update({fig_name:fig})
        fig.set_size_inches(*fig_size if fig_size is not None else [8,8])
        fig.set_dpi(dpi if dpi is not None else self.dpi)
        try:
            mpl.rc('font', size=self.font_size, family='Arial')
        except:
            mpl.rc('font', size=self.font_size)
        return fig

    @staticmethod
    def get_aspect(axes):
        """
        Get aspect ratio of graph.

        Args:
            axes (object): the 'axes' object of the figure

        Returns:
            float: aspect ratio
        """
        print(fdict)
        # Total figure size
        figW, figH = axes.get_figure().get_size_inches()
        # Axis size on figure
        _, _, w, h = axes.get_position().bounds
        # Ratio of display units
        disp_ratio = (figH * h) / (figW * w)
        # Ratio of data units
        # Negative over negative because of the order of subtraction
        # print(axes.get_ylim(),axes.get_xlim())
        data_ratio = op.sub(*axes.get_ylim()) / op.sub(*axes.get_xlim())

        return disp_ratio/data_ratio

    @staticmethod
    def naturalize(fig):
        axes = fig.gca()
        # x_lim, y_lim = axes.get_xlim(), axes.get_ylim()
        # axes.set_aspect((y_lim[1]-y_lim[0])/(x_lim[1]-x_lim[0]))
        axes.set_aspect(1/get_aspect(axes))

    @staticmethod
    def stretch(fig, xs=None, ys=None):
        axes = fig.gca()
        if xs is not None:
            x_lim = axes.get_xlim()
            x_range = x_lim[1]-x_lim[0]
            axes.set_xlim(x_lim[0]-x_range*xs[0],x_lim[1]+x_range*xs[1])
        if ys is not None:
            y_lim = axes.get_ylim()
            y_range = y_lim[1]-y_lim[0]
            axes.set_ylim(y_lim[0]-y_range*ys[0],y_lim[1]+y_range*ys[1])

    @staticmethod
    def covector_fishbone_vertical(x,y, px,py, ref, fishbone_len, n_ticks=5, sf=1, color='DarkBlue'):
        phl, plw, phw  = 0.0, 0.5, 0
        plt.arrow(x,y, 0, -fishbone_len,
                    color=color, ec=color,
                    head_width=phw, head_length=phl, lw=plw,
                    shape='full', overhang=1,
                    length_includes_head=True,
                    head_starts_at_zero=False,)

        dy_per_tick = sf*(ref/py) * (fishbone_len/n_ticks)
        tick_sf = 0.02
        for i_ in range(n_ticks):
            npx = py*tick_sf
            npy = px*tick_sf
            dy = dy_per_tick*(i_+1)
            if dy>fishbone_len: break
            plt.plot([x-npx/2,x+npx/2],[y-dy+npy/2,y-dy-npy/2], c=color)

    @staticmethod
    def covector_fishbone(x,y, px,py, ref, fishbone_len, n_ticks=5, sf=1, color='DarkBlue'):
        phl, plw, phw = 0.0, 0.5, 0
        p_norm = norm((px,py))
        sf_ = sf*fishbone_len/p_norm
        dx = -sf_*px
        dy = -sf_*py
        plt.arrow(x,y, dx,dy,
                    color=color, ec=color,
                    head_width=phw, head_length=phl, lw=plw,
                    shape='full', overhang=1,
                    length_includes_head=True,
                    head_starts_at_zero=False,)

        dx_per_tick = sf*(px/ref) * (fishbone_len/n_ticks)
        dy_per_tick = sf*(py/ref) * (fishbone_len/n_ticks)
        tick_sf = 0.03
        for i_ in range(n_ticks+3):
            dx = dx_per_tick*(i_+1)
            dy = dy_per_tick*(i_+1)
            d_norm = norm((dx,dy))
            npx = tick_sf*dy/d_norm
            npy = tick_sf*dx/d_norm
            # print(px,py,dx_per_tick,dy_per_tick)
            if norm((dx,dy))>fishbone_len: break
            plt.plot([x-dx],[y-dy], 'o', ms=2, c=color)
            plt.plot([x-dx-npx/2,x-dx+npx/2],[y-dy+npy/2,y-dy-npy/2], c=color)

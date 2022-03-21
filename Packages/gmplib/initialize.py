"""
Configure to run in `IPython`_.

---------------------------------------------------------------------

Sets up `IPython`_ environment if we're running
in a `Jupyter notebook`_ or `Jupyter QtConsole`_.

 - prepares Matplotlib to display inline and (for Macs)
   at a 'retina' resolution -- if this
   is not available, a benign error report (currently disabled)
   is made and progress continues
 - enables automatic reloading of :py:mod:`salt`
   (in case the code has been modded) when
   a notebook is re-run in-situ

---------------------------------------------------------------------

Requires `Matplotlib`_ and `IPython`_.

Uses IPython extensions `autoreload`_.

The  `autoreload`_ extension forces the parent package to be reloaded on
restart. This makes code modding and subsequent rerunning of a notebook
smooth and seamless. It is not needed for normal operation, and if
unavailable processing continues regardless.

---------------------------------------------------------------------

.. _Matplotlib: https://matplotlib.org/
.. _autoreload:
    https://ipython.readthedocs.io/en/stable/config/extensions/autoreload.html
.. _IPython: https://ipython.readthedocs.io/en/stable/
.. _Jupyter notebook: https://jupyter-notebook.readthedocs.io/en/stable/
.. _Jupyter QtConsole: https://qtconsole.readthedocs.io/en/stable/
"""

# import logging
# import matplotlib as mpl

# Jupyter `%magic` commands `%load_ext`, `%aimport`, and `%autoreload`
#  are needed here to force the notebook to reload the `streamline` module,
#  and its constituent modules, as changes are made to it.
# Force module to reload

from IPython import get_ipython


def check_is_ipython():
    """Check if we are running an IPython kernel from Jupyter etc."""
    try:
        if "IPKernelApp" not in get_ipython().config:  # pragma: no cover
            return False
    except ImportError:
        return False
    except AttributeError:
        return False
    return True


is_python: bool = check_is_ipython()

if is_python:
    try:
        get_ipython().magic("config InlineBackend.figure_format = 'retina'")
    except NameError:
        pass
    # except:
    #     print('Possibly benign error trying to config Matplotlib backend')

    try:
        get_ipython().magic("matplotlib inline")
    except NameError:
        pass
    # except:
    #     print('Possibly benign error trying to config Matplotlib backend')

    try:
        get_ipython().magic("load_ext autoreload")
        get_ipython().magic("autoreload 2")
        # get_ipython().magic('aimport '+package_name)
    except NameError as error:
        print(
            "Error trying to invoke get_ipython(), "
            + "possibly because not running IPython:",
            error,
        )
    # except:
    #     print('Possibly benign error trying to config autoreload')

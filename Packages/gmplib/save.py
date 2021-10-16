"""
---------------------------------------------------------------------

Export plots to PNG, PDF format files.

---------------------------------------------------------------------

Requires Python packages/modules:
  -  :mod:`os`

TODO: docstrings!!!

---------------------------------------------------------------------

"""

from os.path import exists, join, realpath
from os import mkdir
from sympy import latex
from json import dump
import numpy as np


def create_dir(dir):
    try:
        if not exists(dir):
            mkdir(dir)
        else:
            return dir
    except OSError:
        print('Cannot create directory')
        raise
    except:
        raise
    return dir

def create_directories(results_path=['..','Results'], results_dir='Demo'):
    """
    Create an output directory.

    Throws an exception if the directory cannot be created.
    Returns quietly if the directory already exists.

    Args:
        results_dir_name (str) : name of directory

    Returns:
        str: path to directory (see :mod:`os.path`)
    """
    results_path_ = ['.']+list(results_path)
    create_dir(join(*results_path_))
    results_dir_ = results_path_+[results_dir]
    return create_dir(join(*results_dir_))


def export_results(results_dir, filename, raw_dict, suffix=''):
    """
    Export results to JSON file

    Args:
        results_dir (str) : name of output directory
        suffix (str) : filename suffix
    """
    serializable_dict = {}
    for item in raw_dict.items():
        serializable_dict.update({latex(item[0]):np.float(item[1])})
    results_path_ = [results_dir]+[filename+'_'+suffix+'.json']
    with open(join(*results_path_), 'w') as fp:
        print(join(*results_path_))
        dump(serializable_dict, fp, separators=(', \n', ': '))


def export_plots(fig_dict, results_dir, file_types='pdf', suffix=''):
    """
    Export plots to PDFs or other format files

    Args:
        fig_dict (dict) : dictionary of figures
        results_dir (str) : name of output directory
        file_types (str or list) : file format (or list of file formats)
        suffix (str) : filename suffix
    """
    results_path = realpath(results_dir)
    print('Writing to dir: "'+results_path+'"')
    if type(file_types) != list:
        file_types = [file_types]
    for file_type in file_types:
        for fig_dict_item in list(fig_dict.items()):
            export_plot(*fig_dict_item, results_path, file_type=file_type, suffix=suffix)


def export_plot(fig_name, fig, results_dir, file_type='pdf', suffix=''):
    """
    Export plot to PDF or other format file

    Args:
        fig_name (str) : name to be used for file (extension auto-appended)
        fig (object) : figure object
        results_dir (str) : name of output directory
        file_type (str) : file format
        suffix (str) : filename suffix
    """
    fig_name += suffix+'.'+file_type.lower()
    try:
        fig.savefig(join(results_dir,fig_name), bbox_inches = 'tight', pad_inches = 0.05)
        print('Exported "'+fig_name+'"')
    except OSError:
        print('Failed to export figure "'+fig_name+'"')
        raise
    except:
        raise

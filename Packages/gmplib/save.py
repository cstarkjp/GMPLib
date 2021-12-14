"""
---------------------------------------------------------------------

Export plots to PNG, PDF format files.

---------------------------------------------------------------------

Requires Python packages/modules:
  -  :mod:`sympy`

TODO: docstrings!!!

---------------------------------------------------------------------

"""
import warnings
import logging
from os.path import exists, join, realpath
from os import mkdir
from json import dump

from sympy import latex

warnings.filterwarnings("ignore")

__all__ = ['create_dir', 'create_directories',
           'export_results', 'export_plots','export_plot']

def create_dir(dir_) -> str:
    """
    TBD
    """
    try:
        if not exists(dir_):
            mkdir(dir_)
        else:
            return dir_
    except OSError:
        print('Cannot create directory')
        raise
    except Exception:
        print(Exception)
        raise
    return dir_

def create_directories(results_path=('..','Results'), results_dir='Demo') -> str:
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

def export_results(results_dir, filename, raw_dict, suffix='') -> None:
    """
    Export results to JSON file

    Args:
        results_dir (str) : name of output directory
        suffix (str) : filename suffix
    """
    serializable_dict = {}
    for item in raw_dict.items():
        serializable_dict.update({latex(item[0]):float(item[1])})
    results_path_ = [results_dir]+[filename+'_'+suffix+'.json']
    with open(join(*results_path_), 'w', encoding='latin-1') as fp:
        logging.info(join(*results_path_))
        dump(serializable_dict, fp, separators=(', \n', ': '))

def export_plots(fig_dict, results_dir, file_types='pdf', suffix='', dpi=None) -> None:
    """
    Export plots to PDFs or other format files

    Args:
        fig_dict (dict) : dictionary of figures
        results_dir (str) : name of output directory
        file_types (str or list) : file format (or list of file formats)
        suffix (str) : filename suffix
    """
    results_path = realpath(results_dir)
    logging.info(f'Writing to dir: "{results_path}"')
    file_types_ = [file_types] if not isinstance(file_types, list) else file_types
    for file_type in file_types_:
        # logging.info(f'Image file type: "{file_type}"')
        for fig_dict_item in list(fig_dict.items()):
            export_plot(*fig_dict_item, results_path, file_type=file_type, suffix=suffix,
                        dpi=dpi)

def export_plot(fig_name, fig, results_dir, file_type='pdf', suffix='', dpi=None) -> None:
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
        # logging.info(f'dpi={dpi}')
        fig.savefig(join(
            results_dir,fig_name), bbox_inches='tight', pad_inches=0.05,
            dpi=dpi,
            format=file_type
        )
        logging.info(f'Exported "{fig_name}"')
    except OSError:
        logging.info(f'Failed to export figure "{fig_name}"')
        raise
    except:
        raise

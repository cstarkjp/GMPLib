"""
---------------------------------------------------------------------

Utility functions to help printing and image display.

---------------------------------------------------------------------

Requires Python packages/modules:
  -  :mod:`IPython.display`
  -  :mod:`os`
  -  :mod:`PIL`
  -  :mod:`functools`

---------------------------------------------------------------------

"""

import numpy as np
from copy import deepcopy
from functools import reduce
from sys import stdout
from os import listdir
from os.path import realpath, join
from json import dumps
from IPython.display import Image,display,Math,Latex,display_pretty
import PIL
from sympy import Eq, N, Mul, Matrix
from sympy.physics.units import Quantity, convert_to
from sympy.physics.units.systems import SI

__all__ = ['numify', 'get_pkg_path', 'is_jsonable', 'export_results', 'Results',
           'e2d', 'fetch_images', 'resize']

numify = lambda str: float(str.replace('p','.'))


def get_pkg_path(pkg, dirname=''):
    return realpath(join(pkg.__path__[0],'..','..',dirname))

def is_jsonable(item):
    try:
        dumps(item)
        return True
    except Exception:
        return False

def export_results(results_to_export, results_dir, suffix='', do_parse=True, max_nparray_size=None, do_dolfin_adjoint=False):
    """
    """
    pdebug=print
    if do_dolfin_adjoint:
        import dolfin_adjoint as adj
    if do_parse:
        export = Results()
        for attribute, attribute_value in results_to_export.items():
            attribute_value_copy = deepcopy(attribute_value)
            unjsonable_sub_attributes = {}
            for sub_attribute in attribute_value.__dict__:
                sub_attribute_value = getattr(attribute_value_copy,sub_attribute)
                var_types = [float] if not do_dolfin_adjoint else [float, adj.AdjFloat]
                if any([isinstance(sub_attribute_value, var_type) for var_type in var_types]):
                    setattr(attribute_value_copy, sub_attribute, float(sub_attribute_value))
                elif isinstance(sub_attribute_value, np.ndarray) \
                        and (max_nparray_size is None or sub_attribute_value.size<=max_nparray_size):
                    setattr(attribute_value_copy, sub_attribute, [list(array) for array in sub_attribute_value])
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
    json_filename = 'results'+suffix+'.json'
    json_path = realpath(join(results_dir,json_filename))
    with open(json_path,'w') as json_file:
        print('Writing to "{}"'.format(json_path))
        try:
            json_file.write(json_str)
        except Exception:
            print('Failed to write analysis results JSON file')


class Results():
    def __init__(self):
        pass


def e2d(eqn_or_eqnlist, do_flip=False, do_negate=False):
    if do_negate:
        ngfn = lambda eqn: [-eqn[0],-eqn[1]]
    else:
        ngfn = lambda eqn: eqn
    if type(eqn_or_eqnlist) is list:
        eqndict = {}
        [eqndict.update( dict([reversed(ngfn(eqn.args))] if do_flip else [ngfn(eqn.args)]) )
                                    for eqn in eqn_or_eqnlist]
        return eqndict
    else:
        return dict([reversed(ngfn(eqn_or_eqnlist.args))] if do_flip else [eqn_or_eqnlist.args])

def dict2mat(dct):
    return Matrix([item for item in dct.items()])

def omitdict(dct, omitlist, verbose=False):
    rtn_dct = dct.copy()
    for k in list(omitlist):
        try:
            del rtn_dct[k]
        except KeyError:
            if verbose: print(f'{k} not found: skipping')
    return rtn_dct

def xdict(dct, xlist):
    rtn_dct = {}
    [rtn_dct.update({k:dct[k]}) for k in list(xlist)]
    return rtn_dct

def round(eqn, n=0, sf=1):
    """
    Round numerical RHS of Sympy equation, converting to integer if zero decimal places requested.

    Args:
        eqn (:class:`sympy.Eq <sympy.core.relational.Equality>`): Sympy equation object
        n (int): number of decimal places
        sf (float): scale factor

    Returns:
        eqn (:class:`sympy.Eq <sympy.core.relational.Equality>`): Sympy equation object
    """
    approx_rhs = np.round(float(N(eqn.rhs)*sf),n) if n is not None else N(eqn.rhs)*sf
    rtn_eqn = Eq(eqn.lhs, approx_rhs if n is None or n>0 else int(approx_rhs))
    return rtn_eqn

def convert(eqn, units, n=0, do_raw=False):
    """
    XXX

    Args:
        eqn (:class:`sympy.Eq <sympy.core.relational.Equality>`): Sympy equation object
        n (int): number of decimal places
        sf (float): scale factor

    Returns:
        eqn (:class:`sympy.Eq <sympy.core.relational.Equality>`): Sympy equation object
    """
    tmp = Quantity('unknown_units')
    SI.set_quantity_dimension(tmp, SI.get_quantity_dimension(eqn.lhs))
    cf = convert_to(tmp, units).n()

    # return Eq(eqn.lhs, np.round(float(N(eqn.rhs)), n)*N(cf))
    return Eq(eqn.lhs, np.round(float(N(cf.args[0]*eqn.rhs)), n)*Mul(*cf.args[1:])) if do_raw is not True \
        else Eq(eqn.lhs, np.round(float(N(eqn.rhs)), n)*N(cf))

def vprint(verbose, *args, **kwargs):
    """
    Wrapper for print() with verbose flag to suppress output if desired.

    Args:
        verbose  (bool): turn printing on or off
        *args (str): print() function args
        **kwargs (str): print() function keyword args
    """
    if verbose:
        print(*args, **kwargs, flush=True)
        # Try to really force this line to print before the GPU prints anything
        stdout.flush()

def fetch_images(images=None, image_sources=None, image_paths=None):
    """
    Imports images from a list of source directories.
    If `images` and `image_sources` are `None` new dictionaries are created;
    otherwise, pre-existing such dictionaries are expected.

    This tool is used by the discussion notebooks to import snapshot images
    for inline display.

    Args:
        images (dict): pre-existing dictionary of images
        image_sources (dict): pre-existing dictionary of image source paths
        image_paths (list): source directories from which to fetch new images
    """
    images = {} if images is None else images
    image_sources = {} if image_sources is None else image_sources
    for image_path in image_paths:
        listing = listdir(image_path)
        image_list = [(file.replace('.png','').replace('.PNG','').replace('.jpg','').replace('.jpeg',''),
                       Image(filename=join(image_path,file)))
                      for file in listing if file.endswith('PNG') or file.endswith('png')
                      or file.endswith('jpg') or file.endswith('jpeg')]
        images.update({key: value for (key, value) in list(image_list)})
        image_sources.update({key: image_path for (key) in (listing)})
    return images, image_sources

def resize(image, width=None, height=None):
    if width is not None:
        image.width = width
    if height is not None:
        image.height = height
    return image

def combine_images_vertically( into_filename=None, image_bundle=None, image_sources=None,
                               spacing=20, out_path=None, do_align_right=False ):
    """
    Join together a set of images, with padding, into a vertical combo image.

    Args:
        into_filename  (str): name of output combined-image file
        image_bundle  (list): list of image filenames
        image_sources (dict): dictionary of image source paths
        spacing (int): pixel padding between images
        out_path (list): path to tmp directory to write the combined image file to
        do_align_right (bool): align all images along right margin
    """
    image_list = [PIL.Image.open(join(image_sources[image_name],image_name))
                  for image_name in image_bundle]
    x_size = max([image.size[0] for image in image_list])
    y_sizes = [image.size[1] for image in image_list]
    y_size = reduce(lambda x,y: x+y, y_sizes) + spacing*(len(image_list)-1)
    combo_image = PIL.Image.new('RGB',(x_size, y_size), (255,255,255))
    y_offset = 0
    for image,y_size in zip(image_list,y_sizes):
        x_offset = x_size-image.size[0] if do_align_right else 0
        combo_image.paste(image, (x_offset,y_offset))
        y_offset += y_size + spacing
    combo_image.save(join(out_path,into_filename))

def combine_images_horizontally( into_filename=None, image_bundle=None, image_sources=None,
                                 spacing=20, out_path=None ):
    """
    Join together a set of images, with padding, into a horizontal combo image.

    Args:
        into_filename  (str): name of output combined-image file
        image_bundle  (list): list of image filenames
        image_sources (dict): dictionary of image source paths
        spacing (int): pixel padding between images
        out_path (list): path to tmp directory to write the combined image file to
    """
    image_list = [PIL.Image.open(join(image_sources[image_name],image_name))
                  for image_name in image_bundle]
    y_size = max([image.size[1] for image in image_list])
    x_sizes = [image.size[0] for image in image_list]
    x_size = reduce(lambda x,y: x+y, x_sizes) + spacing*(len(image_list)-1)
    combo_image = PIL.Image.new('RGB',(x_size, y_size), (255,255,255))
    x_offset = 0
    for image,x_size in zip(image_list,x_sizes):
        combo_image.paste(image, (x_offset,0))
        x_offset += x_size + spacing
    combo_image.save(join(out_path,into_filename))

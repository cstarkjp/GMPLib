"""
---------------------------------------------------------------------

Utility functions to combine image files.

---------------------------------------------------------------------

Requires Python packages/modules:
  -  :mod:`IPython.display`
  -  :mod:`PIL`
  -  :mod:`PyPDF2`
  -  :mod:`Wand`

---------------------------------------------------------------------

"""
# Allow failed import of dolfin-adjoint if not using FEniCS
# pylint: disable=import-error, import-outside-toplevel
import warnings
# import logging

# Library modules
import os
from os import listdir
from os.path import join #, realpath, splitext
from functools import reduce
from decimal import Decimal

# Typing
from typing import Dict, Tuple, List, Optional #, Any, Union

# Abstract classes & methods
from abc import ABC, abstractmethod

# Image processing
from IPython.display import Image
from wand.image import Image as PdfImage
import PIL

# PDF processing
from PyPDF2 import PdfFileReader, PdfFileWriter
from PyPDF2.pdf import PageObject

warnings.filterwarnings("ignore")

__all__ = [ 'combine_raster_images_vertically', 'combine_raster_images_horizontally',
            'combine_pdf_images_vertically', 'combine_pdf_images_horizontally',
            'fetch_images', 'resize' ]


class combine_images(ABC):
    """
    Join together a set of images, with padding.

    Args:
        into_filename  (str): name of output combined-image file
        image_bundle  (list): list of image filenames
        image_sources (dict): dictionary of image source paths
        spacing (int): pixel padding between images
        out_path (list): path to tmp directory to write the combined image file to
        do_align_right (bool): align all images along right margin
    """
    def __init__( self,
                  into_filename: os.PathLike,
                  image_bundle: List[str],
                  image_sources: Dict[str,str],
                  file_type: str='jpg',
                  spacing: int=20,
                  out_path: str=None,
                  do_align_right: bool=False ):
        """
        TBD
        """
        self.combo_image: Image = None
        self.combo_page: PdfImage = None
        self.get_images(image_bundle, image_sources, file_type, spacing)
        self.paste_images(spacing, do_align_right)
        self.save_combo_image(out_path, into_filename, file_type)

    @abstractmethod
    def get_images(self, image_bundle, image_sources, file_type, spacing) -> None:
        """
        TBD
        """

    @abstractmethod
    def paste_images(self, spacing, do_align_right) -> None:
        """
        TBD
        """

    @abstractmethod
    def save_combo_image(self, out_path, into_filename, file_type) -> None:
        """
        TBD
        """


class combine_raster_images(combine_images):
    """
    TBD
    """
    def get_images(self, image_bundle, image_sources, file_type, spacing) -> None:
        """
        TBD
        """
        self.image_list = [
            PIL.Image.open(join(image_sources[f'{image_name}.{file_type}'],
                                              f'{image_name}.{file_type}'))
            for image_name in image_bundle
        ]

    def save_combo_image(self, out_path, into_filename, file_type) -> None:
        """
        TBD
        """
        self.combo_image.save(join(str(out_path), f'{into_filename}.{file_type}'))

class combine_raster_images_vertically(combine_raster_images):
    """
    TBD
    """
    def paste_images(self, spacing, do_align_right) -> None:
        """
        TBD
        """
        x_size = max([image.size[0] for image in self.image_list])
        y_sizes = [image.size[1] for image in self.image_list]
        y_size = reduce(lambda x,y: x+y, y_sizes) + spacing*(len(self.image_list)-1)
        self.combo_image = PIL.Image.new('RGB',(x_size, y_size), (255,255,255))
        y_offset = 0
        for image,y_size in zip(self.image_list, y_sizes):
            x_offset = x_size-image.size[0] if do_align_right else 0
            self.combo_image.paste(image, (x_offset,y_offset))
            y_offset += y_size + spacing

class combine_raster_images_horizontally(combine_raster_images):
    """
    TBD
    """
    def paste_images(self, spacing, do_align_right) -> None:
        """
        TBD
        """
        y_size = max([image.size[1] for image in self.image_list])
        x_sizes = [image.size[0] for image in self.image_list]
        x_size = reduce(lambda x,y: x+y, x_sizes) + spacing*(len(self.image_list)-1)
        self.combo_image = PIL.Image.new('RGB',(x_size, y_size), (255,255,255))
        x_offset = 0
        for image,x_size in zip(self.image_list,x_sizes):
            self.combo_image.paste(image, (x_offset,0))
            x_offset += x_size + spacing


class combine_pdf_images(combine_images):
    """
    TBD
    """
    def get_images(self, image_bundle, image_sources, file_type, spacing) -> None:
        """
        TBD
        """
        self.page_list = []
        for image_name in image_bundle:
            pdf_path = join(image_sources[f'{image_name}.{file_type}'],
                                          f'{image_name}.{file_type}')
            with open(pdf_path,'rb') as f:
                pdf_reader = PdfFileReader(f)
            self.page_list.append(pdf_reader.getPage(0))

    def save_combo_image(self, out_path, into_filename, file_type) -> None:
        """
        TBD
        """
        combo_path = join(str(out_path), f'{into_filename}.{file_type}')
        writer = PdfFileWriter()
        writer.addPage(self.combo_page)
        with open(combo_path, 'wb') as f:
            writer.write(f)

class combine_pdf_images_vertically(combine_pdf_images):
    """
    TBD
    """
    def paste_images(self, spacing, do_align_right) -> None:
        """
        TBD
        """
        x_size: Decimal = max([page_.mediaBox.getWidth()
                               for page_ in self.page_list])
        y_sizes: List[Decimal] = [page_.mediaBox.getHeight()
                                  for page_ in self.page_list]
        y_size: Decimal \
            = reduce(lambda x,y: x+y, y_sizes) + (spacing//2)*(len(self.page_list)-1)
        self.combo_page = PageObject.createBlankPage(None, x_size, y_size)
        y_offset = y_size
        for i_, (page_,y_size_) in enumerate(zip(self.page_list, y_sizes)):
            y_offset -= Decimal(y_size_) + Decimal(spacing if i_>0 else 0)
            x_offset = (x_size-page_.mediaBox.getWidth() if do_align_right else 0)
            self.combo_page.mergeTranslatedPage(page_, x_offset,y_offset)

class combine_pdf_images_horizontally(combine_pdf_images):
    """
    TBD
    """
    def paste_images(self, spacing, do_align_right) -> None:
        """
        TBD
        """
        y_size: Decimal = max([page_.mediaBox.getHeight()
                               for page_ in self.page_list])
        x_sizes: List[Decimal] = [page_.mediaBox.getWidth()
                                  for page_ in self.page_list]
        x_sizes.reverse()
        x_size: Decimal \
            = reduce(lambda x,y: x+y, x_sizes) + spacing*(len(self.page_list)-1)
        self.combo_page = PageObject.createBlankPage(None, x_size, y_size)
        x_offset = x_size
        page_list = self.page_list.copy()
        page_list.reverse()
        for i_, (page_,x_size_) in enumerate(zip(page_list,x_sizes)):
            x_offset -= Decimal(x_size_) +  Decimal(spacing if i_>0 else 0)
            self.combo_page.mergeTranslatedPage(page_, x_offset,0)


def fetch_images(images: Optional[Dict[str,Image]]=None,
                 image_sources: Optional[Dict[str,str]]=None,
                 image_paths: Optional[List[str]]=None) \
            -> Tuple[Dict[str,Image],Dict[str,str]]:
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
    if image_paths is not None:
        for image_path in image_paths:
            listing = listdir(image_path)
            for file in listing:
                file_split = os.path.splitext(file)
                file_split[1].lower()
                if file_split[1] in ['.png','.jpg','.jpeg']:
                    images[file] = Image(filename=join(image_path,file))
                elif file_split[1]=='.pdf':
                    images[file] = PdfImage(filename=join(image_path,file))
            image_sources.update({key: image_path for key in listing})
    return images, image_sources

def resize(image: Image, width: int=None, height: int=None) -> Image:
    """
    TBD
    """
    if width is not None:
        image.width = width
    if height is not None:
        image.height = height
    return image






#

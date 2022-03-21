"""
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

# Library
import warnings

# import logging
import os
from os import listdir, PathLike
from os.path import join  # , realpath, splitext
from functools import reduce
from decimal import Decimal
from typing import Dict, Tuple, List, Optional  # , Any, Union

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

__all__ = [
    "CombineImages",
    "CombineRasterImages",
    "CombinePdfImages",
    "CombineRasterImagesVertically",
    "CombineRasterImagesHorizontally",
    "CombinePdfImagesVertically",
    "CombinePdfImagesHorizontally",
    "fetch_images",
    "resize",
]


class CombineImages(ABC):
    """
    Join together a set of images, with padding (abstract class template).

    Args:
        into_filename:
            name of output combined-image file
        image_bundle:
            list of image filenames
        image_sources:
            dictionary of image source paths with filename keys
        file_type:
            file type (usually 'jpg' or 'pdf')
        spacing:
            pixel padding between images
        out_path:
            where to write combined-image file
        do_align_right:
            align all images along right margin
    """

    # Definitions
    combo_image: Image
    combo_page: PdfImage

    def __init__(
        self,
        out_path: PathLike,
        into_filename: PathLike,
        image_bundle: List[str],
        image_sources: Dict[str, str],
        file_type: str = "jpg",
        spacing: int = 20,
        do_align_right: bool = False,
    ) -> None:
        """Initialize."""
        self.combo_image: Image = None
        self.combo_page: PdfImage = None
        self.get_images(image_bundle, image_sources, file_type, spacing)
        self.paste_images(spacing, do_align_right)
        self.save_combo_image(out_path, into_filename, file_type)

    @abstractmethod
    def get_images(
        self,
        image_bundle: List[str],
        image_sources: Dict[str, str],
        file_type: str,
        spacing: float,
    ) -> None:
        """
        How to get image files (abstract method).

        Args:
            image_bundle:
                list of image filenames
            image_sources:
                dictionary of image source paths with filename keys
            file_type:
                file type (usually 'jpg' or 'pdf')
            spacing:
                pixel padding between images
        """

    @abstractmethod
    def paste_images(self, spacing: float, do_align_right: bool) -> None:
        """
        How to combine image files (abstract method).

        Args:
            spacing:
                pixel padding between images
            do_align_right:
                align all images along right margin
        """

    @abstractmethod
    def save_combo_image(
        self, out_path: PathLike, into_filename: PathLike, file_type: str
    ) -> None:
        """
        Provide a tool to write a combined image file (abstract method).

        Args:
            out_path:
                where to write combined-image file
            into_filename:
                name of output combined-image file
            file_type:
                file type (usually 'jpg' or 'pdf')
        """


class CombineRasterImages(CombineImages):
    """
    Combine raster image files.

    Inherits from `combine_images`.
    """

    # Definitions
    image_list: List[Image]

    def get_images(
        self,
        image_bundle: List[str],
        image_sources: Dict[str, str],
        file_type: str,
        spacing: float,
    ) -> None:
        """Get images from raster files."""
        self.image_list = [
            PIL.Image.open(
                join(
                    image_sources[f"{image_name}.{file_type}"],
                    f"{image_name}.{file_type}",
                )
            )
            for image_name in image_bundle
        ]

    def save_combo_image(
        self, out_path: PathLike, into_filename: PathLike, file_type: str
    ) -> None:
        """Write combined image to a raster file."""
        self.combo_image.save(
            join(str(out_path), f"{into_filename}.{file_type}")
        )


class CombineRasterImagesVertically(CombineRasterImages):
    """
    Combine raster images in a vertical layout.

    Inherits from `combine_raster_images`.
    """

    # Definitions
    combo_image: Image

    def paste_images(self, spacing: float, do_align_right: bool) -> None:
        """Combine the images."""
        x_size = max([image.size[0] for image in self.image_list])
        y_sizes = [image.size[1] for image in self.image_list]
        y_size = reduce(lambda x, y: x + y, y_sizes) + spacing * (
            len(self.image_list) - 1
        )
        self.combo_image = PIL.Image.new(
            "RGB", (x_size, y_size), (255, 255, 255)
        )
        y_offset = 0
        for image, y_size in zip(self.image_list, y_sizes):
            x_offset = x_size - image.size[0] if do_align_right else 0
            self.combo_image.paste(image, (x_offset, y_offset))
            y_offset += y_size + spacing


class CombineRasterImagesHorizontally(CombineRasterImages):
    """
    Combine raster images in a horizontal layout.

    Inherits from `combine_raster_images`.
    """

    # Definitions
    combo_image: Image

    def paste_images(self, spacing: float, do_align_right: bool) -> None:
        """Combine the images."""
        y_size = max([image.size[1] for image in self.image_list])
        x_sizes = [image.size[0] for image in self.image_list]
        x_size = reduce(lambda x, y: x + y, x_sizes) + spacing * (
            len(self.image_list) - 1
        )
        self.combo_image = PIL.Image.new(
            "RGB", (x_size, y_size), (255, 255, 255)
        )
        x_offset = 0
        for image, x_size in zip(self.image_list, x_sizes):
            self.combo_image.paste(image, (x_offset, 0))
            x_offset += x_size + spacing


class CombinePdfImages(CombineImages):
    """
    Combine PDF image files.

    Inherits from `combine_images`.
    """

    # Definitions
    page_list: List[PdfImage]

    def get_images(
        self,
        image_bundle: List[str],
        image_sources: Dict[str, str],
        file_type: str,
        spacing: float,
    ) -> None:
        """Combine the image files."""
        self.page_list = []
        for image_name in image_bundle:
            pdf_path = join(
                image_sources[f"{image_name}.{file_type}"],
                f"{image_name}.{file_type}",
            )
            # The following cleaner method doesn't work because PdfFileReader
            #   appears to require pdf files to remain open for subsequent use
            # Exactly how/when they are actually closed is not at all clear
            # with open(pdf_path,'rb') as f:
            #     pdf_reader = PdfFileReader(f)
            #     self.page_list.append(pdf_reader.getPage(0))
            pdf_reader = PdfFileReader(open(pdf_path, "rb"))
            self.page_list.append(pdf_reader.getPage(0))

    def save_combo_image(
        self, out_path: PathLike, into_filename: PathLike, file_type: str
    ) -> None:
        """Write the image to a file."""
        combo_path = join(str(out_path), f"{into_filename}.{file_type}")
        writer = PdfFileWriter()
        writer.addPage(self.combo_page)
        with open(combo_path, "wb") as f:
            writer.write(f)


class CombinePdfImagesVertically(CombinePdfImages):
    """
    Combine PDF images in a vertical layout.

    Inherits from `combine_pdf_images`.
    """

    # Definitions
    combo_page: PdfImage

    def paste_images(self, spacing: float, do_align_right: bool) -> None:
        """Combine the images."""
        x_size: Decimal = max(
            [page_.mediaBox.getWidth() for page_ in self.page_list]
        )
        y_sizes: List[Decimal] = [
            page_.mediaBox.getHeight() for page_ in self.page_list
        ]
        y_size: Decimal = reduce(lambda x, y: x + y, y_sizes) + Decimal(
            spacing
        ) * (len(self.page_list) - 1)
        self.combo_page = PageObject.createBlankPage(None, x_size, y_size)
        y_offset = y_size
        for i_, (page_, y_size_) in enumerate(zip(self.page_list, y_sizes)):
            y_offset -= Decimal(y_size_) + Decimal(spacing if i_ > 0 else 0)
            x_offset = (
                x_size - page_.mediaBox.getWidth() if do_align_right else 0
            )
            self.combo_page.mergeTranslatedPage(page_, x_offset, y_offset)


class CombinePdfImagesHorizontally(CombinePdfImages):
    """
    Combine PDF images in a horizontal layout.

    Inherits from `combine_pdf_images`.
    """

    # Definitions
    combo_page: PdfImage

    def paste_images(self, spacing: float, do_align_right: bool) -> None:
        """Combine the images."""
        y_size: Decimal = max(
            [page_.mediaBox.getHeight() for page_ in self.page_list]
        )
        x_sizes: List[Decimal] = [
            page_.mediaBox.getWidth() for page_ in self.page_list
        ]
        x_sizes.reverse()
        x_size: Decimal = reduce(lambda x, y: x + y, x_sizes) + Decimal(
            spacing
        ) * (len(self.page_list) - 1)
        self.combo_page = PageObject.createBlankPage(None, x_size, y_size)
        x_offset = x_size
        page_list = self.page_list.copy()
        page_list.reverse()
        for i_, (page_, x_size_) in enumerate(zip(page_list, x_sizes)):
            x_offset -= Decimal(x_size_) + Decimal(spacing if i_ > 0 else 0)
            self.combo_page.mergeTranslatedPage(page_, x_offset, 0)


def fetch_images(
    images: Optional[Dict[str, Image]] = None,
    image_sources: Optional[Dict[str, str]] = None,
    image_paths: Optional[List[str]] = None,
) -> Tuple[Dict[str, Image], Dict[str, str]]:
    """
    Import images from a list of source directories.

    If `images` and `image_sources` are `None` new dictionaries are created;
    otherwise, pre-existing such dictionaries are expected.

    This tool is used by the discussion notebooks to import snapshot images
    for inline display.

    Args:
        images: pre-existing dictionary of images
        image_sources: pre-existing dictionary of image source paths
        image_paths: source directories from which to fetch new images

    Returns:
        tuple: dictionaries of images and image source files
    """
    images = {} if images is None else images
    image_sources = {} if image_sources is None else image_sources
    if image_paths is not None:
        for image_path in image_paths:
            listing = listdir(image_path)
            for file in listing:
                file_split = os.path.splitext(file)
                file_split[1].lower()
                if file_split[1] in [".png", ".jpg", ".jpeg"]:
                    images[file] = Image(filename=join(image_path, file))
                elif file_split[1] == ".pdf":
                    images[file] = PdfImage(filename=join(image_path, file))
            image_sources.update({key: image_path for key in listing})
    return (images, image_sources)


def resize(
    image: Image, width: Optional[int] = None, height: Optional[int] = None
) -> Image:
    """
    Modify an :mod:`Image <IPython image>` size.

    Returns:
        image: resized image object
    """
    if width is not None:
        image.width = width
    if height is not None:
        image.height = height
    return image


#

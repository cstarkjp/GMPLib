import abc
from IPython.display import Image
from abc import ABC, abstractmethod
from os import PathLike
from typing import Dict, List, Optional, Tuple
from wand.image import Image as PdfImage

class CombineImages(ABC, metaclass=abc.ABCMeta):
    combo_image: Image
    combo_page: PdfImage
    def __init__(
        self,
        out_path: PathLike,
        into_filename: PathLike,
        image_bundle: List[str],
        image_sources: Dict[str, str],
        file_type: str = ...,
        spacing: int = ...,
        do_align_right: bool = ...,
    ) -> None: ...
    @abstractmethod
    def get_images(
        self,
        image_bundle: List[str],
        image_sources: Dict[str, str],
        file_type: str,
        spacing: float,
    ) -> None: ...
    @abstractmethod
    def paste_images(self, spacing: float, do_align_right: bool) -> None: ...
    @abstractmethod
    def save_combo_image(
        self, out_path: PathLike, into_filename: PathLike, file_type: str
    ) -> None: ...

class CombineRasterImages(CombineImages, metaclass=abc.ABCMeta):
    image_list: List[Image]
    def get_images(
        self,
        image_bundle: List[str],
        image_sources: Dict[str, str],
        file_type: str,
        spacing: float,
    ) -> None: ...
    def save_combo_image(
        self, out_path: PathLike, into_filename: PathLike, file_type: str
    ) -> None: ...

class CombineRasterImagesVertically(CombineRasterImages):
    combo_image: Image
    def paste_images(self, spacing: float, do_align_right: bool) -> None: ...

class CombineRasterImagesHorizontally(CombineRasterImages):
    combo_image: Image
    def paste_images(self, spacing: float, do_align_right: bool) -> None: ...

class CombinePdfImages(CombineImages, metaclass=abc.ABCMeta):
    page_list: List[PdfImage]
    def get_images(
        self,
        image_bundle: List[str],
        image_sources: Dict[str, str],
        file_type: str,
        spacing: float,
    ) -> None: ...
    def save_combo_image(
        self, out_path: PathLike, into_filename: PathLike, file_type: str
    ) -> None: ...

class CombinePdfImagesVertically(CombinePdfImages):
    combo_page: PdfImage
    def paste_images(self, spacing: float, do_align_right: bool) -> None: ...

class CombinePdfImagesHorizontally(CombinePdfImages):
    combo_page: PdfImage
    def paste_images(self, spacing: float, do_align_right: bool) -> None: ...

def fetch_images(
    images: Optional[Dict[str, Image]] = ...,
    image_sources: Optional[Dict[str, str]] = ...,
    image_paths: Optional[List[str]] = ...,
) -> Tuple[Dict[str, Image], Dict[str, str]]: ...
def resize(
    image: Image, width: Optional[int] = ..., height: Optional[int] = ...
) -> Image: ...

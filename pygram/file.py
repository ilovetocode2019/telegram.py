from io import BytesIO

class File:
    """A file to send"""

    def __init__(self, file: BytesIO, filename: str=None):
        self.file = file
        self.filename = filename
        
class Document(File):
    """
    A document to send

    Attributes
    ----------
    file: :class:`io.BytesIO`
        The document
    filename: Optional[:class:`str`]
        The filename of the document

    Parameters
    ----------
    file: :class:`io.BytesIO`
        The document
    filename: :class:`str`
        The filename of the document
    """

class Photo(File):
    """
    A photo to send

    Attributes
    ----------
    file: :class:`io.BytesIO`
        The photo
    filename: Optional[:class:`str`]
        The filename of the photo
    caption: Optional[:class:`str`]
        The caption of the photo

    Parameters
    ----------
    file: :class:`io.BytesIO`
        The photo
    filename: :class:`str`
        The filename of the photo
    caption: :class:`str`
        The caption of the photo
    """

    def __init__(self, file: BytesIO, filename: str=None, caption: str=None):
        super().__init__(file, filename)
        self.caption = caption
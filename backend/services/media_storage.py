import io
import os
import warnings
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageOps, UnidentifiedImageError
from werkzeug.utils import secure_filename


FORMAT_DETAILS = {
    "JPEG": ({"jpg", "jpeg"}, "jpg", "image/jpeg"),
    "PNG": ({"png"}, "png", "image/png"),
    "WEBP": ({"webp"}, "webp", "image/webp"),
    "GIF": ({"gif"}, "gif", "image/gif"),
}


class InvalidMedia(ValueError):
    pass


class MediaTooLarge(InvalidMedia):
    pass


@dataclass(frozen=True)
class StoredImage:
    filename: str
    storage_key: str
    file_type: str


class LocalMediaStorage:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save_image(self, uploaded_file, max_bytes, max_pixels):
        filename = secure_filename(uploaded_file.filename or "")
        if not filename or "." not in filename:
            raise InvalidMedia
        submitted_extension = filename.rsplit(".", 1)[1].casefold()

        content = uploaded_file.stream.read(max_bytes + 1)
        if len(content) > max_bytes:
            raise MediaTooLarge

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(io.BytesIO(content)) as probe:
                    image_format = probe.format
                    if image_format not in FORMAT_DETAILS:
                        raise InvalidMedia
                    extensions, stored_extension, mime_type = FORMAT_DETAILS[image_format]
                    if submitted_extension not in extensions:
                        raise InvalidMedia
                    if probe.width * probe.height > max_pixels:
                        raise InvalidMedia
                    if getattr(probe, "is_animated", False):
                        raise InvalidMedia
                    probe.verify()

                with Image.open(io.BytesIO(content)) as decoded:
                    decoded.load()
                    image = ImageOps.exif_transpose(decoded)
                    if image_format == "JPEG":
                        image = image.convert("RGB")
                    output = io.BytesIO()
                    image.save(output, format=image_format)
        except (
            InvalidMedia,
            UnidentifiedImageError,
            Image.DecompressionBombError,
            Image.DecompressionBombWarning,
            OSError,
            SyntaxError,
            ValueError,
        ) as error:
            if isinstance(error, InvalidMedia):
                raise
            raise InvalidMedia from error

        storage_key = f"{uuid4().hex}.{stored_extension}"
        temporary = self.root / f".{uuid4().hex}.tmp"
        destination = self.root / storage_key
        try:
            with temporary.open("xb") as handle:
                handle.write(output.getvalue())
            os.replace(temporary, destination)
        finally:
            temporary.unlink(missing_ok=True)
        return StoredImage(filename, storage_key, mime_type)

    def delete(self, storage_key):
        if storage_key:
            (self.root / storage_key).unlink(missing_ok=True)

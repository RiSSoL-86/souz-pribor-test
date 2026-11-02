import os
import uuid
from functools import partial
from typing import TYPE_CHECKING, final

if TYPE_CHECKING:
    from django.db.models import Model


@final
class FileUploadService:
    """Application-level operations for handling model file uploads."""

    @staticmethod
    def upload_file_handler_path(
        base_path: str, instance: Model, filename: str
    ) -> str:
        """Store the upload under ``base_path`` with a unique UUID name."""
        new_filename = str(uuid.uuid4())
        if "." in filename:
            extension = filename.split(".")[-1]
            new_filename = f"{new_filename}.{extension}"
        file_path = os.path.join(base_path, new_filename)
        return file_path

    @staticmethod
    def prefix_based_upload_handler(path: str) -> partial[str]:
        """Return a ``FileField.upload_to`` callable bound to ``path``."""
        return partial(FileUploadService.upload_file_handler_path, path)

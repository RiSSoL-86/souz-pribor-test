import os
import uuid
from unittest.mock import Mock, patch

from apps.common.services.file_uploadings import FileUploadService

FILE_UUID = uuid.UUID("12345678-1234-5678-1234-567812345678")


@patch(
    "apps.common.services.file_uploadings.uuid.uuid4",
    return_value=FILE_UUID,
)
def test_upload_path_preserves_final_extension(mock_uuid: Mock) -> None:
    """Create a unique upload name while preserving the final extension."""
    path = FileUploadService.upload_file_handler_path(
        "documents",
        Mock(),
        "report.final.pdf",
    )

    assert path == os.path.join("documents", f"{FILE_UUID}.pdf")
    mock_uuid.assert_called_once_with()


@patch(
    "apps.common.services.file_uploadings.uuid.uuid4",
    return_value=FILE_UUID,
)
def test_upload_path_handles_extensionless_filename(mock_uuid: Mock) -> None:
    """Create a unique upload name for an extensionless source file."""
    path = FileUploadService.upload_file_handler_path(
        "documents",
        Mock(),
        "README",
    )

    assert path == os.path.join("documents", str(FILE_UUID))
    mock_uuid.assert_called_once_with()


@patch(
    "apps.common.services.file_uploadings.uuid.uuid4",
    return_value=FILE_UUID,
)
def test_prefix_handler_binds_upload_directory(mock_uuid: Mock) -> None:
    """Bind a reusable upload handler to a directory prefix."""
    handler = FileUploadService.prefix_based_upload_handler("avatars")

    path = handler(Mock(), "profile.png")

    assert path == os.path.join("avatars", f"{FILE_UUID}.png")
    mock_uuid.assert_called_once_with()

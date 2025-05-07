import io
import pytest
from unittest.mock import patch
from minio.error import S3Error
from app.services import minio_service


# ------------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------------
@pytest.fixture
def dummy_file():
    return io.BytesIO(b"fake_image_data")


# ------------------------------------------------------------------------
# upload_profile_picture()
# ------------------------------------------------------------------------
def test_upload_profile_picture_success(dummy_file):
    filename = "test-image.jpg"
    with patch.object(minio_service.minio_client, "put_object", return_value=None):
        url = minio_service.upload_profile_picture(dummy_file, filename)

    assert url == f"http://localhost:9000/{minio_service.BUCKET_NAME}/{filename}"


def test_upload_profile_picture_failure(dummy_file):
    err = S3Error(
        "InvalidAccessKeyId",  # code
        "Failed",              # message
        "bucket/object",       # resource
        "123",                 # request_id
        "host",                # host_id
        None                   # response (None is fine for tests)
    )
    with patch.object(minio_service.minio_client, "put_object", side_effect=err):
        with pytest.raises(S3Error):
            minio_service.upload_profile_picture(dummy_file, "error.jpg")


# ------------------------------------------------------------------------
# ensure_bucket_exists() – success branches
# ------------------------------------------------------------------------
@patch.object(minio_service.minio_client, "bucket_exists", return_value=True)
def test_ensure_bucket_exists_bucket_already_exists(mock_exists):
    minio_service.ensure_bucket_exists()


@patch.object(minio_service.minio_client, "bucket_exists", return_value=False)
@patch.object(minio_service.minio_client, "make_bucket")
def test_ensure_bucket_exists_creates_bucket(mock_make_bucket, mock_exists):
    minio_service.ensure_bucket_exists()
    mock_make_bucket.assert_called_once_with(minio_service.BUCKET_NAME)


# ------------------------------------------------------------------------
# ensure_bucket_exists() – retry logic branches
# ------------------------------------------------------------------------
def test_ensure_bucket_exists_retries_then_succeeds():
    """
    First four bucket_exists calls raise, fifth returns True → no exception.
    Covers retry loop success path.
    """
    side_effects = [Exception("tmp down")] * 4 + [True]
    with patch.object(minio_service.minio_client, "bucket_exists", side_effect=side_effects):
        with patch.object(minio_service, "time") as mock_time:
            mock_time.sleep.return_value = None   # skip real sleeps
            minio_service.ensure_bucket_exists()  # should complete without error


def test_ensure_bucket_exists_fails_after_retries():
    """
    bucket_exists keeps raising → ensure_bucket_exists should re‑raise after
    all retries exhausted.  Covers retry loop failure path.
    """
    with patch.object(minio_service.minio_client, "bucket_exists", side_effect=Exception("still down")):
        with patch.object(minio_service, "time") as mock_time:
            mock_time.sleep.return_value = None
            with pytest.raises(Exception):
                minio_service.ensure_bucket_exists()

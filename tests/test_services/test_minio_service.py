import io
import pytest
from app.services.minio_service import upload_profile_picture

@pytest.fixture
def dummy_file():
    # Create a dummy image file in memory
    return io.BytesIO(b"fake_image_data")

def test_upload_profile_picture_success(dummy_file):
    filename = "test-image.jpg"
    url = upload_profile_picture(dummy_file, filename)

    assert url.startswith("http://localhost:9000/profile-pictures/")
    assert filename in url

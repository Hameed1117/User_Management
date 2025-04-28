import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_picture_api_success():
    file_content = b"test image data"
    response = client.post(
        "/profile/upload-picture",
        files={"file": ("test.jpg", io.BytesIO(file_content), "image/jpeg")}
    )

    assert response.status_code == 200
    data = response.json()
    assert "file_url" in data
    assert data["file_url"].startswith("http://localhost:9000/profile-pictures/")

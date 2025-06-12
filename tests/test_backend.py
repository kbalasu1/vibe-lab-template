import pytest
from fastapi.testclient import TestClient
from src.backend.main import app
import base64
import os
import json
from unittest.mock import patch, MagicMock

client = TestClient(app)

# Test data
SAMPLE_RESPONSE = {
    "analysis": {
        "description": "Test description",
        "colorTones": "Test color tones",
        "coreApparel": "Test core apparel",
        "accessories": "Test accessories"
    },
    "fashionTips": ["Tip 1", "Tip 2"],
    "suggestedItems": [
        {
            "name": "Test Item",
            "description": "Test description",
            "imageUrl": "https://test.com/image",
            "productUrl": "https://test.com/product"
        }
    ]
}

def test_read_root():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Style-Finder API"}

def test_analyze_invalid_file():
    """Test uploading an invalid file type"""
    files = {"file": ("test.txt", "test content", "text/plain")}
    response = client.post("/api/analyze", files=files)
    assert response.status_code == 400
    assert "not an image" in response.json()["detail"]

@pytest.fixture
def sample_image():
    """Create a small test image"""
    import numpy as np
    from PIL import Image
    img = Image.fromarray(np.zeros((100, 100, 3), dtype=np.uint8))
    img_path = "test_image.jpg"
    img.save(img_path)
    yield img_path
    os.remove(img_path)

@patch("src.backend.main.client.chat.completions.create")
def test_analyze_valid_image(mock_create, sample_image):
    """Test analyzing a valid image"""
    # Mock the OpenAI response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = """### 1. Description
Test description
### 2. Color Tones
Test color tones
### 3. Core Apparel
Test core apparel
### 4. Accessories
Test accessories
### 5. Fashion Tips
- Tip 1
- Tip 2
### 6. Similar Items
1. Test Item
   - Description: Test description"""
    
    mock_create.return_value = mock_response

    with open(sample_image, "rb") as f:
        files = {"file": ("test.jpg", f, "image/jpeg")}
        response = client.post("/api/analyze", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert "analysis" in data
    assert "fashionTips" in data
    assert "suggestedItems" in data

def test_analyze_missing_file():
    """Test the analyze endpoint without a file"""
    response = client.post("/api/analyze")
    assert response.status_code == 422  # FastAPI validation error

@patch("src.backend.main.client.chat.completions.create")
def test_gpt4v_error_handling(mock_create):
    """Test error handling when GPT-4V API fails"""
    mock_create.side_effect = Exception("API Error")
    
    # Create a test image file
    files = {"file": ("test.jpg", b"fake image content", "image/jpeg")}
    response = client.post("/api/analyze", files=files)
    
    assert response.status_code == 500
    assert "API call failed" in response.json()["detail"] 
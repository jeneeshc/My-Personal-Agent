import pytest
from services.google_auth_service import GoogleAuthService

def test_google_auth_service_structure():
    """Test GoogleAuthService instantiation and credential loading."""
    auth_service = GoogleAuthService()
    assert auth_service.email == "jeneeshc@gmail.com"
    result = auth_service.test_connection()
    assert result["email"] == "jeneeshc@gmail.com"
    assert "status" in result

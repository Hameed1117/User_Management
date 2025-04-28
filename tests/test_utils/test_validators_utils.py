import pytest
from app.utils import validators

def test_validate_email_address_valid():
    """
    Test that a valid email address passes validation.
    """
    valid_email = "testuser@gmail.com"  # changed to real domain
    assert validators.validate_email_address(valid_email) is True

def test_validate_email_address_invalid():
    """
    Test that an invalid email address fails validation.
    """
    invalid_email = "invalid-email"
    assert validators.validate_email_address(invalid_email) is False

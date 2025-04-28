import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.email_service import EmailService
from app.utils.template_manager import TemplateManager
from app.models.user_model import User

@pytest.fixture
def mock_template_manager():
    tm = MagicMock(spec=TemplateManager)
    tm.render_template.return_value = "<html>Email Content</html>"
    return tm

@pytest.fixture
def email_service(mock_template_manager):
    return EmailService(template_manager=mock_template_manager)

@pytest.mark.asyncio
async def test_send_user_email_success(email_service):
    user_data = {
        "name": "John",
        "verification_url": "http://example.com/verify",
        "email": "testuser@gmail.com"
    }
    with patch.object(email_service.smtp_client, 'send_email', return_value=None):
        await email_service.send_user_email(user_data, 'email_verification')
    # If no exception, it passes

@pytest.mark.asyncio
async def test_send_user_email_invalid_type(email_service):
    user_data = {
        "name": "John",
        "verification_url": "http://example.com/verify",
        "email": "testuser@gmail.com"
    }
    with pytest.raises(ValueError, match="Invalid email type"):
        await email_service.send_user_email(user_data, 'invalid_type')

@pytest.mark.asyncio
async def test_send_verification_email(email_service):
    user = User(
        id="1234abcd-5678-efgh-ijkl-9876mnopqrst",
        first_name="John",
        email="testuser@gmail.com",
        verification_token="sometoken"
    )
    with patch.object(email_service.smtp_client, 'send_email', return_value=None):
        await email_service.send_verification_email(user)
    # If no exception, it passes

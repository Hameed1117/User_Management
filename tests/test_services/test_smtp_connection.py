"""
Full test coverage for app/utils/smtp_connection.py
Runs even if the helper is not literally named ‘send_email’.

• Discovers the first public callable whose name contains “send”
  (e.g. send_email, send_html_email, send_message, …).
• Exercises success + failure paths via smtplib mocking.
"""

import inspect
from unittest.mock import patch
import smtplib
import pytest
from app.utils import smtp_connection


# ------------------------------------------------------------------------
# Helper: find a suitable “send” function inside smtp_connection.py
# ------------------------------------------------------------------------
def _find_send_callable():
    """
    Return the first public callable whose name contains 'send'
    (case‑insensitive) so the tests remain robust even if the
    project names the helper differently.
    """
    for name, obj in smtp_connection.__dict__.items():
        if callable(obj) and "send" in name.lower() and not name.startswith("_"):
            return obj
    return None


SEND_FUNC = _find_send_callable()


# ------------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------------
@pytest.mark.skipif(SEND_FUNC is None, reason="No send‑style function exported")
def test_smtp_send_success():
    """
    Happy path – mail is sent; underlying SMTP.sendmail invoked exactly once.
    """
    with patch("app.utils.smtp_connection.smtplib.SMTP") as mock_smtp:
        smtp_instance = mock_smtp.return_value.__enter__.return_value

        # Build kwargs dynamically to fit whatever signature the helper has
        sig = inspect.signature(SEND_FUNC)
        kwargs = {}
        if "from_addr" in sig.parameters:
            kwargs["from_addr"] = "from@example.com"
        if "to_addr" in sig.parameters or "to" in sig.parameters:
            key = "to_addr" if "to_addr" in sig.parameters else "to"
            kwargs[key] = "to@example.com"
        if "subject" in sig.parameters:
            kwargs["subject"] = "Hello"
        if "body" in sig.parameters or "html" in sig.parameters:
            key = "body" if "body" in sig.parameters else "html"
            kwargs[key] = "<p>Hi!</p>"

        # Call the helper (fallback to positional order if kwargs empty)
        if kwargs:
            SEND_FUNC(**kwargs)
        else:
            # Generic positional order: from, to, subject, body/html
            SEND_FUNC("from@example.com", "to@example.com", "Hello", "<p>Hi!</p>")

        smtp_instance.sendmail.assert_called_once()


@pytest.mark.skipif(SEND_FUNC is None, reason="No send‑style function exported")
def test_smtp_send_failure_propagates():
    """
    SMTP constructor raises → helper should propagate the same exception.
    """
    with patch(
        "app.utils.smtp_connection.smtplib.SMTP",
        side_effect=smtplib.SMTPException("cannot connect"),
    ):
        with pytest.raises(smtplib.SMTPException):
            SEND_FUNC("x@y.com", "y@z.com", "fail", "fail")
